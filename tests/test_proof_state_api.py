from pathlib import Path

import pytest
import pytest_check as check
from newclid.api import GeometricSolverBuilder


MAX_LEVEL = 10


def test_false_problem_should_still_draw(tmp_path: Path):
    false_problem_str = (
        "a b = segment a b; "
        "c = on_tline c a a b, on_circle c a b; "
        "e = s_angle b a e 55o, on_circle e a b; "
        "d = s_angle b a d 30o, on_circle d a b; "
        "f = on_line f a e, on_line f b c; "
        "g = on_line g a d, on_line g b c "
        "? cong c f g b"
    )

    solver = (
        GeometricSolverBuilder(no_goal=True)
        .load_problem_from_txt(false_problem_str)
        .build()
    )
    solver.draw_figure(tmp_path / "figure.png")


class TestProof:
    @pytest.fixture(autouse=True)
    def setup(self):
        solver = (
            GeometricSolverBuilder()
            .load_problem_from_txt(
                "a b c = triangle a b c; "
                "h = orthocenter a b c; "
                "h1 = foot a b c; "
                "h2 = foot b c a; "
                "h3 = foot c a b; "
                "g1 g2 g3 g = centroid g1 g2 g3 g a b c; "
                "o = circle a b c "
                "? coll h g o",
                translate=False,
            )
            .build()
        )
        self.proof = solver.proof_state
        self.symbols_graph = self.proof.symbols_graph
        self.checker = self.proof.statements.checker

    def test_add_auxiliary_construction(self):
        solver = (
            GeometricSolverBuilder()
            .load_problem_from_txt(
                "a b c = triangle a b c; "
                "d = on_tline d b a c, on_tline d c a b "
                "? perp a d b c",
                translate=False,
            )
            .build()
        )
        solver.add_auxiliary_construction("e = on_line e a c, on_line e b d")
        success = solver.run()
        assert success

    def test_auxiliary_construction_build_error(self):
        """Should raise an error when trying an impossible construction though the api."""
        with pytest.raises(ValueError, match="Auxiliary construction failed"):
            solver = (
                GeometricSolverBuilder()
                .load_problem_from_txt(
                    "a b c = ieq_triangle a b c; m = midpoint m a b; n = midpoint n m a",
                    translate=False,
                )
                .build()
            )
            solver.add_auxiliary_construction("e = on_circle e n a, on_line e b c")

    def test_build_points(self):
        all_points = self.symbols_graph.all_points()
        check.equal(
            {p.name for p in all_points},
            {"a", "b", "c", "g", "h", "o", "g1", "g2", "g3", "h1", "h2", "h3"},
        )

    def test_build_predicates(self):
        (a, b, c, g, h, o, g1, g2, g3, h1, h2, h3) = self.symbols_graph.names2points(
            ["a", "b", "c", "g", "h", "o", "g1", "g2", "g3", "h1", "h2", "h3"]
        )

        # Explicit statements:
        check.is_true(self.checker.check_cong([b, g1, g1, c]))
        check.is_true(self.checker.check_cong([c, g2, g2, a]))
        check.is_true(self.checker.check_cong([a, g3, g3, b]))
        check.is_true(self.checker.check_perp([a, h1, b, c]))
        check.is_true(self.checker.check_perp([b, h2, c, a]))
        check.is_true(self.checker.check_perp([c, h3, a, b]))
        check.is_true(self.checker.check_cong([o, a, o, b]))
        check.is_true(self.checker.check_cong([o, b, o, c]))
        check.is_true(self.checker.check_cong([o, a, o, c]))
        check.is_true(self.checker.check_coll([a, g, g1]))
        check.is_true(self.checker.check_coll([b, g, g2]))
        check.is_true(self.checker.check_coll([g1, b, c]))
        check.is_true(self.checker.check_coll([g2, c, a]))
        check.is_true(self.checker.check_coll([g3, a, b]))
        check.is_true(self.checker.check_perp([a, h, b, c]))
        check.is_true(self.checker.check_perp([b, h, c, a]))

        # These are NOT part of the premises:
        check.is_false(self.checker.check_perp([c, h, a, b]))
        check.is_false(self.checker.check_coll([c, g, g3]))

        # These are automatically inferred by the graph datastructure:
        check.is_true(self.checker.check_eqangle([a, h1, b, c, b, h2, c, a]))
        check.is_true(self.checker.check_eqangle([a, h1, b, h2, b, c, c, a]))
        check.is_true(self.checker.check_eqratio([b, g1, g1, c, c, g2, g2, a]))
        check.is_true(self.checker.check_eqratio([b, g1, g1, c, o, a, o, b]))
        check.is_true(self.checker.check_para([a, h, a, h1]))
        check.is_true(self.checker.check_para([b, h, b, h2]))
        check.is_true(self.checker.check_coll([a, h, h1]))
        check.is_true(self.checker.check_coll([b, h, h2]))
