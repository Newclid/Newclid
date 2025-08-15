from typing import Sequence

import pytest
from newclid.agent.follow_deductions import (
    CachedDeduction,
    CachedRuleDeduction,
    DeductionProvider,
    DeductionType,
    DoubleCheckError,
    FollowDeductions,
)
from newclid.api import GeometricSolverBuilder
from newclid.justifications.justification import Assumption, justify_dependency
from newclid.numerical.geometries import PointNum
from newclid.predicate_types import PredicateArgument
from newclid.predicates import Predicate, predicate_from_construction
from newclid.problem import PredicateConstruction, ProblemSetup
from newclid.proof_state import ProofState
from newclid.rng import setup_rng
from newclid.rule import Rule
from newclid.symbols.points_registry import Point


def p(name: str) -> PredicateArgument:
    return PredicateArgument(name)


class TestDoubleCheckRuleDeduction:
    def test_successfuly_follows_rule_deduction(self):
        self.fixture.given_cached_deductions(
            [
                CachedRuleDeduction(
                    deduction_type=DeductionType.RULE,
                    rule=self.rule,
                    premises=(
                        self.coll_a_b_c,
                        self.perp_a_b_c_d,
                        self.perp_b_c_a_e,
                    ),
                    conclusions=(self.para_a_e_c_d,),
                    point_deps=[],
                )
            ]
        )

        self.fixture.given_pred_graph_contains_by_construction(
            [self.coll_a_b_c, self.perp_a_b_c_d, self.perp_b_c_a_e]
        )
        self.fixture.when_following_deduction(self.nc_problem)
        self.fixture.then_pred_graph_should_contain(
            conclusion=self.para_a_e_c_d,
            why=(
                self.coll_a_b_c,
                self.perp_a_b_c_d,
                self.perp_b_c_a_e,
            ),
        )

    def test_raise_if_premises_not_in_current_graph(self):
        self.fixture.given_cached_deductions(
            [
                CachedRuleDeduction(
                    deduction_type=DeductionType.RULE,
                    rule=self.rule,
                    premises=(
                        self.coll_a_b_c,
                        self.perp_a_b_c_d,
                        self.perp_b_c_a_e,
                    ),
                    conclusions=(self.para_a_e_c_d,),
                    point_deps=[],
                )
            ]
        )

        self.fixture.given_pred_graph_contains_by_construction(
            [self.coll_a_b_c, self.perp_b_c_a_e]
        )

        with pytest.raises(
            DoubleCheckError, match="Premise 'AB ⟂ CD' .* not found in proof state"
        ):
            self.fixture.when_following_deduction(self.nc_problem)

    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixture = FollowDeductionFixture()

        self.nc_problem = ProblemSetup(
            name="test-problem-para-from-perps",
            points=(
                Point(name=p("a"), num=PointNum(x=0, y=0)),
                Point(name=p("b"), num=PointNum(x=1, y=0)),
                Point(name=p("c"), num=PointNum(x=2, y=0)),
                Point(name=p("d"), num=PointNum(x=2, y=1)),
                Point(name=p("e"), num=PointNum(x=0, y=1)),
            ),
            assumptions=(),
            goals=(),
        )

        self.coll_a_b_c = PredicateConstruction.from_str("coll a b c")
        self.perp_a_b_c_d = PredicateConstruction.from_str("perp a b c d")
        self.perp_b_c_a_e = PredicateConstruction.from_str("perp b c a e")
        self.para_a_e_c_d = PredicateConstruction.from_str("para a e c d")

        self.rule = Rule(
            id="fake-rule",
            description="A fake rule for testing",
            premises_txt=("coll A B C", "perp A B C D", "perp B C A E"),
            conclusions_txt=("para A E C D",),
        )


class FakeDeductionProvider(DeductionProvider):
    def __init__(self):
        self.cached_deductions: list[CachedDeduction] = []

    def with_cached_deductions(self, deductions: Sequence[CachedDeduction]):
        self.cached_deductions = list(deductions)

    def ordered_deductions_for_problem(
        self, problem: ProblemSetup
    ) -> list[CachedDeduction]:
        return self.cached_deductions

    @property
    def precomputation_input_str(self) -> str:
        return "Fake deduction provider input"


class FollowDeductionFixture:
    def __init__(self):
        self.rng = setup_rng(42)
        self.deductions_provider = FakeDeductionProvider()
        self.predicates_by_construction: list[PredicateConstruction] = []
        self.proof_state: ProofState | None = None

    def given_pred_graph_contains_by_construction(
        self, predicates_by_construction: list[PredicateConstruction]
    ):
        self.predicates_by_construction = predicates_by_construction

    def given_cached_deductions(self, deductions: Sequence[CachedDeduction]):
        self.deductions_provider.with_cached_deductions(deductions)

    def when_following_deduction(self, nc_problem: ProblemSetup):
        agent = FollowDeductions(self.deductions_provider)
        solver = (
            GeometricSolverBuilder(rng=self.rng)
            .with_deductive_agent(agent)
            .build(nc_problem)
        )

        self.proof_state = solver.proof_state
        for predicate_by_construction in self.predicates_by_construction:
            predicate = predicate_from_construction(
                predicate_by_construction,
                points_registry=self.proof_state.symbols.points,
            )
            if predicate is None:
                raise ValueError(
                    f"Statement {predicate_by_construction} could not be built."
                )
            dep = Assumption(predicate=predicate)
            self.proof_state.apply(dep)
        solver.run()

    def then_pred_graph_should_contain(
        self, conclusion: PredicateConstruction, why: tuple[PredicateConstruction, ...]
    ):
        if self.proof_state is None:
            raise ValueError("Proof state is not set, run the solver first.")

        pred_graph = self.proof_state.graph
        conclusion_predicate = predicate_from_construction(
            conclusion, points_registry=self.proof_state.symbols.points
        )
        if conclusion_predicate is None:
            raise ValueError(
                f"Conclusion {conclusion} could not be built from construction."
            )
        dep = pred_graph.hyper_graph.get(conclusion_predicate)
        assert dep is not None

        expected_why_predicates: list[Predicate] = []
        for why_construction in why:
            expected_why_predicate = predicate_from_construction(
                why_construction,
                points_registry=self.proof_state.symbols.points,
            )
            if expected_why_predicate is None:
                raise ValueError(
                    f"Why predicate {why_construction} could not be built from construction."
                )
            expected_why_predicates.append(expected_why_predicate)
        assert set(justify_dependency(dep, self.proof_state)) == set(
            expected_why_predicates
        )
