from typing import Iterable

from matplotlib.artist import Artist
from matplotlib.axes import Axes

from newclid.draw.geometries import (
    draw_arrow,
    draw_circle,
    draw_complete_arrow,
    draw_segment,
    draw_triangle,
)
from newclid.draw.predicates import draw_line, draw_line_symbol, draw_perp_rectangle
from newclid.draw.rule import circumcenter_of_triangle
from newclid.draw.theme import DrawTheme
from newclid.jgex.clause import JGEXConstruction
from newclid.jgex.formulation import JGEXFormulation
from newclid.symbols.points_registry import Triangle
from newclid.symbols.symbols_registry import SymbolsRegistry


def draw_jgex_problem_clauses(
    ax: Axes,
    jgex_problem: JGEXFormulation,
    symbols_registry: SymbolsRegistry,
    theme: DrawTheme,
):
    for clause in jgex_problem.clauses:
        for construction in clause.constructions:
            draw_jgex_constructions(
                ax, construction, symbols_registry=symbols_registry, theme=theme
            )


def draw_jgex_constructions(
    ax: Axes,
    construction: JGEXConstruction,
    symbols_registry: SymbolsRegistry,
    theme: DrawTheme,
) -> Iterable[Artist]:
    match construction.name:
        case "circle" | "circumcenter":
            x, a, b, c = symbols_registry.points.names2points(construction.args)  # type: ignore
            return [
                draw_circle(
                    ax=ax,
                    center=(x.num.x, x.num.y),
                    radius=x.num.distance(a.num),
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_triangle(
                    ax,
                    a.num,
                    b.num,
                    c.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
            ]
        case "on_circum":
            x, a, b, c = symbols_registry.points.names2points(construction.args)  # type: ignore
            triangle = Triangle([a, b, c])
            center = circumcenter_of_triangle(triangle)
            return [
                draw_triangle(
                    ax,
                    a.num,
                    b.num,
                    c.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_circle(
                    ax=ax,
                    center=(center.x, center.y),
                    radius=center.distance(a.num),
                    line_color=theme.circle_color,
                    line_width=theme.thick_line_width,
                ),
            ]
        case "on_circle":
            _x, o, a = symbols_registry.points.names2points(construction.args)  # type: ignore
            radius = o.num.distance(a.num)
            return [
                draw_circle(
                    ax=ax,
                    center=(o.num.x, o.num.y),
                    radius=radius,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                )
            ]
        case "triangle" | "acute_triangle" | "triangle12":
            a, b, c = symbols_registry.points.names2points(construction.args)  # type: ignore
            return [
                draw_triangle(
                    ax=ax,
                    p0=a.num,
                    p1=b.num,
                    p2=c.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                )
            ]
        case "quadrangle":
            a, b, c, d = symbols_registry.points.names2points(construction.args)  # type: ignore
            return [
                draw_segment(
                    ax=ax,
                    p0=a.num,
                    p1=b.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_segment(
                    ax=ax,
                    p0=b.num,
                    p1=c.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_segment(
                    ax=ax,
                    p0=c.num,
                    p1=d.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_segment(
                    ax=ax,
                    p0=d.num,
                    p1=a.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
            ]
        case "pentagon":
            a, b, c, d, e = symbols_registry.points.names2points(construction.args)  # type: ignore
            return [
                draw_segment(
                    ax=ax,
                    p0=a.num,
                    p1=b.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_segment(
                    ax=ax,
                    p0=b.num,
                    p1=c.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_segment(
                    ax=ax,
                    p0=c.num,
                    p1=d.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_segment(
                    ax=ax,
                    p0=d.num,
                    p1=e.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_segment(
                    ax=ax,
                    p0=e.num,
                    p1=a.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
            ]
        case "on_line":
            _x, a, b = symbols_registry.points.names2points(construction.args)  # type: ignore
            return [
                draw_line(
                    ax=ax,
                    p0=a.num,
                    p1=b.num,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                )
            ]
        case "on_tline":
            x, y, a, b = symbols_registry.points.names2points(construction.args)  # type: ignore
            xy = symbols_registry.lines.line_thru_pair(x, y)
            ab = symbols_registry.lines.line_thru_pair(a, b)
            return [
                draw_line_symbol(
                    ax=ax,
                    line=xy,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line_symbol(
                    ax=ax,
                    line=ab,
                    line_color=theme.line_color,
                    line_width=theme.thin_line_width,
                    ls=":",
                ),
                draw_perp_rectangle(
                    ax=ax,
                    line0=xy,
                    line1=ab,
                    color=theme.perpendicular_color,
                ),
            ]
        case "on_pline" | "on_pline0":
            x, y, a, b = symbols_registry.points.names2points(construction.args)  # type: ignore
            return [
                draw_line(
                    ax=ax,
                    p0=a.num,
                    p1=b.num,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line(
                    ax=ax,
                    p0=x.num,
                    p1=y.num,
                    line_color=theme.line_color,
                    line_width=theme.thin_line_width,
                    ls=":",
                ),
            ]
        case "intersection_ll":
            _x, a, b, c, d = symbols_registry.points.names2points(construction.args)  # type: ignore
            ab = symbols_registry.lines.line_thru_pair(a, b)
            cd = symbols_registry.lines.line_thru_pair(c, d)
            return [
                draw_line_symbol(
                    ax=ax,
                    line=ab,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line_symbol(
                    ax=ax,
                    line=cd,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
            ]
        case "intersection_lp":
            x, a, b, c, m, n = symbols_registry.points.names2points(construction.args)  # type: ignore
            ab = symbols_registry.lines.line_thru_pair(a, b)
            mn = symbols_registry.lines.line_thru_pair(m, n)
            return [
                draw_line_symbol(
                    ax=ax,
                    line=ab,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line_symbol(
                    ax=ax,
                    line=mn,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line(
                    ax=ax,
                    p0=c.num,
                    p1=x.num,
                    line_color=theme.line_color,
                    line_width=theme.thin_line_width,
                    ls=":",
                ),
            ]
        case "on_dia":
            x, a, b = symbols_registry.points.names2points(construction.args)  # type: ignore
            xa = symbols_registry.lines.line_thru_pair(x, a)
            xb = symbols_registry.lines.line_thru_pair(x, b)
            return [
                draw_line_symbol(
                    ax=ax,
                    line=xa,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line_symbol(
                    ax=ax,
                    line=xb,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_perp_rectangle(
                    ax=ax,
                    line0=xa,
                    line1=xb,
                    color=theme.perpendicular_color,
                ),
            ]
        case "r_triangle":
            x, a, b = symbols_registry.points.names2points(construction.args)  # type: ignore
            xa = symbols_registry.lines.line_thru_pair(x, a)
            xb = symbols_registry.lines.line_thru_pair(x, b)
            return [
                draw_triangle(
                    ax=ax,
                    p0=x.num,
                    p1=a.num,
                    p2=b.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_perp_rectangle(
                    ax=ax,
                    line0=xa,
                    line1=xb,
                    color=theme.perpendicular_color,
                ),
            ]
        case "midpoint" | "between" | "between_bound":
            x, a, b = symbols_registry.points.names2points(construction.args)  # type: ignore
            ab = symbols_registry.lines.line_thru_pair(a, b)
            return [
                draw_line_symbol(
                    ax=ax,
                    line=ab,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
            ]
        case "trisegment":
            x, y, a, b = symbols_registry.points.names2points(construction.args)  # type: ignore
            ab = symbols_registry.lines.line_thru_pair(a, b)
            return [
                draw_line_symbol(
                    ax=ax,
                    line=ab,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
            ]
        case "segment":
            a, b = symbols_registry.points.names2points(construction.args)  # type: ignore
            return [
                draw_line(
                    ax=ax,
                    p0=a.num,
                    p1=b.num,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                )
            ]
        case "foot":
            f, a, b, c = symbols_registry.points.names2points(construction.args)  # type: ignore
            af = symbols_registry.lines.line_thru_pair(a, f)
            bc = symbols_registry.lines.line_thru_pair(b, c)
            return [
                draw_line_symbol(
                    ax=ax,
                    line=af,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line_symbol(
                    ax=ax,
                    line=bc,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_perp_rectangle(
                    ax=ax, line0=af, line1=bc, color=theme.perpendicular_color
                ),
            ]
        case "incenter":
            d, a, b, c = symbols_registry.points.names2points(construction.args)  # type: ignore
            ad = symbols_registry.lines.line_thru_pair(a, d)
            bd = symbols_registry.lines.line_thru_pair(b, d)
            cd = symbols_registry.lines.line_thru_pair(c, d)
            return [
                draw_triangle(
                    ax,
                    a.num,
                    b.num,
                    c.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line_symbol(
                    ax=ax,
                    line=ad,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line_symbol(
                    ax=ax,
                    line=bd,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line_symbol(
                    ax=ax,
                    line=cd,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
            ]
        case "excenter":
            d, a, b, c = symbols_registry.points.names2points(construction.args)  # type: ignore
            ad = symbols_registry.lines.line_thru_pair(a, d)
            bd = symbols_registry.lines.line_thru_pair(b, d)
            cd = symbols_registry.lines.line_thru_pair(c, d)
            return [
                draw_triangle(
                    ax,
                    a.num,
                    b.num,
                    c.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line_symbol(
                    ax=ax,
                    line=ad,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line_symbol(
                    ax=ax,
                    line=bd,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
                draw_line_symbol(
                    ax=ax,
                    line=cd,
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                ),
            ]
        case "simtri" | "simtrir":
            r, a, b, c, p, q = symbols_registry.points.names2points(construction.args)  # type: ignore
            return [
                draw_triangle(
                    ax=ax,
                    p0=a.num,
                    p1=b.num,
                    p2=c.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_triangle(
                    ax=ax,
                    p0=p.num,
                    p1=q.num,
                    p2=r.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_arrow(
                    ax,
                    a.num,
                    b.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
                draw_arrow(
                    ax,
                    b.num,
                    c.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
                draw_arrow(
                    ax,
                    c.num,
                    a.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
                draw_arrow(
                    ax,
                    p.num,
                    q.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
                draw_arrow(
                    ax,
                    q.num,
                    r.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
                draw_arrow(
                    ax,
                    r.num,
                    p.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
            ]
        case "contri" | "contrir":
            q, r, a, b, c, p = symbols_registry.points.names2points(construction.args)  # type: ignore
            return [
                draw_triangle(
                    ax=ax,
                    p0=a.num,
                    p1=b.num,
                    p2=c.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_triangle(
                    ax=ax,
                    p0=p.num,
                    p1=q.num,
                    p2=r.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thick_line_width,
                ),
                draw_arrow(
                    ax,
                    a.num,
                    b.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
                draw_arrow(
                    ax,
                    b.num,
                    c.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
                draw_arrow(
                    ax,
                    c.num,
                    a.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
                draw_arrow(
                    ax,
                    p.num,
                    q.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
                draw_arrow(
                    ax,
                    q.num,
                    r.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
                draw_arrow(
                    ax,
                    r.num,
                    p.num,
                    line_color=theme.triangle_color,
                    line_width=theme.thin_line_width,
                ),
            ]
        case "shift":
            x, b, c, d = symbols_registry.points.names2points(construction.args)
            return [
                draw_complete_arrow(
                    ax,
                    d.num,
                    c.num,
                    line_color=theme.line_color,
                    line_width=theme.thin_line_width,
                ),
                draw_complete_arrow(
                    ax,
                    b.num,
                    x.num,
                    line_color=theme.line_color,
                    line_width=theme.thin_line_width,
                ),
            ]
        case "mirror":
            x, a, b = symbols_registry.points.names2points(construction.args)
            return [
                draw_complete_arrow(
                    ax,
                    b.num,
                    a.num,
                    line_color=theme.line_color,
                    line_width=theme.thin_line_width,
                ),
                draw_complete_arrow(
                    ax,
                    b.num,
                    x.num,
                    line_color=theme.line_color,
                    line_width=theme.thin_line_width,
                ),
            ]
        # Create an explicit case for constructions that do not need anything to be drawn but the points
        case "free":
            return []
        case _:
            return []
