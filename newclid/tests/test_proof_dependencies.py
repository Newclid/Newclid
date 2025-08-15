import pytest
from newclid.justifications._index import JustificationError
from newclid.justifications.justification import DirectConsequence, Justification
from newclid.numerical.geometries import PointNum
from newclid.predicate_types import PredicateArgument
from newclid.predicates import Predicate
from newclid.predicates.collinearity import Coll
from newclid.problem import ProblemSetup
from newclid.proof_justifications import _proof_of_predicate  # type: ignore
from newclid.proof_state import ProofState
from newclid.symbols.points_registry import Point
from pytest_mock import MockerFixture


def p(name: str) -> PredicateArgument:
    return PredicateArgument(name)


class TestProofDependencies:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.proof_state = ProofState(
            problem=ProblemSetup(
                points=(
                    Point(name=p("a"), num=PointNum(x=0.0, y=0.0)),
                    Point(name=p("b"), num=PointNum(x=1.0, y=0.0)),
                    Point(name=p("c"), num=PointNum(x=2.0, y=0.0)),
                    Point(name=p("d"), num=PointNum(x=3.0, y=0.0)),
                    Point(name=p("e"), num=PointNum(x=4.0, y=0.0)),
                    Point(name=p("f"), num=PointNum(x=5.0, y=0.0)),
                ),
                assumptions=(),
                goals=(),
            ),
            rule_matcher=None,  # type: ignore
            deductors=[],
            rng=42,
        )
        self.pred_graph = self.proof_state.graph

        a, b, c, d, e, f = self.proof_state.symbols.points.names2points(
            [PredicateArgument(name) for name in ("a", "b", "c", "d", "e", "f")]
        )
        self.pred_A = Coll(points=(a, b, c))
        self.pred_B = Coll(points=(b, c, d))
        self.pred_C = Coll(points=(c, d, e))
        self.pred_D = Coll(points=(d, e, f))

    def test_proof_of_predicate_linear_proof(self):
        """Test a simple linear proof structure: A -> B -> C."""
        dep_A = DirectConsequence(predicate=self.pred_A, premises=())
        dep_B_from_A = DirectConsequence(predicate=self.pred_B, premises=(self.pred_A,))
        dep_C_from_B = DirectConsequence(predicate=self.pred_C, premises=(self.pred_B,))

        self.pred_graph.hyper_graph = {
            self.pred_A: dep_A,
            self.pred_B: dep_B_from_A,
            self.pred_C: dep_C_from_B,
        }

        sub_proof: dict[Predicate, tuple[Justification, ...]] = {}
        proof = _proof_of_predicate(self.pred_C, self.proof_state, sub_proof=sub_proof)

        assert proof == (dep_A, dep_B_from_A, dep_C_from_B)
        assert sub_proof[self.pred_A] == ()
        assert sub_proof[self.pred_B] == (dep_A,)
        assert sub_proof[self.pred_C] == (dep_A, dep_B_from_A)

    def test_proof_of_predicate_branching_proof(self):
        """Test a branching proof structure: A, B -> C."""
        # B is a premise here
        dep_A = DirectConsequence(predicate=self.pred_A, premises=())
        dep_B = DirectConsequence(predicate=self.pred_B, premises=())
        dep_C_from_AB = DirectConsequence(
            predicate=self.pred_C, premises=(self.pred_A, self.pred_B)
        )

        self.pred_graph.hyper_graph = {
            self.pred_A: dep_A,
            self.pred_B: dep_B,
            self.pred_C: dep_C_from_AB,
        }

        sub_proof: dict[Predicate, tuple[Justification, ...]] = {}
        proof = _proof_of_predicate(self.pred_C, self.proof_state, sub_proof=sub_proof)

        # The order of premises A and B in the proof depends on iteration order.
        expected_proof = (dep_A, dep_B, dep_C_from_AB)
        assert set(proof) == set(expected_proof)
        assert len(proof) == len(expected_proof)

        assert sub_proof[self.pred_A] == ()
        assert sub_proof[self.pred_B] == ()
        assert set(sub_proof[self.pred_C]) == set((dep_A, dep_B))

    def test_proof_of_predicate_dag_proof(self):
        """Test a DAG structure: A -> B, A -> C, (B, C) -> D."""
        dep_A = DirectConsequence(predicate=self.pred_A, premises=())
        dep_B_from_A = DirectConsequence(predicate=self.pred_B, premises=(self.pred_A,))
        dep_C_from_A = DirectConsequence(predicate=self.pred_C, premises=(self.pred_A,))
        dep_D_from_BC = DirectConsequence(
            predicate=self.pred_D, premises=(self.pred_B, self.pred_C)
        )

        self.pred_graph.hyper_graph = {
            self.pred_A: dep_A,
            self.pred_B: dep_B_from_A,
            self.pred_C: dep_C_from_A,
            self.pred_D: dep_D_from_BC,
        }

        sub_proof: dict[Predicate, tuple[Justification, ...]] = {}
        proof = _proof_of_predicate(self.pred_D, self.proof_state, sub_proof=sub_proof)

        expected_proof_without_duplicates = (
            dep_A,
            dep_B_from_A,
            dep_C_from_A,
            dep_D_from_BC,
        )
        assert proof == expected_proof_without_duplicates

        assert sub_proof[self.pred_A] == ()
        assert sub_proof[self.pred_B] == (dep_A,)
        assert sub_proof[self.pred_C] == (dep_A,)
        assert sub_proof[self.pred_D] == (dep_A, dep_B_from_A, dep_C_from_A)

    def test_dependency_not_found_in_hyper_graph(self, mocker: MockerFixture):
        """Test re-evaluating dependency with predicate.why()."""
        dep_A = DirectConsequence(predicate=self.pred_A, premises=())

        self.pred_graph.hyper_graph = {
            self.pred_A: dep_A,
            # dep_B_from_A is missing
        }

        sub_proof: dict[Predicate, tuple[Justification, ...]] = {}
        mocker.patch.object(
            self.proof_state.symbols.lines,
            "why_colllinear",
            return_value=DirectConsequence(
                predicate=self.pred_B, premises=(self.pred_A,)
            ),
        )
        proof = _proof_of_predicate(self.pred_B, self.proof_state, sub_proof=sub_proof)

        dep_B_from_A = DirectConsequence(predicate=self.pred_B, premises=(self.pred_A,))
        assert proof == (dep_A, dep_B_from_A)
        assert self.pred_B in self.pred_graph.hyper_graph
        assert self.pred_graph.hyper_graph[self.pred_B] == dep_B_from_A

    def test_dependency_not_found_and_why_fails(self):
        """Test case where dependency is missing and predicate.why() fails."""
        self.pred_graph.hyper_graph = {}
        sub_proof: dict[Predicate, tuple[Justification, ...]] = {}
        with pytest.raises(JustificationError):
            _proof_of_predicate(self.pred_A, self.proof_state, sub_proof=sub_proof)


class DummyPredicate:
    """A dummy predicate for testing purposes."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.preloaded_reason: str | None = None
        self.preloaded_why: tuple[Predicate, ...] | None = None
        self.why_called_count: int = 0

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        return args

    def add(self, proof_state: ProofState) -> tuple[Predicate, ...]:
        return ()

    def check(self, proof_state: ProofState) -> bool:
        return True

    def check_numerical(self) -> bool:
        return True

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)
