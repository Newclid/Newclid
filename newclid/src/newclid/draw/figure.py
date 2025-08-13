from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from matplotlib.text import Annotation

from newclid.draw.jgex_constructions import draw_jgex_problem_clauses
from newclid.draw.predicates import draw_predicate
from newclid.draw.theme import DrawTheme
from newclid.proof_justifications import goals_justifications
from newclid.symbols.points_registry import Point

if TYPE_CHECKING:
    from newclid.jgex.formulation import JGEXFormulation
    from newclid.proof_state import ProofState


def init_figure(ax: Axes, points: list[Point]) -> None:
    ax.set_facecolor((0.0, 0.0, 0.0))
    ax.set_aspect("equal")

    xmin, xmax = min(p.num.x for p in points), max(p.num.x for p in points)
    x_range = xmax - xmin
    ymin, ymax = min(p.num.y for p in points), max(p.num.y for p in points)
    y_range = ymax - ymin
    side_range = max(x_range, y_range)

    ax.set_xlim(xmin - 0.1 * side_range, xmin + 1.1 * side_range)
    ax.set_ylim(ymin - 0.1 * side_range, ymin + 1.1 * side_range)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)


def draw_figure(
    fig: Figure,
    ax: Axes,
    proof: "ProofState",
    jgex_problem: JGEXFormulation | None,
    theme: DrawTheme,
    save_to: Path | None = None,
    format: str = "svg",
) -> tuple[Figure, Axes]:
    """Draw everything on the same canvas."""
    symbols_registry = proof.symbols
    points: list[Point] = list(symbols_registry.points.name_to_point.values())
    init_figure(ax, points)
    ax.set_aspect("equal", adjustable="datalim")

    if jgex_problem is not None:
        draw_jgex_problem_clauses(
            ax,
            jgex_problem=jgex_problem,
            symbols_registry=symbols_registry,
            theme=theme,
        )

    if proof.check_goals():
        justifications, _ = goals_justifications(proof.goals, proof_state=proof)
        predicates_to_draw = [
            justification.predicate for justification in justifications
        ]
    else:
        predicates_to_draw = proof.graph.predicates

    for predicate in predicates_to_draw:
        draw_predicate(ax, predicate, symbols_registry, theme=theme)
    for p in points:
        draw_point(ax, p, point_color=theme.point_color, zorder=100)

    if save_to is not None:
        save_to.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_to, format=format)  # type: ignore

    return fig, ax


def draw_point(
    ax: "Axes",
    p: Point,
    point_color: str,
    fontsize: float = 20,
    point_size: float = 25.0,
    zorder: float = 100.0,
) -> tuple[PathCollection, Annotation]:
    """draw a point."""
    point_artist = ax.scatter(  # type: ignore
        p.num.x,
        p.num.y,
        color=point_color,
        s=point_size,
        zorder=zorder,
        rasterized=True,
    )
    annotation_artist = ax.annotate(  # type: ignore
        str(p),
        (p.num.x, p.num.y),
        color=point_color,
        fontsize=fontsize,
        zorder=zorder,
        rasterized=True,
    )
    return point_artist, annotation_artist
