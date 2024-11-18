from fractions import Fraction
import pytest

from newclid.api import GeometricSolverBuilder
from newclid.dependencies.dependency import Dependency, Reason
from newclid.dependencies.dependency_building import DependencyBody
from newclid.predicates import Predicate
from newclid.reasoning_engines.formulas import (
    MenelausFormula,
    PythagoreanFormula,
    make_rconst_hashs_from_colls,
)
from newclid.reasoning_engines.engines_interface import Derivation, ReasoningEngine
from newclid.statements.statement import Statement
from newclid.symbols_graph import SymbolsGraphBuilder


class TestPythagorean:
    @pytest.fixture(autouse=True)
    def setup(self, reasoning_fixture: "ReasoningEngineFixture"):
        self.solver_builder = GeometricSolverBuilder()
        self.reasoning_fixture = reasoning_fixture
        points_names = ["a", "b", "c"]
        lengths = ["3", "4", "5"]

        self.symbols_graph = (
            SymbolsGraphBuilder()
            .with_points_named(points_names)
            .with_lengths(lengths)
            .build()
        )
        self.points = self.symbols_graph.names2points(points_names)
        self.lengths = self.symbols_graph.names2nodes(lengths)

    @pytest.mark.parametrize("use_engine", [True, False])
    def test_implication_simple_problem(self, use_engine: bool):
        solver_builder = self.solver_builder.load_problem_from_txt(
            "a = free a; "
            "b = lconst b a 3; "
            "c = on_tline c a b a, lconst c a 4 "
            "? lconst c b 5"
        )
        if use_engine:
            solver_builder.with_additional_reasoning_engine(
                PythagoreanFormula, "Pythagorean"
            )

        solver = solver_builder.build()
        success = solver.run()
        assert success == use_engine

    def test_implication_hypotenuse(self):
        """Should be able to use Pythagorean theorem to get the missing hypotenuse.

        AB ⟂ AC => AB² + AC² = BC²

        Thus if AB=3 and AC=4, we should find BC=5.

        """
        a, b, c = self.points
        l_3, l_4, l_5 = self.lengths

        self.reasoning_fixture.given_engine(PythagoreanFormula(self.symbols_graph))
        given_dependencies = [
            Dependency(Statement(Predicate.PERPENDICULAR, (a, b, a, c)), why=[]),
            Dependency(Statement(Predicate.CONSTANT_LENGTH, (a, b, l_3)), why=[]),
            Dependency(Statement(Predicate.CONSTANT_LENGTH, (a, c, l_4)), why=[]),
        ]
        for dep in given_dependencies:
            self.reasoning_fixture.given_added_dependency(dep)

        self.reasoning_fixture.when_resolving_dependencies()
        self.reasoning_fixture.then_new_derivations_should_be(
            [
                Derivation(
                    Statement(Predicate.CONSTANT_LENGTH, (b, c, l_5)),
                    DependencyBody(Reason("Pythagorean"), why=given_dependencies),
                ),
            ]
        )

    def test_implication_side(self):
        """Should be able to use Pythagorean theorem to get the missing side length.

        AB ⟂ AC => AB² + AC² = BC²

        Thus if AB=3 and BC=5, we should find AC=4.

        """
        a, b, c = self.points
        l_3, l_4, l_5 = self.lengths

        self.reasoning_fixture.given_engine(PythagoreanFormula(self.symbols_graph))
        given_dependencies = [
            Dependency(Statement(Predicate.PERPENDICULAR, (a, b, a, c)), why=[]),
            Dependency(Statement(Predicate.CONSTANT_LENGTH, (a, b, l_3)), why=[]),
            Dependency(Statement(Predicate.CONSTANT_LENGTH, (b, c, l_5)), why=[]),
        ]
        for dep in given_dependencies:
            self.reasoning_fixture.given_added_dependency(dep)

        self.reasoning_fixture.when_resolving_dependencies()
        self.reasoning_fixture.then_new_derivations_should_be(
            [
                Derivation(
                    Statement(Predicate.CONSTANT_LENGTH, (a, c, l_4)),
                    DependencyBody(Reason("Pythagorean"), why=given_dependencies),
                ),
            ]
        )

    # TODO
    @pytest.mark.skip
    def test_implication_not_intersection(self):
        """Should be able to use Pythagorean theorem
        even if the perp is not an intesection itself."""

    @pytest.mark.parametrize("use_engine", [False, True])
    def test_reciprocal_simple_problem(self, use_engine: bool):
        solver_builder = self.solver_builder.load_problem_from_txt(
            "a = free a; "
            "b = lconst b a 3; "
            "c = lconst c b 5, lconst c a 4 "
            "? perp a b a c"
        )
        if use_engine:
            solver_builder.with_additional_reasoning_engine(
                PythagoreanFormula, "Pythagorean"
            )

        solver = solver_builder.build()
        success = solver.run()
        assert success == use_engine

    def test_reciprocal(self):
        """Should be able to use Pythagorean theorem to get perp from constant lengths.

        AB² + AC² = BC² => AB ⟂ AC

        Thus if AB=3 and AC=4 and BC=5, we should find AB ⟂ AC

        """
        a, b, c = self.points
        l_3, l_4, l_5 = self.lengths

        self.reasoning_fixture.given_engine(PythagoreanFormula(self.symbols_graph))
        given_dependencies = [
            Dependency(Statement(Predicate.CONSTANT_LENGTH, (b, c, l_5)), why=[]),
            Dependency(Statement(Predicate.CONSTANT_LENGTH, (a, b, l_3)), why=[]),
            Dependency(Statement(Predicate.CONSTANT_LENGTH, (a, c, l_4)), why=[]),
        ]
        for dep in given_dependencies:
            self.reasoning_fixture.given_added_dependency(dep)

        self.reasoning_fixture.when_resolving_dependencies()
        self.reasoning_fixture.then_new_derivations_should_be(
            [
                Derivation(
                    Statement(Predicate.PERPENDICULAR, (a, b, a, c)),
                    DependencyBody(Reason("Pythagorean"), why=given_dependencies),
                ),
            ]
        )


class TestMenelaus:
    @pytest.fixture(autouse=True)
    def setup(self, reasoning_fixture: "ReasoningEngineFixture"):
        self.solver_builder = GeometricSolverBuilder()
        self.reasoning_fixture = reasoning_fixture
        points_names = ["a", "b", "c", "d", "e", "f"]
        ratios = ["1/3", "1/2"]

        self.symbols_graph = (
            SymbolsGraphBuilder()
            .with_points_named(points_names)
            .with_ratios(ratios)
            .build()
        )
        self.points = self.symbols_graph.names2points(points_names)
        self.ratios = self.symbols_graph.names2nodes(ratios)

    @pytest.mark.parametrize("use_engine", [True, False])
    def test_simple_problem(self, use_engine: bool):
        solver_builder = self.solver_builder.load_problem_from_txt(
            "a b c = triangle a b c; "
            "f = on_line f a b, rconst2 f a b 1/2; "
            "d = on_line d b c, rconst2 d b c 1/2; "
            "e = on_line e d f, on_line e c a "
            "? rconst c e a e 4/1"
        )
        if use_engine:
            solver_builder.with_additional_reasoning_engine(MenelausFormula, "Menelaus")

        solver = solver_builder.build()
        success = solver.run()
        assert success == use_engine

    def test_implication(self):
        """Should be able to use Menelaus theorem to get the completing ratio.

        ncoll e d f, coll a b f, coll c d b, coll e d f, coll c e a
        => AF/FB * BD/DC * CE/DA = 1

        """
        a, b, c, d, e, f = self.points
        r1_3, r1_2 = self.ratios

        self.reasoning_fixture.given_engine(MenelausFormula(self.symbols_graph))

        given_dependencies = [
            Dependency(Statement(Predicate.COLLINEAR, (a, b, f)), why=[]),
            Dependency(Statement(Predicate.COLLINEAR, (c, b, d)), why=[]),
            Dependency(Statement(Predicate.COLLINEAR, (e, d, f)), why=[]),
            Dependency(Statement(Predicate.COLLINEAR, (c, e, a)), why=[]),
            Dependency(Statement(Predicate.CONSTANT_RATIO, (a, f, f, b, r1_3)), why=[]),
            Dependency(Statement(Predicate.CONSTANT_RATIO, (b, d, d, c, r1_2)), why=[]),
        ]
        for dep in given_dependencies:
            self.reasoning_fixture.given_added_dependency(dep)

        self.reasoning_fixture.when_resolving_dependencies()

        expected_r_inv_fraction = Fraction(r1_2.name) * Fraction(r1_3.name)
        expected_r, _ = self.symbols_graph.get_or_create_const_rat(
            expected_r_inv_fraction.denominator, expected_r_inv_fraction.numerator
        )

        self.reasoning_fixture.then_new_derivations_should_be(
            [
                Derivation(
                    Statement(Predicate.CONSTANT_RATIO, (c, e, a, e, expected_r)),
                    DependencyBody(Reason("Menelaus"), why=given_dependencies),
                ),
            ]
        )

    @staticmethod
    @pytest.mark.parametrize(
        "main_coll,triplet_points,inverse,output",
        [
            (
                ("a", "c", "e"),
                [("a", "b", "f"), ("d", "e", "f"), ("b", "c", "d")],
                False,
                [("a", "b", "a", "f"), ("c", "d", "b", "c"), ("e", "f", "d", "e")],
            ),
            (
                ("a", "c", "e"),
                [("a", "b", "f"), ("d", "e", "f"), ("b", "c", "d")],
                True,
                [("a", "f", "a", "b"), ("b", "c", "c", "d"), ("d", "e", "e", "f")],
            ),
            (
                ("a", "b", "i"),
                [("a", "b", "e"), ("a", "c", "k"), ("b", "c", "j")],
                False,
                [],
            ),
            (
                ("a", "c", "e"),
                [("a", "b", "f"), ("d", "c", "e"), ("b", "c", "d")],
                False,
                [],
            ),
        ],
    )
    def test_make_rconst_hashs_from_colls(
        main_coll: tuple[str, ...],
        triplet_points: list[tuple[str, ...]],
        inverse: bool,
        output: list[tuple[str, ...]],
    ):
        assert (
            make_rconst_hashs_from_colls(main_coll, triplet_points, inverse) == output
        )


@pytest.fixture
def reasoning_fixture() -> "ReasoningEngineFixture":
    return ReasoningEngineFixture()


class ReasoningEngineFixture:
    def given_engine(self, engine: ReasoningEngine):
        self._engine = engine

    def given_added_dependency(self, dependency: Dependency):
        self._engine.ingest(dependency)

    def when_resolving_dependencies(self):
        self._derivations = self._engine.resolve()

    def then_new_derivations_should_be(self, expected_derivation: list[Derivation]):
        assert self._derivations == expected_derivation
