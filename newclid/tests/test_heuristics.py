import numpy as np
import pytest
from newclid.heuristics._index import HeuristicName
from newclid.heuristics._interface import Heuristic
from newclid.heuristics.alphabet import get_available_from_alphabet
from newclid.heuristics.apply_heuristics import (
    apply_complete_the_picture_heuristics,
    apply_heuristics_on_nc_problem,
    build_nc_problem_from_jgex_problem,
)
from newclid.heuristics.centers_of_cyclic import CentersOfCyclicHeuristic
from newclid.heuristics.foots_on_lines import FootHeuristic
from newclid.heuristics.heuristic_from_config import heuristic_from_name
from newclid.heuristics.line_intersections import LineIntersectionsHeuristic
from newclid.heuristics.midpoint import MidpointHeuristic
from newclid.heuristics.transfer_distances import TransferDistancesHeuristic
from newclid.jgex.clause import JGEXClause
from newclid.jgex.formulation import JGEXFormulation
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.problem import PredicateConstruction, ProblemSetup
from newclid.tools import pretty_basemodel_list_diff


class TestBaseCasesOfHeuristics:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixture = HeuristicFixture()

    @pytest.mark.parametrize("heuristic_name", HeuristicName)
    def test_each_heuristic_can_be_applied(self, heuristic_name: HeuristicName):
        """Test that each heuristic can be applied."""
        self.fixture.given_jgex_problem(
            "a b c = triangle a b c; d e = segment d e; f = on_circum f a b c;"
            " g = on_aline0 g a b c d e f d ? eqangle f a a b f c c b"
        )
        self.fixture.when_applying_heuristic(heuristic_from_name(heuristic_name))
        self.fixture.then_there_should_be_at_least_n_new_points(1)

    def test_max_points_limit(self):
        """Test that max_new_points limit is respected."""
        self.fixture.given_jgex_problem("a b c = triangle a b c")
        max_new_points = 2
        self.fixture.when_applying_heuristic(MidpointHeuristic(), max_new_points)
        self.fixture.then_there_should_be_at_least_n_new_points(1)
        self.fixture.then_there_should_be_at_most_n_new_points(max_new_points)

    def test_deterministic_behavior(self):
        """Test that heuristics produce deterministic results with same seed."""
        rng = np.random.default_rng(123)
        jgex_problem = JGEXFormulation.from_text("a b c = triangle a b c")
        nc_problem = build_nc_problem_from_jgex_problem(jgex_problem, rng)

        # Apply heuristics with same seed
        rng1 = np.random.default_rng(123)
        ncproblem1, added_clauses1 = apply_heuristics_on_nc_problem(
            nc_problem, jgex_problem, MidpointHeuristic(), rng1, max_new_points=3
        )

        rng2 = np.random.default_rng(123)
        ncproblem2, added_clauses2 = apply_heuristics_on_nc_problem(
            nc_problem, jgex_problem, MidpointHeuristic(), rng2, max_new_points=3
        )

        # Results should be identical
        assert ncproblem1.points == ncproblem2.points
        assert ncproblem1.assumptions == ncproblem2.assumptions
        assert added_clauses1 == added_clauses2


class TestLineIntersectionsHeuristic:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixture = HeuristicFixture()

    def test_successful_line_intersections_heuristic(self):
        """Test that line intersections heuristic works."""
        self.fixture.given_jgex_problem("a b = segment a b; c d = segment c d")
        self.fixture.when_applying_heuristic(LineIntersectionsHeuristic())
        self.fixture.then_there_should_be_new_assumptions_of_predicate(
            PredicateType.COLLINEAR
        )
        self.fixture.then_there_should_be_at_least_n_new_points(1)


class TestTransferDistancesHeuristic:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixture = HeuristicFixture()

    def test_successful_transfer_distances_heuristic(self):
        """Test that transfer distances heuristic works."""
        self.fixture.given_jgex_problem("a b c = triangle a b c")
        self.fixture.when_applying_heuristic(TransferDistancesHeuristic())
        self.fixture.then_there_should_be_new_assumptions_of_predicate(
            PredicateType.CONGRUENT
        )
        self.fixture.then_there_should_be_at_least_n_new_points(1)


class TestMidpointHeuristic:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixture = HeuristicFixture()

    def test_successful_midpoint_heuristic(self):
        """Test that midpoint heuristic works."""
        self.fixture.given_jgex_problem("a b c = triangle a b c")
        self.fixture.when_applying_heuristic(MidpointHeuristic())
        self.fixture.then_there_should_be_new_assumptions_of_predicate(
            PredicateType.MIDPOINT
        )
        self.fixture.then_there_should_be_at_least_n_new_points(1)


class TestCentersOfCyclicHeuristic:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixture = HeuristicFixture()

    def test_successful_centers_of_cyclic_heuristic(self):
        """Test that centers of cyclic heuristic works."""
        self.fixture.given_jgex_problem("a b c = triangle a b c; d = on_circum d a b c")
        self.fixture.when_applying_heuristic(
            CentersOfCyclicHeuristic(), max_new_points=5
        )
        self.fixture.then_there_should_be_new_assumptions_of_predicate(
            PredicateType.CIRCUMCENTER
        )
        self.fixture.then_there_should_be_at_least_n_new_points(1)

    def test_center_after_solver_application(self):
        """Test that we find center of cyclic that were found by the solver."""
        self.fixture.given_jgex_problem(
            "a b = segment a b; c = on_dia c a b; d = on_dia d a b"
        )
        self.fixture.when_applying_heuristic(CentersOfCyclicHeuristic())
        self.fixture.then_there_should_be_at_least_n_new_points(1)
        self.fixture.then_there_should_be_new_assumptions_of_predicate(
            PredicateType.CIRCUMCENTER
        )


class TestFootHeuristic:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixture = HeuristicFixture()

    def test_successful_foot_heuristic(self):
        """Test that foot heuristic works."""
        self.fixture.given_jgex_problem("a b = segment a b; c = on_tline c b a b")
        self.fixture.when_applying_heuristic(FootHeuristic())
        self.fixture.then_there_should_be_at_least_n_new_points(1)


class TestCompleteThePictureHeuristics:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixture = HeuristicFixture()

    def test_complete_the_picture(self):
        """Test applying multiple heuristics."""
        self.fixture.given_jgex_problem(
            "a b c = triangle a b c; d e = segment d e; f = on_circum f a b c;"
            " g = on_aline0 g a b c d e f d ? eqangle f a a b f c c b"
        )
        self.fixture.when_applying_complete_the_picture_heuristics()
        self.fixture.then_there_should_be_at_least_n_new_points(2)
        self.fixture.then_heuristic_should_have_added_predicates_of_predicate(
            HeuristicName.CENTERS, PredicateType.CIRCUMCENTER
        )
        self.fixture.then_heuristic_should_have_added_predicates_of_predicate(
            HeuristicName.LINE_INTERSECTIONS, PredicateType.COLLINEAR
        )
        self.fixture.then_heuristic_should_have_added_predicates_of_predicate(
            HeuristicName.ANGLE_VERTICES, PredicateType.COLLINEAR
        )


class HeuristicFixture:
    def __init__(self):
        self.rng = np.random.default_rng(42)
        self._problem: JGEXFormulation | None = None
        self._resulting_nc_problem: ProblemSetup | None = None
        self._resulting_jgex_problem: JGEXFormulation | None = None
        self._added_clauses: list[JGEXClause] | None = None

    @property
    def problem(self) -> JGEXFormulation:
        if self._problem is None:
            raise ValueError("No problem was given")
        return self._problem

    @property
    def result(self) -> ProblemSetup:
        if self._resulting_nc_problem is None:
            raise ValueError("No heuristics applied")
        return self._resulting_nc_problem

    @property
    def points_added(self) -> int:
        return len(self.result.points) - len(self.problem.points)

    def given_jgex_problem(self, problem_txt: str):
        self._problem = JGEXFormulation.from_text(problem_txt)

    def when_applying_heuristic(
        self,
        heuristic: Heuristic,
        max_new_points: int | None = None,
    ):
        if self._problem is None:
            raise ValueError("No problem was given")

        self._initial_nc_problem = build_nc_problem_from_jgex_problem(
            self.problem, self.rng
        )
        (
            self._resulting_nc_problem,
            self._added_clauses_consequences,
        ) = apply_heuristics_on_nc_problem(
            self._initial_nc_problem, self.problem, heuristic, self.rng, max_new_points
        )

    def when_applying_complete_the_picture_heuristics(
        self, max_new_points: int | None = None
    ):
        if self._problem is None:
            raise ValueError("No problem was given")
        self._initial_nc_problem = build_nc_problem_from_jgex_problem(
            self.problem, self.rng
        )
        (
            self._resulting_nc_problem,
            self._resulting_jgex_problem,
            self._clauses_consequences_per_heuristic,
        ) = apply_complete_the_picture_heuristics(
            self._initial_nc_problem, self.problem, self.rng, max_new_points
        )

    def then_there_should_be_no_new_points(self):
        assert self.points_added == 0

    def then_there_should_be_at_least_n_new_points(self, n: int):
        assert self.points_added >= n

    def then_there_should_be_at_most_n_new_points(self, n: int):
        assert self.points_added <= n

    def then_clauses_should_be_added(self, expected_clauses: list[JGEXClause]):
        if self._added_clauses is None:
            raise ValueError("No clauses were added")
        assert self._added_clauses == expected_clauses, pretty_basemodel_list_diff(
            self._added_clauses, expected_clauses
        )

    def then_heuristic_should_have_added_predicates_of_predicate(
        self, heuristic: HeuristicName, predicate_type: PredicateType
    ):
        clauses_added_by_heuristic = self._clauses_consequences_per_heuristic[heuristic]
        added_statments_by_heuristic: list[PredicateConstruction] = []
        for clause_consequences in clauses_added_by_heuristic:
            for constru_consequence in clause_consequences.construction_consequences:
                added_statments_by_heuristic.extend(
                    constru_consequence.added_predicates
                )

        added_predicates_of_predicate = [
            predicate_construction
            for predicate_construction in added_statments_by_heuristic
            if predicate_construction.predicate_type == predicate_type
        ]

        assert len(added_predicates_of_predicate) > 0, (
            f"No predicates of predicate {predicate_type} found. "
            f"All added predicates: {added_statments_by_heuristic}"
        )

    def then_there_should_be_new_assumptions_of_predicate(
        self, predicate_type: PredicateType
    ):
        new_assumptions = [
            assumption
            for assumption in self.result.assumptions
            if assumption not in self._initial_nc_problem.assumptions
        ]
        new_assumptions_of_predicate = [
            assumption
            for assumption in new_assumptions
            if assumption.predicate_type == predicate_type
        ]
        assert len(new_assumptions_of_predicate) > 0, (
            f"No new assumptions of predicate {predicate_type} found. "
            f"All new assumptions: {new_assumptions}"
        )


def test_get_available_from_alphabet():
    """Test that get_available_from_alphabet returns the first unused point name."""
    used_points = [
        PredicateArgument("a"),
        PredicateArgument("b"),
        PredicateArgument("c"),
    ]
    available = get_available_from_alphabet(used_points)
    assert available == PredicateArgument("d")

    # Test with all points used except one
    used_points = [
        PredicateArgument("a"),
        PredicateArgument("b"),
        PredicateArgument("c"),
        PredicateArgument("e"),
    ]
    available = get_available_from_alphabet(used_points)
    assert available == PredicateArgument("d")

    # Test with empty list
    available = get_available_from_alphabet([])
    assert available == PredicateArgument("a")
