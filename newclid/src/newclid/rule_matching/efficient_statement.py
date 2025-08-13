"""
Efficient statement handling for geometric theorem proving.

This module provides data structures and utilities for representing and manipulating
geometric statements in a theorem proving system. It includes:

- Named tuple classes for different types of geometric statements (perpendicular,
  parallel, equal angles, etc.)
- Named tuple classes for corresponding predicates with variable names
- Functions for generating permutations of statements based on geometric symmetries
- Functions for normalizing statements to canonical forms
- Utilities for finding representatives of equivalence classes

The module is designed for efficiency in geometric theorem proving by providing
canonical representations and symmetry handling for geometric statements.
"""

from __future__ import annotations

import itertools
import typing
from typing import Iterator, Literal, TypeAlias, Union

from newclid.predicate_types import PredicateArgument
from newclid.predicates import Predicate
from newclid.predicates._index import PredicateType
from newclid.rule import VarName


def efficient_version(predicate: Predicate) -> EfficientStatement:
    match predicate.predicate_type:
        case PredicateType.EQUAL_ANGLES:
            return EqangleStatement("eqangle", *predicate.to_tokens())
        case PredicateType.PERPENDICULAR:
            return PerpStatement("perp", *predicate.to_tokens())
        case PredicateType.PARALLEL:
            return ParaStatement("para", *predicate.to_tokens())
        case PredicateType.CONGRUENT:
            return CongStatement("cong", *predicate.to_tokens())
        case PredicateType.MIDPOINT:
            return MidptStatement("midp", *predicate.to_tokens())
        case PredicateType.EQUAL_RATIOS:
            return EqratioStatement("eqratio", *predicate.to_tokens())
        case PredicateType.COLLINEAR:
            return CollStatement("coll", *predicate.to_tokens())
        case PredicateType.CIRCUMCENTER:
            return CircleStatement("circle", *predicate.to_tokens())
        case PredicateType.CYCLIC:
            return CyclicStatement("cyclic", *predicate.to_tokens())
        case PredicateType.SIMTRI_CLOCK | PredicateType.SIMTRI_REFLECT:
            return TriangleStatement(
                predicate.predicate_type.value, *predicate.to_tokens()
            )
        case _:
            raise NotImplementedError(f"Unknown predicate: {predicate.predicate_type}")


class PerpStatement(typing.NamedTuple):
    name: Literal["perp"]
    a: PredicateArgument
    b: PredicateArgument
    c: PredicateArgument
    d: PredicateArgument


class PerpPredicate(typing.NamedTuple):
    name: Literal["perp"]
    A: VarName
    B: VarName
    C: VarName
    D: VarName


class ParaStatement(typing.NamedTuple):
    name: Literal["para"]
    a: PredicateArgument
    b: PredicateArgument
    c: PredicateArgument
    d: PredicateArgument


class ParaPredicate(typing.NamedTuple):
    name: Literal["para"]
    A: VarName
    B: VarName
    C: VarName
    D: VarName


class EqangleStatement(typing.NamedTuple):
    name: Literal["eqangle"]
    a: PredicateArgument
    b: PredicateArgument
    c: PredicateArgument
    d: PredicateArgument
    e: PredicateArgument
    f: PredicateArgument
    g: PredicateArgument
    h: PredicateArgument


class EqanglePredicate(typing.NamedTuple):
    name: Literal["eqangle"]
    A: VarName
    B: VarName
    C: VarName
    D: VarName
    E: VarName
    F: VarName
    G: VarName
    H: VarName


class EqratioStatement(typing.NamedTuple):
    name: Literal["eqratio"]
    a: PredicateArgument
    b: PredicateArgument
    c: PredicateArgument
    d: PredicateArgument
    e: PredicateArgument
    f: PredicateArgument
    g: PredicateArgument
    h: PredicateArgument


class EqratioPredicate(typing.NamedTuple):
    name: Literal["eqratio"]
    A: VarName
    B: VarName
    C: VarName
    D: VarName
    E: VarName
    F: VarName
    G: VarName
    H: VarName


class CongStatement(typing.NamedTuple):
    name: Literal["cong"]
    a: PredicateArgument
    b: PredicateArgument
    c: PredicateArgument
    d: PredicateArgument


class CongPredicate(typing.NamedTuple):
    name: Literal["cong"]
    A: VarName
    B: VarName
    C: VarName
    D: VarName


class MidptStatement(typing.NamedTuple):
    name: Literal["midp"]
    a: PredicateArgument
    b: PredicateArgument
    c: PredicateArgument


class MidptPredicate(typing.NamedTuple):
    name: Literal["midp"]
    A: VarName
    B: VarName
    C: VarName


class TriangleStatement(typing.NamedTuple):
    name: Literal["simtri", "simtrir", "contri", "contrir"]
    a: PredicateArgument
    b: PredicateArgument
    c: PredicateArgument
    p: PredicateArgument
    q: PredicateArgument
    r: PredicateArgument


class TrianglePredicate(typing.NamedTuple):
    name: Literal["simtri", "simtrir", "contri", "contrir"]
    A: VarName
    B: VarName
    C: VarName
    P: VarName
    Q: VarName
    R: VarName


class CollStatement(tuple[str, ...]):
    def __new__(cls, predicate_name: str, *points: str):
        return super().__new__(cls, (predicate_name, *points))


class CollPredicate(tuple[str, ...]):
    def __new__(cls, predicate_name: str, *points: str):
        return super().__new__(cls, (predicate_name, *points))


class CircleStatement(tuple[str, ...]):
    def __new__(cls, predicate_name: str, *points: str):
        return super().__new__(cls, (predicate_name, *points))


class CirclePredicate(tuple[str, ...]):
    def __new__(cls, predicate_name: str, *points: str):
        return super().__new__(cls, (predicate_name, *points))


class CyclicStatement(tuple[str, ...]):
    def __new__(cls, predicate_name: str, *points: str):
        return super().__new__(cls, (predicate_name, *points))


class CyclicPredicate(tuple[str, ...]):
    def __new__(cls, predicate_name: str, *points: str):
        return super().__new__(cls, (predicate_name, *points))


EfficientStatement: TypeAlias = Union[
    PerpStatement,
    ParaStatement,
    EqangleStatement,
    EqratioStatement,
    CongStatement,
    MidptStatement,
    CollStatement,
    CircleStatement,
    TriangleStatement,
    CyclicStatement,
]

EfficientPredicateType: TypeAlias = Union[
    PerpPredicate,
    ParaPredicate,
    EqanglePredicate,
    EqratioPredicate,
    CongPredicate,
    MidptPredicate,
    CollPredicate,
    CirclePredicate,
    TrianglePredicate,
    CyclicPredicate,
]


def generate_permutations(stmt: EfficientStatement) -> Iterator[EfficientStatement]:
    match stmt:
        case PerpStatement():
            return perp_perms(stmt)
        case ParaStatement():
            return para_perms(stmt)
        case EqangleStatement():
            return eqangle_perms(stmt)
        case EqratioStatement():
            return eqratio_perms(stmt)
        case CongStatement():
            return cong_perms(stmt)
        case MidptStatement():
            return midpt_perms(stmt)
        case CollStatement():
            return coll_perms(stmt)
        case CircleStatement():
            return circle_perms(stmt)
        case TriangleStatement():
            return triangle_perms(stmt)
        case CyclicStatement():
            return cyclic_perms(stmt)
    raise ValueError(f"Unknown symmetries for statement: {stmt}")


def cyclic_perms(stmt: CyclicStatement) -> Iterator[CyclicStatement]:
    pts = stmt[1:]
    for perm in itertools.permutations(pts):
        yield CyclicStatement("cyclic", *perm)


def coll_perms(stmt: CollStatement) -> Iterator[CollStatement]:
    pts = stmt[1:]
    for perm in itertools.permutations(pts):
        yield CollStatement("coll", *perm)


def circle_perms(stmt: CircleStatement) -> Iterator[CircleStatement]:
    center, pts = stmt[1], stmt[2:]
    for perm in itertools.permutations(pts):
        yield CircleStatement("circle", center, *perm)


def triangle_perms(stmt: TriangleStatement) -> Iterator[TriangleStatement]:
    pts = stmt[1:]
    a, b, c, p, q, r = pts
    for (a1, a2, a3), (p1, p2, p3) in zip(
        itertools.permutations((a, b, c), 3),
        itertools.permutations((p, q, r), 3),
    ):
        yield TriangleStatement("simtri", a1, a2, a3, p1, p2, p3)
        yield TriangleStatement("simtri", p1, p2, p3, a1, a2, a3)


def normalize_triangle(stmt_pts: TriangleStatement) -> TriangleStatement:
    relation, a, b, c, p, q, r = stmt_pts
    (a0, p0), (b0, q0), (c0, r0) = sorted(((a, p), (b, q), (c, r)))
    (a1, p1), (b1, q1), (c1, r1) = sorted(((p, a), (q, b), (r, c)))
    return TriangleStatement(
        relation, *min((a0, b0, c0, p0, q0, r0), (a1, b1, c1, p1, q1, r1))
    )


def normalize_midpt(stmt_pts: MidptStatement) -> MidptStatement:
    _, m, a, b = stmt_pts
    return MidptStatement("midp", m, a, b)


def midpt_perms(stmt_pts: MidptStatement) -> Iterator[MidptStatement]:
    _, m, a, b = stmt_pts
    yield MidptStatement("midp", m, a, b)
    yield MidptStatement("midp", m, b, a)


def normalize_cong(stmt_pts: CongStatement) -> CongStatement:
    _, a, b, c, d = stmt_pts
    a, b = sorted((a, b))
    c, d = sorted((c, d))
    return CongStatement("cong", a, b, c, d)


def cong_perms(
    stmt_pts: CongStatement,
) -> Iterator[CongStatement]:
    _, a, b, c, d = stmt_pts
    for l1, l2 in [((a, b), (c, d)), ((c, d), (a, b))]:
        for l1_perm in itertools.permutations(l1):
            for l2_perm in itertools.permutations(l2):
                yield (
                    CongStatement(
                        "cong",
                        l1_perm[0],
                        l1_perm[1],
                        l2_perm[0],
                        l2_perm[1],
                    )
                )


def normalize_eqratio(stmt_pts: EqratioStatement) -> EqratioStatement:
    _, a, b, c, d, e, f, g, h = stmt_pts
    a, b = sorted((a, b))
    c, d = sorted((c, d))
    e, f = sorted((e, f))
    g, h = sorted((g, h))
    a, b, c, d, e, f, g, h = min(
        [
            (a, b, c, d, e, f, g, h),
            (c, d, a, b, g, h, e, f),
            (e, f, g, h, a, b, c, d),
            (g, h, e, f, c, d, a, b),
        ]
    )

    return EqratioStatement("eqratio", a, b, c, d, e, f, g, h)


def eqratio_perms(
    stmt_pts: EqratioStatement,
) -> Iterator[EqratioStatement]:
    _, a, b, c, d, e, f, g, h = stmt_pts
    for l1, l2, l3, l4 in [
        ((a, b), (c, d), (e, f), (g, h)),
        ((c, d), (a, b), (g, h), (e, f)),
        ((e, f), (g, h), (a, b), (c, d)),
        ((g, h), (e, f), (c, d), (a, b)),
    ]:
        for l1_perm in itertools.permutations(l1):
            for l2_perm in itertools.permutations(l2):
                for l3_perm in itertools.permutations(l3):
                    for l4_perm in itertools.permutations(l4):
                        yield (
                            EqratioStatement(
                                "eqratio",
                                l1_perm[0],
                                l1_perm[1],
                                l2_perm[0],
                                l2_perm[1],
                                l3_perm[0],
                                l3_perm[1],
                                l4_perm[0],
                                l4_perm[1],
                            )
                        )


def normalize_eqangle(
    stmt_pts: EqangleStatement,
) -> EqangleStatement:
    _, a, b, c, d, e, f, g, h = stmt_pts
    a, b = sorted((a, b))
    c, d = sorted((c, d))
    e, f = sorted((e, f))
    g, h = sorted((g, h))
    return EqangleStatement(
        "eqangle",
        *min(
            (a, b, c, d, e, f, g, h),
            (c, d, a, b, g, h, e, f),
            (e, f, g, h, a, b, c, d),
            (g, h, e, f, c, d, a, b),
        ),
    )


def eqangle_perms(
    stmt_pts: EqangleStatement,
) -> Iterator[EqangleStatement]:
    _, a, b, c, d, e, f, g, h = stmt_pts

    for l1, l2, l3, l4 in [
        ((a, b), (c, d), (e, f), (g, h)),
        ((c, d), (a, b), (g, h), (e, f)),
        ((e, f), (g, h), (a, b), (c, d)),
        ((g, h), (e, f), (c, d), (a, b)),
    ]:
        for l1_perm in itertools.permutations(l1):
            for l2_perm in itertools.permutations(l2):
                for l3_perm in itertools.permutations(l3):
                    for l4_perm in itertools.permutations(l4):
                        yield (
                            EqangleStatement(
                                "eqangle",
                                l1_perm[0],
                                l1_perm[1],
                                l2_perm[0],
                                l2_perm[1],
                                l3_perm[0],
                                l3_perm[1],
                                l4_perm[0],
                                l4_perm[1],
                            )
                        )


def normalize_para(stmt_pts: ParaStatement) -> ParaStatement:
    _, a, b, c, d = stmt_pts
    a, b = sorted((a, b))
    c, d = sorted((c, d))
    return ParaStatement("para", a, b, c, d)


def para_perms(
    stmt_pts: ParaStatement,
) -> Iterator[ParaStatement]:
    _, a, b, c, d = stmt_pts
    for l1, l2 in [((a, b), (c, d)), ((c, d), (a, b))]:
        for l1_perm in itertools.permutations(l1):
            for l2_perm in itertools.permutations(l2):
                yield (
                    ParaStatement(
                        "para",
                        l1_perm[0],
                        l1_perm[1],
                        l2_perm[0],
                        l2_perm[1],
                    )
                )


def normalize_perp(stmt_pts: PerpStatement) -> PerpStatement:
    _, a, b, c, d = stmt_pts
    a, b = sorted((a, b))
    c, d = sorted((c, d))
    return PerpStatement("perp", a, b, c, d)


def perp_perms(
    stmt_pts: PerpStatement,
) -> Iterator[PerpStatement]:
    _, a, b, c, d = stmt_pts
    for l1, l2 in [((a, b), (c, d)), ((c, d), (a, b))]:
        for l1_perm in itertools.permutations(l1):
            for l2_perm in itertools.permutations(l2):
                yield (
                    PerpStatement(
                        "perp",
                        l1_perm[0],
                        l1_perm[1],
                        l2_perm[0],
                        l2_perm[1],
                    )
                )


def normalize_coll(stmt_pts: CollStatement) -> CollStatement:
    pts = stmt_pts[1:]
    return CollStatement("coll", *sorted(pts))


def normalize_circle(stmt_pts: CircleStatement) -> CircleStatement:
    center, pts = stmt_pts[1], stmt_pts[2:]
    return CircleStatement("circle", center, *sorted(pts))


def normalize_cyclic(stmt_pts: CyclicStatement) -> CyclicStatement:
    pts = stmt_pts[1:]
    return CyclicStatement("cyclic", *sorted(pts))


def get_representative_of_equivalence_class(
    stmt: EfficientStatement,
) -> EfficientStatement:
    match stmt:
        case EqangleStatement():
            return normalize_eqangle(stmt)
        case EqratioStatement():
            return normalize_eqratio(stmt)
        case CongStatement():
            return normalize_cong(stmt)
        case MidptStatement():
            return normalize_midpt(stmt)
        case PerpStatement():
            return normalize_perp(stmt)
        case ParaStatement():
            return normalize_para(stmt)
        case CollStatement():
            return normalize_coll(stmt)
        case CircleStatement():
            return normalize_circle(stmt)
        case TriangleStatement():
            return normalize_triangle(stmt)
        case CyclicStatement():
            return normalize_cyclic(stmt)
    raise ValueError(f"Unknown statement to normalize: {stmt}")
