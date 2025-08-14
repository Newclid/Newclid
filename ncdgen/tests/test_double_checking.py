from __future__ import annotations

import networkx as nx
import numpy as np
import pytest
from ncdgen.double_checking import (
    DoubleCheckStatistics,
    do_double_check,
    points_requirements_graph_from_jgex_clauses,
)
from ncdgen.testing import StubJGEXSolver
from newclid.jgex.clause import JGEXClause, JGEXConstruction
from newclid.jgex.constructions._index import JGEXConstructionName
from newclid.jgex.formulation import JGEXFormulation, alphabetize
from newclid.jgex.geometries import JGEXPoint
from newclid.jgex.to_newclid import JGEXClauseConsequences
from newclid.justifications.justification import Assumption
from newclid.numerical.geometries import PointNum
from newclid.predicate_types import PredicateArgument
from newclid.predicates import predicate_from_construction
from newclid.problem import (
    PredicateConstruction,
    ProblemSetup,
    rename_predicate_construction,
)
from newclid.proof_state import ProofState
from newclid.rng import setup_rng
from newclid.run_loop import RunInfos
from newclid.symbols.points_registry import Point
from py_yuclid.omni_matcher import OmniMatcher
from py_yuclid.yuclid_adapter import YuclidAdapter


class TestDoubleChecking:
    def test_true_aux_when_fails_without_single_aux_clause(self):
        """If a subproblem is solvable with aux clauses, but not without, then it's a true aux clause."""
        subgoal = PredicateConstruction.from_str("perp a b c d")
        setup_clauses = (self.a_b_c_free,)
        self.fixture.given_solver_will_fail_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses, aux_clauses=(), goals=(subgoal,)
            )
        )

        all_aux_clauses = (self.d_from_a_b_c,)
        self.fixture.given_solver_will_succeed_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses, aux_clauses=all_aux_clauses, goals=(subgoal,)
            )
        )

        self.fixture.when_double_checking_all_aux_clauses(
            setup_clauses, all_aux_clauses, subgoal
        )

        self.fixture.then_true_aux_list_should_be(
            [str(clause) for clause in all_aux_clauses]
        )

    def test_alphabetized_subproblem_is_used(self):
        """Test that the alphabetized subproblem is used in the double check."""

        subgoal = PredicateConstruction.from_str("perp a b c d")
        setup_clauses = (self.a_b_c_free,)
        self.fixture.given_solver_will_fail_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses, aux_clauses=(), goals=(subgoal,)
            )
        )

        all_aux_clauses = (self.d_from_a_b_c,)
        self.fixture.given_solver_will_succeed_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses, aux_clauses=all_aux_clauses, goals=(subgoal,)
            )
        )

        mapping = {
            PredicateArgument("a"): PredicateArgument("w"),
            PredicateArgument("b"): PredicateArgument("y"),
            PredicateArgument("c"): PredicateArgument("z"),
        }
        w_y_z_free = self.a_b_c_free.renamed(mapping)
        d_from_w_y_z = self.d_from_a_b_c.renamed(mapping)
        subgoal_renamed = rename_predicate_construction(subgoal, mapping)
        self.fixture.when_double_checking_all_aux_clauses(
            setup_clauses=(w_y_z_free,),
            aux_clauses=(d_from_w_y_z,),
            goal_construction=subgoal_renamed,
        )

        self.fixture.then_true_aux_list_should_be([str(self.d_from_a_b_c)])

    def test_false_positive_when_succeeds_without_single_aux_clause(self):
        """If a subproblem is solvable without aux clauses, then it's a false positive."""
        subgoal = PredicateConstruction.from_str("perp a b c d")
        setup_clauses = (self.a_b_c_free,)
        self.fixture.given_solver_will_succeed_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses, aux_clauses=(), goals=(subgoal,)
            ),
        )

        all_aux_clauses = (self.d_from_a_b_c,)
        self.fixture.given_solver_will_succeed_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses, aux_clauses=all_aux_clauses, goals=(subgoal,)
            )
        )

        self.fixture.when_double_checking_all_aux_clauses(
            setup_clauses, all_aux_clauses, subgoal
        )

        self.fixture.then_true_aux_list_should_be([])

    def test_find_when_all_clauses_are_used(self):
        """Test that when all clauses necessary to solve the problem, then all aux clauses are true."""
        subgoal = PredicateConstruction.from_str("perp a b c d")
        setup_clauses = (
            self.a_b_c_free,
            self.d_from_a_b_c,
            self.e_f_free,
        )

        self.fixture.given_solver_will_fail_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses, aux_clauses=(), goals=(subgoal,)
            ),
        )

        all_aux_clauses = (
            self.g_from_c_e_f,
            self.h_from_d_g,
        )
        self.fixture.given_solver_will_succeed_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses, aux_clauses=all_aux_clauses, goals=(subgoal,)
            )
        )
        # Fail without h
        self.fixture.given_solver_will_fail_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses, aux_clauses=(self.g_from_c_e_f,), goals=(subgoal,)
            )
        )

        self.fixture.when_double_checking_all_aux_clauses(
            setup_clauses, all_aux_clauses, subgoal
        )
        self.fixture.then_true_aux_list_should_be(
            [str(clause) for clause in all_aux_clauses]
        )

    def test_find_true_aux_subset_in_graph(self):
        """Test that we can find the subset of true aux clauses given they have the following requirements graph:

        Setup:
        a, b, c free
        e, f free
        i, j free

        Aux:
        a, b, c -> d
        b, c, e, f -> g
        d, g -> h
        i, j -> k

        And that g and k are the only necessary aux point, only g and k clauses should be kept as true aux.
        """
        setup_clauses = (self.a_b_c_free, self.e_f_free, self.i_j_free)
        subgoal = PredicateConstruction.from_str("perp a b c d")

        self.fixture.given_solver_will_fail_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses, aux_clauses=(), goals=(subgoal,)
            )
        )

        all_aux_clauses = (
            self.d_from_a_b_c,
            self.g_from_c_e_f,
            self.h_from_d_g,
            self.k_from_i_j,
        )
        self.fixture.given_solver_will_succeed_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses, aux_clauses=all_aux_clauses, goals=(subgoal,)
            )
        )

        # All the intermediate cases that should be tested

        # Succeed without h
        self.fixture.given_solver_will_succeed_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses,
                aux_clauses=(self.d_from_a_b_c, self.g_from_c_e_f, self.k_from_i_j),
                goals=(subgoal,),
            )
        )

        # Fail without g
        self.fixture.given_solver_will_fail_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses,
                aux_clauses=(self.d_from_a_b_c, self.k_from_i_j),
                goals=(subgoal,),
            )
        )

        # Succeed with g but without d
        self.fixture.given_solver_will_succeed_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses,
                aux_clauses=(self.g_from_c_e_f, self.k_from_i_j),
                goals=(subgoal,),
            )
        )

        # Fail without k
        self.fixture.given_solver_will_fail_for_problem(
            _alphabetized_problem_with_clauses(
                setup_clauses,
                aux_clauses=(self.d_from_a_b_c, self.g_from_c_e_f, self.h_from_d_g),
                goals=(subgoal,),
            )
        )

        self.fixture.when_double_checking_all_aux_clauses(
            setup_clauses, all_aux_clauses, subgoal
        )

        final_expected_minimal_problem = JGEXFormulation(
            setup_clauses=setup_clauses + (self.g_from_c_e_f, self.k_from_i_j),
            goals=(subgoal,),
        )
        alphabetized_problem, final_reversed_mapping = alphabetize(
            final_expected_minimal_problem
        )

        self.fixture.then_true_aux_list_should_be(
            [
                str(clause)
                for clause in alphabetized_problem.clauses
                if clause.renamed(final_reversed_mapping) in all_aux_clauses
            ]
        )

    @pytest.fixture(autouse=True)
    def setup(
        self,
        double_check_fixture: DoubleCheckFixture,
        graph_clauses: tuple[JGEXClause, ...],
    ):
        self.fixture = double_check_fixture
        self.goal_tuple = ()
        (
            self.a_b_c_free,
            self.d_from_a_b_c,
            self.e_f_free,
            self.g_from_c_e_f,
            self.h_from_d_g,
            self.i_j_free,
            self.k_from_i_j,
        ) = graph_clauses


def _alphabetized_problem_with_clauses(
    setup_clauses: tuple[JGEXClause, ...],
    aux_clauses: tuple[JGEXClause, ...],
    goals: tuple[PredicateConstruction, ...],
) -> JGEXFormulation:
    problem = JGEXFormulation(
        setup_clauses=setup_clauses,
        auxiliary_clauses=aux_clauses,
        goals=goals,
    )
    alphabetized_problem, _ = alphabetize(problem)
    return alphabetized_problem


@pytest.fixture
def double_check_fixture() -> DoubleCheckFixture:
    return DoubleCheckFixture()


class DoubleCheckFixture:
    def __init__(self, rng: np.random.Generator | int | None = None):
        self.jgex_solver = StubJGEXSolver()
        self.aux_tag = "!aux"
        self.rng = setup_rng(rng)
        self._double_check_stats: DoubleCheckStatistics | None = None
        self._run_infos_for_problem: dict[JGEXFormulation, RunInfos] = {}

    @property
    def double_check_stats(self) -> DoubleCheckStatistics:
        assert self._double_check_stats is not None, "Double check did not run"
        return self._double_check_stats

    def given_solver_will_fail_for_problem(self, problem: JGEXFormulation):
        failure_after_1s = RunInfos(
            success=False, runtime=1.0, steps=10, success_per_goal={}
        )
        self._run_infos_for_problem[problem] = failure_after_1s

    def given_solver_will_succeed_for_problem(self, problem: JGEXFormulation):
        success_after_1s = RunInfos(
            success=True, runtime=1.0, steps=10, success_per_goal={}
        )
        self._run_infos_for_problem[problem] = success_after_1s

    def when_double_checking_all_aux_clauses(
        self,
        setup_clauses: tuple[JGEXClause, ...],
        aux_clauses: tuple[JGEXClause, ...],
        goal_construction: PredicateConstruction,
    ):
        jgex_larger_problem, nc_larger_problem, clauses_consequences = (
            _fake_larger_problem(setup_clauses, aux_clauses, self.rng)
        )
        he_adapter = YuclidAdapter()
        proof_state = ProofState(
            problem=nc_larger_problem,
            rule_matcher=OmniMatcher(he_adapter=he_adapter),
            deductors=[],
            rng=self.rng,
        )
        for problem, run_infos in self._run_infos_for_problem.items():
            self.jgex_solver.with_outputs_for_problem_clauses(
                problem, run_infos, proof_state=proof_state
            )

        goal = predicate_from_construction(
            goal_construction,
            points_registry=proof_state.symbols.points,
        )
        assert goal is not None

        proof_state.graph.hyper_graph[goal] = Assumption(predicate=goal)

        subproblem = JGEXFormulation(
            setup_clauses=setup_clauses,
            auxiliary_clauses=aux_clauses,
            goals=(goal_construction,),
        )
        self._double_check_stats = do_double_check(
            subproblem=subproblem,
            larger_problem=jgex_larger_problem,
            large_nc_problem=nc_larger_problem,
            clauses_consequences=clauses_consequences,
            solver=self.jgex_solver,
            aux_tag=self.aux_tag,
            rng=self.rng,
        )

    def then_true_aux_list_should_be(self, aux_clauses: list[str]):
        assert self.double_check_stats.true_aux_clauses == aux_clauses


def _fake_larger_problem(
    setup_clauses: tuple[JGEXClause, ...],
    aux_clauses: tuple[JGEXClause, ...],
    rng: np.random.Generator,
) -> tuple[JGEXFormulation, ProblemSetup, dict[JGEXClause, JGEXClauseConsequences]]:
    jgex_larger_problem = JGEXFormulation(
        setup_clauses=setup_clauses,
        auxiliary_clauses=aux_clauses,
        goals=(),
    )
    points: list[Point] = []
    clauses_consequences: dict[JGEXClause, JGEXClauseConsequences] = {}
    for clause in jgex_larger_problem.clauses:
        fake_points = {
            p: JGEXPoint(x=100 * rng.random(), y=100 * rng.random())
            for p in clause.points
        }
        clauses_consequences[clause] = JGEXClauseConsequences(
            new_points=fake_points,
            construction_consequences=[],
            numerical_requirements=[],
        )
        for pname, jgex_point in fake_points.items():
            points.append(
                Point(
                    name=PredicateArgument(pname),
                    num=PointNum(x=jgex_point.x, y=jgex_point.y),
                )
            )

    nc_larger_problem = ProblemSetup(points=tuple(points), assumptions=(), goals=())
    return jgex_larger_problem, nc_larger_problem, clauses_consequences


class TestPointsRequirementsGraph:
    def test_graph_from_clauses(self, graph_clauses: tuple[JGEXClause, ...]):
        (
            a_b_c_free,
            d_from_a_b_c,
            e_f_free,
            g_from_c_e_f,
            h_from_d_g,
            i_j_free,
            k_from_i_j,
        ) = graph_clauses

        points_graph = points_requirements_graph_from_jgex_clauses(
            [
                a_b_c_free,
                d_from_a_b_c,
                e_f_free,
                g_from_c_e_f,
                h_from_d_g,
                i_j_free,
                k_from_i_j,
            ]
        )

        expected_graph: nx.DiGraph[str] = nx.DiGraph()
        expected_graph.add_node("a", clause=a_b_c_free)
        expected_graph.add_node("b", clause=a_b_c_free)
        expected_graph.add_node("c", clause=a_b_c_free)
        expected_graph.add_node("d", clause=d_from_a_b_c)
        expected_graph.add_node("e", clause=e_f_free)
        expected_graph.add_node("f", clause=e_f_free)
        expected_graph.add_node("g", clause=g_from_c_e_f)
        expected_graph.add_node("h", clause=h_from_d_g)
        expected_graph.add_node("i", clause=i_j_free)
        expected_graph.add_node("j", clause=i_j_free)
        expected_graph.add_node("k", clause=k_from_i_j)

        expected_graph.add_edge("a", "d")
        expected_graph.add_edge("b", "d")
        expected_graph.add_edge("c", "d")

        expected_graph.add_edge("b", "g")
        expected_graph.add_edge("c", "g")
        expected_graph.add_edge("e", "g")
        expected_graph.add_edge("f", "g")

        expected_graph.add_edge("a", "h")
        expected_graph.add_edge("b", "h")
        expected_graph.add_edge("d", "h")
        expected_graph.add_edge("g", "h")

        expected_graph.add_edge("i", "k")
        expected_graph.add_edge("j", "k")

        assert sorted(points_graph.nodes) == sorted(expected_graph.nodes)
        assert sorted(points_graph.edges) == sorted(expected_graph.edges)
        for expected_node, expected_clause in expected_graph.nodes(data="clause"):
            actual_clause = points_graph.nodes[PredicateArgument(expected_node)][
                "clause"
            ]
            assert actual_clause == expected_clause


@pytest.fixture
def graph_clauses() -> tuple[JGEXClause, ...]:
    a_b_c_free = JGEXClause(
        points=(PredicateArgument("a"), PredicateArgument("b"), PredicateArgument("c")),
        constructions=(
            JGEXConstruction.from_tuple(
                (JGEXConstructionName.TRIANGLE.value, "a", "b", "c")
            ),
        ),
    )
    d_from_a_b_c = JGEXClause(
        points=(PredicateArgument("d"),),
        constructions=(
            JGEXConstruction.from_tuple(
                (JGEXConstructionName.ON_PARA_LINE.value, "d", "a", "b", "c")
            ),
            JGEXConstruction.from_tuple(
                (JGEXConstructionName.ON_PARA_LINE.value, "d", "c", "a", "b")
            ),
        ),
    )

    e_f_free = JGEXClause(
        points=(PredicateArgument("e"), PredicateArgument("f")),
        constructions=(
            JGEXConstruction.from_tuple((JGEXConstructionName.SEGMENT.value, "e", "f")),
        ),
    )
    g_from_c_e_f = JGEXClause(
        points=(PredicateArgument("g"),),
        constructions=(
            JGEXConstruction.from_tuple(
                (JGEXConstructionName.ON_LINE.value, "g", "e", "f")
            ),
            JGEXConstruction.from_tuple(
                (JGEXConstructionName.ON_LINE.value, "g", "c", "b")
            ),
        ),
    )
    h_from_d_g = JGEXClause(
        points=(PredicateArgument("h"),),
        constructions=(
            JGEXConstruction.from_tuple(
                (JGEXConstructionName.ON_LINE.value, "h", "d", "g")
            ),
            JGEXConstruction.from_tuple(
                (JGEXConstructionName.ON_LINE.value, "h", "a", "b")
            ),
        ),
    )
    i_j_free = JGEXClause(
        points=(PredicateArgument("i"), PredicateArgument("j")),
        constructions=(
            JGEXConstruction.from_tuple((JGEXConstructionName.SEGMENT.value, "i", "j")),
        ),
    )
    k_from_i_j = JGEXClause(
        points=(PredicateArgument("k"),),
        constructions=(
            JGEXConstruction.from_tuple(
                (JGEXConstructionName.MIDPOINT.value, "k", "i", "j")
            ),
        ),
    )

    return (
        a_b_c_free,
        d_from_a_b_c,
        e_f_free,
        g_from_c_e_f,
        h_from_d_g,
        i_j_free,
        k_from_i_j,
    )
