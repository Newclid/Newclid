import numpy as np
import pytest
from newclid.numerical.geometries import PointNum
from newclid.predicates.collinearity import Coll
from newclid.predicates.cyclic import Cyclic
from newclid.symbols.circles_registry import CirclesRegistry
from newclid.symbols.lines_registry import LinesRegistry
from newclid.symbols.points_registry import Point


class TestLinesMerging:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixture = LinesRegistryFixture()

    def test_merge_two_lines_because_they_are_collinear(self):
        a, b, c = (
            Point(num=PointNum(x=0.0, y=0.0), name="a"),
            Point(num=PointNum(x=1.0, y=0.0), name="b"),
            Point(num=PointNum(x=2.0, y=0.0), name="c"),
        )
        self.fixture.given_registry_contains_line_thru_points({a, b})
        self.fixture.when_making_collinear(Coll(points=(a, b, c)))
        self.fixture.then_registry_should_contains_lines_thru_points([{a, b, c}])


class LinesRegistryFixture:
    def __init__(self):
        self.lines_registry = LinesRegistry()

    def given_registry_contains_line_thru_points(self, points: set[Point]):
        self.lines_registry.create_line_thru_points(points)

    def when_making_collinear(self, justification: Coll):
        self.lines_registry.make_collinear(
            points=justification.points, justification=justification
        )

    def then_registry_should_contains_lines_thru_points(self, lines: list[set[Point]]):
        expected_lines_str = [
            "-".join(sorted(point.name for point in line)) for line in lines
        ]
        assert len(self.lines_registry._lines) == len(lines), (  # pyright: ignore
            f"Registry contains lines {[str(line) for line in self.lines_registry]},"
            f" but expected only lines through points {expected_lines_str}"
        )
        for line in lines:
            assert self.lines_registry.line_containing(set(line)) is not None


class TestCirclesMerging:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixture = CirclesRegistryFixture()

    def test_merge_two_circles_because_they_are_cyclic(self):
        a, b, c, d, e = (
            Point(num=PointNum(x=0.0, y=0.0), name="a"),
            Point(num=PointNum(x=1.0, y=0.0), name="b"),
            Point(num=PointNum(x=0.0, y=1.0), name="c"),
            Point(num=PointNum(x=1.0, y=1.0), name="d"),
            Point(num=PointNum(x=np.cos(np.pi / 3), y=np.sin(np.pi / 3)), name="e"),
        )
        self.fixture.given_registry_contains_circle_thru_points(
            {a, b, c, d}, Cyclic(points=(a, b, c, d))
        )
        self.fixture.when_making_cyclic(Cyclic(points=(b, c, d, e)))
        self.fixture.then_registry_should_contains_circles_thru_points(
            [{a, b, c, d, e}]
        )


class CirclesRegistryFixture:
    def __init__(self):
        self.circles_registry = CirclesRegistry()

    def given_registry_contains_circle_thru_points(
        self, points: set[Point], because: Cyclic
    ):
        self.circles_registry.create_circle_thru_points(points, because=because)

    def when_making_cyclic(self, justification: Cyclic):
        self.circles_registry.make_cyclic(
            points=justification.points, justification=justification
        )

    def then_registry_should_contains_circles_thru_points(
        self, circles: list[set[Point]]
    ):
        expected_circles_str = [
            "-".join(sorted(point.name for point in circle)) for circle in circles
        ]
        assert len(self.circles_registry._circles) == len(circles), (  # pyright: ignore
            f"Registry contains circles {[str(circle) for circle in self.circles_registry]},"
            f" but expected only circles through points {expected_circles_str}"
        )
        for circle in circles:
            assert self.circles_registry.circle_containing(set(circle)) is not None
