import logging
from pathlib import Path

import newclid.api
import newclid.proof_state
import pytest
from ncdgen.generation_configuration import DiagramGenerationConfig
from ncdgen.generation_loop import run_data_generation_loop
from ncdgen.read_datapoints import read_datapoints_from_file
from newclid.jgex.formulation import (
    ALPHABET,
    JGEXFormulation,
    alphabetize,
    jgex_formulation_from_txt_file,
)
from newclid.tools import points_by_construction_order

import newclid


class TestDiagramGeneration:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path):
        self.newclid_logger_api = logging.getLogger(newclid.api.__name__)
        self.newclid_logger_api.setLevel(logging.WARNING)
        self.newclid_logger_proof = logging.getLogger(newclid.proof_state.__name__)
        self.newclid_logger_proof.setLevel(logging.WARNING)
        self.newclid_logger = logging.getLogger(newclid.__name__)
        self.newclid_logger.setLevel(logging.INFO)
        self.config = DiagramGenerationConfig(
            debug=True,
            min_pts=1,
            max_pts=1,
            random_seed=42,
            jsonl_dump_file=tmp_path / "dump.jsonl",
            min_rules_applied=0,
            timeout=0.1,
        )

    def test_diagram_generation_from_scratch(self):
        """Test that we can generate data from scratch."""
        datapoints_generated = run_data_generation_loop(generation_config=self.config)
        assert datapoints_generated > 1

    def test_diagram_generation_from_problem(self):
        """Test that we can start from a problem and generate data of (hopefully) auxiliary constructions on top of it."""
        IMO_PROBLEMS_PATH = (
            Path(newclid.__file__).parents[2].joinpath("problems_datasets", "imo.txt")
        )
        ag_problems = jgex_formulation_from_txt_file(IMO_PROBLEMS_PATH)
        initial_problem = ag_problems["2019_p2"]
        self.config.initial_jgex_problem = str(initial_problem)
        datapoints_generated = run_data_generation_loop(generation_config=self.config)
        assert datapoints_generated > 1
        datapoints = read_datapoints_from_file(self.config.jsonl_dump_file)
        initial_problem.auxiliary_clauses = ()
        alphabetized_problem, _ = alphabetize(initial_problem)
        alphabetized_setup = str(alphabetized_problem).split(" ? ")[0]
        for datapoint in datapoints:
            larger_problem_txt = datapoint.subproblem.larger_problem
            assert larger_problem_txt.startswith(alphabetized_setup)
            _ensure_points_in_construction_order_and_unique(larger_problem_txt)

    def test_dump_aux_datapoints_on_know_diagram(self):
        """Test that we can dump aux datapoints on a known diagram."""
        self.config.initial_jgex_problem = PROBLEM_WITH_AUX_CONSTRUCTIONS
        self.config.emit_only_double_checked_aux_subproblems = True
        n_dataponts = run_data_generation_loop(generation_config=self.config)
        assert n_dataponts > 1
        dumped_datapoints = read_datapoints_from_file(self.config.jsonl_dump_file)
        assert len(dumped_datapoints) > 1
        for datapoint in dumped_datapoints:
            subproblem = datapoint.subproblem
            assert subproblem.has_double_checked_aux_construction

            double_check_statistics = subproblem.double_check_statistics
            assert double_check_statistics is not None, (
                "Aux datapoint should have double check statistics"
            )
            assert double_check_statistics.true_aux_clauses, (
                "Aux datapoint should have true aux clauses"
            )
            assert double_check_statistics.final_proof is not None, (
                "Aux datapoint should have final proof"
            )

            training_data = double_check_statistics.training_data
            assert training_data is not None, "Aux datapoint should have training data"
            assert training_data.aux_io, "Aux datapoint should have aux io"


def _ensure_points_in_construction_order_and_unique(problem: str):
    """Ensure that no point name is used more than once in the problem."""
    jgex_problem = JGEXFormulation.from_text(problem)
    points_checked = 0
    for clause in jgex_problem.clauses:
        for point in clause.points:
            assert point == ALPHABET[points_checked], (
                f"Point {point} is not in construction order. Expected {ALPHABET[points_checked]}"
            )
            points_checked += 1


@pytest.mark.parametrize(
    "points, expected",
    [
        (["c", "b", "b", "a1", "a"], ["a", "b", "c", "a1"]),
    ],
)
def test_points_by_construction_order(points: list[str], expected: list[str]):
    assert points_by_construction_order(set(points)) == expected


PROBLEM_WITH_AUX_CONSTRUCTIONS = (
    "a b c d = rectangle a b c d; "
    "e = intersection_lc e c d b; "
    "f g = trisegment f g b d; "
    "h = intersection_tt h f e a g d c; "
    "i = intersection_lp i g h b e a; "
    "j k l m = centroid j k l m f a i; "
)
