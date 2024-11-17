import logging
from typing import TYPE_CHECKING
from newclid.ddar import get_proof_steps
from newclid.graph import Graph
from newclid.pretty import pretty_nl

if TYPE_CHECKING:
    from newclid.problem import Dependency, Problem


def write_solution(proof: "Graph", problem: "Problem", out_file: str) -> None:
    """Output the solution to out_file.

    Args:
      g: gh.Graph object, containing the proof state.
      p: Problem object, containing the theorem.
      out_file: file to write to, empty string to skip writing to file.
    """
    setup, aux, proof_steps, refs = get_proof_steps(
        proof, problem.goal, merge_trivials=False
    )

    solution = "\n=========================="
    solution += "\n * From theorem premises:\n"
    premises_nl = []
    for premises, [points] in setup:
        solution += " ".join([p.name.upper() for p in points]) + " "
        if not premises:
            continue
        premises_nl += [
            _natural_language_statement(p) + " [{:02}]".format(refs[p.hashed()])
            for p in premises
        ]
    solution += ": Points\n" + "\n".join(premises_nl)

    solution += "\n\n * Auxiliary Constructions:\n"
    aux_premises_nl = []
    for premises, [points] in aux:
        solution += " ".join([p.name.upper() for p in points]) + " "
        aux_premises_nl += [
            _natural_language_statement(p) + " [{:02}]".format(refs[p.hashed()])
            for p in premises
        ]
    solution += ": Points\n" + "\n".join(aux_premises_nl)

    # some special case where the deduction rule has a well known name.
    r2name = {
        "r32": "(SSS)",
        "r33": "(SAS)",
        "r34": "(Similar Triangles)",
        "r35": "(Similar Triangles)",
        "r36": "(ASA)",
        "r37": "(ASA)",
        "r38": "(Similar Triangles)",
        "r39": "(Similar Triangles)",
        "r40": "(Congruent Triangles)",
        "a00": "(Distance chase)",
        "a01": "(Ratio chase)",
        "a02": "(Angle chase)",
    }

    solution += "\n\n * Proof steps:\n"
    for i, step in enumerate(proof_steps):
        _, [con] = step
        nl = _proof_step_string(step, refs, last_step=i == len(proof_steps) - 1)
        rule_name = r2name.get(con.rule_name, "")
        nl = nl.replace("\u21d2", f"{rule_name}\u21d2 ")
        solution += "{:03}. ".format(i + 1) + nl + "\n"

    solution += "==========================\n"
    logging.info(solution)
    if out_file:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(solution)
        logging.info("Solution written to %s.", out_file)


def _proof_step_string(
    proof_step: "Dependency", refs: dict[tuple[str, ...], int], last_step: bool
) -> str:
    """Translate proof to natural language.

    Args:
      proof_step: Dependency with .name and .args
      refs: dict(hash: int) to keep track of derived predicates
      last_step: boolean to keep track whether this is the last step.

    Returns:
      a string of (pseudo) natural language of the proof step for human reader.
    """
    premises, [conclusion] = proof_step

    premises_nl = " & ".join(
        [
            _natural_language_statement(p) + " [{:02}]".format(refs[p.hashed()])
            for p in premises
        ]
    )

    if not premises:
        premises_nl = "similarly"

    refs[conclusion.hashed()] = len(refs)

    conclusion_nl = _natural_language_statement(conclusion)
    if not last_step:
        conclusion_nl += " [{:02}]".format(refs[conclusion.hashed()])

    return f"{premises_nl} \u21d2 {conclusion_nl}"


def _natural_language_statement(logical_statement: "Dependency") -> str:
    """Convert logical_statement to natural language.

    Args:
      logical_statement: Dependency with .name and .args

    Returns:
      a string of (pseudo) natural language of the predicate for human reader.
    """
    names = [a.name.upper() for a in logical_statement.args]
    names = [(n[0] + "_" + n[1:]) if len(n) > 1 else n for n in names]
    return pretty_nl(logical_statement.name, names)
