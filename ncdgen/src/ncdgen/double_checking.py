from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import networkx as nx
import numpy as np
from newclid.jgex.clause import JGEXClause, order_clauses_by_points_construction_order
from newclid.jgex.constructions import ALL_JGEX_CONSTRUCTIONS_BY_NAME
from newclid.jgex.definition import input_points_of_clause
from newclid.jgex.formulation import JGEXFormulation, alphabetize
from newclid.jgex.jgex_setup_data import JGEXSetupData, jgex_clauses_to_setup_data
from newclid.jgex.to_newclid import (
    JGEXClauseConsequences,
    rename_points_in_clause_consequences,
)
from newclid.llm_input import TrainingDatapoint
from newclid.predicate_types import PredicateArgument
from newclid.problem import (
    ProblemSetup,
    filter_points_from_nc_problem,
    rename_points_in_nc_problem,
    rename_predicate_construction,
)
from newclid.proof_data import ProofData, proof_data_from_state
from newclid.run_loop import RunInfos
from pydantic import BaseModel

if TYPE_CHECKING:
    from ncdgen.solver import SolverInterface

LOGGER = logging.getLogger(__name__)


class SingleDoubleCheckStatistics(BaseModel):
    setup_clauses: list[str]
    """The setup clauses in JGEX format."""
    aux_clauses_used: list[str]
    """The aux clauses that were used in this double check in JGEX format."""
    aux_clauses_unused: list[str]
    """The aux clauses that were not used in this double check in JGEX format."""
    alpha_mapping: dict[PredicateArgument, PredicateArgument]
    """The mapping from the original points to the alphabetized points."""
    run_infos: RunInfos
    """The statistics for the solver run on the subproblem."""
    double_check_setup: JGEXSetupData
    """The double-checked proof data of the subproblem in case it was solvable."""
    double_check_proof: ProofData | None
    """The double-checked proof data of the subproblem in case it was solvable."""


class DoubleCheckStatistics(BaseModel):
    """Statistics for a double check run."""

    single_double_check_stats: list[SingleDoubleCheckStatistics]
    """Statistics for each aux double check."""
    true_aux_clauses: list[str]
    """The double-checked true aux clauses."""
    false_positive_aux_clauses: list[str]
    """The double-checked false positive aux clauses."""
    final_proof: ProofData | None
    """The final double-checked proof data of the subproblem with all and only true aux clauses."""
    training_data: TrainingDatapoint | None
    """The alphabetized i/o training data for the subproblem for each aux construction in it plus the proof to predict."""


def do_double_check(
    subproblem: JGEXFormulation,
    larger_problem: JGEXFormulation,
    large_nc_problem: ProblemSetup,
    clauses_consequences: dict[JGEXClause, JGEXClauseConsequences],
    solver: SolverInterface,
    aux_tag: str,
    rng: np.random.Generator,
) -> DoubleCheckStatistics:
    assert len(subproblem.auxiliary_clauses) > 0, (
        "Aux clauses are required for double check"
    )

    double_check_start_time = time.perf_counter()

    double_check_single_stats: list[SingleDoubleCheckStatistics] = []

    # First check if the problem is solvable without any aux clauses and if so return the proof
    no_aux_double_check_stats = _double_check_with_aux_clauses(
        subproblem=subproblem,
        large_nc_problem=large_nc_problem,
        larger_problem=larger_problem,
        aux_clauses_used=[],
        aux_clauses_unused=list(subproblem.auxiliary_clauses),
        clauses_consequences=clauses_consequences,
        solver=solver,
        rng=rng,
    )
    double_check_single_stats.append(no_aux_double_check_stats)

    if no_aux_double_check_stats.double_check_proof is not None:
        LOGGER.warning(
            "(---) False positive aux constructions, solved without any of them: "
            "Setup: %s. Auxiliary constructions: %s. Goals: %s. With mapping: %s from larger problem: %s",
            no_aux_double_check_stats.setup_clauses,
            [str(clause) for clause in subproblem.auxiliary_clauses],
            subproblem.goals,
            no_aux_double_check_stats.alpha_mapping,
            larger_problem,
        )
        return DoubleCheckStatistics(
            single_double_check_stats=double_check_single_stats,
            true_aux_clauses=[],
            false_positive_aux_clauses=[
                str(clause) for clause in subproblem.auxiliary_clauses
            ],
            final_proof=no_aux_double_check_stats.double_check_proof,
            training_data=None,
        )

    valid_aux_clauses: set[JGEXClause] = set()
    rejected_aux_clauses: set[JGEXClause] = set()

    points_requirements_graph = points_requirements_graph_from_jgex_clauses(
        list(subproblem.clauses)
    )

    for point in reversed(list(nx.topological_sort(points_requirements_graph))):
        clause_tested = points_requirements_graph.nodes[point]["clause"]
        if clause_tested not in subproblem.auxiliary_clauses:
            continue
        if clause_tested in valid_aux_clauses or clause_tested in rejected_aux_clauses:
            continue

        clause_descendants = _descendants_clauses(points_requirements_graph, point)
        aux_clauses_used: list[JGEXClause] = []
        aux_clauses_unused: list[JGEXClause] = []
        for clause in subproblem.auxiliary_clauses:
            if clause == clause_tested or clause in clause_descendants:
                aux_clauses_unused.append(clause)
            else:
                aux_clauses_used.append(clause)

        double_check_stats = _double_check_with_aux_clauses(
            subproblem=subproblem,
            larger_problem=larger_problem,
            large_nc_problem=large_nc_problem,
            aux_clauses_used=aux_clauses_used,
            aux_clauses_unused=aux_clauses_unused,
            clauses_consequences=clauses_consequences,
            solver=solver,
            rng=rng,
        )
        double_check_single_stats.append(double_check_stats)

        if double_check_stats.double_check_proof is None:
            # If we could not solve the problem without the aux clause, then all the aux clauses in the ancestors are required
            valid_aux_clauses.add(clause_tested)
            ancestors_clauses = _ancestors_clauses(points_requirements_graph, point)
            ancestors_aux_clauses = [
                clause
                for clause in ancestors_clauses
                if clause in subproblem.auxiliary_clauses
            ]
            valid_aux_clauses.update(ancestors_aux_clauses)
        else:
            # If we could solve the problem without the aux clause, then itself can be rejected
            rejected_aux_clauses.add(clause_tested)

    # Now we need to check if we can solve the problem with the all valid aux clauses (and get the proof_data)
    ordered_valid_aux_clauses = order_clauses_by_points_construction_order(
        list(valid_aux_clauses)
    )
    ordered_rejected_aux_clauses: list[JGEXClause] = [
        clause
        for clause in subproblem.auxiliary_clauses
        if clause not in ordered_valid_aux_clauses
    ]

    final_double_check_stats = _double_check_with_aux_clauses(
        subproblem=subproblem,
        larger_problem=larger_problem,
        large_nc_problem=large_nc_problem,
        aux_clauses_used=ordered_valid_aux_clauses,
        aux_clauses_unused=ordered_rejected_aux_clauses,
        clauses_consequences=clauses_consequences,
        solver=solver,
        rng=rng,
    )
    double_check_single_stats.append(final_double_check_stats)

    double_check_time = time.perf_counter() - double_check_start_time
    if final_double_check_stats.double_check_proof is None:
        LOGGER.warning(
            "Could not solve even all aux clauses in %.2fs found for %s. "
            "Aux clauses: %s. Setup: %s. In larger problem: %s",
            double_check_time,
            subproblem,
            [str(clause) for clause in subproblem.auxiliary_clauses],
            list(subproblem.setup_clauses),
            larger_problem,
        )
        return DoubleCheckStatistics(
            single_double_check_stats=double_check_single_stats,
            true_aux_clauses=[],
            false_positive_aux_clauses=[
                str(clause) for clause in subproblem.auxiliary_clauses
            ],
            final_proof=None,
            training_data=None,
        )

    conclusion_message = (
        "(!!!) Found valid aux construction"
        if valid_aux_clauses
        else "(...) False positive aux construction, no valid aux after graph traversal"
    )
    LOGGER.warning(
        f"{conclusion_message} in {double_check_time:.2f}s: Goal: {subproblem.goals}."
        f" Aux clauses: '{final_double_check_stats.aux_clauses_used}'. Setup: '{final_double_check_stats.setup_clauses}'."
        f" Rejected aux clauses: {final_double_check_stats.aux_clauses_unused}."
        f" With mapping {final_double_check_stats.alpha_mapping} from larger problem: {larger_problem}.",
    )

    final_proof = final_double_check_stats.double_check_proof
    return DoubleCheckStatistics(
        single_double_check_stats=double_check_single_stats,
        true_aux_clauses=final_double_check_stats.aux_clauses_used,
        false_positive_aux_clauses=final_double_check_stats.aux_clauses_unused,
        final_proof=final_proof,
        training_data=TrainingDatapoint.from_proof_data_aux_combinations(
            setup_data=final_double_check_stats.double_check_setup,
            proof_data=final_proof,
            aux_tag=aux_tag,
        ),
    )


def _double_check_with_aux_clauses(
    subproblem: JGEXFormulation,
    larger_problem: JGEXFormulation,
    large_nc_problem: ProblemSetup,
    aux_clauses_used: list[JGEXClause],
    aux_clauses_unused: list[JGEXClause],
    clauses_consequences: dict[JGEXClause, JGEXClauseConsequences],
    solver: SolverInterface,
    rng: np.random.Generator,
) -> SingleDoubleCheckStatistics:
    LOGGER.debug(
        "Running double check on %s. (n_aux_clauses_used=%s, n_aux_clauses_unused=%s)",
        subproblem,
        len(aux_clauses_used),
        len(aux_clauses_unused),
    )

    subproblem_with_only_used_aux_clauses = JGEXFormulation(
        setup_clauses=subproblem.setup_clauses,
        auxiliary_clauses=tuple(aux_clauses_used),
        goals=subproblem.goals,
    )
    alphabetized_jgex_subproblem, reverse_mapping = alphabetize(
        subproblem_with_only_used_aux_clauses
    )

    alpha_mapping = {v: k for k, v in reverse_mapping.items()}
    alphabetized_nc_subproblem = rename_points_in_nc_problem(
        filter_points_from_nc_problem(
            large_nc_problem, points_to_keep=list(alpha_mapping.keys())
        ),
        alpha_mapping,
    )
    alphabetized_nc_subproblem.goals = tuple(
        rename_predicate_construction(goal, alpha_mapping) for goal in subproblem.goals
    )

    run_infos, proof_state = solver.solve_problem(
        nc_problem=alphabetized_nc_subproblem,
        sub_problem=alphabetized_jgex_subproblem,
        larger_problem=larger_problem,
        rng=rng,
    )

    alphabetized_clauses_consequences: dict[JGEXClause, JGEXClauseConsequences] = {}
    for clause in subproblem_with_only_used_aux_clauses.clauses:
        alphabetized_clauses_consequences[clause.renamed(alpha_mapping)] = (
            rename_points_in_clause_consequences(
                clauses_consequences[clause], alpha_mapping
            )
        )

    double_checked_proof: ProofData | None = None
    setup_data, _predicates_ids = jgex_clauses_to_setup_data(
        setup_clauses=list(alphabetized_jgex_subproblem.setup_clauses),
        aux_clauses=list(alphabetized_jgex_subproblem.auxiliary_clauses),
        goals=list(subproblem.goals),
        clauses_consequences=alphabetized_clauses_consequences,
    )
    if run_infos.success:
        double_checked_proof = proof_data_from_state(
            goals_constructions=list(subproblem.goals),
            proof_state=proof_state,
        )

    return SingleDoubleCheckStatistics(
        setup_clauses=[
            str(clause) for clause in alphabetized_jgex_subproblem.setup_clauses
        ],
        aux_clauses_used=[
            str(clause) for clause in alphabetized_jgex_subproblem.auxiliary_clauses
        ],
        aux_clauses_unused=[str(clause) for clause in aux_clauses_unused],
        alpha_mapping=reverse_mapping,
        run_infos=run_infos,
        double_check_setup=setup_data,
        double_check_proof=double_checked_proof,
    )


def _descendants_clauses(
    graph: nx.DiGraph[PredicateArgument], point: PredicateArgument
) -> set[JGEXClause]:
    descendants = nx.descendants(graph, point)  # type: ignore
    return set(graph.nodes[descendant]["clause"] for descendant in descendants)


def _ancestors_clauses(
    graph: nx.DiGraph[PredicateArgument], point: PredicateArgument
) -> list[JGEXClause]:
    ancestors = nx.ancestors(graph, point)  # type: ignore
    clauses = set(graph.nodes[ancestor]["clause"] for ancestor in ancestors)
    return order_clauses_by_points_construction_order(list(clauses))


def points_requirements_graph_from_jgex_clauses(
    aux_clauses: list[JGEXClause],
) -> nx.DiGraph[PredicateArgument]:
    graph: nx.DiGraph[PredicateArgument] = nx.DiGraph()
    # Add nodes
    for clause in aux_clauses:
        for point in clause.points:
            graph.add_node(point, clause=clause)

    # Add edges
    for clause in aux_clauses:
        input_points = input_points_of_clause(clause, ALL_JGEX_CONSTRUCTIONS_BY_NAME)
        for point in clause.points:
            for input_point in input_points:
                graph.add_edge(input_point, point)
    return graph
