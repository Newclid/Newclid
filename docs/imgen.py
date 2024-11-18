from __future__ import annotations
import os

import numpy as np
from numpy.random import random, choice
from random import sample
from random import seed as pyseed
import matplotlib.pyplot as plt

from datetime import datetime
from pathlib import Path
from typing import Optional

from newclid import AGENTS_REGISTRY
from newclid.api import GeometricSolverBuilder
from newclid.configs import default_configs_path


from newclid.numerical.geometries import Circle, Line, Point, Angle, Segment

from typing import Any
from newclid.theorem import Theorem


def seed(k):
    np.random.seed(k)
    pyseed(k)


def load_problem(
    problem_txt_or_file: str,
    translate: bool,
    solver_builder: GeometricSolverBuilder,
) -> None:
    PATH_NAME_SEPARATOR = ":"

    if PATH_NAME_SEPARATOR not in problem_txt_or_file:
        solver_builder.load_problem_from_txt(problem_txt_or_file, translate)
        return

    path, problem_name = problem_txt_or_file.split(PATH_NAME_SEPARATOR)
    solver_builder.load_problem_from_file(Path(path), problem_name, translate)


def resolve_config_path(path_str: Optional[str]) -> Optional[Path]:
    if path_str is None:
        return path_str

    path = Path(path_str)
    if path.exists():
        return path

    path = default_configs_path().joinpath(path_str)
    if path.exists():
        return path

    raise FileNotFoundError(
        f"Could not find file for path {path} nor under default_configs"
    )


def resolve_output_path(path_str: Optional[str], problem_name: str) -> Path:
    if path_str is None:
        if problem_name:
            return Path("run_results") / problem_name
        return Path("run_results") / str(datetime.now())
    return Path(path_str)


def draw_line(
    ax: plt.Axes,
    line: Line,
    style: Any = "white",
    lw: float = 1.2,
    alpha: float = 0.8,
) -> None:
    """Draw a line in plt."""
    if style == "--":
        color = "grey"
        ls = "--"
    else:
        color = style
        ls = "-"

    p1 = Point(100, 100).foot(line)
    p2 = Point(-100, -100).foot(line)
    # print(p1, p2)
    ax.plot((p1.x, p2.x), (p1.y, p2.y), color=color, lw=lw, alpha=alpha, ls=ls)


def draw_segment(
    ax: plt.Axes,
    s: Segment,
    style: Any = "white",
    lw: float = 1.2,
    alpha: float = 0.8,
) -> None:
    """Draw a line in plt."""
    if style == "--":
        color = "black"
        ls = "--"
    else:
        color = style
        ls = "-"

    # print(s.p1, s.p2)
    ax.plot((s.p1.x, s.p2.x), (s.p1.y, s.p2.y), color=color, lw=lw, alpha=alpha, ls=ls)


def draw_point(
    ax: plt.Axes,
    p: Point,
    name: str,
    color: str = "lightgreen",
    size: float = 15,
) -> None:
    """draw a point."""
    ax.scatter(p.x, p.y, color=color, s=size)
    ax.annotate(name, (p.x, p.y), color=color, fontsize=15)


def draw_angle(ax: plt.Axes, angle: Angle, color1: Any, color2: Any) -> None:
    """Draw an angle on plt ax."""
    draw_line(ax, angle.l1, color1)
    draw_line(ax, angle.l2, color2)


def draw_circle(
    ax: plt.Axes,
    circle: Circle,
    color: Any = None,
) -> None:
    """Draw an angle on plt ax."""
    if color is None:
        color = "white"
    # print(tuple(circle.center))
    # ax.add_patch(patches.Circle(tuple(circle.center), circle.radius, edgecolor=color))
    # print(circle.radius)
    ax.add_patch(
        plt.Circle(
            tuple(circle.center),
            circle.radius,
            color=color,
            alpha=0.8,
            fill=False,
        )
    )
    # add_patch(patches.Circle((5, 5), circle.radius, edgecolor=color))


def metaexchange(A, B, C, D):
    if random() < 0.5:
        A, B, C, D = C, D, A, B
    if random() < 0.5:
        A, B = B, A
    if random() < 0.5:
        C, D = D, C
    return A, B, C, D


def isany(A, *args) -> bool:
    for B in args:
        if A is B:
            return True
    return False


# Applying
# After the move, it should be guarantee that the predicate is satisfied on the given points
# Somehow minimal move should be implemented
# Every combination of moving points should be randomly possibly chosen


def apply_perp(A: Point, B: Point, C: Point, D: Point):
    while True:
        A, B, C, D = metaexchange(A, B, C, D)
        if not isany(D, A, B):
            break
    direction = C.perpendicular_line(Line(A, B)).point_at(100) - C
    direction /= abs(direction)
    # print(direction)
    res = C + (D - C).dot(direction) * direction
    D.x, D.y = res.x, res.y


def apply_ncoll(*points):
    line = Line(points[0], points[1])
    for i in range(2, len(points)):
        p = points[i]
        if line.point_at(p.x, p.y) is not None:
            for p in points:
                p.x, p.y = random(), random()
            return


def apply_eqangle(
    A: Point, B: Point, C: Point, D: Point, E: Point, F: Point, G: Point, H: Point
):
    faith = 20
    flag = 1.0
    while True and faith > 0:
        if random() < 0.5:
            A, B, C, D, E, F, G, H = E, F, G, H, A, B, C, D
        if random() < 0.5:
            flag *= -1.0
            E, F, G, H = G, H, E, F
        if random() < 0.5:
            G, H = H, G
        if not isany(H, A, B, C, D):
            break
        faith -= 1
    alpha = flag * ((D - C).angle() - (B - A).angle())
    direction = (F - E).rotatea(alpha)
    direction /= abs(direction)
    res = G + direction.dot(H - G) * direction
    H.x, H.y = res.x, res.y


apply_eqangle6 = apply_eqangle


def apply_cong(A: Point, B: Point, C: Point, D: Point, rand=True):
    while True and rand:
        A, B, C, D = metaexchange(A, B, C, D)
        if not isany(D, A, B):
            break
    if A is D or B is D:
        return
    direction = D - C
    direction /= abs(direction)
    res = C + abs(A - B) * direction
    D.x, D.y = res.x, res.y


def apply_cyclic(*points: list[Point]):
    points = choice(points, len(points), replace=False)
    circle = Circle(p1=points[0], p2=points[1], p3=points[2])
    for i in range(3, len(points)):
        p = points[i]
        direction = p - circle.center
        direction /= abs(direction)
        res = circle.center + circle.radius * direction
        p.x, p.y = res.x, res.y


def apply_circle(Op: Point, A: Point, B: Point, C: Point):
    A, B, C = sample([A, B, C], 3)
    if random() < 0.5:
        res = Circle(p1=A, p2=B, p3=C).center
        Op.x = res.x
        Op.y = res.y
    else:
        apply_cong(Op, A, Op, B, False)
        apply_cong(Op, A, Op, C, False)


def apply_para(A: Point, B: Point, C: Point, D: Point, rand: bool = True):
    if rand:
        A, B, C, D = metaexchange(A, B, C, D)
    direction = B - A
    # print(direction)
    # print(abs(direction))
    direction /= abs(direction)
    res = C + direction.dot(D - C) * direction
    D.x, D.y = res.x, res.y
    # assert not math.isnan(D.x)
    # assert not math.isnan(D.y)


def apply_npara(A: Point, B: Point, C: Point, D: Point, rand: bool = True):
    pass


def apply_midp(E: Point, A: Point, B: Point):
    if random() < 0.5:
        A, B = B, A
    if random() < 0.5:
        res = (A + B) / 2
        E.x, E.y = res.x, res.y
    else:
        res = E + E - A
        B.x, B.y = res.x, res.y


def apply_coll(*points: list[Point]):
    points = choice(points, len(points), replace=False)
    direction = points[1] - points[0]
    direction /= abs(direction)
    for i in range(2, len(points)):
        # print(i)
        p = points[i]
        # print(p, points[i])
        res = points[1] + direction.dot(p - points[1]) * direction
        p.x = res.x
        p.y = res.y
        # assert not math.isnan(p.x)
        # assert not math.isnan(p.y)


def apply_eqratio3(A: Point, B: Point, C: Point, D: Point, M: Point, N: Point):
    return
    # (A, B), (C, D), (M, N) = sample([(A, B), (C, D), (M, N)], 3)
    # apply_para(A, B, C, D, False)
    # apply_para(C, D, M, N, False)
    # if M == N:
    #     res = Line(A, C).intersect(Line(B, D))
    #     M.x, M.y = res.x, res.y
    #     N.x, N.y = res.x, res.y
    # else:
    #     # print(">")
    #     # print(M, N)
    #     res = M.foot(Line(A, C))
    #     M.x, M.y = res.x, res.y
    #     res = N.foot(Line(A, C))
    #     N.x, N.y = res.x, res.y
    #     # print(M, N)
    #     # print("<")
    #     res = Line(B, D).intersect(Line(M, N))
    #     N.x, N.y = res.x, res.y


def apply_eqratio(
    A: Point, B: Point, C: Point, D: Point, E: Point, F: Point, G: Point, H: Point
):
    faith = 20
    while True and faith > 0:
        if random() < 0.5:
            (A, B), (C, D), (E, F), (G, H) = (E, F), (G, H), (A, B), (C, D)
        if random() < 0.5:
            G, H = H, G
        if isany(H, A, B, C, D):
            break
        faith -= 1
    direction = H - G
    direction /= abs(direction)
    res = G + direction * (abs(F - E) * abs(D - C) / abs(B - A))
    H.x, H.y = res.x, res.y


apply_eqratio6 = apply_eqratio


def apply_sameside(Op: Point, A: Point, B: Point, E: Point, X: Point, Y: Point):
    while True:
        if random() < 0.5:
            A, Op, B, X, E, Y = X, E, Y, A, Op, B
        if random() < 0.5:
            X, Y = Y, X
        if Y != A and Y != B and Y != Op:
            break
    sign = 1 if (B - Op).dot(A - Op) > 0 else -1
    res = E + sign * (Y - E)
    Y.x, Y.y = res.x, res.y


# Adding


def random_color():
    return (
        random() * 0.5 + 0.5,
        random() * 0.5 + 0.5,
        random() * 0.5 + 0.5,
    )


def add_perp(ax, A: Point, B: Point, C: Point, D: Point):
    draw_line(ax, Line(A, B))
    draw_line(ax, Line(C, D))


def add_ncoll(*args, **kwargs):
    return


def add_para(*args, **kwargs):
    return


def add_npara(*args, **kwargs):
    return


def add_eqangle(
    ax, A: Point, B: Point, C: Point, D: Point, E: Point, F: Point, G: Point, H: Point
):
    color1 = random_color()
    color2 = random_color()
    draw_angle(ax, Angle(Line(A, B), Line(C, D)), color1=color1, color2=color2)
    draw_angle(ax, Angle(Line(E, F), Line(G, H)), color1=color1, color2=color2)


add_eqangle6 = add_eqangle


def add_cong(ax, A: Point, B: Point, C: Point, D: Point):
    color = random_color()
    draw_segment(ax, Segment(A, B), style=color)
    draw_segment(ax, Segment(C, D), style=color)


def add_cyclic(ax, *points: list[Point]):
    draw_circle(ax, Circle(p1=points[0], p2=points[1], p3=points[2]))


def add_midp(ax, E: Point, A: Point, B: Point):
    draw_segment(ax, Segment(A, B))


def add_coll(ax, *points: list[Point]):
    draw_line(ax, Line(points[0], points[1]), style="--")


def add_eqratio3(*args, **kwargs):
    return


def add_eqratio(*args, **kwargs):
    return


add_eqratio6 = add_eqratio


def add_circle(ax, Op: Point, A: Point, B: Point, C: Point):
    add_cyclic(ax, A, B, C)


def add_sameside(ax, A: Point, Op: Point, B: Point, X: Point, E: Point, Y: Point):
    draw_segment(ax, Segment(Op, A))
    draw_segment(ax, Segment(Op, B))
    draw_segment(ax, Segment(E, X))
    draw_segment(ax, Segment(E, Y))


def draw_rule(
    rule: Theorem,
    init_points: dict[str, Any] | int,
    block: bool = True,
    save_to: str = None,
    theme: str = "dark",
):
    if init_points == -1:
        return
    if isinstance(init_points, int):
        seed(init_points)
    else:
        seed(233)
    props = rule.premises + [rule.conclusion]
    name2point: dict[str, Point] = dict()
    for construction in rule.premises:
        for arg in construction.args:
            name2point[arg] = (
                Point(*init_points[arg])
                if isinstance(init_points, dict) and init_points.get(arg) is not None
                else Point(x=random(), y=random())
            )

    def reset_if_unrational(name2point):
        rational = False
        flag = False
        while not rational:
            if flag:
                for name in name2point:
                    name2point[name] = Point(x=random(), y=random())
            flag = True
            rational = True
            for name, p in name2point.items():
                if abs(p.x) > 50 or abs(p.y) > 50:
                    rational = False
                    break
                for name1, p1 in name2point.items():
                    if name == name1:
                        continue
                    if p.distance(p1) < 0.01:
                        rational = False
                        break
                if not rational:
                    break

    to_be_ignored = ["contri", "contri2", "contri*", "simtri", "simtri2", "simtri*"]
    for _ in range(200):
        construction = choice(props)
        if construction.name in to_be_ignored:
            continue
        print(construction.name, construction.args)
        reset_if_unrational(name2point)
        globals()["apply_" + construction.name](
            *[name2point[point_name] for point_name in construction.args]
        )

    points = [t for _, t in name2point.items()]
    pointnames = [t for t, _ in name2point.items()]

    imsize = 512 / 100
    fig, ax = plt.subplots(figsize=(imsize, imsize), dpi=100)

    if theme == "dark":
        ax.set_facecolor((0.0, 0.0, 0.0))
    else:
        ax.set_facecolor((1.0, 1.0, 1.0))

    for i in range(len(points)):
        draw_point(ax, points[i], pointnames[i])

    plt.axis("equal")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
    xmin = min([p.x for p in points])
    xmax = max([p.x for p in points])
    ymin = min([p.y for p in points])
    ymax = max([p.y for p in points])
    xmargin = (xmax - xmin) * 0.1
    ymargin = (ymax - ymin) * 0.1
    plt.xlim(xmin - xmargin, xmax + xmargin)
    plt.ylim(ymin - ymargin, ymax + ymargin)

    for construction in props:
        if construction.name in to_be_ignored:
            continue
        globals()["add_" + construction.name](
            ax, *[name2point[point_name] for point_name in construction.args]
        )

    if save_to is not None:
        fig.savefig(save_to)

    if block:
        plt.show(block=block)
    plt.close(fig)


def demo_draw_rule(k, save_to=None, block=True):
    solver_builder = GeometricSolverBuilder()
    load_problem(
        "../problems_datasets/testing_minimal_rules.txt:r00", False, solver_builder
    )
    solver_builder.load_defs_from_file(resolve_config_path(None))

    relative_path = r"..\src\newclid\default_configs\new_rules.txt"
    absolute_path = os.path.abspath(relative_path)
    solver_builder.load_rules_from_file(absolute_path)

    agent = AGENTS_REGISTRY.load_agent("bfsddar")
    solver_builder.with_deductive_agent(agent)

    solver = solver_builder.build()

    # print(len(solver.rules))
    print(k)
    rule = solver.rules[k]
    init_points = dict()
    shift = 0.8
    init_points[0] = 20
    init_points[1] = 20
    init_points[2] = 30
    init_points[3] = 30
    init_points[4] = 10
    init_points[5] = 101
    init_points[6] = 15
    init_points[7] = 10
    init_points[8] = 15
    init_points[9] = {
        "a": (0.07, 0.58),
        "b": (0.21, 0.85),
        "c": (-0.02, 0.47),
        "d": (0.34, 0.75),
        "e": (0.3, 0.63),
        "f": (0.44, 0.63),
        "m": (0.07 + shift, 0.58 + shift),
        "n": (0.21 + shift, 0.85 + shift),
        "p": (-0.02 + shift, 0.47 + shift),
        "q": (0.34 + shift, 0.75 + shift),
        "r": (0.3 + shift, 0.63 + shift),
        "u": (0.44 + shift, 0.63 + shift),
    }
    init_points[10] = -1  # no need for figure
    init_points[11] = 7  # How to prove this?
    # init_points[11] = {
    #     'a' : (0.3, 0.2),
    #     'b' : (0.2, 0.64),
    #     'c' : (1.13, 0.64),
    #     'd' : (0.45, 0.64)
    # }
    init_points[12] = 12  # to be fixed eqratio
    init_points[13] = 15
    init_points[14] = 15
    # init_points[15] = {
    #     'O' : (0.55, 0.55),
    #     'A' : (0.52, 0.95),
    #     'B' : (0.25, 0.25),
    #     'C' : (0.92, 0.25),
    #     'X' : (0.05, 0.94)
    # }
    init_points[15] = 20
    init_points[16] = 20
    init_points[17] = 20
    init_points[18] = 11
    # init_points[18] = {
    #     'O' : (0.52, 0.49),
    #     'A' : (0.25, 0.72),
    #     'B' : (0.71, 0.79),
    #     'C' : (0.86, 0.37),
    #     'M' : (0.79, 0.56)
    # }
    init_points[19] = 10
    init_points[20] = 10
    # init_points[20] = {
    #     'O' : (0.52, 0.49),
    #     'A' : (0.25, 0.72),
    #     'B' : (0.71, 0.79),
    #     'C' : (0.86, 0.37),
    #     # 'M' : (0.79, 0.56)
    # }
    init_points[21] = 19
    init_points[22] = 10
    init_points[23] = 15
    init_points[24] = 20
    # init_points[24] = {
    #     'O' : (0.36, 0.45),
    #     'A' : (0.29, 0.21),
    #     'B' : (0.14, 0.57),
    #     'P' : (0.14, 0.34),
    #     'Q' : (0.58, 0.58),
    # }
    init_points[25] = 15
    init_points[26] = 1
    init_points[27] = 13
    # init_points[27] = {
    #     'O' : (0.51, 0.82),
    #     'A' : (0.31, 0.59),
    #     'C' : (0.13, 0.34),
    #     'B' : (0.72, 0.61),
    #     'D' : (0.82, 0.1)
    # }
    init_points[28] = 1
    init_points[29] = 1
    init_points[30] = 2
    init_points[31] = 120
    init_points[32] = 2
    init_points[33] = 233
    init_points[34] = 2
    init_points[35] = 2
    init_points[36] = 3
    init_points[37] = 2
    init_points[38] = 4
    init_points[39] = 2
    init_points[40] = 2
    init_points[41] = 2
    init_points[42] = 2

    draw_rule(rule, init_points.get(k, 0), save_to=save_to, block=block)


if __name__ == "__main__":
    for k in range(50):
        demo_draw_rule(k, f"_static/Images/rules/r{k:02d}", block=False)
