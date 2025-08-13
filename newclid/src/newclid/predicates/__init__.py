"""Define predicates used in Newclid."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, TypeAlias

from pydantic import Field

from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.predicates.circumcenter import Circumcenter
from newclid.predicates.collinearity import Coll, NColl
from newclid.predicates.congruence import Cong
from newclid.predicates.constant_angle import ACompute, ConstantAngle
from newclid.predicates.constant_length import ConstantLength, LCompute
from newclid.predicates.constant_ratio import ConstantRatio, RCompute
from newclid.predicates.cyclic import Cyclic
from newclid.predicates.different import Diff
from newclid.predicates.equal_angles import EqAngle
from newclid.predicates.equal_ratios import EqRatio
from newclid.predicates.equation_angle import AngleEquation
from newclid.predicates.equation_length import LengthEquation
from newclid.predicates.midpoint import MidPoint
from newclid.predicates.obtuse_angle import ObtuseAngle
from newclid.predicates.parallelism import NPara, Para
from newclid.predicates.perpendicularity import NPerp, Perp
from newclid.predicates.pythagoras import PythagoreanConclusions, PythagoreanPremises
from newclid.predicates.sameclock import SameClock
from newclid.predicates.sameside import NSameSide, SameSide
from newclid.predicates.squared_constant_length import SquaredConstantLength
from newclid.predicates.squared_constant_ratio import SquaredConstantRatio
from newclid.predicates.triangles_congruent import ContriClock, ContriReflect
from newclid.predicates.triangles_similar import SimtriClock, SimtriReflect
from newclid.tools import str_to_fraction

if TYPE_CHECKING:
    from newclid.problem import PredicateConstruction
    from newclid.symbols.points_registry import PointsRegisty

SYMBOLIC_PREDICATES = {
    PredicateType.ANGLE_EQUATION: AngleEquation,
    PredicateType.COLLINEAR: Coll,
    PredicateType.CONGRUENT: Cong,
    PredicateType.LENGTH_EQUATION: LengthEquation,
    PredicateType.MIDPOINT: MidPoint,
    PredicateType.PARALLEL: Para,
    PredicateType.PERPENDICULAR: Perp,
    PredicateType.CYCLIC: Cyclic,
    PredicateType.CIRCUMCENTER: Circumcenter,
    PredicateType.EQUAL_ANGLES: EqAngle,
    PredicateType.EQUAL_RATIOS: EqRatio,
    PredicateType.CONSTANT_LENGTH: ConstantLength,
    PredicateType.CONSTANT_RATIO: ConstantRatio,
    PredicateType.CONSTANT_ANGLE: ConstantAngle,
    PredicateType.SQUARED_CONSTANT_LENGTH: SquaredConstantLength,
    PredicateType.SQUARED_CONSTANT_RATIO: SquaredConstantRatio,
    PredicateType.SIMTRI_CLOCK: SimtriClock,
    PredicateType.SIMTRI_REFLECT: SimtriReflect,
    PredicateType.CONTRI_CLOCK: ContriClock,
    PredicateType.CONTRI_REFLECT: ContriReflect,
}

NUMERICAL_PREDICATES = {
    PredicateType.DIFFERENT: Diff,
    PredicateType.N_COLLINEAR: NColl,
    PredicateType.N_PARALLEL: NPara,
    PredicateType.N_PERPENDICULAR: NPerp,
    PredicateType.N_SAME_SIDE: NSameSide,
    PredicateType.OBTUSE_ANGLE: ObtuseAngle,
    PredicateType.SAME_CLOCK: SameClock,
    PredicateType.SAME_SIDE: SameSide,
}

INTEGRATED_PREDICATES = {
    PredicateType.PYTHAGOREAN_PREMISES: PythagoreanPremises,
    PredicateType.PYTHAGOREAN_CONCLUSIONS: PythagoreanConclusions,
}
COMPUTE = {
    PredicateType.A_COMPUTE: ACompute,
    PredicateType.R_COMPUTE: RCompute,
    PredicateType.L_COMPUTE: LCompute,
}

PREDICATES = (
    SYMBOLIC_PREDICATES | NUMERICAL_PREDICATES | INTEGRATED_PREDICATES | COMPUTE
)

NAME_TO_PREDICATE = {
    predicate_type: predicate for predicate_type, predicate in PREDICATES.items()
}


def predicate_class_from_type(
    predicate_type: PredicateType,
) -> type[PredicateInterface]:
    return NAME_TO_PREDICATE[predicate_type]  # type: ignore


Predicate: TypeAlias = Annotated[
    Circumcenter
    | Cong
    | Coll
    | NColl
    | Cyclic
    | ConstantAngle
    | ACompute
    | LCompute
    | ConstantLength
    | ConstantRatio
    | EqAngle
    | Diff
    | RCompute
    | ObtuseAngle
    | MidPoint
    | EqRatio
    | Perp
    | NPerp
    | Para
    | NPara
    | SameClock
    | SameSide
    | NSameSide
    | PythagoreanPremises
    | PythagoreanConclusions
    | SquaredConstantLength
    | SquaredConstantRatio
    | SimtriClock
    | SimtriReflect
    | ContriClock
    | ContriReflect
    | AngleEquation
    | LengthEquation,
    Field(discriminator="predicate_type"),
]


def predicate_from_construction(
    construction: PredicateConstruction, points_registry: PointsRegisty
) -> Predicate | None:
    predicate_class = predicate_class_from_type(construction.predicate_type)
    canonical_args = predicate_class.preparse(construction.args)
    if canonical_args is None:
        return None

    match construction.predicate_type:
        case PredicateType.CIRCUMCENTER:
            center, *points_around = points_registry.names2points(canonical_args)
            return Circumcenter(center=center, points=tuple(points_around))
        case PredicateType.CONGRUENT:
            a, b, c, d = points_registry.names2points(canonical_args)
            return Cong(segment1=(a, b), segment2=(c, d))
        case PredicateType.COLLINEAR:
            a, b, c = points_registry.names2points(canonical_args)
            return Coll(points=(a, b, c))
        case PredicateType.CYCLIC:
            return Cyclic(points=tuple(points_registry.names2points(canonical_args)))
        case PredicateType.CONSTANT_ANGLE:
            a, b, c, d = points_registry.names2points(canonical_args[:-1])
            y = str_to_fraction(construction.args[-1])
            return ConstantAngle(line1=(a, b), line2=(c, d), angle=y)
        case PredicateType.A_COMPUTE:
            a, b, c, d = points_registry.names2points(canonical_args)
            return ACompute(segment1=(a, b), segment2=(c, d))
        case PredicateType.N_COLLINEAR:
            return NColl(points=tuple(points_registry.names2points(canonical_args)))
        case PredicateType.CONSTANT_LENGTH:
            a, b = points_registry.names2points(canonical_args[:-1])
            length = str_to_fraction(construction.args[-1])
            return ConstantLength(segment=(a, b), length=length)
        case PredicateType.L_COMPUTE:
            a, b = points_registry.names2points(canonical_args)
            return LCompute(segment=(a, b))
        case PredicateType.CONSTANT_RATIO:
            a, b, c, d = points_registry.names2points(canonical_args[:-1])
            ratio = str_to_fraction(construction.args[-1])
            return ConstantRatio(ratio=((a, b), (c, d)), value=ratio)
        case PredicateType.R_COMPUTE:
            a, b, c, d = points_registry.names2points(canonical_args)
            return RCompute(ratio=((a, b), (c, d)))
        case PredicateType.DIFFERENT:
            a, b = points_registry.names2points(canonical_args)
            return Diff(points=(a, b))
        case PredicateType.EQUAL_ANGLES:
            a, b, c, d, e, f, g, h = points_registry.names2points(canonical_args)
            return EqAngle(angle1=((a, b), (c, d)), angle2=((e, f), (g, h)))
        case PredicateType.EQUAL_RATIOS:
            a, b, c, d, e, f, g, h = points_registry.names2points(canonical_args)
            return EqRatio(ratio1=((a, b), (c, d)), ratio2=((e, f), (g, h)))
        case PredicateType.PYTHAGOREAN_PREMISES:
            a, b, c = points_registry.names2points(canonical_args)
            return PythagoreanPremises(A=a, B=b, C=c)
        case PredicateType.PYTHAGOREAN_CONCLUSIONS:
            a, b, c = points_registry.names2points(canonical_args)
            return PythagoreanConclusions(A=a, B=b, C=c)
        case PredicateType.OBTUSE_ANGLE:
            a, b, c = points_registry.names2points(canonical_args)
            return ObtuseAngle(head1=a, corner=b, head2=c)
        case PredicateType.MIDPOINT:
            m, a, b = points_registry.names2points(canonical_args)
            return MidPoint(midpoint=m, segment=(a, b))
        case PredicateType.PERPENDICULAR:
            a, b, c, d = points_registry.names2points(canonical_args)
            return Perp(line1=(a, b), line2=(c, d))
        case PredicateType.N_PERPENDICULAR:
            a, b, c, d = points_registry.names2points(canonical_args)
            return NPerp(line1=(a, b), line2=(c, d))
        case PredicateType.PARALLEL:
            a, b, c, d = points_registry.names2points(canonical_args)
            return Para(line1=(a, b), line2=(c, d))
        case PredicateType.N_PARALLEL:
            a, b, c, d = points_registry.names2points(canonical_args)
            return NPara(line1=(a, b), line2=(c, d))
        case PredicateType.SAME_CLOCK:
            a, b, c, p, q, r = points_registry.names2points(canonical_args)
            return SameClock(triangle1=(a, b, c), triangle2=(p, q, r))
        case PredicateType.SAME_SIDE:
            a, b, c, p, q, r = points_registry.names2points(canonical_args)
            return SameSide(triangle1=(a, b, c), triangle2=(p, q, r))
        case PredicateType.N_SAME_SIDE:
            a, b, c, p, q, r = points_registry.names2points(canonical_args)
            return NSameSide(triangle1=(a, b, c), triangle2=(p, q, r))
        case PredicateType.SIMTRI_CLOCK:
            a, b, c, p, q, r = points_registry.names2points(canonical_args)
            return SimtriClock(triangle1=(a, b, c), triangle2=(p, q, r))
        case PredicateType.SIMTRI_REFLECT:
            a, b, c, p, q, r = points_registry.names2points(canonical_args)
            return SimtriReflect(triangle1=(a, b, c), triangle2=(p, q, r))
        case PredicateType.CONTRI_CLOCK:
            a, b, c, p, q, r = points_registry.names2points(canonical_args)
            return ContriClock(triangle1=(a, b, c), triangle2=(p, q, r))
        case PredicateType.CONTRI_REFLECT:
            a, b, c, p, q, r = points_registry.names2points(canonical_args)
            return ContriReflect(triangle1=(a, b, c), triangle2=(p, q, r))
        case PredicateType.SQUARED_CONSTANT_LENGTH:
            a, b = points_registry.names2points(canonical_args[:-1])
            square_length = str_to_fraction(canonical_args[-1])
            return SquaredConstantLength(segment=(a, b), square_length=square_length)
        case PredicateType.SQUARED_CONSTANT_RATIO:
            a, b, c, d = points_registry.names2points(canonical_args[:-1])
            square_ratio = str_to_fraction(canonical_args[-1])
            return SquaredConstantRatio(
                segment1=(a, b), segment2=(c, d), square_ratio=square_ratio
            )
        case PredicateType.ANGLE_EQUATION:
            raise NotImplementedError("AngleEquationPredicate is not implemented")
        case PredicateType.LENGTH_EQUATION:
            raise NotImplementedError("LengthEquationPredicate is not implemented")
    raise ValueError(f"Unknown predicate type: {construction.name}")
