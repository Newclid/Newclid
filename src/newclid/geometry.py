"""Implements geometric objects used in the graph representation."""

from __future__ import annotations
from fractions import Fraction
from typing import TYPE_CHECKING, Any, Generator, Optional, Type, TypeVar
from typing_extensions import Self

if TYPE_CHECKING:
    from newclid.dependencies.dependency import Dependency

T = TypeVar("T")


class Symbol:
    r"""Symbol in the symbols graph.

    Can be Point, Line, Circle, etc.

    Each node maintains a merge history to
    other nodes if they are (found out to be) equivalent

    ::
        a -> b -
                \
            c -> d -> e -> f -> g


    d.merged_to = e
    d.rep = g
    d.merged_from = {a, b, c, d}
    d.equivs = {a, b, c, d, e, f, g}

    """

    def __init__(self, name: str = "", graph: Any = None):
        self.name = name or str(self)
        self.graph = graph

        self.edge_graph: dict[Symbol, dict[Self, list["Dependency"]]] = {}
        # Edge graph: what other nodes is connected to this node.
        # edge graph = {
        #   other1: {self1: deps, self2: deps},
        #   other2: {self2: deps, self3: deps}
        # }

        self.merge_graph: dict[Self, dict[Self, list["Dependency"]]] = {}
        # Merge graph: history of merges with other nodes.
        # merge_graph = {self1: {self2: deps1, self3: deps2}}

        self.rep_by = None  # represented by.
        self.members = {self}

        self._val: Optional[Symbol] = None
        self._obj: Optional[Symbol] = None

        self.deps: list["Dependency"] = []

        # numerical representation.
        self.num = None
        self.change = set()  # what other nodes' num rely on this node?

    def set_rep(self, node: Symbol) -> None:
        if node == self:
            return
        self.rep_by = node
        node.merge_edge_graph(self.edge_graph)
        node.members.update(self.members)

    def rep(self) -> Self:
        x = self
        while x.rep_by:
            x = x.rep_by
        return x

    def why_rep(self) -> list[Any]:
        return self.why_equal([self.rep()])

    def rep_and_why(self) -> tuple[Self, list["Dependency"]]:
        rep = self.rep()
        return rep, self.why_equal([rep])

    def neighbors(
        self, oftype: Type[T], return_set: bool = False, do_rep: bool = True
    ) -> list[T] | set[T]:
        """Neighbors of this node in the proof state graph."""
        if do_rep:
            rep = self.rep()
        else:
            rep = self
        result = set()

        for n in rep.edge_graph:
            if oftype is None or oftype and isinstance(n, oftype):
                if do_rep:
                    result.add(n.rep())
                else:
                    result.add(n)

        if return_set:
            return result
        return list(result)

    def merge_edge_graph(
        self, new_edge_graph: dict[Symbol, dict[Symbol, list[Symbol]]]
    ) -> None:
        for x, xdict in new_edge_graph.items():
            if x in self.edge_graph:
                self.edge_graph[x].update(dict(xdict))
            else:
                self.edge_graph[x] = dict(xdict)

    def merge(self, nodes: list[Symbol], deps: list["Dependency"]) -> None:
        for node in nodes:
            self.merge_one(node, deps)

    def merge_one(self, node: Symbol, deps: list["Dependency"]) -> None:
        node.rep().set_rep(self.rep())

        if node in self.merge_graph:
            return

        self.merge_graph[node] = deps
        node.merge_graph[self] = deps

    def is_val(self, node: Symbol) -> bool:
        return (
            isinstance(self, Line)
            and isinstance(node, Direction)
            or isinstance(self, Segment)
            and isinstance(node, Length)
            or isinstance(self, Length)
            and isinstance(node, LengthValue)
            or isinstance(self, Angle)
            and isinstance(node, AngleValue)
            or isinstance(self, Ratio)
            and isinstance(node, RatioValue)
        )

    def set_val(self, node: Symbol) -> None:
        self._val = node

    def set_obj(self, node: Symbol) -> None:
        self._obj = node

    @property
    def val(self) -> Symbol:
        if self._val is None:
            return None
        return self._val.rep()

    @property
    def obj(self) -> Symbol:
        if self._obj is None:
            return None
        return self._obj.rep()

    def equivs(self) -> set[Self]:
        return self.rep().members

    def connect_to(self, node: Symbol, deps: list["Dependency"] = None) -> None:
        rep = self.rep()

        if node in rep.edge_graph:
            rep.edge_graph[node].update({self: deps})
        else:
            rep.edge_graph[node] = {self: deps}

        if self.is_val(node):
            self.set_val(node)
            node.set_obj(self)

    def equivs_upto(self) -> dict[Symbol, Symbol]:
        """What are the equivalent nodes."""
        parent = {self: None}
        visited = set()
        queue = [self]
        i = 0

        while i < len(queue):
            current = queue[i]
            i += 1
            visited.add(current)

            for neighbor in current.merge_graph:
                if neighbor in visited:
                    continue
                queue.append(neighbor)
                parent[neighbor] = current

        return parent

    def why_equal(self, others: list[Symbol]) -> list["Dependency"]:
        """BFS why this node is equal to other nodes."""
        others = set(others)
        found = 0

        parent = {}
        queue = [self]
        i = 0

        while i < len(queue):
            current = queue[i]
            if current in others:
                found += 1
            if found == len(others):
                break

            i += 1

            for neighbor in current.merge_graph:
                if neighbor in parent:
                    continue
                queue.append(neighbor)
                parent[neighbor] = current

        return bfs_backtrack(self, others, parent)

    def why_equal_groups(
        self, groups: list[list[Symbol]]
    ) -> tuple[list["Dependency"], list[Symbol]]:
        """BFS for why self is equal to at least one member of each group."""
        others = [None for _ in groups]
        found = 0

        parent = {}
        queue = [self]
        i = 0

        while i < len(queue):
            current = queue[i]

            for j, grp in enumerate(groups):
                if others[j] is None and current in grp:
                    others[j] = current
                    found += 1

            if found == len(others):
                break

            i += 1

            for neighbor in current.merge_graph:
                if neighbor in parent:
                    continue
                queue.append(neighbor)
                parent[neighbor] = current

        return bfs_backtrack(self, others, parent), others

    def __repr__(self) -> str:
        return self.name


def is_equiv(x: Symbol, y: Symbol) -> bool:
    return x.why_equal([y]) is not None


def is_equal(x: Symbol, y: Symbol) -> bool:
    if x == y:
        return True
    if x._val is None or y._val is None:
        return False
    if x.val != y.val:
        return False
    return is_equiv(x._val, y._val)


def bfs_backtrack(
    root: Symbol, leafs: list[Symbol], parent: dict[Symbol, Symbol]
) -> list["Dependency"]:
    """Return the path given BFS trace of parent nodes."""
    backtracked = {root}  # no need to backtrack further when touching this set.
    deps = []
    for node in leafs:
        if node is None:
            return None
        if node in backtracked:
            continue
        if node not in parent:
            return None
        while node not in backtracked:
            backtracked.add(node)
            dep = node.merge_graph[parent[node]]
            deps.append(dep)
            node = parent[node]

    return deps


class Point(Symbol):
    rely_on: list[Point] = None
    plevel: int
    group: list[Self]
    dep_points = set[Self]
    why: list["Dependency"]  # to generate txt logs.


class Line(Symbol):
    """Symbol of type Line."""

    points: tuple[Point, Point]
    _val: Direction

    def new_val(self) -> Direction:
        return Direction()

    def why_coll(self, points: list[Point]) -> Optional[list["Dependency"]]:
        """Why points are connected to self."""

        groups: list[list[Point]] = []
        for p in points:
            group = [
                level
                for level, dependency in self.edge_graph[p].items()
                if dependency is None
            ]
            if not group:
                return None
            groups.append(group)

        min_deps = None
        for line in groups[0]:
            deps, others = line.why_equal_groups(groups[1:])
            if deps is None:
                continue
            for p, o in zip(points, [line] + others):
                deps.append(self.edge_graph[p][o])
            if min_deps is None or len(deps) < len(min_deps):
                min_deps = deps

        if min_deps is None:
            return None
        return [d for d in min_deps if d is not None]


class Segment(Symbol):
    points: tuple[Point, Point]
    _val: Length

    def new_val(self) -> Length:
        return Length()


class Circle(Symbol):
    """Symbol of type Circle."""

    points: list[Point]

    def why_cyclic(self, points: list[Point]) -> list[Any]:
        """Why points are connected to self."""
        groups: list[list[Circle]] = []
        for p in points:
            group = [c for c, d in self.edge_graph[p].items() if d is None]
            if not group:
                return None
            groups.append(group)

        min_deps = None
        for circle in groups[0]:
            deps, others = circle.why_equal_groups(groups[1:])
            if deps is None:
                continue
            for p, o in zip(points, [circle] + others):
                deps.append(self.edge_graph[p][o])

            if min_deps is None or len(deps) < len(min_deps):
                min_deps = deps

        if min_deps is None:
            return None
        return [d for d in min_deps if d is not None]


class Angle(Symbol):
    """Symbol of type Angle."""

    opposite: Optional[Angle] = None
    _d: tuple[Optional[Direction], Optional[Direction]] = (None, None)
    _val: AngleValue

    def new_val(self) -> AngleValue:
        return AngleValue()

    def set_directions(self, d1: Direction, d2: Direction) -> None:
        self._d = d1, d2

    @property
    def directions(self) -> tuple[Direction, Direction]:
        d1, d2 = self._d
        if d1 is None or d2 is None:
            return d1, d2
        return d1.rep(), d2.rep()


class Ratio(Symbol):
    """Symbol of type Ratio."""

    opposite: Optional[Angle] = None
    _l: tuple[Optional[Length], Optional[Length]] = (None, None)
    _val: RatioValue
    value: Fraction

    def new_val(self) -> RatioValue:
        return RatioValue()

    def set_lengths(self, l1: Length, l2: Length) -> None:
        self._l = l1, l2

    @property
    def lengths(self) -> tuple[Length, Length]:
        l1, l2 = self._l
        if l1 is None or l2 is None:
            return l1, l2
        return l1.rep(), l2.rep()


class Direction(Symbol):
    _obj: Line


class Length(Symbol):
    _obj: Segment
    value: float


class LengthValue(Symbol):
    _obj: Length


class AngleValue(Symbol):
    _obj: Angle


class RatioValue(Symbol):
    _obj: Ratio


def all_angles(
    d1: Direction, d2: Direction
) -> Generator[Angle, list[Direction], list[Direction]]:
    d1s = d1.equivs_upto()
    d2s = d2.equivs_upto()

    for angle in d1.rep().neighbors(Angle):
        d1_, d2_ = angle._d
        if d1_ in d1s and d2_ in d2s:
            yield angle, d1s, d2s


def all_ratios(
    d1: Direction, d2: Direction
) -> Generator[Ratio, list[Direction], list[Direction]]:
    d1s = d1.equivs_upto()
    d2s = d2.equivs_upto()

    for ratio in d1.rep().neighbors(Ratio):
        d1_, d2_ = ratio._l
        if d1_ in d1s and d2_ in d2s:
            yield ratio, d1s, d2s


def all_lengths(segment: Segment) -> Generator[Angle, list[Direction], list[Direction]]:
    equivalent_segments = segment.equivs_upto()
    for neighbor_lenght in segment.rep().neighbors(Length):
        if neighbor_lenght._obj in equivalent_segments:
            yield neighbor_lenght, equivalent_segments


RANKING = {
    Point: 0,
    Line: 1,
    Segment: 2,
    Circle: 3,
    Direction: 4,
    Length: 5,
    Angle: 6,
    Ratio: 7,
    AngleValue: 8,
    RatioValue: 9,
    LengthValue: 10,
}
