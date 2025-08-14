import cProfile
import logging
from pathlib import Path

import numpy as np
import pytest
from newclid.api import GeometricSolver, GeometricSolverBuilder
from newclid.jgex.formulation import JGEXFormulation, jgex_formulation_from_txt_file
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.problems import ALL_PROBLEMS
from newclid.problems.problem import Problem, ProblemFormulation

from .test_jgex_builds import PROBLEMS_EXPECTED_TO_FAIL_TO_BUILD

ROOT_PATH = Path(__file__).parent.parent
DATASET_PATH = ROOT_PATH.joinpath("problems_datasets")
LOGGER = logging.getLogger(__name__)

PROBLEMS_EXPECTED_TO_FAIL = [
    "breaking_cc_tangent",
    "breaking_cc_tangent_by_kiss",
    "breaking_cc_itangent",
    "breaking_cc_itangent_by_kiss",
    # Pythagorean theorem removed for now as it produces a lot of irrelevant predicates
    # due to the irrationality result not compatible with lengths being Fractions
    # TODO: Fix pythagorean theorem
    "pyt_test_formula_to_perp",
    "pyt_test_perp_to_formula",
    # Acompute is not supported by Yuclid
    "acompute_test",
    # Cannot prescribe numerical check as goal to Yuclid
    "numerical_check_npara",
    "numerical_check_ncoll",
]

PROBLEMS_NOT_SOLVED_BEFORE = [
    "two_goals_perp_cong",
    "worlds_hardest_easy_geometry_problem1",
    "worlds_hardest_easy_geometry_problem2",
    "double_angle_implies_central_angle_2",
    "menelaus_test",
    "menelaus_frac1_test",
    "menelaus_crossed_cong_test",
    "test_l2const",
    "2020_p1",
    "2008_p6",
    "2011_p6",
    "2015_p3",
    "2021_p3",
    "1983_p2",
    "1975_p3",
]


FAILLING_PROBLEMS_NOT_EXPECTED_TO_FAIL = [
    "1995_p1",
    "2009_sl_g3_excenters",
    "imo_sl_2023_p2_constr",
    "pappus",
    "imo_sl_2023_g4_constr",
]

LARGE_EXAMPLE_PROBLEMS = jgex_formulation_from_txt_file(
    DATASET_PATH.joinpath("large_examples.txt")
)


EXAMPLE_PROBLEMS = jgex_formulation_from_txt_file(DATASET_PATH.joinpath("examples.txt"))


def _filter_problems(problem_name: str) -> None:
    if problem_name in PROBLEMS_EXPECTED_TO_FAIL_TO_BUILD:
        pytest.skip("fails to even build")
    if problem_name in PROBLEMS_EXPECTED_TO_FAIL:
        pytest.xfail("expected to fail")
    if problem_name in PROBLEMS_NOT_SOLVED_BEFORE:
        pytest.skip("not solved before")
    if problem_name in FAILLING_PROBLEMS_NOT_EXPECTED_TO_FAIL:
        pytest.skip("not expected to fail")


@pytest.mark.parametrize(
    argnames="problem",
    argvalues=EXAMPLE_PROBLEMS.values(),
    ids=EXAMPLE_PROBLEMS.keys(),
)
def test_example_problems(problem: JGEXFormulation):
    _filter_problems(problem.name)
    match_logger = logging.getLogger("newclid.match_theorems")
    match_logger.setLevel(logging.INFO)
    rng = np.random.default_rng(42)
    problem_builder = JGEXProblemBuilder(rng).with_problem(problem)
    solver = GeometricSolverBuilder(rng).build(problem_builder.build())
    success = solver.run()
    assert success


@pytest.mark.slow
@pytest.mark.parametrize(
    argnames="problem",
    argvalues=LARGE_EXAMPLE_PROBLEMS.values(),
    ids=LARGE_EXAMPLE_PROBLEMS.keys(),
)
def test_large_example_problems(problem: JGEXFormulation):
    _filter_problems(problem.name)
    rng = np.random.default_rng(42)
    problem_builder = JGEXProblemBuilder(rng).with_problem(problem)
    solver: GeometricSolver = GeometricSolverBuilder(rng).build(problem_builder.build())
    match_logger = logging.getLogger("newclid.match_theorems")
    match_logger.setLevel(logging.INFO)
    profile = False
    if profile:
        prof = cProfile.Profile()
        success = prof.runcall(solver.run)
        profilings_path = Path(__file__).parent.joinpath(
            "large_example_problems_profiling"
        )
        profilings_path.mkdir(parents=True, exist_ok=True)
        profilings_file = str(profilings_path.joinpath(f"{problem.name}.prof"))
        prof.dump_stats(profilings_file)
    else:
        success = solver.run()

    print(solver.run_infos)
    assert success


IMO_PROBLEMS = jgex_formulation_from_txt_file(DATASET_PATH.joinpath("imo.txt"))


@pytest.mark.slow
@pytest.mark.parametrize(
    argnames="problem",
    argvalues=IMO_PROBLEMS.values(),
    ids=IMO_PROBLEMS.keys(),
)
def test_imo(problem: JGEXFormulation):
    _filter_problems(problem.name)
    rng = np.random.default_rng(42)
    jgex_problem_setup = (
        JGEXProblemBuilder(rng)
        .with_problem(problem)
        .include_auxiliary_clauses()
        .build()
    )
    solver: GeometricSolver = GeometricSolverBuilder(rng).build(jgex_problem_setup)
    match_logger = logging.getLogger("newclid.match_theorems")
    match_logger.setLevel(logging.INFO)
    success = solver.run()
    assert success


IMO_PROBLEMS_SL = jgex_formulation_from_txt_file(DATASET_PATH.joinpath("imo_sl.txt"))


@pytest.mark.slow
@pytest.mark.parametrize(
    argnames="problem",
    argvalues=IMO_PROBLEMS_SL.values(),
    ids=IMO_PROBLEMS_SL.keys(),
)
def test_imo_sl(problem: JGEXFormulation):
    _filter_problems(problem.name)
    rng = np.random.default_rng(42)
    jgex_problem_setup = (
        JGEXProblemBuilder(rng)
        .with_problem(problem)
        .include_auxiliary_clauses()
        .build()
    )
    solver: GeometricSolver = GeometricSolverBuilder(rng).build(jgex_problem_setup)
    match_logger = logging.getLogger("newclid.match_theorems")
    match_logger.setLevel(logging.INFO)
    success = solver.run()
    assert success


@pytest.mark.parametrize(
    argnames="problem,formulation",
    argvalues=[
        (problem, formulation)
        for problem in ALL_PROBLEMS
        for formulation in problem.formulations
    ],
    ids=[
        f"{problem.name} | {formulation.name}"
        for problem in ALL_PROBLEMS
        for formulation in problem.formulations
    ],
)
def test_problem_constants(problem: Problem, formulation: ProblemFormulation):
    jgex_logger = logging.getLogger("newclid.jgex")
    jgex_logger.setLevel(logging.INFO)
    match_logger = logging.getLogger("newclid.match_theorems")
    match_logger.setLevel(logging.INFO)

    rng = np.random.default_rng(42)

    formulation_version = formulation.formulation
    match formulation_version.formulation_type:
        case "jgex":
            problem_setup = (
                JGEXProblemBuilder(rng, max_attempts_per_clause=10)
                .with_problem(formulation_version)
                .include_auxiliary_clauses()
                .build(max_attempts_to_satisfy_goals_numerically=100)
            )
    solver: GeometricSolver = GeometricSolverBuilder(rng).build(problem_setup)

    success = solver.run()
    assert success
