import logging
from abc import ABC, abstractmethod

import numpy as np
from newclid.api import GeometricSolverBuilder
from newclid.jgex.formulation import JGEXFormulation
from newclid.problem import ProblemSetup
from newclid.proof_state import ProofBuildError, ProofState
from newclid.run_loop import RunInfos
from py_yuclid.yuclid_adapter import YuclidError

LOGGER = logging.getLogger(__name__)


class SolverInterface(ABC):
    @abstractmethod
    def solve_problem(
        self,
        nc_problem: ProblemSetup,
        rng: np.random.Generator,
        sub_problem: JGEXFormulation,
        larger_problem: JGEXFormulation,
    ) -> tuple[RunInfos, ProofState]:
        """Solve a subproblem ."""


class SolverError(Exception):
    """Error when solving a problem."""


class NewclidSolver(SolverInterface):
    def solve_problem(
        self,
        nc_problem: ProblemSetup,
        rng: np.random.Generator,
        sub_problem: JGEXFormulation,
        larger_problem: JGEXFormulation,
    ) -> tuple[RunInfos, ProofState]:
        try:
            solver = GeometricSolverBuilder(rng=rng).build(nc_problem)
            solver.run()
        except YuclidError as e:
            error_msg = (
                f"Error when solving subproblem {sub_problem} within larger problem {larger_problem}: {e}."
                f"\nNcProblem: {nc_problem.model_dump_json()}"
            )
            LOGGER.error(error_msg)
            raise SolverError(error_msg) from e
        except ProofBuildError as e:
            error_msg = (
                f"Error when building proof state for subproblem {sub_problem} within larger problem {larger_problem}: {e}."
                f"\nNcProblem: {nc_problem.model_dump_json()}"
            )
            LOGGER.error(error_msg)
            raise SolverError(error_msg) from e

        if solver.run_infos is None:
            raise ValueError("Solver should have ran")  # pragma: no cover

        return (
            solver.run_infos,
            solver.proof_state,
        )
