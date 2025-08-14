from typing import Self

from newclid.jgex.formulation import JGEXFormulation
from newclid.problem import ProblemSetup
from newclid.proof_state import ProofState
from newclid.run_loop import RunInfos
from numpy.random._generator import Generator as Generator

from ncdgen.solver import SolverInterface


class StubJGEXSolver(SolverInterface):
    def __init__(self):
        self._outputs_for_aux_clauses: dict[
            str,
            tuple[RunInfos, ProofState],
        ] = {}

    def with_outputs_for_problem_clauses(
        self, problem: JGEXFormulation, run_infos: RunInfos, proof_state: ProofState
    ) -> Self:
        key = str(problem)
        self._outputs_for_aux_clauses[key] = (run_infos, proof_state)
        return self

    def solve_problem(
        self,
        nc_problem: ProblemSetup,
        rng: Generator,
        sub_problem: JGEXFormulation,
        larger_problem: JGEXFormulation,
    ) -> tuple[RunInfos, ProofState]:
        assert nc_problem.goals == sub_problem.goals, (
            f"Nc problem goals {nc_problem.goals} do not match sub problem goals {sub_problem.goals}"
        )
        key = str(sub_problem)
        if key not in self._outputs_for_aux_clauses:
            raise ValueError(f"No given outputs for problem {sub_problem}")
        return self._outputs_for_aux_clauses[key]
