"""Helper functions to write proofs in a natural language."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional


from newclid.defs.clause import Construction
from newclid.statements.statement import Statement
import newclid.pretty as pt
import newclid.trace_back as trace_back

from newclid.dependencies.dependency import Dependency

if TYPE_CHECKING:
    from newclid.problem import Problem
    from newclid.proof import Proof


def extend_differences(x: list, y: list):
    for t in y:
        if t not in x:
            x.append(t)


def get_proof_steps(
    proof: "Proof", goals: list["Construction"], merge_trivials: bool = False
) -> tuple[
    list[Dependency],
    list[Dependency],
    list[tuple[list[Dependency], list[Dependency]]],
    dict[tuple[str, ...], int],
]:
    """Extract proof steps from the built DAG."""

    setup = []
    aux = []
    log = []
    setup_points = set()
    refs = {}

    for goal in goals:
        if not proof.check_construction(goal):
            continue

        goal_args = proof.symbols_graph.names2nodes(goal.args)
        goal = Statement(goal.name, goal_args)
        _setup, _aux, _log, _setup_points = trace_back.get_logs(
            goal, proof, merge_trivials=merge_trivials
        )

        _setup = trace_back.point_log(_setup, refs, set())
        _aux = trace_back.point_log(_aux, refs, setup_points)

        extend_differences(setup, [(prems, [tuple(p)]) for p, prems in _setup])
        extend_differences(aux, [(prems, [tuple(p)]) for p, prems in aux])
        extend_differences(log, _log)
        setup_points = setup_points.union(_setup_points)

    return setup, aux, log, refs


def natural_language_statement(logical_statement: Dependency) -> str:
    """Convert logical_statement to natural language.

    Args:
      logical_statement: pr.Dependency with .name and .args

    Returns:
      a string of (pseudo) natural language of the predicate for human reader.
    """
    names = [a.name.upper() for a in logical_statement.statement.args]
    return pt.pretty_nl(logical_statement.statement.name, names)


def proof_step_string(
    proof_step: tuple[list[Dependency], list[Dependency]],
    refs: dict[tuple[str, ...], int],
    last_step: bool,
) -> str:
    """Translate proof to natural language.

    Args:
      proof_step: pr.Dependency with .name and .args
      refs: dict(hash: int) to keep track of derived predicates
      last_step: boolean to keep track whether this is the last step.

    Returns:
      a string of (pseudo) natural language of the proof step for human reader.
    """
    premises, [conclusion] = proof_step

    premises_nl = " & ".join(
        [
            natural_language_statement(p)
            + " [{:02}]".format(refs[p.statement.hash_tuple])
            for p in premises
        ]
    )

    if not premises:
        premises_nl = "similarly"

    refs[conclusion.statement.hash_tuple] = len(refs)

    conclusion_nl = natural_language_statement(conclusion)
    if not last_step:
        conclusion_nl += " [{:02}]".format(refs[conclusion.statement.hash_tuple])

    return f"{premises_nl} \u21d2 {conclusion_nl}"


def write_solution(
    proof: "Proof", problem: "Problem", out_file: Optional[Path]
) -> None:
    """Output the solution to out_file.

    Args:
      proof: Proof state.
      problem: Containing the problem definition and theorems.
      out_file: file to write to, empty string to skip writing to file.
    """
    setup, aux, proof_steps, refs = get_proof_steps(
        proof, problem.goals, merge_trivials=False
    )

    solution = "\n=========================="
    solution += "\n * From theorem premises:\n"
    premises_nl = []
    for premises, [points] in setup:
        solution += " ".join([p.name.upper() for p in points]) + " "
        if not premises:
            continue
        premises_nl += [
            natural_language_statement(p)
            + " [{:02}]".format(refs[p.statement.hash_tuple])
            for p in premises
        ]
    solution += ": Points\n" + "\n".join(premises_nl)

    solution += "\n\n * Auxiliary Constructions:\n"
    aux_premises_nl = []
    for premises, [points] in aux:
        solution += " ".join([p.name.upper() for p in points]) + " "
        aux_premises_nl += [
            natural_language_statement(p)
            + " [{:02}]".format(refs[p.statement.hash_tuple])
            for p in premises
        ]
    solution += ": Points\n" + "\n".join(aux_premises_nl)

    # some special case where the deduction rule has a well known name.
    r2name = {
        "r32": "(SSS 32)",
        "r33": "(SAS 33)",
        "r34": "(Similar Triangles 34)",
        "r35": "(Similar Triangles 35)",
        "r36": "(ASA 36)",
        "r37": "(ASA 37)",
        "r38": "(Similar Triangles 38)",
        "r39": "(Similar Triangles 39)",
        "r40": "(Congruent Triangles 40)",
        "a00": "(Distance chase)",
        "a01": "(Ratio chase)",
        "a02": "(Angle chase)",
    }

    solution += "\n\n * Proof steps:\n"
    for i, step in enumerate(proof_steps):
        _, [con] = step
        nl = proof_step_string(step, refs, last_step=i == len(proof_steps) - 1)
        reason_name = con.reason.name if con.reason else ""
        reason_pretty = r2name.get(reason_name, f"({reason_name})")
        nl = nl.replace("\u21d2", f"{reason_pretty}\u21d2 ")
        solution += (
            "{:03}. ".format(i + 1)
            + nl
            + ("(*)" if con.statement in proof.goals_as_statements() else "")
            + "\n"
        )

    solution += "==========================\n"
    logging.info(solution)
    if out_file is not None:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(solution)
        logging.info("Solution written to %s.", out_file)
