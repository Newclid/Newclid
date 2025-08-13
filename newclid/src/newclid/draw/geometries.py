from typing import TypedDict

from matplotlib import patches
from matplotlib.artist import Artist
from matplotlib.axes import Axes

from newclid.numerical.geometries import PointNum
from newclid.symbols.circles_registry import CircleSymbol


class ArtistKwargs(TypedDict, total=False):
    color: str
    lw: float
    linewidth: float
    linestyle: str
    alpha: float
    zorder: int
    arrowstyle: str | patches.ArrowStyle
    width: float
    height: float
    fill: bool


def draw_circle_symbol(
    ax: Axes,
    circle: CircleSymbol,
    line_color: str,
    line_width: float,
) -> Artist:
    return draw_circle(
        ax,
        (circle.num.center.x, circle.num.center.y),
        circle.num.radius,
        line_color,
        line_width,
    )


def draw_circle(
    ax: Axes,
    center: tuple[float, float],
    radius: float,
    line_color: str,
    line_width: float,
) -> Artist:
    circle = patches.Circle(
        center,
        radius,
        color=line_color,
        fill=False,
        lw=line_width,
    )
    ax.add_artist(circle)
    return circle


def draw_triangle(
    ax: Axes,
    p0: PointNum,
    p1: PointNum,
    p2: PointNum,
    line_color: str,
    line_width: float,
) -> Artist:
    triangle = patches.Polygon(
        ((p0.x, p0.y), (p1.x, p1.y), (p2.x, p2.y)),
        closed=True,
        zorder=15,
        color=line_color,
        lw=line_width,
        fill=False,
    )
    ax.add_artist(triangle)
    return triangle


def draw_segment(
    ax: Axes,
    p0: PointNum,
    p1: PointNum,
    line_color: str,
    line_width: float,
) -> Artist:
    segment = patches.Polygon(
        ((p0.x, p0.y), (p1.x, p1.y)),
        closed=False,
        zorder=15,
        color=line_color,
        lw=line_width,
        fill=False,
    )
    ax.add_artist(segment)
    return segment


def draw_arrow(
    ax: Axes,
    p0: PointNum,
    p1: PointNum,
    line_color: str,
    line_width: float,
) -> Artist:
    midpoint = (p0 + p1) / 2
    arrow = patches.FancyArrowPatch(
        (p0.x, p0.y),
        (midpoint.x, midpoint.y),
        zorder=5,
        color=line_color,
        lw=line_width,
        arrowstyle="simple,head_length=10,head_width=10",
    )
    ax.add_artist(arrow)
    return arrow
