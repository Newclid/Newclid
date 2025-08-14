from newclid.deductors.deductor_interface import Deductor
from newclid.justifications.justification import (
    DirectConsequence,
    Justification,
    NumericalCheck,
)
from newclid.predicates import Predicate
from newclid.predicates._index import PredicateType
from newclid.predicates.congruence import Cong
from newclid.predicates.constant_angle import ACompute, aconst_from_acompute
from newclid.predicates.constant_length import LCompute, lconst_from_lcompute
from newclid.predicates.constant_ratio import RCompute, rconst_from_rcompute
from newclid.symbols.symbols_registry import SymbolsRegistry


def justify_predicate(
    predicate: Predicate,
    deductors: list[Deductor],
    symbols: SymbolsRegistry,
) -> Justification | None:
    match predicate.predicate_type:
        # From symbols
        case PredicateType.COLLINEAR:
            return symbols.lines.why_colllinear(predicate)
        case PredicateType.CYCLIC:
            return symbols.circles.why_cyclic(predicate)

        # By definition
        case PredicateType.CIRCUMCENTER:
            o = predicate.center
            p0 = predicate.points[0]
            why = tuple(
                Cong(segment1=(o, p0), segment2=(o, pi)) for pi in predicate.points[1:]
            )
            return DirectConsequence(predicate=predicate, premises=why)

        case (
            PredicateType.A_COMPUTE | PredicateType.L_COMPUTE | PredicateType.R_COMPUTE
        ):
            constant_predicate = _constant_predicate_from_compute(predicate)
            constant_predicate_justification = justify_predicate(
                constant_predicate, deductors=deductors, symbols=symbols
            )
            if constant_predicate_justification is None:
                # We cannot compute the constant predicate
                return None
            return DirectConsequence(
                predicate=predicate, premises=(constant_predicate,)
            )

        # Numerical check
        case (
            PredicateType.DIFFERENT
            | PredicateType.N_COLLINEAR
            | PredicateType.N_PERPENDICULAR
            | PredicateType.N_PARALLEL
            | PredicateType.SAME_SIDE
            | PredicateType.N_SAME_SIDE
            | PredicateType.SAME_CLOCK
            | PredicateType.OBTUSE_ANGLE
        ):
            return NumericalCheck(predicate=predicate)

        case _:
            return None


def _constant_predicate_from_compute(
    predicate: ACompute | LCompute | RCompute,
) -> Predicate:
    match predicate.predicate_type:
        case PredicateType.A_COMPUTE:
            return aconst_from_acompute(predicate)
        case PredicateType.L_COMPUTE:
            return lconst_from_lcompute(predicate)
        case PredicateType.R_COMPUTE:
            return rconst_from_rcompute(predicate)
