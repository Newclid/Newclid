from copy import deepcopy
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, Collection, Optional, Union

import numpy as np


from newclid.numerical.geometries import (
    PointNum,
    intersect,
)
from newclid.dependencies.symbols import Point, Circle, Line
import matplotlib.patches as patches
from numpy.random import Generator
from matplotlib.axes import Axes
from matplotlib.figure import Figure

if TYPE_CHECKING:
    from newclid.proof import ProofState
    from newclid.statement import Statement

PALETTE = [
    "#e6194b",
    "#3cb44b",
    "#ffe119",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#46f0f0",
    "#f032e6",
    "#bcf60c",
    "#fabebe",
    "#008080",
    "#e6beff",
    "#9a6324",
    "#fffac8",
    "#800000",
    "#aaffc3",
    "#808000",
    "#ffd8b1",
    "#0000cd",
    "#808080",
    "#ffffff",
]


def init_figure() -> "Figure":
    imsize = 512 / 100
    fig = Figure(figsize=(imsize, imsize))
    ax = fig.add_subplot(111)  # type: ignore
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
    ax.set_facecolor((0.0, 0.0, 0.0))
    ax.set_aspect("equal", adjustable="datalim")
    return fig


def draw_figure(
    proof: "ProofState",
    *,
    save_to: Optional[Union[Path, BytesIO]] = None,
    rng: Generator,
    format: str = "svg",
) -> None:
    """Draw everything on the same canvas."""
    if proof.fig is None:
        raise ValueError(
            "Cannot draw the figure if the ProofState was built without it."
        )

    symbols_graph = proof.symbols_graph
    points: list[Point] = list(symbols_graph.nodes_of_type(Point))
    fig = deepcopy(proof.fig)
    (ax,) = fig.axes

    if proof.check_goals():
        _draw(
            ax,
            points,
            [dep.statement for dep in proof.dep_graph.proof_deps(proof.goals)],
            rng,
        )
    else:
        _draw(ax, points, proof.dep_graph.checked(), rng)

    if save_to is not None:
        fig.savefig(save_to, format=format)  # type: ignore


def _draw(
    ax: "Axes", points: list[Point], statements: Collection["Statement"], rng: Generator
):
    """Draw everything."""
    for statement in statements:
        statement.draw(ax, rng)
    for p in points:
        draw_point(ax, p)


def fill_missing(d0: dict[Any, Any], d1: dict[Any, Any]):
    for k in d1.keys():
        if k not in d0:
            d0[k] = d1[k]


def draw_circle(ax: "Axes", c: Circle, **args: Any) -> None:
    fill_missing(
        args,
        {
            "color": "cyan",
            "fill": False,
            "lw": 0.8,
        },
    )
    ax.add_patch(
        patches.Circle(  # type: ignore
            (c.num.center.x, c.num.center.y), c.num.radius, **args
        )
    )


def draw_line(ax: "Axes", line: Line, **args: Any):
    """Draw a line. Return the two extremities"""
    fill_missing(args, {"color": "white", "lw": 0.4, "alpha": 0.9})

    points: list[PointNum] = [p.num for p in line.points]
    p0, p1 = points[:2]
    ax.axline((p0.x, p0.y), (p1.x, p1.y), **args)  # type: ignore


def draw_segment(ax: "Axes", p0: Point, p1: Point, **args: Any):
    fill_missing(args, {"color": "white", "lw": 0.4, "alpha": 0.9})
    ax.plot((p0.num.x, p1.num.x), (p0.num.y, p1.num.y), **args)  # type: ignore


def draw_segment_num(ax: "Axes", p0: PointNum, p1: PointNum, **args: Any):
    fill_missing(args, {"color": "white", "lw": 0.4, "alpha": 0.9})
    ax.plot((p0.x, p1.x), (p0.y, p1.y), **args)  # type: ignore


def draw_angle(ax: "Axes", line0: Line, line1: Line, **args: Any):
    (o,) = intersect(line0.num, line1.num)
    ang0, ang1 = line0.num.angle(), line1.num.angle()
    if ang0 > ang1:
        ang0, ang1 = ang1, ang0
    if ang0 - ang1 + np.pi < ang1 - ang0:
        ang0, ang1 = ang1 - np.pi, ang0
    wedge = patches.Wedge(
        (o.x, o.y), theta1=ang0 / np.pi * 180, theta2=ang1 / np.pi * 180, **args
    )
    ax.add_patch(wedge)


def draw_rectangle(ax: "Axes", line0: Line, line1: Line, **args: Any):
    (o,) = intersect(line0.num, line1.num)
    ang0 = min(line0.num.angle(), line1.num.angle())
    rectangle = patches.Rectangle((o.x, o.y), angle=ang0 / np.pi * 180, **args)
    ax.add_patch(rectangle)


def draw_point(
    ax: "Axes",
    p: Point,
    args_point: Optional[dict[Any, Any]] = None,
    args_name: Optional[dict[Any, Any]] = None,
) -> None:
    """draw a point."""
    args_point = args_point or {}
    args_name = args_name or {}
    fill_missing(args_point, {"color": "white", "s": 5.0})
    ax.scatter(p.num.x, p.num.y, **args_point)  # type: ignore
    fill_missing(args_name, {"color": "lime", "fontsize": 10})
    ax.annotate(  # type: ignore
        p.pretty_name, (p.num.x, p.num.y), **args_name
    )
