from typing import Iterable

from matplotlib.artist import Artist
from matplotlib.axes import Axes

from newclid.draw.geometries import draw_circle, draw_triangle
from newclid.draw.predicates import draw_line, draw_line_symbol, draw_perp_rectangle
from newclid.draw.theme import DrawTheme
from newclid.jgex.clause import JGEXConstruction
from newclid.jgex.formulation import JGEXFormulation
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
        case "circle":
            x, a, _b, _c = symbols_registry.points.names2points(construction.args)  # type: ignore
            return [
                draw_circle(
                    ax=ax,
                    center=(x.num.x, x.num.y),
                    radius=x.num.distance(a.num),
                    line_color=theme.line_color,
                    line_width=theme.thick_line_width,
                )
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
        case "triangle":
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
        case "on_pline":
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
        case "midpoint":
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
        case _:
            return []
