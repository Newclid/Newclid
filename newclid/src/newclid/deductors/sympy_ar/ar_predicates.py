from __future__ import annotations

import itertools
import logging
from fractions import Fraction
from typing import Iterator, TypeVar, cast

import numpy as np
import sympy as sp  # type: ignore

from newclid.deductors.sympy_ar.table_angles import AnglesTable
from newclid.deductors.sympy_ar.table_ratios import RatiosTable
from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.problem import PredicateConstruction
from newclid.symbols.lines_registry import LineSymbol
from newclid.symbols.points_registry import Segment
from newclid.symbols.symbols_registry import SymbolsRegistry
from newclid.tools import fraction_to_angle, fraction_to_ratio, get_quotient

TableType = TypeVar("TableType", bound=AnglesTable | RatiosTable)

LOGGER = logging.getLogger(__name__)


def coll_expressions(lines: list[LineSymbol], table: AnglesTable) -> list[sp.Expr]:
    expressions: list[sp.Expr] = []
    for line in lines:
        expression = cast(
            sp.Expr,
            table.line_symbol(line) - table.line_symbol(line),  # type: ignore
        )
        expressions.append(expression)
    return expressions


def parallel_expressions(
    l1: LineSymbol,
    l2: LineSymbol,
    table: AnglesTable,
) -> list[sp.Expr]:
    v1 = table.line_symbol(l1)
    v2 = table.line_symbol(l2)
    expression = cast(sp.Expr, v1 - v2)  # type: ignore
    return [expression]


def enumerate_parallels(
    table: AnglesTable, symbols: SymbolsRegistry
) -> Iterator[tuple[PredicateConstruction, sp.Expr]]:
    for v1, v2 in table.expected_parallels.copy():
        para_expression: sp.Expr = cast(sp.Expr, v2 - v1)  # pyright: ignore
        if not table.inner_table.expr_delta(para_expression):
            continue

        l1 = table.sympy_to_newclid_symbol[v1]
        l2 = table.sympy_to_newclid_symbol[v2]

        l1_points = symbols.lines.get_all_points_on_line_and_equivalent_lines(l1)
        l2_points = symbols.lines.get_all_points_on_line_and_equivalent_lines(l2)

        for pt_0, pt_1 in itertools.combinations(l1_points, 2):
            for pt_2, pt_3 in itertools.combinations(l2_points, 2):
                args = tuple(
                    PredicateArgument(pt.name) for pt in (pt_0, pt_1, pt_2, pt_3)
                )
                para_construction = PredicateConstruction.from_predicate_type_and_args(
                    PredicateType.PARALLEL, args
                )
                yield para_construction, para_expression


def perpendicular_expressions(
    l1: LineSymbol,
    l2: LineSymbol,
    table: AnglesTable,
) -> list[sp.Expr]:
    v1 = table.line_symbol(l1)
    v2 = table.line_symbol(l2)
    expression = cast(sp.Expr, v1 - v2)  # type: ignore
    return [expression]


def enumerate_perpendiculars(
    table: AnglesTable, symbols: SymbolsRegistry
) -> Iterator[tuple[PredicateConstruction, sp.Expr]]:
    for v1, v2 in table.expected_perpendiculars.copy():
        perp_expression: sp.Expr = cast(sp.Expr, v2 - v1)  # pyright: ignore
        if not table.inner_table.expr_delta(perp_expression):
            continue

        l1 = table.sympy_to_newclid_symbol[v1]
        l2 = table.sympy_to_newclid_symbol[v2]

        l1_points = symbols.lines.get_all_points_on_line_and_equivalent_lines(l1)
        l2_points = symbols.lines.get_all_points_on_line_and_equivalent_lines(l2)

        # This has to match the order that is in Perp.constant_expressions.
        for pt_0, pt_1 in itertools.combinations(l1_points, 2):
            for pt_2, pt_3 in itertools.combinations(l2_points, 2):
                args = tuple(
                    PredicateArgument(pt.name) for pt in (pt_0, pt_1, pt_2, pt_3)
                )
                perp_construction = PredicateConstruction.from_predicate_type_and_args(
                    PredicateType.PERPENDICULAR, args
                )
                yield perp_construction, perp_expression


def aconst_expression(
    l1: LineSymbol,
    l2: LineSymbol,
    angle: Fraction,
    table: AnglesTable,
) -> list[sp.Expr]:
    v1 = table.line_symbol(l1)
    v2 = table.line_symbol(l2)
    va = sp.Rational(angle.numerator, angle.denominator)
    expression = cast(sp.Expr, v2 - v1 - va)  # type: ignore
    return [expression]


def enumerate_aconsts(
    table: AnglesTable, symbols: SymbolsRegistry
) -> Iterator[tuple[PredicateConstruction, sp.Expr]]:
    for (l1, l2), expected_aconst_value in table.expected_aconsts.copy().items():
        expression = cast(sp.Expr, l1 - l2)  # pyright: ignore
        subbed_in = table.inner_table.substitute_in_existing_expressions(expression)
        if not len(subbed_in.free_symbols) == 0:
            continue

        aconst_value = (-subbed_in) % 1  # pyright: ignore
        n, d = sp.fraction(aconst_value)  # pyright: ignore

        aconst_rad_value = float(np.pi * subbed_in % np.pi)  # pyright: ignore
        if not close_enough(aconst_rad_value, expected_aconst_value):
            LOGGER.debug(
                f"Angle {aconst_value} ({aconst_rad_value}) is the expected numerical value {expected_aconst_value} in between lines {(l1, l2)}"
            )

        if n == 0:
            continue

        l1_newclid = symbols.lines.representent(table.sympy_to_newclid_symbol[l1])
        l2_newclid = symbols.lines.representent(table.sympy_to_newclid_symbol[l2])

        for p1, p2 in itertools.combinations(l1_newclid.points, 2):
            for p3, p4 in itertools.combinations(l2_newclid.points, 2):
                p1, p2 = sorted((p1, p2), key=lambda x: x.name)
                p3, p4 = sorted((p3, p4), key=lambda x: x.name)
                fraction = PredicateArgument(
                    fraction_to_angle(Fraction(int(n), int(d)))
                )
                points = tuple(PredicateArgument(pt.name) for pt in (p1, p2, p3, p4))
                yield (
                    PredicateConstruction.from_predicate_type_and_args(
                        PredicateType.CONSTANT_ANGLE,
                        args=tuple(points) + (fraction,),
                    ),
                    expression,
                )


def eqangle_expressions(
    l1: LineSymbol,
    l2: LineSymbol,
    l3: LineSymbol,
    l4: LineSymbol,
    table: AnglesTable,
) -> list[sp.Expr]:
    v1 = table.line_symbol(l1)
    v2 = table.line_symbol(l2)
    v3 = table.line_symbol(l3)
    v4 = table.line_symbol(l4)
    expression = cast(sp.Expr, v1 - v2 - v3 + v4)  # type: ignore
    return [expression]


def enumerate_eqangles(
    table: AnglesTable, symbols: SymbolsRegistry
) -> Iterator[tuple[PredicateConstruction, sp.Expr]]:
    for v1, v2, v3, v4 in table.expected_eqangles.copy():
        eqangle_expression: sp.Expr = cast(sp.Expr, v1 - v2 - v3 + v4)  # pyright: ignore
        if not table.inner_table.expr_delta(eqangle_expression):
            continue

        l1 = table.sympy_to_newclid_symbol[v1]
        l1_points = symbols.lines.get_all_points_on_line_and_equivalent_lines(l1)

        l2 = table.sympy_to_newclid_symbol[v2]
        l2_points = symbols.lines.get_all_points_on_line_and_equivalent_lines(l2)

        l3 = table.sympy_to_newclid_symbol[v3]
        l3_points = symbols.lines.get_all_points_on_line_and_equivalent_lines(l3)

        l4 = table.sympy_to_newclid_symbol[v4]
        l4_points = symbols.lines.get_all_points_on_line_and_equivalent_lines(l4)

        for pt_2, pt_3 in itertools.combinations(l1_points, 2):
            for pt_0, pt_1 in itertools.combinations(l2_points, 2):
                for pt_6, pt_7 in itertools.combinations(l3_points, 2):
                    for pt_4, pt_5 in itertools.combinations(l4_points, 2):
                        points = tuple(
                            PredicateArgument(pt.name)
                            for pt in (pt_0, pt_1, pt_2, pt_3, pt_4, pt_5, pt_6, pt_7)
                        )
                        eqangle_construction = (
                            PredicateConstruction.from_predicate_type_and_args(
                                PredicateType.EQUAL_ANGLES, points
                            )
                        )
                        yield eqangle_construction, eqangle_expression


def cong_expressions(
    segment1: Segment,
    segment2: Segment,
    table: RatiosTable,
) -> list[sp.Expr]:
    a, b = segment1
    v1 = table.segment_log_length((a, b))

    c, d = segment2
    v2 = table.segment_log_length((c, d))

    expression = cast(sp.Expr, v1 - v2)  # type: ignore
    return [expression]


def enumerate_congs(
    table: RatiosTable,
) -> Iterator[tuple[PredicateConstruction, sp.Expr]]:
    for l1, l2 in table.expected_congs.copy():
        cong_expression = cast(sp.Expr, l1 - l2)  # pyright: ignore
        if not table.inner_table.expr_delta(cong_expression):
            continue

        p0, p1 = table.sympy_symbol_to_str_symbol[l1]
        p2, p3 = table.sympy_symbol_to_str_symbol[l2]

        args = tuple(PredicateArgument(pt.name) for pt in (p0, p1, p2, p3))
        congs_construction = PredicateConstruction.from_predicate_type_and_args(
            PredicateType.CONGRUENT, args
        )
        yield congs_construction, cong_expression


def eqratio_expressions(
    ratio1: tuple[Segment, Segment],
    ratio2: tuple[Segment, Segment],
    table: RatiosTable,
) -> list[sp.Expr]:
    (a, b), (c, d) = ratio1
    (e, f), (g, h) = ratio2
    v1 = table.segment_log_length((a, b))
    v2 = table.segment_log_length((c, d))
    v3 = table.segment_log_length((e, f))
    v4 = table.segment_log_length((g, h))
    expression = cast(sp.Expr, v1 - v2 - v3 + v4)  # type: ignore
    return [expression]


def enumerate_eqratios(
    table: RatiosTable,
) -> Iterator[tuple[PredicateConstruction, sp.Expr]]:
    for l1, l2, l3, l4 in table.expected_eqratios.copy():
        eqratio_expression = cast(sp.Expr, l1 - l2 - l3 + l4)  # pyright: ignore
        if not table.inner_table.expr_delta(eqratio_expression):
            continue

        p0, p1 = table.sympy_symbol_to_str_symbol[l1]
        p2, p3 = table.sympy_symbol_to_str_symbol[l2]
        p4, p5 = table.sympy_symbol_to_str_symbol[l3]
        p6, p7 = table.sympy_symbol_to_str_symbol[l4]

        args = tuple(
            PredicateArgument(pt.name) for pt in (p0, p1, p2, p3, p4, p5, p6, p7)
        )
        eqratio_construction = PredicateConstruction.from_predicate_type_and_args(
            PredicateType.EQUAL_RATIOS, args
        )
        yield eqratio_construction, eqratio_expression


def constant_ratio_expressions(
    ratio: tuple[Segment, Segment],
    value: Fraction,
    table: RatiosTable,
) -> list[sp.Expr]:
    (a, b), (c, d) = ratio
    v1 = table.segment_log_length((a, b))
    v2 = table.segment_log_length((c, d))
    vr = sp.log(value.numerator) - sp.log(value.denominator)  # type: ignore

    expression = cast(sp.Expr, v1 - v2 - vr)  # type: ignore
    return [expression]


def enumerate_rconsts(
    table: RatiosTable,
) -> Iterator[tuple[PredicateConstruction, sp.Expr]]:
    for (seg_1, seg_2), expected_ratio in table.expected_rconsts.copy().items():
        rconst_expression = cast(sp.Expr, seg_1 - seg_2)  # pyright: ignore
        subbed_in = table.inner_table.substitute_in_existing_expressions(
            rconst_expression
        )
        if not len(subbed_in.free_symbols) == 0:
            continue

        ratio: sp.Expr = sp.exp(subbed_in)  # pyright: ignore
        if not close_enough(float(ratio), expected_ratio):
            LOGGER.error(
                f"Ratio {ratio} is not equal to expected ratio {expected_ratio}"
            )

        n, d = sp.fraction(ratio)  # pyright: ignore

        p0, p1 = table.sympy_symbol_to_str_symbol[seg_1]
        p2, p3 = table.sympy_symbol_to_str_symbol[seg_2]
        fraction = PredicateArgument(fraction_to_ratio(Fraction(int(n), int(d))))
        points = tuple(PredicateArgument(pt.name) for pt in (p0, p1, p2, p3))
        rconst_construction = PredicateConstruction.from_predicate_type_and_args(
            PredicateType.CONSTANT_RATIO, points + (fraction,)
        )
        yield rconst_construction, rconst_expression


def constant_length_expression(
    segment: Segment,
    length: Fraction,
    table: RatiosTable,
) -> list[sp.Expr]:
    p0, p1 = segment
    line_var = table.segment_log_length((p0, p1))
    log_length = sp.log(length)
    expression = cast(sp.Expr, line_var - log_length)  # type: ignore
    return [expression]


def enumerate_lconsts(
    table: RatiosTable,
) -> Iterator[tuple[PredicateConstruction, sp.Expr]]:
    for segment, expected_length_value in table.expected_lconsts.copy():  # pyright: ignore
        lconst_expression = cast(sp.Expr, segment)  # pyright: ignore
        subbed_in = table.inner_table.substitute_in_existing_expressions(
            lconst_expression
        )
        if not len(subbed_in.free_symbols) == 0:
            continue

        length: sp.Expr = sp.exp(subbed_in)  # pyright: ignore
        if not close_enough(float(length), expected_length_value):  # pyright: ignore
            LOGGER.error(
                f"Length {length} is not equal to expected length {expected_length_value}"
            )

        p0, p1 = table.sympy_symbol_to_str_symbol[segment]
        points = tuple(PredicateArgument(pt.name) for pt in (p0, p1))

        length_arg = PredicateArgument(fraction_to_ratio(get_quotient(length)))
        lconst_construction = PredicateConstruction.from_predicate_type_and_args(
            PredicateType.CONSTANT_LENGTH, points + (length_arg,)
        )
        yield lconst_construction, lconst_expression
