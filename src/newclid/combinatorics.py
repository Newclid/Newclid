"""Utilizations for graph representation.

Mainly for listing combinations and permutations of elements.
"""

from typing import Generator, List, Tuple, TypeVar
from newclid.geometry import Point
from itertools import tee
from types import GeneratorType


Tee = tee([], 1)[0].__class__


def memoized(f):
    cache = {}

    def ret(*args):
        if args not in cache:
            cache[args] = f(*args)
        if isinstance(cache[args], (GeneratorType, Tee)):
            # the original can't be used any more,
            # so we need to change the cache as well
            cache[args], r = tee(cache[args])
            return r
        return cache[args]

    return ret


Element = TypeVar("Element")


@memoized
def _cross_product(elems1: List[Element], elems2: List[Element]):
    for e1 in elems1:
        for e2 in elems2:
            yield e1, e2


def cross_product(
    elems1: List[Element], elems2: List[Element]
) -> List[Tuple[Element, Element]]:
    return list(_cross_product(tuple(elems1), tuple(elems2)))


@memoized
def _arrangement_pairs(elems):
    if len(elems) < 2:
        return
    for i, e1 in enumerate(elems[:-1]):
        for e2 in elems[i + 1 :]:
            yield e1, e2


def arrangement_pairs(elems: List[Element]) -> List[Tuple[Element, Element]]:
    return list(_arrangement_pairs(tuple(elems)))


@memoized
def _arrangement_triplets(elems):
    if len(elems) < 3:
        return
    for i, e1 in enumerate(elems[:-2]):
        for j, e2 in enumerate(elems[i + 1 : -1]):
            for e3 in elems[i + j + 2 :]:
                yield e1, e2, e3


def arrangement_triplets(
    elems: List[Element],
) -> List[Tuple[Element, Element, Element]]:
    return list(_arrangement_triplets(tuple(elems)))


@memoized
def _arrangement_quadruplets(elems):
    if len(elems) < 4:
        return
    for i, e1 in enumerate(elems[:-3]):
        for j, e2 in enumerate(elems[i + 1 : -2]):
            for e3, e4 in _arrangement_pairs(elems[i + j + 2 :]):
                yield e1, e2, e3, e4


def arrangement_quadruplets(
    elems: List[Element],
) -> List[Tuple[Element, Element, Element, Element]]:
    return list(_arrangement_quadruplets(tuple(elems)))


@memoized
def _permutation_pairs(elems):
    for e1, e2 in arrangement_pairs(elems):
        yield e1, e2
        yield e2, e1


def permutations_pairs(elems):
    return list(_permutation_pairs(tuple(elems)))


@memoized
def _all_4points(l1, l2):
    p1s = l1.neighbors(Point)
    p2s = l2.neighbors(Point)
    for a, b in permutations_pairs(p1s):
        for c, d in permutations_pairs(p2s):
            yield a, b, c, d


def all_4points(l1, l2):
    return list(_all_4points(l1, l2))


@memoized
def _all_8points(l1, l2, l3, l4):
    for a, b, c, d in all_4points(l1, l2):
        for e, f, g, h in all_4points(l3, l4):
            yield (a, b, c, d, e, f, g, h)


def all_8points(l1, l2, l3, l4):
    return list(_all_8points(l1, l2, l3, l4))


@memoized
def _perm3(elems):
    for x in elems:
        for y in elems:
            if y == x:
                continue
            for z in elems:
                if z not in (x, y):
                    yield x, y, z


def permutations_triplets(elems):
    return list(_perm3(tuple(elems)))


@memoized
def _perm4(elems):
    for x in elems:
        for y in elems:
            if y == x:
                continue
            for z in elems:
                if z in (x, y):
                    continue
                for t in elems:
                    if t not in (x, y, z):
                        yield x, y, z, t


def permutations_quadruplets(elems):
    return list(_perm4(tuple(elems)))


def enum_sides(points: list[Point]) -> Generator[list[Point], None, None]:
    a, b, c, x, y, z = points
    yield [a, b, x, y]
    yield [b, c, y, z]
    yield [c, a, z, x]


def enum_triangle(points: list[Point]) -> Generator[list[Point], None, None]:
    a, b, c, x, y, z = points
    yield [a, b, a, c, x, y, x, z]
    yield [b, a, b, c, y, x, y, z]
    yield [c, a, c, b, z, x, z, y]


def enum_triangle_reflect(points: list[Point]) -> Generator[list[Point], None, None]:
    a, b, c, x, y, z = points
    yield [a, b, a, c, x, z, x, y]
    yield [b, a, b, c, y, z, y, x]
    yield [c, a, c, b, z, y, z, x]
