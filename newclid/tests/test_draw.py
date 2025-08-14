from pathlib import Path

import numpy as np
import pytest
from newclid.animation import html_animation
from newclid.api import GeometricSolverBuilder
from newclid.draw.theme import DrawTheme
from newclid.jgex.problem_builder import JGEXProblemBuilder


def test_draw_initial_orthocenter(tmp_path: Path):
    rng = np.random.default_rng(1234)
    jgex_problem_builder = JGEXProblemBuilder(rng=rng).with_problem_from_txt(
        "a b c = triangle a b c; h = on_tline h b a c, on_tline h c a b ? perp a h b c"
    )
    solver = GeometricSolverBuilder(rng=rng).build(jgex_problem_builder.build())

    out_dir = tmp_path / "orthocenter"

    # Draw the initial figure
    solver.draw_figure(
        out_file=out_dir / "initial_figure.svg",
        jgex_problem=jgex_problem_builder.jgex_problem,
    )

    # Run the solver
    solver.run()

    # Draw the final figure
    solver.draw_figure(
        out_file=out_dir / "final_figure.svg",
        jgex_problem=jgex_problem_builder.jgex_problem,
    )


@pytest.mark.skip(reason="Too slow to run")
def test_draw_animation_with_jgex_problem():
    rng = np.random.default_rng(0)

    jgex_problem_builder = (
        JGEXProblemBuilder(rng=rng)
        .include_auxiliary_clauses()
        .with_problem_from_txt(
            "a m n = triangle a m n"
            "; b = on_circle b m a, on_circle b n a"
            "; c = on_line c m n, on_circle c m a"
            "; d = on_line d m n, on_circle d n a"
            "; p = circle p a c d"
            "; e = on_line e a p, on_circle e m a"
            "; f = on_line f a p, on_circle f n a"
            "; h = on_tline h p m n, on_tline h m p n"
            "; o = circle o b e f"
            "; x = on_dia x o h, on_pline x h a p"
            " | w = circle w d e f"
            " ? cong o x o b"
            "; obtuse_angle c m n"
            "; obtuse_angle m n d"
        )
    )

    solver = GeometricSolverBuilder(rng=rng).build(jgex_problem_builder.build())
    solver.run()
    assert jgex_problem_builder.jgex_problem is not None
    custom_theme = DrawTheme(
        circle_color="#000000",
        line_color="#000000",
        triangle_color="#000000",
        goal_color="#000000",
        aux_point_color="#000000",
        construction_color="#000000",
        point_color="#000000",
        text_color="#000000",
        perpendicular_color="#000000",
        title_color="#000000",
        thick_line_width=10,
        thin_line_width=5,
    )
    html_animation(
        solver.animate(jgex_problem_builder.jgex_problem, theme=custom_theme)
    )
