from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Any, Optional

from newclid.predicates.constant_length import ConstantLength
from newclid.dependencies.dependency import Dependency
from newclid.dependencies.symbols import Point
from newclid.numerical import close_enough
from newclid.predicates.perpendicularity import Perp
from newclid.predicates.predicate import Predicate
from newclid.tools import InfQuotientError, get_quotient

if TYPE_CHECKING:
    from newclid.dependencies.dependency_graph import DependencyGraph
    from newclid.statement import Statement

LOGGER = logging.getLogger(__name__)

PythagorasVerification = "Pythagoras Verification"


class PythagoreanPremises(Predicate):
    """PythagoreanPremises a b c
    abc is in the form of a right angled triangle. ab is perpendicular to ac
    """

    NAME = "PythagoreanPremises"

    @classmethod
    def preparse(cls, args: tuple[str, ...]) -> Optional[tuple[str, ...]]:
        a, b, c = args
        if a == b or a == c:
            return None
        b, c = sorted((b, c))
        return (a, b, c)

    @classmethod
    def parse(
        cls, args: tuple[str, ...], dep_graph: DependencyGraph
    ) -> Optional[tuple[Any, ...]]:
        preparse = cls.preparse(args)
        return (
            tuple(dep_graph.symbols_graph.names2points(preparse)) if preparse else None
        )

    @classmethod
    def check_numerical(cls, statement: Statement) -> bool:
        args: tuple[Point, ...] = statement.args
        a, b, c = args
        return close_enough(abs((a.num - b.num).dot(a.num - c.num)), 0)

    @classmethod
    def check(cls, statement: Statement) -> bool:
        return statement.why() is not None

    @classmethod
    def pretty(cls, statement: Statement) -> str:
        args: tuple[Point, ...] = statement.args
        a, b, c = args
        return f"Pythagorean Theorem's premises on {a.pretty_name}, {b.pretty_name}, {c.pretty_name} are satisfied"

    @classmethod
    def why(cls, statement: Statement) -> Optional[Dependency]:
        args: tuple[Point, ...] = statement.args
        a, b, c = args
        perp = statement.with_new(Perp, (a, b, a, c))
        perp_check = perp.check()
        try:
            ab = statement.with_new(
                ConstantLength, (a, b, get_quotient(a.num.distance(b.num)))
            )
            ac = statement.with_new(
                ConstantLength, (a, c, get_quotient(a.num.distance(c.num)))
            )
            bc = statement.with_new(
                ConstantLength, (b, c, get_quotient(b.num.distance(c.num)))
            )
        except InfQuotientError:
            return None
        check_ab = ab.check()
        check_ac = ac.check()
        check_bc = bc.check()
        if check_ab and check_ac and check_bc:
            return Dependency.mk(statement, PythagorasVerification, (ab, ac, bc))
        if perp_check and check_ac and check_bc:
            return Dependency.mk(
                statement,
                PythagorasVerification,
                (perp, ac, bc),
            )
        if perp_check and check_ab and check_bc:
            return Dependency.mk(statement, PythagorasVerification, (ab, perp, bc))
        if perp_check and check_ab and check_ac:
            return Dependency.mk(statement, PythagorasVerification, (ab, ac, perp))
        return None


class PythagoreanConclusions(Predicate):
    NAME = "PythagoreanConclusions"

    @classmethod
    def preparse(cls, args: tuple[str, ...]) -> Optional[tuple[str, ...]]:
        return PythagoreanPremises.preparse(args)

    @classmethod
    def parse(
        cls, args: tuple[str, ...], dep_graph: DependencyGraph
    ) -> Optional[tuple[Any, ...]]:
        return PythagoreanPremises.parse(args, dep_graph)

    @classmethod
    def check_numerical(cls, statement: Statement) -> bool:
        return PythagoreanPremises.check_numerical(statement)

    @classmethod
    def add(cls, dep: Dependency):
        statement = dep.statement
        args: tuple[Point, ...] = statement.args
        a, b, c = args
        perp = statement.with_new(Perp, (a, b, a, c))
        perp_check = perp.check()
        if not perp_check:
            dep.with_new(perp).add()
        try:
            ab = statement.with_new(
                ConstantLength, (a, b, get_quotient(a.num.distance(b.num)))
            )
            ac = statement.with_new(
                ConstantLength, (a, c, get_quotient(a.num.distance(c.num)))
            )
            bc = statement.with_new(
                ConstantLength, (b, c, get_quotient(b.num.distance(c.num)))
            )
        except InfQuotientError:
            LOGGER.warning(
                "lconst result could be added, but the irrational number len cannot be represented."
            )
            return
        check_ab = ab.check()
        check_ac = ac.check()
        check_bc = bc.check()
        if not check_ab:
            dep.with_new(ab).add()
        if not check_ac:
            dep.with_new(ac).add()
        if not check_bc:
            dep.with_new(bc).add()
