from typing import TYPE_CHECKING, Any, Optional

import newclid.geometry as gm
from newclid.predicates import Predicate
from newclid.numerical.angles import ang_of
from newclid.numerical.check import clock
from newclid.numerical.geometries import (
    CircleNum,
    InvalidLineIntersectError,
    InvalidQuadSolveError,
    LineNum,
    PointNum,
    bring_together,
    circle_circle_intersection,
    circle_segment_intersect,
    line_line_intersection,
)
from newclid._lazy_loading import lazy_import


if TYPE_CHECKING:
    import numpy
    import matplotlib
    import matplotlib.pyplot
    import matplotlib.colors
    import matplotlib.patches
    import matplotlib.transforms

np: "numpy" = lazy_import("numpy")
matplt: "matplotlib" = lazy_import("matplotlib")
plt: "matplotlib.pyplot" = lazy_import("matplotlib.pyplot")
colors: "matplotlib.colors" = lazy_import("matplotlib.colors")
patches: "matplotlib.patches" = lazy_import("matplotlib.patches")
transforms: "matplotlib.transforms" = lazy_import("matplotlib.transforms")


HCOLORS = None
THEME = "dark"


def draw_figure(
    points: list[gm.Point],
    lines: list[gm.Line],
    circles: list[gm.Circle],
    segments: list[gm.Segment],
    goal: Any = None,
    highlights: list[tuple[str, list[gm.Point]]] = None,
    equal_angles: Optional[list[tuple[gm.Angle, gm.Angle]]] = None,
    equal_segments: Optional[list[tuple[gm.Segment, gm.Segment]]] = None,
    block: bool = True,
    save_to: str = None,
    theme: str = "dark",
) -> None:
    """Draw everything on the same canvas."""
    plt.close()
    imsize = 512 / 100
    fig, ax = plt.subplots(figsize=(imsize, imsize), dpi=100)

    set_theme(theme)

    if get_theme() == "dark":
        ax.set_facecolor((0.0, 0.0, 0.0))
    else:
        ax.set_facecolor((1.0, 1.0, 1.0))

    _draw(ax, points, lines, circles, goal, equal_angles, equal_segments, highlights)

    plt.axis("equal")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
    if points:
        xmin = min([p.num.x for p in points])
        xmax = max([p.num.x for p in points])
        ymin = min([p.num.y for p in points])
        ymax = max([p.num.y for p in points])
        plt.margins((xmax - xmin) * 0.1, (ymax - ymin) * 0.1)

    if save_to is not None:
        fig.savefig(save_to)

    plt.show(block=block)
    if block or save_to is not None:
        plt.close(fig)


def _draw(
    ax: "matplotlib.pyplot.Axes",
    points: list[gm.Point],
    lines: list[gm.Line],
    circles: list[gm.Circle],
    goal: Any,
    equal_angles: Optional[list[tuple[gm.Angle, gm.Angle]]],
    equal_segments: Optional[list[tuple[gm.Segment, gm.Segment]]],
    highlights: list[tuple[str, list[gm.Point]]],
):
    """Draw everything."""
    colors = ["red", "green", "blue", "orange", "magenta", "purple"]
    pcolor = "black"
    lcolor = "black"
    ccolor = "grey"
    if get_theme() == "dark":
        pcolor, lcolor, ccolor = "white", "white", "cyan"
    elif get_theme() == "light":
        pcolor, lcolor, ccolor = "black", "black", "blue"
    elif get_theme() == "grey":
        pcolor, lcolor, ccolor = "black", "black", "grey"
        colors = ["grey"]

    line_boundaries = []
    for line in lines:
        p1, p2 = draw_line(ax, line, color=lcolor)
        line_boundaries.append((p1, p2))
    circles = [draw_circle(ax, c, color=ccolor) for c in circles]

    for p in points:
        draw_point(ax, p.num, p.name, line_boundaries, circles, color=pcolor)

    if equal_segments is None:
        equal_segments = []
    for i, segs in enumerate(equal_segments):
        color = colors[i % len(colors)]
        for a, b in segs:
            mark_segment(ax, a, b, color, 0.5)

    if equal_angles is None:
        equal_angles = []
    for i, args in enumerate(equal_angles):
        color = colors[i % len(colors)]
        nums = [p.num for p in args]
        highlight_angle(ax, *nums[:4], color, 0.5)
        highlight_angle(ax, *nums[4:], color, 0.5)

    if highlights:
        global HCOLORS
        if HCOLORS is None:
            HCOLORS = [
                k for k in colors.mcolors.TABLEAU_COLORS.keys() if "red" not in k
            ]

        for i, (name, args) in enumerate(highlights):
            color_i = HCOLORS[i % len(HCOLORS)]
            highlight(ax, name, args, "black", color_i, color_i)

    if goal:
        raise NotImplementedError
        name, args = goal
        lcolor = color1 = color2 = "red"
        highlight(ax, name, args, lcolor, color1, color2)


def get_theme() -> str:
    return THEME


def set_theme(theme) -> None:
    global THEME
    THEME = theme


def draw_angle(
    ax: "matplotlib.pyplot.Axes",
    head: PointNum,
    p1: PointNum,
    p2: PointNum,
    color: Any = "red",
    alpha: float = 0.5,
) -> None:
    """Draw an angle on plt ax."""
    clockwise = clock(head, p1, p2) > 0
    if not clockwise:
        p1, p2 = p2, p1

    AngleAnnotation(
        (head.x, head.y),
        (p1.x, p1.y),
        (p2.x, p2.y),
        ax=ax,
        color=color,
        alpha=alpha,
        linewidth=2,
        size=int(75 * np.random.uniform(0.5, 1.5)),
        text_kw={"color": color, "alpha": alpha},
    )


def draw_circle(
    ax: "matplotlib.pyplot.Axes", circle: CircleNum, color: Any = "cyan"
) -> CircleNum:
    """Draw a circle."""
    if circle.num is not None:
        circle = circle.num
    else:
        points = circle.neighbors(gm.Point)
        if len(points) <= 2:
            return
        points = [p.num for p in points]
        p1, p2, p3 = points[:3]
        circle = CircleNum(p1=p1, p2=p2, p3=p3)

    _draw_circle(ax, circle, color)
    return circle


def _draw_circle(
    ax: "matplotlib.pyplot.Axes", c: CircleNum, color: Any = "cyan", lw: float = 1.2
) -> None:
    ls = "-"
    if color == "--":
        color = "black"
        ls = "--"

    ax.add_patch(
        plt.Circle(
            (c.center.x, c.center.y),
            c.radius,
            color=color,
            alpha=0.8,
            fill=False,
            lw=lw,
            ls=ls,
        )
    )


def draw_line(
    ax: "matplotlib.pyplot.Axes", line: LineNum, color: Any = "white"
) -> tuple[PointNum, PointNum]:
    """Draw a line."""
    points = line.neighbors(gm.Point)
    if len(points) <= 1:
        return

    points = [p.num for p in points]
    p1, p2 = points[:2]

    ax.axline((p1.x, p1.y), (p2.x, p2.y), color=color, alpha=0.8, lw=0.2)

    pmin, pmax = (p1, 0.0), (p2, (p2 - p1).dot(p2 - p1))

    for p in points[2:]:
        v = (p - p1).dot(p2 - p1)
        if v < pmin[1]:
            pmin = p, v
        if v > pmax[1]:
            pmax = p, v

    p1, p2 = pmin[0], pmax[0]
    _draw_line(ax, p1, p2, color=color)
    return p1, p2


def _draw_line(
    ax: "matplotlib.pyplot.Axes",
    p1: PointNum,
    p2: PointNum,
    color: Any = "white",
    lw: float = 1.2,
    alpha: float = 0.8,
) -> None:
    """Draw a line in plt."""
    ls = "-"
    if color == "--":
        color = "black"
        ls = "--"

    lx, ly = (p1.x, p2.x), (p1.y, p2.y)
    ax.plot(lx, ly, color=color, lw=lw, alpha=alpha, ls=ls)


def draw_point(
    ax: "matplotlib.pyplot.Axes",
    p: PointNum,
    name: str,
    lines: list[LineNum],
    circles: list[CircleNum],
    color: Any = "white",
    size: float = 15,
) -> None:
    """draw a point."""
    ax.scatter(p.x, p.y, color=color, s=size)

    if color == "white":
        color = "lightgreen"
    else:
        color = "grey"

    name = name.upper()
    if len(name) > 1:
        name = name[0] + "_" + name[1:]

    ax.annotate(name, naming_position(ax, p, lines, circles), color=color, fontsize=15)


def mark_segment(
    ax: "matplotlib.pyplot.Axes", p1: PointNum, p2: PointNum, color: Any, alpha: float
) -> None:
    _ = alpha
    x, y = (p1.x + p2.x) / 2, (p1.y + p2.y) / 2
    ax.scatter(x, y, color=color, alpha=1.0, marker="o", s=50)


def highlight_angle(
    ax: "matplotlib.pyplot.Axes",
    a: PointNum,
    b: PointNum,
    c: PointNum,
    d: PointNum,
    color: Any,
    alpha: float,
) -> None:
    """Highlight an angle between ab and cd with (color, alpha)."""
    try:
        x, _y, x, _z = bring_together(a, b, c, d)
    except (InvalidLineIntersectError, InvalidQuadSolveError):
        return
    draw_angle(ax, x, _y, _z, color=color, alpha=alpha)


def highlight(
    ax: "matplotlib.pyplot.Axes",
    name: str,
    args: list[gm.Point],
    lcolor: Any,
    color1: Any,
    color2: Any,
) -> None:
    """Draw highlights."""
    args = list(map(lambda x: x.num if isinstance(x, gm.Point) else x, args))

    if name == Predicate.CYCLIC.value:
        a, b, c, d = args
        _draw_circle(ax, CircleNum(p1=a, p2=b, p3=c), color=color1, lw=2.0)
    if name == Predicate.COLLINEAR.value:
        a, b, c = args
        a, b = max(a, b, c), min(a, b, c)
        _draw_line(ax, a, b, color=color1, lw=2.0)
    if name == Predicate.PARALLEL.value:
        a, b, c, d = args
        _draw_line(ax, a, b, color=color1, lw=2.0)
        _draw_line(ax, c, d, color=color2, lw=2.0)
    if name == Predicate.EQANGLE.value:
        a, b, c, d, e, f, g, h = args

        x = line_line_intersection(LineNum(a, b), LineNum(c, d))
        if b.distance(x) > a.distance(x):
            a, b = b, a
        if d.distance(x) > c.distance(x):
            c, d = d, c
        a, b, d = x, a, c

        y = line_line_intersection(LineNum(e, f), LineNum(g, h))
        if f.distance(y) > e.distance(y):
            e, f = f, e
        if h.distance(y) > g.distance(y):
            g, h = h, g
        e, f, h = y, e, g

        _draw_line(ax, a, b, color=lcolor, lw=2.0)
        _draw_line(ax, a, d, color=lcolor, lw=2.0)
        _draw_line(ax, e, f, color=lcolor, lw=2.0)
        _draw_line(ax, e, h, color=lcolor, lw=2.0)
        if color1 == "--":
            color1 = "red"
        draw_angle(ax, a, b, d, color=color1, alpha=0.5)
        if color2 == "--":
            color2 = "red"
        draw_angle(ax, e, f, h, color=color2, alpha=0.5)
    if name == Predicate.PERPENDICULAR.value:
        a, b, c, d = args
        _draw_line(ax, a, b, color=color1, lw=2.0)
        _draw_line(ax, c, d, color=color1, lw=2.0)
    if name == "ratio":
        a, b, c, d, m, n = args
        _draw_line(ax, a, b, color=color1, lw=2.0)
        _draw_line(ax, c, d, color=color2, lw=2.0)
    if name == Predicate.CONGRUENT.value:
        a, b, c, d = args
        _draw_line(ax, a, b, color=color1, lw=2.0)
        _draw_line(ax, c, d, color=color2, lw=2.0)
    if name == Predicate.MIDPOINT.value:
        m, a, b = args
        _draw_line(ax, a, m, color=color1, lw=2.0, alpha=0.5)
        _draw_line(ax, b, m, color=color2, lw=2.0, alpha=0.5)
    if name == Predicate.EQRATIO.value:
        a, b, c, d, m, n, p, q = args
        _draw_line(ax, a, b, color=color1, lw=2.0, alpha=0.5)
        _draw_line(ax, c, d, color=color2, lw=2.0, alpha=0.5)
        _draw_line(ax, m, n, color=color1, lw=2.0, alpha=0.5)
        _draw_line(ax, p, q, color=color2, lw=2.0, alpha=0.5)


def naming_position(
    ax: "matplotlib.pyplot.Axes",
    p: PointNum,
    lines: list[LineNum],
    circles: list[CircleNum],
) -> tuple[float, float]:
    """Figure out a good naming position on the drawing."""
    _ = ax
    r = 0.08
    c = CircleNum(center=p, radius=r)
    avoid = []
    for p1, p2 in lines:
        try:
            avoid.extend(circle_segment_intersect(c, p1, p2))
        except InvalidQuadSolveError:
            continue
    for x in circles:
        try:
            avoid.extend(circle_circle_intersection(c, x))
        except InvalidQuadSolveError:
            continue

    if not avoid:
        return [p.x + 0.01, p.y + 0.01]

    angs = sorted([ang_of(p, a) for a in avoid])
    angs += [angs[0] + 2 * np.pi]
    angs = [(angs[i + 1] - a, a) for i, a in enumerate(angs[:-1])]

    d, a = max(angs)
    ang = a + d / 2

    name_pos = p + PointNum(np.cos(ang), np.sin(ang)) * r

    x, y = (name_pos.x - r / 1.5, name_pos.y - r / 1.5)
    return x, y


class AngleAnnotation(patches.Arc):
    """
    Draws an arc between two vectors which appears circular in display space.
    """

    def __init__(
        self,
        xy,
        p1,
        p2,
        size=75,
        unit="points",
        ax=None,
        text="",
        textposition="inside",
        text_kw=None,
        **kwargs,
    ):
        """
        Parameters
        ----------
        xy, p1, p2 : tuple or array of two floats
            Center position and two points. Angle annotation is drawn between
            the two vectors connecting *p1* and *p2* with *xy*, respectively.
            Units are data coordinates.

        size : float
            Diameter of the angle annotation in units specified by *unit*.

        unit : str
            One of the following strings to specify the unit of *size*:

            * "pixels": pixels
            * "points": points, use points instead of pixels to not have a
              dependence on the DPI
            * "axes width", "axes height": relative units of Axes width, height
            * "axes min", "axes max": minimum or maximum of relative Axes
              width, height

        ax : `matplotlib.axes.Axes`
            The Axes to add the angle annotation to.

        text : str
            The text to mark the angle with.

        textposition : {"inside", "outside", "edge"}
            Whether to show the text in- or outside the arc. "edge" can be used
            for custom positions anchored at the arc's edge.

        text_kw : dict
            Dictionary of arguments passed to the Annotation.

        **kwargs
            Further parameters are passed to `matplotlib.patches.Arc`. Use this
            to specify, color, linewidth etc. of the arc.

        """
        self.ax = ax or plt.gca()
        self._xydata = xy  # in data coordinates
        self.vec1 = p1
        self.vec2 = p2
        self.size = size
        self.unit = unit
        self.textposition = textposition

        super().__init__(
            self._xydata,
            size,
            size,
            angle=0.0,
            theta1=self.theta1,
            theta2=self.theta2,
            **kwargs,
        )

        self.set_transform(transforms.IdentityTransform())
        self.ax.add_patch(self)

        self.kw = dict(
            ha="center",
            va="center",
            xycoords=transforms.IdentityTransform(),
            xytext=(0, 0),
            textcoords="offset points",
            annotation_clip=True,
        )
        self.kw.update(text_kw or {})
        self.text = ax.annotate(text, xy=self._center, **self.kw)

    def get_size(self):
        factor = 1.0
        if self.unit == "points":
            factor = self.ax.figure.dpi / 72.0
        elif self.unit[:4] == "axes":
            b = transforms.TransformedBbox(transforms.Bbox.unit(), self.ax.transAxes)
            dic = {
                "max": max(b.width, b.height),
                "min": min(b.width, b.height),
                "width": b.width,
                "height": b.height,
            }
            factor = dic[self.unit[5:]]
        return self.size * factor

    def set_size(self, size):
        self.size = size

    def get_center_in_pixels(self):
        """return center in pixels"""
        return self.ax.transData.transform(self._xydata)

    def set_center(self, xy):
        """set center in data coordinates"""
        self._xydata = xy

    def get_theta(self, vec):
        vec_in_pixels = self.ax.transData.transform(vec) - self._center
        return np.rad2deg(np.arctan2(vec_in_pixels[1], vec_in_pixels[0]))

    def get_theta1(self):
        return self.get_theta(self.vec1)

    def get_theta2(self):
        return self.get_theta(self.vec2)

    def set_theta(self, angle):
        pass

    # Redefine attributes of the Arc to always give values in pixel space
    _center = property(get_center_in_pixels, set_center)
    theta1 = property(get_theta1, set_theta)
    theta2 = property(get_theta2, set_theta)
    width = property(get_size, set_size)
    height = property(get_size, set_size)

    # The following two methods are needed to update the text position.
    def draw(self, renderer):
        self.update_text()
        super().draw(renderer)

    def update_text(self):
        c = self._center
        s = self.get_size()
        angle_span = (self.theta2 - self.theta1) % 360
        angle = np.deg2rad(self.theta1 + angle_span / 2)
        r = s / 2
        if self.textposition == "inside":
            r = s / np.interp(angle_span, [60, 90, 135, 180], [3.3, 3.5, 3.8, 4])
        self.text.xy = c + r * np.array([np.cos(angle), np.sin(angle)])
        if self.textposition == "outside":

            def R90(a, r, w, h):
                if a < np.arctan(h / 2 / (r + w / 2)):
                    return np.sqrt((r + w / 2) ** 2 + (np.tan(a) * (r + w / 2)) ** 2)
                else:
                    c = np.sqrt((w / 2) ** 2 + (h / 2) ** 2)
                    T = np.arcsin(c * np.cos(np.pi / 2 - a + np.arcsin(h / 2 / c)) / r)
                    xy = r * np.array([np.cos(a + T), np.sin(a + T)])
                    xy += np.array([w / 2, h / 2])
                    return np.sqrt(np.sum(xy**2))

            def R(a, r, w, h):
                aa = (a % (np.pi / 4)) * ((a % (np.pi / 2)) <= np.pi / 4) + (
                    np.pi / 4 - (a % (np.pi / 4))
                ) * ((a % (np.pi / 2)) >= np.pi / 4)
                return R90(aa, r, *[w, h][:: int(np.sign(np.cos(2 * a)))])

            bbox = self.text.get_window_extent()
            X = R(angle, r, bbox.width, bbox.height)
            trans = self.ax.figure.dpi_scale_trans.inverted()
            offs = trans.transform(((X - s / 2), 0))[0] * 72
            self.text.set_position([offs * np.cos(angle), offs * np.sin(angle)])
