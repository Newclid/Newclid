from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal

from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.predicates.constant_length import ConstantLength
from newclid.predicates.perpendicularity import Perp
from newclid.symbols.points_registry import Point
from newclid.tools import InfQuotientError, get_quotient

if TYPE_CHECKING:
    from newclid.predicates import Predicate
    from newclid.proof_state import ProofState


LOGGER = logging.getLogger(__name__)


class PythagoreanPremises(PredicateInterface):
    """PythagoreanPremises a b c
    abc is in the form of a right angled triangle. ab is perpendicular to ac
    """

    predicate_type: Literal[PredicateType.PYTHAGOREAN_PREMISES] = (
        PredicateType.PYTHAGOREAN_PREMISES
    )
    A: Point
    B: Point
    C: Point

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        a, b, c = args
        if a == b or a == c:
            return None
        b, c = sorted((b, c))
        return (a, b, c)

    def check_numerical(self) -> bool:
        return close_enough(
            abs((self.A.num - self.B.num).dot(self.A.num - self.C.num)), 0
        )

    def check(self, proof_state: ProofState) -> bool | None:
        return self.why(proof_state) is not None

    def why(self, proof_state: ProofState) -> tuple[str, tuple[Predicate, ...]] | None:
        a, b, c = self.A, self.B, self.C
        perp = Perp(line1=(a, b), line2=(a, c))
        perp_check = proof_state.check(perp)
        try:
            ab = ConstantLength(
                segment=(a, b), length=get_quotient(a.num.distance(b.num))
            )
            ac = ConstantLength(
                segment=(a, c), length=get_quotient(a.num.distance(c.num))
            )
            bc = ConstantLength(
                segment=(b, c), length=get_quotient(b.num.distance(c.num))
            )
        except InfQuotientError:
            return None

        check_ab = proof_state.check(ab)
        check_ac = proof_state.check(ac)
        check_bc = proof_state.check(bc)

        justification: tuple[ConstantLength | Perp, ...] | None = None
        if check_ab and check_ac and check_bc:
            justification = (ab, ac, bc)
        if perp_check and check_ac and check_bc:
            justification = (perp, ac, bc)
        if perp_check and check_ab and check_bc:
            justification = (ab, perp, bc)
        if perp_check and check_ab and check_ac:
            justification = (ab, ac, perp)
        if justification is None:
            return None
        return ("Pythagorean verification", justification)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in (self.A, self.B, self.C))

    def __str__(self) -> str:
        return f"Pythagorean Theorem's premises on {self.A}, {self.B}, {self.C} are satisfied"


class PythagoreanConclusions(PredicateInterface):
    predicate_type: Literal[PredicateType.PYTHAGOREAN_CONCLUSIONS] = (
        PredicateType.PYTHAGOREAN_CONCLUSIONS
    )
    A: Point
    B: Point
    C: Point

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        return PythagoreanPremises.preparse(args)

    def check_numerical(self) -> bool:
        return PythagoreanPremises(A=self.A, B=self.B, C=self.C).check_numerical()

    def add(self, proof_state: ProofState) -> tuple[PredicateInterface, ...]:
        a, b, c = self.A, self.B, self.C
        perp = Perp(line1=(a, b), line2=(a, c))
        perp_check = proof_state.check(perp)
        consequences: list[PredicateInterface] = []
        if not perp_check:
            consequences.append(perp)
        try:
            ab = ConstantLength(
                segment=(a, b), length=get_quotient(a.num.distance(b.num))
            )
            ac = ConstantLength(
                segment=(a, c), length=get_quotient(a.num.distance(c.num))
            )
            bc = ConstantLength(
                segment=(b, c), length=get_quotient(b.num.distance(c.num))
            )
        except InfQuotientError:
            LOGGER.info(
                "lconst result could be added, but the irrational number len cannot be represented."
            )
            return ()

        check_ab = proof_state.check(ab)
        check_ac = proof_state.check(ac)
        check_bc = proof_state.check(bc)

        if not check_ab:
            consequences.append(ab)
        if not check_ac:
            consequences.append(ac)
        if not check_bc:
            consequences.append(bc)
        return tuple(consequences)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(PredicateArgument(p.name) for p in (self.A, self.B, self.C))

    def __str__(self) -> str:
        return f"Pythagorean Theorem's conclusion on {self.A}, {self.B}, {self.C} is satisfied"
