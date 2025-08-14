"""Implementing Algebraic Reasoning (AR)."""
# pyright: ignore

from __future__ import annotations

import os
from typing import TYPE_CHECKING, TypeAlias, cast

import numpy as np
import scipy.optimize as opt  # type: ignore
from sympy import Eq  # type: ignore
from sympy import solve as sp_solve  # type: ignore
from sympy.core.backend import Symbol as SympySymbol  # type: ignore

if TYPE_CHECKING:
    from sympy import Expr  # type: ignore

    from newclid.predicates import Predicate
else:
    from symengine.lib.symengine_wrapper import Expr  # type: ignore

from newclid.numerical import ATOM

EqDict: TypeAlias = dict[SympySymbol, Expr]

# MARK: gotchas
# Everywhere we use sp.Expr, they represent an expression that's constant


os.environ.setdefault("USE_SYMENGINE", "1")


class ARTable:
    """The coefficient matrix."""

    def __init__(self):
        self.v2e: EqDict = {}  # the table {var: {vark : coefk}} var = sum coefk*vark

        # for why (linprog)
        self._c = np.zeros((0))
        self._v2i: dict[SympySymbol, int] = {}  # v -> index of row in A.
        self.predicates: list[Predicate] = []  # equal number of columns.
        self._mA: np.ndarray[tuple[int, ...], np.dtype[np.float64]] = np.zeros((0, 0))

    def expr_delta(self, vc: Expr) -> bool:
        """
        There is only constant delta between vc and the system
        """
        sub_result = self.substitute_in_existing_expressions(vc)
        is_constant = len(sub_result.free_symbols) == 0
        return is_constant

    def substitute_in_existing_expressions(self, vc: Expr) -> Expr:
        before_simp = vc.xreplace(self.v2e)
        after_simp = cast(Expr, before_simp.expand())
        return after_simp

    def add_expr(self, expression: Expr, predicate: Predicate) -> bool:
        """
        Add a new equality (sum cv = 0), represented by the list of tuples vc=[(v, c), ..].
        Return True iff the equality can already be deduced by the internal system
        """
        simplified_expression = self.substitute_in_existing_expressions(expression)

        if len(simplified_expression.free_symbols) == 0:
            return False

        new_vars: set[SympySymbol] = simplified_expression.free_symbols - set(
            self.v2e.keys()
        )

        if len(new_vars) == 0:
            v, e = _reconcile(simplified_expression)
            if self.v2e[v] != v:
                assert False, (
                    f"{expression=} simplified to {simplified_expression=}, {v=}, {e=}. Previously, {self.v2e[v]=}. "
                    f"This should never happen because we should have already reconciled this variable above."
                )
            self._replace(v, e)

        else:
            # We have at least one new variable.
            assert simplified_expression != 0

            for v in new_vars:
                self._add_free(v)

            # Select one new variable to be dependent.
            dependent_variable = new_vars.pop()
            expr = cast(
                list[Expr], sp_solve(Eq(simplified_expression, 0), dependent_variable)
            )[0]

            self.v2e[dependent_variable] = expr

        self._register(simplified_expression, predicate)
        return True

    def why_expr(self, vc: Expr) -> tuple[Predicate, ...]:
        """AR traceback == MILP."""
        # why expr == 0?
        # Solve min(c^Tx) s.t. A_eq * x = b_eq, x >= 0
        vc = vc.expand()
        if vc == 0:
            no_justification: list[Predicate] = []
            return tuple(no_justification)

        b_eq = np.array([0] * len(self._v2i))
        for v in cast(set[SympySymbol], vc.free_symbols):
            b_eq[self._v2i[v]] += float(vc.coeff(v))

        try:
            x = opt.linprog(c=self._c, A_eq=self._mA, b_eq=b_eq, method="highs")["x"]
        except ValueError:
            x = opt.linprog(c=self._c, A_eq=self._mA, b_eq=b_eq)["x"]

        if x is None:
            ar_lines = "\n".join(f"{k} = {v}" for k, v in self.v2e.items())
            raise ValueError(
                f"Could not fild a traceback through AR for expression {vc} = 0.\nAR table:\n{ar_lines}"
            )

        predicates: list[Predicate] = []
        for i, dep in enumerate(self.predicates):
            if x[2 * i] > ATOM or x[2 * i + 1] > ATOM:
                if dep not in predicates:
                    predicates.append(dep)
        return tuple(predicates)

    def _register(self, vc: Expr, predicate: Predicate) -> None:
        """Register a new equality vc=[(v, c), ..] with traceback dependency dep."""
        vc = cast(Expr, vc.expand())
        if vc == 0:
            return

        for v in cast(set[SympySymbol], vc.free_symbols):
            if v not in self._v2i:
                self._v2i[v] = len(self._v2i)

        (m, n), length = self._mA.shape, len(self._v2i)
        if length > m:
            self._mA = np.concatenate([self._mA, np.zeros([length - m, n])], 0)

        new_column = np.zeros((len(self._v2i), 2))  # N, 2
        for v, c in _vars_and_coeffs(vc).items():
            new_column[self._v2i[v], 0] += c
            new_column[self._v2i[v], 1] -= c

        self._mA = np.concatenate((self._mA, new_column), 1)
        self._c = np.concatenate((self._c, np.array([1.0, -1.0])))
        self.predicates += [predicate]

    def _add_free(self, v: SympySymbol) -> None:
        self.v2e[v] = v

    def _replace(self, v0: SympySymbol, e0: Expr) -> None:
        for v, e in list(self.v2e.items()):
            self.v2e[v] = e.subs(v0, e0).expand()


def _reconcile(e: Expr) -> tuple[SympySymbol, Expr]:
    """Reconcile one variable in the expression e=0, given const."""
    e = e.expand()
    free_vars = set(cast(set[SympySymbol], e.free_symbols))
    assert len(free_vars) > 0, f"{e=} should have at least two free variables"
    v0 = free_vars.pop()
    return v0, sp_solve(e, v0)[0]


def _vars_and_coeffs(expr: Expr) -> dict[SympySymbol, float]:
    ret: dict[SympySymbol, float] = {}
    for v in expr.free_symbols:
        assert isinstance(v, SympySymbol)
        coeff: SympySymbol = expr.coeff(v)
        assert coeff.is_number
        ret[v] = float(coeff)
    return ret
