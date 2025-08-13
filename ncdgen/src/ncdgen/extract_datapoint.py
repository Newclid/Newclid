from __future__ import annotations

import logging
import time
import traceback
from collections import defaultdict
from typing import cast

import numpy as np
import yaml
from newclid.agent.ddarn import DDARNStats
from newclid.jgex.clause import JGEXClause
from newclid.jgex.formulation import JGEXFormulation, alphabetize
from newclid.predicates._index import PredicateType
from newclid.problem import PredicateConstruction, ProblemSetup
from newclid.proof_data import ProofData, proof_data_from_state
from newclid.proof_writing import write_proof
from pydantic import BaseModel

from ncdgen.aux_discriminators import discriminator_from_name
from ncdgen.build_diagram import Diagram, DiagramGenerationMetadata, build_diagram
from ncdgen.constructions import load_constructions
from ncdgen.double_checking import DoubleCheckStatistics, do_double_check
from ncdgen.extract_subproblems import extract_subproblems_and_their_dependencies
from ncdgen.generation_configuration import (
    DiagramGenerationConfig,
    sample_sweep_parameters,
)
from ncdgen.solver import SolverError, SolverInterface

LOGGER = logging.getLogger(__name__)

FREE, INTERSECT, OTHER = load_constructions()


class SubProblemDatapoint(BaseModel):
    double_check_statistics: DoubleCheckStatistics | None = None
    """When double-checking, we store the statistics for the solver run on the subproblem with specific aux or not."""
    subproblem_str: str
    """The non-alphabetized subproblem JGEX string. Includes all potential auxiliary constructions."""
    alphabetized_subproblem_str: str
    """The alphabetized subproblem JGEX string. Includes all potential auxiliary constructions."""
    sub_problem_proof: ProofData
    """The entire proof content extracted from the subproblem."""
    level_predicate_count: list[tuple[int, PredicateType, int]] | None = None
    """How many predicates of each type do we have at each DDARN level of the diagram."""
    solution_natural_language: str
    """The proof of the subproblem in natural language."""
    larger_problem: str
    """The JGEX string of the larger problem that the subproblem is a part of. """
    larger_nc_problem: ProblemSetup
    """The full setting with points coordinates of the larger problem that the subproblem is a part of."""

    @property
    def has_double_checked_aux_construction(self) -> bool:
        """Whether the subproblem has an aux construction or not"""
        if self.double_check_statistics is None:
            return False
        return len(self.double_check_statistics.true_aux_clauses) > 0


SKIPPED_PREDICATES_AS_GOAL: set[PredicateType] = {
    PredicateType.SQUARED_CONSTANT_LENGTH,
    PredicateType.SQUARED_CONSTANT_RATIO,
    PredicateType.CONSTANT_RATIO,
    PredicateType.SIMTRI_CLOCK,
    PredicateType.SIMTRI_REFLECT,
    PredicateType.CONTRI_CLOCK,
    PredicateType.CONTRI_REFLECT,
}


def generate_subproblems_datapoints(
    generation_config: DiagramGenerationConfig,
    seed: bytes,
    jgex_solver: SolverInterface,
) -> tuple[list[SubProblemDatapoint], DiagramGenerationMetadata]:
    rng = np.random.default_rng(
        int.from_bytes(seed, byteorder="big", signed=False) % 2**32
    )

    sweep_config = sample_sweep_parameters(generation_config, rng)
    LOGGER.debug(
        "Sweep selection:\n%s", yaml.dump(sweep_config.model_dump(mode="json"))
    )

    diagram, metadata = build_diagram(
        generation_config,
        sweep_config,
        free=FREE,
        intersect=INTERSECT,
        other=OTHER,
        rng=rng,
    )
    if diagram is None:
        LOGGER.info("Failed to build diagram.")
        return [], metadata

    n_pts = sum(len(c.points) for c in diagram.jgex_problem.clauses)
    LOGGER.info(
        f"Built {n_pts}-point diagram in {metadata.diagram_construction_time_sec:.2f}s"
    )

    setup_description = f"{n_pts}-point diagram {diagram.jgex_problem}"
    get_dependencies_start_time = time.perf_counter()
    try:
        LOGGER.debug(f"Running solver on generated {setup_description}")
        diagram.solver.run()
        run_time = time.perf_counter() - get_dependencies_start_time
        metadata.saturation_time_sec = run_time
        metadata.saturation_succeeded = True
        metadata.agent_saturation_stats = diagram.solver.deductive_agent.get_stats()
        LOGGER.debug(f"Exausted diagram in {run_time:.2f}s")
    except Exception as e:
        LOGGER.error(
            f"Error when running solver on the diagram: {e}\n{traceback.format_exc()}"
        )
        metadata.saturation_time_sec = time.perf_counter() - get_dependencies_start_time
        metadata.saturation_succeeded = False
        metadata.agent_saturation_stats = diagram.solver.deductive_agent.get_stats()
        return [], metadata

    LOGGER.debug(f"Extracting subgoals from {setup_description}")
    aux_discriminator = discriminator_from_name(generation_config.aux_discriminator)
    subproblems = extract_subproblems_and_their_dependencies(
        diagram, aux_discriminator=aux_discriminator
    )
    subproblems_with_aux = [s for s in subproblems if s.auxiliary_clauses]
    LOGGER.info(
        f"Found {len(subproblems)} ({len(subproblems_with_aux)} aux) potential subgoals in {run_time:.2f}s"
    )

    if generation_config.emit_only_double_checked_aux_subproblems:
        LOGGER.debug(
            f"Processing only the {len(subproblems_with_aux)} aux subgoals.",
        )
        subproblems = subproblems_with_aux

    if not subproblems:
        LOGGER.debug("No subgoals found. Exiting.")
        return [], metadata

    goal_predicate_types = set(s.goals[0].predicate_type for s in subproblems)
    subgoal_processed_per_predicate: dict[PredicateType, int] = defaultdict(lambda: 0)
    n_subgoal_per_predicate: dict[PredicateType, int] = {
        predicate_type: sum(
            1
            for subproblem in subproblems
            if subproblem.goals[0].predicate_type == predicate_type
        )
        for predicate_type in goal_predicate_types
    }
    LOGGER.info(
        f"Processing {len(subproblems)} subgoals {[(p.value, n) for p, n in n_subgoal_per_predicate.items()]}"
        f" found in {run_time:.2f}s. On {setup_description}"
    )

    datapoints: list[SubProblemDatapoint] = []
    blacklisted_aux_setup_pairs: set[tuple[str, str]] = set()

    for subproblem in rng.permuted(np.array(subproblems)):
        subproblem = cast(JGEXFormulation, subproblem)
        subgoal = subproblem.goals[0]
        if subgoal.predicate_type in SKIPPED_PREDICATES_AS_GOAL:
            LOGGER.debug("Skipping subgoal %s by its predicate.", subgoal)
            continue

        goal_predicate_type = subgoal.predicate_type
        if generation_config.max_check_per_predicate > 0:
            if all(
                subgoal_processed_per_predicate[predicate_type]
                >= generation_config.max_check_per_predicate
                for predicate_type in goal_predicate_types
            ):
                LOGGER.info(
                    "Reached the limit of %s processed subgoals per predicate for all predicates %s. Exiting.",
                    generation_config.max_check_per_predicate,
                    tuple(subgoal_processed_per_predicate.keys()),
                )
                break

            if (
                subgoal_processed_per_predicate[goal_predicate_type]
                >= generation_config.max_check_per_predicate
            ):
                LOGGER.debug(
                    "Skipping subgoal %s because its predicate has reached the limit of %s processed subgoals per predicate.",
                    subproblem,
                    generation_config.max_check_per_predicate,
                )
                continue

        LOGGER.debug(f"Checking subgoal {subproblem}")
        try:
            subgoal_datapoint = _get_diagram_subproblem(
                diagram,
                goal=subgoal,
                setup_clauses=list(subproblem.setup_clauses),
                aux_clauses=list(subproblem.auxiliary_clauses),
            )

            if (
                subgoal_datapoint.sub_problem_proof.proof_rules_length
                < generation_config.min_rules_applied
            ):
                LOGGER.debug(
                    "Skipped short proof with only %s rule applications: %s.",
                    subgoal_datapoint.sub_problem_proof.proof_rules_length,
                    subgoal,
                )
                metadata.subproblem_summary_stats.skipped_not_enough_rules_applications_subproblems += 1
                continue

            subgoal_processed_per_predicate[goal_predicate_type] += 1
            should_double_check = (
                rng.random() < generation_config.double_check_probability
            )
            if should_double_check and subproblem.auxiliary_clauses:
                setup_clauses_txt = "; ".join(str(c) for c in subproblem.setup_clauses)
                aux_clauses_txt = "; ".join(
                    str(c) for c in subproblem.auxiliary_clauses
                )
                if (aux_clauses_txt, setup_clauses_txt) in blacklisted_aux_setup_pairs:
                    LOGGER.debug(
                        "Skipping double check on %s because it's a blacklisted aux setup pair: %s",
                        subproblem,
                        (aux_clauses_txt, setup_clauses_txt),
                    )
                    metadata.subproblem_summary_stats.skipped_blacklisted_aux_setup_pairs += 1
                    continue

                try:
                    subgoal_datapoint.double_check_statistics = do_double_check(
                        subproblem=subproblem,
                        larger_problem=diagram.jgex_problem,
                        large_nc_problem=diagram.nc_problem,
                        clauses_consequences=diagram.jgex_clauses_consequences,
                        solver=jgex_solver,
                        aux_tag=generation_config.aux_tag,
                        rng=rng,
                    )
                except SolverError:
                    blacklisted_aux_setup_pairs.add(
                        (aux_clauses_txt, setup_clauses_txt)
                    )
                    continue

                if (
                    not subgoal_datapoint.double_check_statistics.true_aux_clauses
                    and generation_config.skip_aux_setup_pairs_previous_false_positive
                ):
                    LOGGER.debug(
                        "Blacklisting aux setup pair that has no true aux: %s",
                        (aux_clauses_txt, setup_clauses_txt),
                    )
                    blacklisted_aux_setup_pairs.add(
                        (aux_clauses_txt, setup_clauses_txt)
                    )

        except ValueError as e:
            metadata.subproblem_summary_stats.unhandled_failure_to_build_subproblem_count += 1
            LOGGER.error(
                f"Error in querying result. problem: {diagram.jgex_problem}, subgoal: {subproblem}, exception: {e}"
            )
            LOGGER.error("Traceback:")
            LOGGER.error(traceback.format_exc())
            continue

        if (
            subgoal_datapoint.has_double_checked_aux_construction
            or not generation_config.emit_only_double_checked_aux_subproblems
        ):
            datapoints.append(subgoal_datapoint)

    return datapoints, metadata


def _get_diagram_subproblem(
    diagram: Diagram,
    goal: PredicateConstruction,
    setup_clauses: list[JGEXClause],
    aux_clauses: list[JGEXClause],
) -> SubProblemDatapoint:
    """Generate a subproblem datapoint from a given subgoal."""

    proof_data = proof_data_from_state(
        goals_constructions=[goal],
        proof_state=diagram.solver.proof_state,
    )

    nl_solution = write_proof(proof_data)

    agent_stats = diagram.solver.deductive_agent.get_stats()
    level_predicate_count = None
    if isinstance(agent_stats, DDARNStats):
        level_predicate_count = agent_stats.level_predicate_count

    jgex_subproblem = JGEXFormulation(
        setup_clauses=tuple(setup_clauses),
        auxiliary_clauses=tuple(aux_clauses),
        goals=(goal,),
    )
    alphabetized_jgex_subproblem, _mapping = alphabetize(jgex_subproblem)

    return SubProblemDatapoint(
        subproblem_str=str(jgex_subproblem),
        alphabetized_subproblem_str=str(alphabetized_jgex_subproblem),
        sub_problem_proof=proof_data,
        solution_natural_language=nl_solution,
        larger_problem=str(diagram.jgex_problem),
        level_predicate_count=level_predicate_count,
        larger_nc_problem=diagram.nc_problem,
    )
