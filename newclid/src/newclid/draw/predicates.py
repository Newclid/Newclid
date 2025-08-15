from random import random
from typing import Any, cast

import numpy as np
from matplotlib import patches
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.lines import AxLine, Line2D

from newclid.draw.geometries import draw_circle_symbol
from newclid.draw.theme import PALETTE, DrawTheme, fill_missing
from newclid.jgex.geometries import LENGTH_UNIT
from newclid.numerical.geometries import PointNum, line_line_intersection
from newclid.predicates import Predicate
from newclid.predicates._index import PredicateType
from newclid.predicates.congruence import Cong
from newclid.predicates.equal_angles import EqAngle
from newclid.predicates.equal_ratios import EqRatio
from newclid.predicates.perpendicularity import Perp
from newclid.symbols.lines_registry import LineSymbol
from newclid.symbols.points_registry import Line, Point
from newclid.symbols.symbols_registry import SymbolsRegistry


def draw_predicate(
    ax: Axes,
    predicate: Predicate,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> set[Artist]:
    match predicate.predicate_type:
        case PredicateType.COLLINEAR:
            line = symbols.lines.line_containing(set(predicate.points))
            if line is None:
                raise ValueError(f"Line not found for args: {predicate.points}")

            return {
                draw_line_symbol(
                    ax,
                    line,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                    ls="dashed",
                )
            }
        case PredicateType.EQUAL_ANGLES:
            return _draw_equal_angle_predicate(ax, predicate, symbols, theme=theme)
        case PredicateType.CONGRUENT:
            return cast(
                set[Artist],
                _draw_congruent_predicate(ax, predicate, theme=theme),
            )
        case PredicateType.PERPENDICULAR:
            return _draw_perpendicular_predicate(ax, predicate, symbols, theme=theme)
        case PredicateType.CYCLIC:
            circle = symbols.circles.circle_containing(set(predicate.points))
            if circle is None:
                raise ValueError(f"Circle not found for args: {predicate.points}")
            return {
                draw_circle_symbol(
                    ax,
                    circle,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                )
            }
        case PredicateType.PARALLEL:
            return cast(
                set[Artist],
                _draw_parallel(ax, (predicate.line1, predicate.line2), theme=theme),
            )
        case PredicateType.SIMTRI_CLOCK | PredicateType.SIMTRI_REFLECT:
            triangles_sides = set(_draw_triangle(ax, *predicate.triangle1, theme=theme))
            return cast(set[Artist], triangles_sides)
        case PredicateType.EQUAL_RATIOS:
            return cast(
                set[Artist],
                _draw_eqratio_predicate(ax, predicate, symbols, theme=theme),
            )
        case _:
            return set()


def _draw_eqratio_predicate(
    ax: "Axes", predicate: EqRatio, symbols: SymbolsRegistry, theme: DrawTheme
) -> set[Line2D]:
    segments: set[Line2D] = set()
    segments.update(
        _draw_segment_num(
            ax,
            predicate.ratio1[0][0].num,
            predicate.ratio1[0][1].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        )
    )
    segments.update(
        _draw_segment_num(
            ax,
            predicate.ratio1[0][0].num,
            predicate.ratio1[0][1].num,
            line_color=theme.perpendicular_color,
            line_width=theme.thick_line_width,
        )
    )
    segments.update(
        _draw_segment_num(
            ax,
            predicate.ratio2[0][0].num,
            predicate.ratio2[0][1].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        )
    )
    segments.update(
        _draw_segment_num(
            ax,
            predicate.ratio2[0][0].num,
            predicate.ratio2[0][1].num,
            line_color=theme.perpendicular_color,
            line_width=theme.thick_line_width,
        )
    )
    return segments


def _draw_perpendicular_predicate(
    ax: "Axes", predicate: Perp, symbols: SymbolsRegistry, theme: DrawTheme
) -> set[Artist]:
    line1 = symbols.lines.line_containing(set(predicate.line1))
    if line1 is None:
        raise ValueError(f"Line not found for args: {predicate.line1}")
    line2 = symbols.lines.line_containing(set(predicate.line2))
    if line2 is None:
        raise ValueError(f"Line not found for args: {predicate.line2}")
    return _draw_perpendicular_lines(ax, line1, line2, theme=theme)


def _draw_perpendicular_lines(
    ax: "Axes", line1: LineSymbol, line2: LineSymbol, theme: DrawTheme
) -> set[Artist]:
    return {
        draw_perp_rectangle(
            ax,
            line1,
            line2,
            color=theme.perpendicular_color,
            zorder=0,
        ),
        draw_line_symbol(
            ax,
            line1,
            line_color=theme.line_color,
            line_width=theme.thin_line_width,
            zorder=0,
        ),
        draw_line_symbol(
            ax,
            line2,
            line_color=theme.line_color,
            line_width=theme.thin_line_width,
            zorder=0,
        ),
    }


def draw_perp_rectangle(
    ax: "Axes",
    line0: LineSymbol,
    line1: LineSymbol,
    color: str,
    **kwargs: Any,
) -> patches.Rectangle:
    args = fill_missing(
        {
            "color": color,
            "fill": False,
            "width": 0.025 * LENGTH_UNIT,
            "height": 0.025 * LENGTH_UNIT,
        },
        kwargs,
    )
    (o,) = line_line_intersection(line0.num, line1.num, ensure_point=True)
    ang0 = min(line0.num.angle(), line1.num.angle())
    rectangle = patches.Rectangle((o.x, o.y), angle=ang0 / np.pi * 180, **args)  # type: ignore
    ax.add_patch(rectangle)
    return rectangle


def _draw_congruent_predicate(
    ax: "Axes", predicate: Cong, theme: DrawTheme
) -> set[Line2D]:
    segments: set[Line2D] = set()
    for a, b in (predicate.segment1, predicate.segment2):
        segments.update(
            _draw_segment(
                ax,
                a,
                b,
                line_color=theme.line_color,
                line_width=theme.thick_line_width,
            )
        )
    return segments


def _draw_parallel(
    ax: "Axes",
    lines: tuple[Line, Line],
    theme: DrawTheme,
) -> set[Line2D]:
    setattr(ax, "para_color", (getattr(ax, "para_color", 0) + 1) % len(PALETTE))
    seglen: int | float = 100
    lines_artists: set[Line2D] = set()

    for a, b in lines:
        lines_artists.update(
            _draw_segment(
                ax,
                a,
                b,
                line_color=theme.line_color,
                line_width=theme.thin_line_width,
                ls="dashed",
            )
        )
        seglen = min(seglen, a.num.distance(b.num))

    seglen /= 3.0
    for a, b in lines:
        d = b.num - a.num  # type: ignore
        d = d / abs(d)  # type: ignore
        d = d.rot90()
        if d.x < 0.0:
            d = -0.03 * d
        else:
            d = 0.03 * d
        p = b.num - a.num  # type: ignore
        p = p / abs(p)  # type: ignore
        p = p * (a.num.distance(b.num) - seglen) * 0.5
        lines_artists.update(
            _draw_segment_num(
                ax,
                a.num + d + p,
                b.num + d - p,
                line_color=PALETTE[ax.para_color],  # type: ignore
                line_width=theme.thin_line_width,
            )
        )
    return lines_artists


def _draw_equal_angle_predicate(
    ax: "Axes",
    predicate: EqAngle,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> set[Artist]:
    angles: list[tuple[LineSymbol, LineSymbol]] = []
    for angle in (predicate.angle1, predicate.angle2):
        l1 = symbols.lines.line_containing(set(angle[0]))
        l2 = symbols.lines.line_containing(set(angle[1]))
        assert l1 and l2
        angles.append((l1, l2))
    return _draw_equal_angles(ax, angles[0], angles[1], theme=theme)


def _draw_equal_angles(
    ax: "Axes",
    angle1: tuple[LineSymbol, LineSymbol],
    angle2: tuple[LineSymbol, LineSymbol],
    theme: DrawTheme,
) -> set[Artist]:
    setattr(ax, "angle_color", (getattr(ax, "angle_color", 0) + 1) % len(PALETTE))
    color = PALETTE[ax.angle_color]  # type: ignore
    r = (1 + 4 * random()) * LENGTH_UNIT / 50
    border_width = 0.05 * r
    artists: set[Artist] = set()
    for line1, line2 in (angle1, angle2):
        if not line1.num.is_parallel(line2.num):
            artists.add(
                _draw_angle_wedge(
                    ax,
                    line1,
                    line2,
                    color=color,
                    alpha=0.5,
                    r=r,
                    width=border_width,
                    zorder=1,
                )
            )
        artists.add(
            draw_line_symbol(
                ax,
                line1,
                line_color=theme.line_color,
                line_width=theme.thin_line_width,
                ls=":",
                zorder=1,
            )
        )
        artists.add(
            draw_line_symbol(
                ax,
                line2,
                line_color=theme.line_color,
                line_width=theme.thin_line_width,
                ls=":",
                zorder=1,
            )
        )
    return artists


def _draw_angle_wedge(
    ax: "Axes", line0: LineSymbol, line1: LineSymbol, **args: Any
) -> patches.Wedge:
    (o,) = line_line_intersection(line0.num, line1.num, ensure_point=True)
    ang0, ang1 = line0.num.angle(), line1.num.angle()
    if ang0 > ang1:
        ang0, ang1 = ang1, ang0
    if ang0 - ang1 + np.pi < ang1 - ang0:
        ang0, ang1 = ang1 - np.pi, ang0
    wedge = patches.Wedge(
        (o.x, o.y),
        theta1=ang0 / np.pi * 180,
        theta2=ang1 / np.pi * 180,
        **args,
    )
    ax.add_patch(wedge)
    return wedge


def draw_line_symbol(
    ax: "Axes", line: LineSymbol, line_color: str, line_width: float, **kwargs: Any
) -> AxLine:
    """Draw a line. Return the two extremities"""
    points: list[PointNum] = [p.num for p in line.points]
    p0, p1 = points[:2]
    return draw_line(ax, p0, p1, line_color=line_color, line_width=line_width, **kwargs)  # type: ignore


def draw_line(
    ax: "Axes",
    p0: PointNum,
    p1: PointNum,
    line_color: str,
    line_width: float,
    **kwargs: Any,
) -> AxLine:
    kwargs = fill_missing(kwargs, {"color": line_color, "lw": line_width})
    return ax.axline((p0.x, p0.y), (p1.x, p1.y), **kwargs)  # type: ignore


def _draw_triangle(
    ax: "Axes",
    a: Point,
    b: Point,
    c: Point,
    theme: DrawTheme,
) -> set[Line2D]:
    lines: set[Line2D] = set()
    lines.update(
        _draw_segment(
            ax,
            a,
            b,
            line_color=theme.line_color,
            line_width=theme.thin_line_width,
            ls="dashed",
        )
    )
    lines.update(
        _draw_segment(
            ax,
            b,
            c,
            line_color=theme.line_color,
            line_width=theme.thin_line_width,
            ls="dashed",
        )
    )
    lines.update(
        _draw_segment(
            ax,
            a,
            c,
            line_color=theme.line_color,
            line_width=theme.thin_line_width,
            ls="dashed",
        )
    )
    return lines


def _draw_segment(
    ax: "Axes",
    p0: Point,
    p1: Point,
    line_color: str,
    line_width: float,
    ls: str = "solid",
) -> list[Line2D]:
    lines = ax.plot(  # type: ignore
        (p0.num.x, p1.num.x),
        (p0.num.y, p1.num.y),
        color=line_color,
        lw=line_width,
        ls=ls,
    )
    return lines


def _draw_segment_num(
    ax: "Axes",
    p0: PointNum,
    p1: PointNum,
    line_color: str,
    line_width: float,
    **kwargs: Any,
) -> list[Line2D]:
    args = fill_missing(kwargs, {"color": line_color, "lw": line_width})
    lines = ax.plot((p0.x, p1.x), (p0.y, p1.y), **args)  # type: ignore
    return lines


def draw_free_perpendicular_symbol(
    ax: Axes,
    foot: PointNum,
    other_point: PointNum,
    theme: DrawTheme,
) -> Artist:
    vector = other_point - foot
    angle = vector.angle()
    rectangle = patches.Rectangle(
        (foot.x, foot.y),
        angle=angle / np.pi * 180,
        color=theme.perpendicular_color,
        fill=False,
        width=0.025,
        height=0.025,
    )  # type: ignore
    ax.add_artist(rectangle)
    return rectangle
