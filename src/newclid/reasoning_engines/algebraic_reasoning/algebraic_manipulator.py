from __future__ import annotations
from decimal import Decimal
from enum import Enum
from math import exp
from typing import TYPE_CHECKING


from newclid.dependencies.dependency import Dependency, Reason
from newclid.reasoning_engines.engines_interface import Derivation, ReasoningEngine
from newclid.predicates import Predicate
from newclid.dependencies.dependency_building import DependencyBody
from newclid.geometry import is_equiv


from newclid.statements.statement import Statement, ratio_to_num_den, angle_to_num_den

from newclid.reasoning_engines.algebraic_reasoning.geometric_tables import (
    AngleTable,
    DistanceTable,
    RatioTable,
    get_quotient,
    report,
)

if TYPE_CHECKING:
    from newclid.symbols_graph import SymbolsGraph

config = dict()


class AlgebraicRules(Enum):
    Distance_Chase = "a00"
    Ratio_Chase = "a01"
    Angle_Chase = "a02"


class AlgebraicManipulator(ReasoningEngine):
    def __init__(self, symbols_graph: "SymbolsGraph") -> None:
        self.symbols_graph = symbols_graph

        self.atable = AngleTable("pi", self.symbols_graph.get_or_create_const_ang(1, 1))
        self.dtable = DistanceTable()
        self.rtable = RatioTable("1", self.symbols_graph.get_or_create_const_rat(1, 1))
        self.verbose = config.get("verbose", "")

        self.PREDICATE_TO_ADDER = {
            Predicate.PARALLEL: self._add_para,
            Predicate.PERPENDICULAR: self._add_perp,
            Predicate.CONGRUENT: self._add_cong,
            Predicate.EQANGLE: self._add_eqangle,
            Predicate.EQRATIO: self._add_eqratio,
            Predicate.CONSTANT_ANGLE: self._add_aconst,
            Predicate.S_ANGLE: self._add_aconst,
            Predicate.CONSTANT_RATIO: self._add_rconst,
            Predicate.CONSTANT_LENGTH: self._add_lconst,
        }

        self.derive_buffer = []

    def ingest(self, dependency: "Dependency") -> None:
        """Add new algebraic predicates."""
        adder = self.PREDICATE_TO_ADDER.get(dependency.statement.predicate)
        if adder is not None:
            adder(dependency)

    def resolve(self, **kwargs) -> list[Derivation]:
        """Derive new algebraic predicates."""
        self.derive_angle_algebra()
        self.derive_cong_algebra()
        self.derive_ratio_algebra()

        if "a" in self.verbose:
            report(self.atable.v2e)
        if "d" in self.verbose:
            report(self.dtable.v2e)
        if "r" in self.verbose:
            report(self.rtable.v2e)

        res = self.derive_buffer
        self.derive_buffer = []
        return res

    def derive_ratio_algebra(self):
        """Derive new eqratio predicates."""

        for *x, why in self.rtable.get_all_eqs_and_why():
            dep_body = DependencyBody(
                reason=Reason(AlgebraicRules.Ratio_Chase), why=why
            )

            if len(x) == 2:
                mn, pq = x
                if is_equiv(mn, pq):
                    continue

                (m, n), (p, q) = mn._obj.points, pq._obj.points
                cong = Statement(Predicate.CONGRUENT, (m, n, p, q))
                self.derive_buffer.append(Derivation(cong, dep_body))
            elif len(x) == 3:
                mn, pq, v = x
                (m, n) = mn._obj.points
                if pq == self.symbols_graph.get_or_create_const_rat(1, 1):
                    num, denum = get_quotient(exp(v + 1))
                    self.derive_buffer.append(
                        Derivation(
                            Statement(
                                Predicate.CONSTANT_LENGTH,
                                (
                                    m,
                                    n,
                                    self.symbols_graph.get_or_create_const_length(
                                        Decimal(num / denum)
                                    ),
                                ),
                            ),
                            dep_body,
                        )
                    )
                    continue
                num, denum = get_quotient(exp(v))
                ratio, *_ = self.symbols_graph.get_or_create_const_rat(num, denum)
                (p, q) = pq._obj.points
                ratio1, *_ = self.symbols_graph.get_or_create_ratio_from_lengths(
                    mn, pq, None
                )
                if is_equiv(ratio, ratio1):
                    continue
                self.derive_buffer.append(
                    Derivation(
                        Statement(Predicate.CONSTANT_RATIO, (m, n, p, q, ratio)),
                        dep_body,
                    )
                )
            elif len(x) == 4:
                ab, cd, mn, pq = x
                points = (
                    *ab._obj.points,
                    *cd._obj.points,
                    *mn._obj.points,
                    *pq._obj.points,
                )
                eqratio = Statement(Predicate.EQRATIO, points)
                self.derive_buffer.append(Derivation(eqratio, dep_body))

        return self.derive_buffer

    def derive_angle_algebra(self):
        """Derive new eqangles predicates."""

        for x in self.atable.get_all_eqs_and_why():
            x, why = x[:-1], x[-1]
            dep = DependencyBody(reason=Reason(AlgebraicRules.Angle_Chase), why=why)

            if len(x) == 2:
                ab, cd = x
                if is_equiv(ab, cd):
                    continue

                points = (*ab._obj.points, *cd._obj.points)
                para = Statement(Predicate.PARALLEL, points)
                self.derive_buffer.append(Derivation(para, dep))

            if len(x) == 3:
                ef, pq, v = x
                (n, d) = get_quotient(v)
                points = (*ef._obj.points, *pq._obj.points)
                angle, _ = self.symbols_graph.get_or_create_const_ang(n, d)
                aconst = Statement(Predicate.CONSTANT_ANGLE, (*points, angle))
                self.derive_buffer.append(Derivation(aconst, dep))

            if len(x) == 4:
                ab, cd, mn, pq = x
                points = (
                    *ab._obj.points,
                    *cd._obj.points,
                    *mn._obj.points,
                    *pq._obj.points,
                )
                eqangle = Statement(Predicate.EQANGLE, points)
                self.derive_buffer.append(Derivation(eqangle, dep))

        return self.derive_buffer

    def derive_cong_algebra(self):
        """Derive new cong predicates."""

    def _add_para(self, dep: "Dependency"):
        a, b, c, d = dep.statement.args
        ab, _ = self.symbols_graph.get_line_thru_pair_why(a, b)
        cd, _ = self.symbols_graph.get_line_thru_pair_why(c, d)
        self.atable.add_para(ab._val, cd._val, dep)

    def _add_perp(self, dep: "Dependency"):
        a, b, c, d = dep.statement.args
        ab = self.symbols_graph.get_line_thru_pair(a, b)
        cd = self.symbols_graph.get_line_thru_pair(c, d)
        self.atable.add_const_angle(ab.val, cd.val, 0.5, dep)

    def _add_eqangle(self, dep: "Dependency"):
        a, b, c, d, m, n, p, q = dep.statement.args
        ab, _ = self.symbols_graph.get_line_thru_pair_why(a, b)
        cd, _ = self.symbols_graph.get_line_thru_pair_why(c, d)
        mn, _ = self.symbols_graph.get_line_thru_pair_why(m, n)
        pq, _ = self.symbols_graph.get_line_thru_pair_why(p, q)
        ab_cd, _, _ = self.symbols_graph.get_or_create_angle_from_lines(
            ab, cd, dep=None
        )
        mn_pq, _, _ = self.symbols_graph.get_or_create_angle_from_lines(
            mn, pq, dep=None
        )
        ab, cd = ab_cd._d
        mn, pq = mn_pq._d
        self.atable.add_eqangle(ab, cd, mn, pq, dep)

    def _add_eqratio(self, dep: "Dependency"):
        a, b, c, d, m, n, p, q = dep.statement.args
        ab = self.symbols_graph.get_node_val(
            self.symbols_graph.get_or_create_segment(a, b, dep=None), dep=None
        )
        cd = self.symbols_graph.get_node_val(
            self.symbols_graph.get_or_create_segment(c, d, dep=None), dep=None
        )
        pq = self.symbols_graph.get_node_val(
            self.symbols_graph.get_or_create_segment(p, q, dep=None), dep=None
        )
        mn = self.symbols_graph.get_node_val(
            self.symbols_graph.get_or_create_segment(m, n, dep=None), dep=None
        )
        if (ab, cd) == (pq, mn):
            self.rtable.add_eq(ab, cd, dep)
        else:
            self.rtable.add_eqratio(ab, cd, mn, pq, dep)

    def _add_aconst(
        self, dep: "Dependency"
    ):  # not sure, in addr, add ab_cd as well as cd_ab
        a, b, c, d, ang = dep.statement.args
        ab, _ = self.symbols_graph.get_line_thru_pair_why(a, b)
        cd, _ = self.symbols_graph.get_line_thru_pair_why(c, d)
        ab_cd, _, _ = self.symbols_graph.get_or_create_angle_from_lines(
            ab, cd, dep=None
        )
        ab, cd = ab_cd._d
        num, den = angle_to_num_den(ang)
        self.atable.add_const_angle(ab, cd, num / den, dep)

    def _add_rconst(
        self, dep: "Dependency"
    ):  # not sure, in addr, add ab_cd as well as cd_ab
        a, b, c, d, ratio = dep.statement.args
        num, den = ratio_to_num_den(ratio)
        ab = self.symbols_graph.get_or_create_segment(a, b, dep=None)
        cd = self.symbols_graph.get_or_create_segment(c, d, dep=None)
        self.rtable.add_const_ratio(
            self.symbols_graph.get_node_val(ab, dep=None),
            self.symbols_graph.get_node_val(cd, dep=None),
            num,
            den,
            dep,
        )

    def _add_lconst(self, dep: "Dependency"):
        a, b, length = dep.statement.args
        length_num = Decimal(length.name)
        ab = self.symbols_graph.get_or_create_segment(a, b, dep=None)
        self.rtable.add_const_length(ab.val, length_num, dep)

    def _add_cong(self, dep: "Dependency"):
        a, b, c, d = dep.statement.args
        ab, _ = self.symbols_graph.get_line_thru_pair_why(a, b)
        cd, _ = self.symbols_graph.get_line_thru_pair_why(c, d)
        self.dtable.add_cong(ab, cd, a, b, c, d, dep)

        ab = self.symbols_graph.get_or_create_segment(a, b, dep=None)
        cd = self.symbols_graph.get_or_create_segment(c, d, dep=None)
        self.rtable.add_eq(ab.val, cd.val, dep)
