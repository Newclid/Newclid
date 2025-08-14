from pathlib import Path

import numpy as np
import pytest
from newclid.jgex.formulation import JGEXFormulation, jgex_formulation_from_txt_file
from newclid.llm_input import problem_to_llm_input

ALL_JGEX_COMPATIBLE_PROBLEM_FILES = [
    "examples.txt",
    "large_examples.txt",
    "imo.txt",
    "imo_sl.txt",
]

PROBLEMS_EXPECTED_TO_FAIL_TO_BUILD = [
    "breaking_cc_tangent",
    "breaking_cc_tangent_by_kiss",
    "breaking_cc_itangent",
    "breaking_cc_itangent_by_kiss",
    "2020_p1",
    # ag-shortlist
    "2018_sl_g4a",
    # non-ag 30
    "2005_p1",
    "2007_p2",
    "2013_p3",
]

ALL_PROBLEMS: list[JGEXFormulation] = []
for file_name in ALL_JGEX_COMPATIBLE_PROBLEM_FILES:
    ALL_PROBLEMS.extend(
        jgex_formulation_from_txt_file(
            Path(__file__).parent.parent.joinpath("problems_datasets", file_name)
        ).values()
    )


@pytest.mark.parametrize(
    "jgex_problem", ALL_PROBLEMS, ids=[p.name for p in ALL_PROBLEMS]
)
def test_can_build_all_example_problems(jgex_problem: JGEXFormulation):
    if jgex_problem.name in PROBLEMS_EXPECTED_TO_FAIL_TO_BUILD:
        pytest.skip("This problem is expected to fail to build.")
    rng = np.random.default_rng(42)
    problem_to_llm_input(jgex_problem, rng=rng, aux_tag="!aux")
