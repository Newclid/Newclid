from __future__ import annotations

from typing import Literal

from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.symbols.points_registry import Ratio


class EqRatio(PredicateInterface):
    """eqratio AB CD EF GH -

    Represent that AB/CD=EF/GH, as ratios between lengths of segments.
    """

    predicate_type: Literal[PredicateType.EQUAL_RATIOS] = PredicateType.EQUAL_RATIOS
    ratio1: Ratio
    ratio2: Ratio

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        a, b, c, d, e, f, g, h = args
        a, b = sorted((a, b))
        c, d = sorted((c, d))
        e, f = sorted((e, f))
        g, h = sorted((g, h))
        if min((a, b), (c, d)) > min((e, f), (g, h)):
            a, b, c, d, e, f, g, h = e, f, g, h, a, b, c, d
        if (a, b) > (c, d):
            a, b, c, d, e, f, g, h = c, d, a, b, g, h, e, f
        if (c, d) > (e, f):
            c, d, e, f = e, f, c, d
        return (a, b, c, d, e, f, g, h)

    def check_numerical(self) -> bool:
        (num, den) = (None, None)
        for (a, b), (c, d) in (self.ratio1, self.ratio2):
            (_num, _den) = (a.num.distance2(b.num), c.num.distance2(d.num))
            if num is not None and not close_enough(num * _den, _num * den):  # type: ignore
                return False
            num, den = _num, _den
        return True

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        return tuple(
            PredicateArgument(p.name)
            for (a, b), (c, d) in (self.ratio1, self.ratio2)
            for p in (a, b, c, d)
        )

    def __str__(self) -> str:
        return " = ".join(
            f"{a}{b}:{c}{d}" for (a, b), (c, d) in (self.ratio1, self.ratio2)
        )
