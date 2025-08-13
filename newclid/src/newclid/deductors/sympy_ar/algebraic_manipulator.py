# mypy: disable-error-code="type-arg, misc"
# MyPy does a false positive on the generics here
# maybe it can be fixed but it's not a priority

from __future__ import annotations

import logging
from fractions import Fraction
from typing import Callable, Iterator, cast

from sympy import Expr  # type: ignore

from newclid.deductors import ARReason
from newclid.deductors.deductor_interface import (
    ARCoefficient,
    ARDeduction,
    ARPremise,
    Deductor,
)
from newclid.deductors.sympy_ar.ar_predicates import (
    aconst_expression,
    coll_expressions,
    cong_expressions,
    constant_length_expression,
    constant_ratio_expressions,
    enumerate_aconsts,
    enumerate_congs,
    enumerate_eqangles,
    enumerate_eqratios,
    enumerate_lconsts,
    enumerate_parallels,
    enumerate_perpendiculars,
    enumerate_rconsts,
    eqangle_expressions,
    eqratio_expressions,
    parallel_expressions,
    perpendicular_expressions,
)
from newclid.deductors.sympy_ar.ar_table import ARTable
from newclid.deductors.sympy_ar.table_angles import AnglesTable
from newclid.deductors.sympy_ar.table_ratios import RatiosTable
from newclid.justifications.justification import Justification
from newclid.predicates import Predicate, predicate_from_construction
from newclid.predicates._index import PredicateType
from newclid.problem import PredicateConstruction
from newclid.symbols.lines_registry import LineSymbol
from newclid.symbols.symbols_registry import SymbolsRegistry

LOGGER = logging.getLogger(__name__)


AngleEnumerator = Callable[
    [AnglesTable, SymbolsRegistry], Iterator[tuple[PredicateConstruction, Expr]]
]

RatioEnumerator = Callable[[RatiosTable], Iterator[tuple[PredicateConstruction, Expr]]]


class SympyARDeductor(Deductor):
    def __init__(self) -> None:
        self.atable = AnglesTable(ARTable())
        self.rtable = RatiosTable(ARTable())

        self.angle_enumerators: list[AngleEnumerator] = [
            enumerate_aconsts,
            enumerate_perpendiculars,
            enumerate_parallels,
            enumerate_eqangles,
        ]
        self.ratio_enumerators: list[RatioEnumerator] = [
            enumerate_lconsts,
            enumerate_congs,
            enumerate_rconsts,
            enumerate_eqratios,
        ]

        self._n_numericaly_false_deps_produced_by_ar = 0

    def deduce(self, symbols_registry: SymbolsRegistry) -> Iterator[Justification]:
        for angle_enumerator in self.angle_enumerators:
            for construction, _expression in angle_enumerator(
                self.atable, symbols_registry
            ):
                predicate = predicate_from_construction(
                    construction, symbols_registry.points
                )
                if predicate is None:
                    raise ValueError(f"AR built predicate {construction} is not valid")
                yield ARDeduction(predicate=predicate, ar_reason=ARReason.ANGLE_CHASING)

        for ratio_enumerator in self.ratio_enumerators:
            for construction, _expression in ratio_enumerator(self.rtable):
                predicate = predicate_from_construction(
                    construction, symbols_registry.points
                )
                if predicate is None:
                    raise ValueError(f"AR built predicate {construction} is not valid")
                yield ARDeduction(predicate=predicate, ar_reason=ARReason.RATIO_CHASING)

    def add_dependency(
        self, dependency: Justification, symbols_registry: SymbolsRegistry
    ) -> None:
        predicate = dependency.predicate
        table = self._table_for_predicate(predicate)
        if table is None:
            return
        expressions = predicate_to_expressions(predicate, symbols_registry, table)
        for expression in expressions:
            table.inner_table.add_expr(expression, predicate)

    def check_predicate(
        self, predicate: Predicate, symbols_registry: SymbolsRegistry
    ) -> bool:
        table = self._table_for_predicate(predicate)
        if table is None:
            return False
        expressions = predicate_to_expressions(predicate, symbols_registry, table)
        return all(table.inner_table.expr_delta(eq) for eq in expressions)

    def justify_predicate(
        self, predicate: Predicate, symbols_registry: SymbolsRegistry
    ) -> Justification:
        whys: list[Predicate] = []
        table = self._table_for_predicate(predicate)
        if table is None:
            raise ValueError(f"Cannot justify predicate {predicate} through AR")

        reason = reason_for_table(table)
        expressions = predicate_to_expressions(predicate, symbols_registry, table)
        for expression in expressions:
            whys.extend(table.inner_table.why_expr(expression))
        return ARDeduction(
            predicate=predicate,
            ar_reason=reason,
            ar_premises=tuple(
                ARPremise(
                    predicate=why,
                    coefficient=ARCoefficient(lhs_terms={}, coeff=Fraction(1)),
                )
                for why in whys
            ),
        )

    def _table_for_predicate(
        self, predicate: Predicate
    ) -> AnglesTable | RatiosTable | None:
        match predicate.predicate_type:
            # ANGLES
            case PredicateType.COLLINEAR:
                return self.atable
            case PredicateType.EQUAL_ANGLES:
                return self.atable
            case PredicateType.CONSTANT_ANGLE:
                return self.atable
            case PredicateType.PARALLEL:
                return self.atable
            case PredicateType.PERPENDICULAR:
                return self.atable
            # RATIOS
            case PredicateType.CONSTANT_LENGTH:
                return self.rtable
            case PredicateType.CONSTANT_RATIO:
                return self.rtable
            case PredicateType.CONGRUENT:
                return self.rtable
            case PredicateType.EQUAL_RATIOS:
                return self.rtable
            case _:
                return None


def reason_for_table(table: AnglesTable | RatiosTable) -> ARReason:
    if isinstance(table, AnglesTable):
        return ARReason.ANGLE_CHASING
    return ARReason.RATIO_CHASING


def predicate_to_expressions(
    predicate: Predicate,
    symbols_registry: SymbolsRegistry,
    table: AnglesTable | RatiosTable,
) -> list[Expr]:
    if isinstance(table, AnglesTable):
        return predicate_to_angle_expressions(predicate, symbols_registry, table)
    return predicate_to_ratio_expressions(predicate, table)


def predicate_to_angle_expressions(
    predicate: Predicate, symbols_registry: SymbolsRegistry, table: AnglesTable
) -> list[Expr]:
    match predicate.predicate_type:
        case PredicateType.COLLINEAR:
            lines = [
                cast(LineSymbol, symbol)
                for symbol in predicate.symbols(symbols_registry)
            ]
            return coll_expressions(lines, table=table)
        case PredicateType.EQUAL_ANGLES:
            l1, l2, l3, l4 = [
                cast(LineSymbol, symbol)
                for symbol in predicate.symbols(symbols_registry)
            ]
            return eqangle_expressions(l1, l2, l3, l4, table=table)
        case PredicateType.CONSTANT_ANGLE:
            l1, l2 = [
                cast(LineSymbol, symbol)
                for symbol in predicate.symbols(symbols_registry)
            ]
            return aconst_expression(l1, l2, predicate.angle, table=table)
        case PredicateType.PARALLEL:
            l1, l2 = [
                cast(LineSymbol, symbol)
                for symbol in predicate.symbols(symbols_registry)
            ]
            return parallel_expressions(l1, l2, table=table)
        case PredicateType.PERPENDICULAR:
            l1, l2 = [
                cast(LineSymbol, symbol)
                for symbol in predicate.symbols(symbols_registry)
            ]
            return perpendicular_expressions(l1, l2, table=table)
        case _:
            return []


def predicate_to_ratio_expressions(
    predicate: Predicate, table: RatiosTable
) -> list[Expr]:
    match predicate.predicate_type:
        case PredicateType.CONSTANT_LENGTH:
            return constant_length_expression(
                predicate.segment,
                predicate.length,
                table=table,
            )
        case PredicateType.CONSTANT_RATIO:
            return constant_ratio_expressions(
                predicate.ratio,
                predicate.value,
                table=table,
            )
        case PredicateType.CONGRUENT:
            return cong_expressions(
                predicate.segment1,
                predicate.segment2,
                table=table,
            )
        case PredicateType.EQUAL_RATIOS:
            return eqratio_expressions(
                predicate.ratio1,
                predicate.ratio2,
                table=table,
            )
        case _:
            return []
