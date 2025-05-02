"""Implementing Algebraic Reasoning (AR)."""

from fractions import Fraction
import logging
from typing import TYPE_CHECKING, Any, Literal
import numpy as np
import scipy.optimize as opt  # type: ignore

if TYPE_CHECKING:
    from newclid.dependencies.dependency import Dependency
    from newclid.dependencies.symbols import Point

LOGGER = logging.getLogger(__name__)

ATOM: float = 1e-9
NLOGATOM: int = 9


Angle_Chase = "Angle Chasing"
Ratio_Chase = "Ratio Chasing"


SumCV = dict[str, Fraction]
EqDict = dict[str, SumCV]


def strip(e: SumCV) -> SumCV:
    return {v: c for v, c in e.items() if c != Fraction(0)}


def plus(e1: SumCV, e2: SumCV) -> SumCV:
    e = dict(e1)
    for v, c in e2.items():
        if v in e:
            e[v] += c
        else:
            e[v] = c
    return strip(e)


def plus_all(*es: SumCV) -> SumCV:
    result = {}
    for e in es:
        result = plus(result, e)
    return result


def mult(e: SumCV, m: Fraction) -> SumCV:
    return strip({v: m * c for v, c in e.items()})


def minus(e1: SumCV, e2: SumCV) -> SumCV:
    return plus(e1, mult(e2, Fraction(-1)))


def recon(e: SumCV) -> tuple[str, SumCV]:
    """Reconcile one variable in the expression e=0, given const."""
    e = strip(e)
    v0 = None
    for v in e:
        v0 = v
        break
    assert v0, "e should not be empty"

    c0 = e.pop(v0)
    return v0, {v: -c / c0 for v, c in e.items()}


def replace(e: SumCV, v0: str, e0: SumCV) -> SumCV:
    if v0 not in e:
        return e
    e = dict(e)
    m = e.pop(v0)
    return plus(e, mult(e0, m))


def _fix_width(s: Any, width: int, align: Literal["right", "left", "center"] = "right"):
    if align != "right":
        raise NotImplementedError
    s = str(s)
    return " " * (width - len(s)) + s


def report(eqdict: EqDict):
    table_str = ">>>>>>>>>table begins\n"
    maxlv = 0
    maxlcoef = 0
    setv_right: set[str] = set()
    setv_left: set[str] = set()
    for leftv, eq in eqdict.items():
        setv_left.add(leftv)
        maxlv = max(maxlv, len(str(leftv)))
        for rightv, coef in eq.items():
            setv_right.add(rightv)
            maxlv = max(maxlv, len(str(rightv)))
            maxlcoef = max(maxlcoef, len(str(coef)))
    listv_left = sorted(setv_left)
    listv_right = sorted(setv_right)
    for leftv in listv_left:
        table_str += f"{_fix_width(leftv, maxlv)} = "
        for rightv in listv_right:
            try:
                coef = eqdict[leftv][rightv]
                table_str += f"{_fix_width(str(coef), maxlcoef)} * {str(rightv)}"
                if rightv != listv_right[-1]:
                    table_str += " + "
            except KeyError:
                table_str += f"{_fix_width('', len(str(rightv))+maxlcoef+3)}"
                if rightv != listv_right[-1]:
                    table_str += "   "
        table_str += "\n"
    table_str += "table ends<<<<<<<<<<<\n"
    LOGGER.debug(table_str)


class Table:
    """The coefficient matrix."""

    def __init__(self, verbose: bool = False):
        self.v2e: EqDict = {}  # the table {var: {vark : coefk}} var = sum coefk*vark
        self.verbose = verbose

        # for why (linprog)
        self._c = np.zeros((0))
        self._v2i: dict[str, int] = {}  # v -> index of row in A.
        self.deps: list[Dependency] = []  # equal number of columns.
        self._mA = np.zeros((0, 0))

    def add_free(self, v: str) -> None:
        self.v2e[v] = {v: Fraction(1)}

    def replace(self, v0: str, e0: SumCV) -> None:
        for v, e in list(self.v2e.items()):
            self.v2e[v] = replace(e, v0, e0)

    def sumcv_from_list(self, vc: list[tuple[str, Fraction]]) -> SumCV:
        return strip(plus_all(*[{v: c} for v, c in vc]))

    def expr_delta(self, vc: SumCV) -> bool:
        """
        There is only constant delta between vc and the system
        """
        vc = strip(vc)
        if len(vc) == 0:
            return True
        result = {}

        for v, c in vc.items():
            if v in self.v2e:
                result = plus(result, mult(self.v2e[v], c))
            else:
                return False

        return len(result) == 0

    def add_expr(self, vc: SumCV, dep: "Dependency") -> bool:
        """
        Add a new equality (sum cv = 0), represented by the list of tuples vc=[(v, c), ..].
        Return True iff the equality can already be deduced by the internal system
        """
        vc = strip(vc)
        if len(vc) == 0:
            return False
        result = {}
        new_vars: list[tuple[str, Fraction]] = []

        for v, c in vc.items():
            if v in self.v2e:
                result = plus(result, mult(self.v2e[v], c))
            else:
                new_vars.append((v, c))

        result = strip(result)

        if len(new_vars) == 0:
            if len(result) == 0:
                return False
            v, e = recon(result)
            self.replace(v, e)

        else:
            dependent_v: tuple[str, Fraction] = new_vars[0]
            for v, m in new_vars[1:]:
                self.add_free(v)
                result = plus(result, {v: m})

            v, m = dependent_v
            self.v2e[v] = mult(result, Fraction(-1) / m)

        self._register(vc, dep)
        if self.verbose:
            LOGGER.debug(f"By {dep.pretty()} the table updates:")
            report(self.v2e)
        return True

    def _register(self, vc: SumCV, dep: "Dependency") -> None:
        """Register a new equality vc=[(v, c), ..] with traceback dependency dep."""
        vc = strip(vc)
        if len(vc) == 0:
            return

        for v in vc:
            if v not in self._v2i:
                self._v2i[v] = len(self._v2i)

        (m, n), length = self._mA.shape, len(self._v2i)
        if length > m:
            self._mA = np.concatenate([self._mA, np.zeros([length - m, n])], 0)

        new_column = np.zeros((len(self._v2i), 2))  # N, 2
        for v, c in vc.items():
            new_column[self._v2i[v], 0] += c
            new_column[self._v2i[v], 1] -= c

        self._mA = np.concatenate((self._mA, new_column), 1)
        self._c = np.concatenate((self._c, np.array([1.0, -1.0])))
        self.deps += [dep]

    def why(self, vc: SumCV) -> list["Dependency"]:
        """AR traceback == MILP."""
        # why expr == 0?
        # Solve min(c^Tx) s.t. A_eq * x = b_eq, x >= 0
        vc = strip(vc)
        if len(vc) == 0:
            return []

        b_eq = np.array([0] * len(self._v2i))
        for v, c in vc.items():
            b_eq[self._v2i[v]] += c

        try:
            x = opt.linprog(c=self._c, A_eq=self._mA, b_eq=b_eq, method="highs")["x"]  # type: ignore
        except ValueError:
            x = opt.linprog(c=self._c, A_eq=self._mA, b_eq=b_eq)["x"]  # type: ignore

        deps: list[Dependency] = []
        for i, dep in enumerate(self.deps):
            if x[2 * i] > ATOM or x[2 * i + 1] > ATOM:
                if dep not in deps:
                    deps.append(dep)
        return deps

    def get_equal_elements(self, a: str) -> SumCV:
        """
        a = constant
        """
        return self.sumcv_from_list([(a, Fraction(1))])

    def get_equal_elements_up_to(self, a: str, b: str) -> SumCV:
        """
        a = b + constant
        """
        return self.sumcv_from_list([(a, Fraction(1)), (b, Fraction(-1))])

    def get_equal_difference_up_to(self, a: str, b: str, c: str, d: str) -> SumCV:
        """
        a - b = c - d + constant
        """
        return self.sumcv_from_list(
            [(a, Fraction(1)), (b, Fraction(-1)), (c, Fraction(-1)), (d, Fraction(1))]
        )

    @classmethod
    def get_length(cls, p0: "Point", p1: "Point") -> str:
        if p0.name > p1.name:
            p0, p1 = p1, p0
        length = f"l({p0.name},{p1.name})"
        return length
