"""Implementing Algebraic Reasoning (AR)."""

from collections import defaultdict
from math import log
from typing import TYPE_CHECKING, Any, Generator, Literal, Optional, TypeVar

from numpy import exp

from newclid.geometry import Direction, Length, Line, Symbol, Point
from newclid.numerical import ATOM, NLOGATOM
from newclid.ratios import simplify
from newclid._lazy_loading import lazy_import

if TYPE_CHECKING:
    from newclid.dependencies.dependency import Dependency

    import numpy
    import scipy.optimize


def cast_return(func):
    """Decorator that casts the return value of a special __method__
    back to the original type of 'self'."""

    def wrapped(self, *args, **kwargs):
        return self.__class__(func(self, *args, **kwargs))

    return wrapped


class Coef(float):
    def __hash__(self):
        return hash(round(self, NLOGATOM))

    def __eq__(self, other: "Coef"):
        return hash(self) == hash(other)

    def __ne__(self, other: "Coef") -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"{self:.2f}"

    __add__ = cast_return(float.__add__)
    __sub__ = cast_return(float.__sub__)
    __mul__ = cast_return(float.__mul__)
    __truediv__ = cast_return(float.__truediv__)
    __neg__ = cast_return(float.__neg__)
    __mod__ = cast_return(float.__mod__)


np: "numpy" = lazy_import("numpy")
opt: "scipy.optimize" = lazy_import("scipy.optimize")
SumCV = dict[str, Coef]
EqDict = dict[str, SumCV]


class InfQuotientError(Exception):
    pass


# maximum denominator for a fraction.
MAX_DENOMINATOR = 1000000

# tolerance for fraction approximation
TOL = 1e-10


def get_quotient(v) -> tuple[int, int]:
    v = float(v)
    n = v
    d = 1
    while abs(n - round(n)) > TOL:
        d += 1
        n += v
        if d > MAX_DENOMINATOR:
            e = InfQuotientError(v)
            raise e

    n = int(round(n))
    return simplify(n, d)


def hashed(e: SumCV) -> tuple[tuple[str, Coef], ...]:
    return tuple(sorted(list(e.items())))


def is_zero(e: SumCV) -> bool:
    return len(strip(e)) == 0


def strip(e: SumCV) -> SumCV:
    return {v: c for v, c in e.items() if c != Coef(0)}


def plus(e1: SumCV, e2: SumCV) -> SumCV:
    e = dict(e1)
    for v, c in e2.items():
        if v in e:
            e[v] += c
        else:
            e[v] = c
    return strip(e)


def plus_all(*es: list[SumCV]) -> SumCV:
    result = {}
    for e in es:
        result = plus(result, e)
    return result


def mult(e: SumCV, m: Coef) -> SumCV:
    return {v: m * c for v, c in e.items()}


def minus(e1: SumCV, e2: SumCV) -> SumCV:
    return plus(e1, mult(e2, Coef(-1)))


def div(e1: SumCV, e2: SumCV) -> Coef:
    """Divide e1 by e2."""
    e1 = strip(e1)
    e2 = strip(e2)
    if set(e1.keys()) != set(e2.keys()):
        return None

    n, d = None, None

    for v, c1 in e1.items():
        c2 = e2[v]  # we want c1/c2 = n/d => c1*d=c2*n
        if n is not None and c1 * d != c2 * n:
            return None
        n, d = c1, c2
    return Coef(n) / Coef(d)


def recon(e: SumCV, const: str) -> Optional[tuple[str, SumCV]]:
    """Reconcile one variable in the expression e=0, given const."""
    e = strip(e)
    if len(e) == 0:
        return None

    v0 = None
    for v in e:
        if v != const:
            v0 = v
            break
    if v0 is None:
        return None

    c0 = e.pop(v0)
    return v0, {v: -c / c0 for v, c in e.items()}


def replace(e: SumCV, v0: str, e0: SumCV) -> SumCV:
    if v0 not in e:
        return e
    e = dict(e)
    m = e.pop(v0)
    return plus(e, mult(e0, m))


T = TypeVar("T")


def comb2(elems: list[T]) -> Generator[tuple[T, T], None, None]:
    if len(elems) < 1:
        return
    for i, e1 in enumerate(elems[:-1]):
        for e2 in elems[i + 1 :]:
            yield e1, e2


def perm2(elems: list[T]) -> Generator[tuple[T, T], None, None]:
    for e1, e2 in comb2(elems):
        yield e1, e2
        yield e2, e1


def chain2(elems: list[T]) -> Generator[tuple[T, T], None, None]:
    if len(elems) < 2:
        return
    for i, e1 in enumerate(elems[:-1]):
        yield e1, elems[i + 1]


def _fix_width(s: Any, width: int, align: Literal["right", "left", "center"] = "right"):
    if align != "right":
        raise NotImplementedError
    s = str(s)
    return " " * (width - len(s)) + s


def coef2str(x: Coef):
    try:
        n, d = get_quotient(x)
        return f"{n}/{d}"
    except InfQuotientError as _:
        n, d = get_quotient(exp(x))
        return f"log{n}/{d}"


def report(eqdict: EqDict):
    print(">>>>>>>>>table begins")
    maxlv = 0
    maxlcoef = 0
    setv_right = set()
    setv_left = set()
    for leftv, eq in eqdict.items():
        setv_left.add(leftv)
        maxlv = max(maxlv, len(str(leftv)))
        for rightv, coef in eq.items():
            setv_right.add(rightv)
            maxlv = max(maxlv, len(str(rightv)))
            maxlcoef = max(maxlcoef, len(coef2str(coef)))
    listv_left = sorted(setv_left)
    listv_right = sorted(setv_right)
    for leftv in listv_left:
        print(end=f"{_fix_width(leftv, maxlv)} = ")
        for rightv in listv_right:
            try:
                coef = eqdict[leftv][rightv]
                if abs(coef) < ATOM:
                    raise ValueError
                print(end=f"{_fix_width(coef2str(coef), maxlcoef)} * {str(rightv)}")
                if rightv != listv_right[-1]:
                    print(end=" + ")
            except (KeyError, ValueError) as _:
                print(end=f"{_fix_width('', len(str(rightv))+maxlcoef+3)}")
                if rightv != listv_right[-1]:
                    print(end="   ")
        print()
    print("table ends<<<<<<<<<<<")


class Table:
    """The coefficient matrix."""

    def __init__(self, const: str = "1"):
        self.const = const
        self.v2e: EqDict = {}  # the table {var: {vark : coefk}} var = sum coefk*vark
        self.add_free(const)

        # to cache what is already derived/inputted
        self.eqs = set()
        self.groups = []  # groups of pairs s.t. v1-v2 are equal.

        # for why (linprog)
        self.c = []
        self.v2i = {}  # v -> index of row in A.
        self.deps = []  # equal number of columns.
        self.A = np.zeros([0, 0])
        self.do_why = True

    def add_free(self, v: str) -> None:
        self.v2e[v] = {v: Coef(1)}

    def replace(self, v0: str, e0: SumCV) -> None:
        for v, e in list(self.v2e.items()):
            self.v2e[v] = replace(e, v0, e0)

    def add_expr(self, vc: list[tuple[str, Coef]]) -> bool:
        """Add a new equality (sum cv = 0), represented by the list of tuples vc=[(v, c), ..]."""
        result = {}
        new_vars: list[tuple[str, Coef]] = []

        for v, c in vc:
            if v in self.v2e:
                result = plus(result, mult(self.v2e[v], c))
            else:
                new_vars += [(v, c)]

        if new_vars == []:
            if is_zero(self.modulo(result)):
                return False
            result_recon = recon(result, self.const)
            if result_recon is None:
                return False
            v, e = result_recon
            self.replace(v, e)

        elif len(new_vars) == 1:
            v, m = new_vars[0]
            self.v2e[v] = mult(result, Coef(-1) / m)

        else:
            dependent_v = None
            for v, m in new_vars:
                if dependent_v is None:
                    dependent_v = (v, m)
                    continue

                self.add_free(v)
                result = plus(result, {v: m})

            v, m = dependent_v
            self.v2e[v] = mult(result, Coef(-1) / m)

        return True

    def register(self, vc: list[tuple[str, Coef]], dep: "Dependency") -> None:
        """Register a new equality vc=[(v, c), ..] with traceback dependency dep."""
        result = plus_all(*[{v: c} for v, c in vc])
        if is_zero(result):
            return

        vs, _ = zip(*vc)
        for v in vs:
            if v not in self.v2i:
                self.v2i[v] = len(self.v2i)

        (m, n), length = self.A.shape, len(self.v2i)
        if length > m:
            self.A = np.concatenate([self.A, np.zeros([length - m, n])], 0)

        new_column = np.zeros([len(self.v2i), 2])  # N, 2
        for v, c in vc:
            new_column[self.v2i[v], 0] += c
            new_column[self.v2i[v], 1] -= c

        self.A = np.concatenate([self.A, new_column], 1)
        self.c += [1.0, -1.0]
        self.deps += [dep]

    def register3(self, a: str, b: str, f: Coef, dep: "Dependency") -> None:
        self.register([(a, Coef(1)), (b, Coef(-1)), (self.const, -f)], dep)

    def register4(self, a: str, b: str, c: str, d: str, dep: "Dependency") -> None:
        self.register([(a, Coef(1)), (b, Coef(-1)), (c, Coef(-1)), (d, Coef(1))], dep)

    def why(self, e: SumCV) -> list[Any]:
        """AR traceback == MILP."""
        if not self.do_why:
            return []
        # why expr == 0?
        # Solve min(c^Tx) s.t. A_eq * x = b_eq, x >= 0
        e = strip(e)
        if not e:
            return []

        b_eq = [0] * len(self.v2i)
        for v, c in e.items():
            b_eq[self.v2i[v]] += c

        try:
            x = opt.linprog(c=self.c, A_eq=self.A, b_eq=b_eq, method="highs")["x"]
        except ValueError:
            x = opt.linprog(c=self.c, A_eq=self.A, b_eq=b_eq)["x"]

        deps = []
        for i, dep in enumerate(self.deps):
            if x[2 * i] > 1e-12 or x[2 * i + 1] > 1e-12:
                if dep not in deps:
                    deps.append(dep)
        return deps

    def record_eq(self, v1: str, v2: str, v3: str, v4: str) -> None:
        self.eqs.add((v1, v2, v3, v4))
        self.eqs.add((v2, v1, v4, v3))
        self.eqs.add((v3, v4, v1, v2))
        self.eqs.add((v4, v3, v2, v1))

    def check_record_eq(self, v1: str, v2: str, v3: str, v4: str) -> bool:
        return (v1, v2, v3, v4) in self.eqs

    def add_eq2(self, a: str, b: str, m, n, dep: "Dependency") -> None:
        """
        a/b = m/n
        """
        coef = -Coef(log(m) - log(n))
        expr = (
            [(a, Coef(1)), (b, Coef(-1)), (self.const, coef)]
            if b != self.one
            else [(a, Coef(1)), (self.const, coef)]
        )
        if not self.add_expr(expr):
            return []
        self.register(expr, dep)

    def add_eq3(self, a: str, b: str, f, dep: "Dependency") -> None:
        """
        a - b = f * constant
        """
        self.eqs.add((a, b, Coef(f)))

        if not self.add_expr([(a, Coef(1)), (b, Coef(-1)), (self.const, -Coef(f))]):
            return []

        self.register3(a, b, Coef(f), dep)

    def add_eq4(self, a: str, b: str, c: str, d: str, dep: "Dependency") -> None:
        """
        a - b = c - d
        """
        self.record_eq(a, b, c, d)
        self.record_eq(a, c, b, d)

        expr = list(minus({a: Coef(1), b: Coef(-1)}, {c: Coef(1), d: Coef(-1)}).items())

        if not self.add_expr(expr):
            return []

        self.register4(a, b, c, d, dep)
        self.groups, _, _ = update_groups(
            self.groups, [{(a, b), (c, d)}, {(b, a), (d, c)}]
        )

    def pairs(self) -> Generator[list[tuple[str, str]], None, None]:
        for v1, v2 in perm2(list(self.v2e.keys())):
            yield v1, v2

    def modulo(self, e: SumCV) -> SumCV:
        return strip(e)

    def get_all_eqs(
        self,
    ) -> dict[tuple[tuple[str, Coef], ...], list[tuple[str, str]]]:
        h2pairs = defaultdict(list)
        for v1, v2 in self.pairs():
            e1, e2 = self.v2e[v1], self.v2e[v2]
            e12 = minus(e1, e2)
            h12 = hashed(self.modulo(e12))
            h2pairs[h12].append((v1, v2))
        return h2pairs

    def get_all_eqs_and_why(
        self, return_quads: bool = True
    ) -> Generator[Any, None, None]:
        """Check all 4/3/2-permutations for new equalities."""
        groups = []

        for h, vv in self.get_all_eqs().items():
            if h == ():
                for v1, v2 in vv:
                    if self.const in {v1, v2}:
                        continue
                    if (v1, v2) in self.eqs:
                        continue
                    self.eqs.add((v1, v2))
                    self.eqs.add((v2, v1))
                    # why v1 - v2 = e12 ?  (note modulo(e12) == 0)
                    why_dict = minus(
                        {v1: Coef(1), v2: Coef(-1)}, minus(self.v2e[v1], self.v2e[v2])
                    )
                    yield v1, v2, self.why(why_dict)
                continue

            if len(h) == 1 and h[0][0] == self.const:
                for v1, v2 in vv:
                    frac = h[0][1]
                    if (v1, v2, frac) in self.eqs:
                        continue
                    self.eqs.add((v1, v2, frac))
                    # why v1 - v2 = e12 ?  (note modulo(e12) == 0)
                    why_dict = minus(
                        {v1: Coef(1), v2: Coef(-1)}, minus(self.v2e[v1], self.v2e[v2])
                    )
                    yield v1, v2, frac, self.why(why_dict)
                continue

            groups.append(vv)

        if not return_quads:
            return

        self.groups, links, _ = update_groups(self.groups, groups)
        for (v1, v2), (v3, v4) in links:
            if self.const in {v1, v2, v3, v4}:
                continue
            if self.check_record_eq(v1, v2, v3, v4):
                continue
            e12 = minus(self.v2e[v1], self.v2e[v2])
            e34 = minus(self.v2e[v3], self.v2e[v4])

            why_dict = minus(  # why (v1-v2)-(v3-v4)=e12-e34?
                minus({v1: Coef(1), v2: Coef(-1)}, {v3: Coef(1), v4: Coef(-1)}),
                minus(e12, e34),
            )
            self.record_eq(v1, v2, v3, v4)
            yield v1, v2, v3, v4, self.why(why_dict)


def update_groups(
    groups1: list[Any], groups2: list[Any]
) -> tuple[list[Any], list[tuple[Any, Any]], list[list[Any]]]:
    """Update groups of equivalent elements.

    Given groups1 = [set1, set2, set3, ..]
    where all elems within each set_i is defined to be "equivalent" to each other.
    (but not across the sets)

    Incoming groups2 = [set1, set2, ...] similar to set1 - it is the
    additional equivalent information on elements in groups1.

    Return the new updated groups1 and the set of links
    that make it that way.

    Example:
      groups1 = [{1, 2}, {3, 4, 5}, {6, 7}]
      groups2 = [{2, 3, 8}, {9, 10, 11}]

    => new groups1 and links:
      groups1 = [{1, 2, 3, 4, 5, 8}, {6, 7}, {9, 10, 11}]
      links = (2, 3), (3, 8), (9, 10), (10, 11)

    Explain: since groups2 says 2 and 3 are equivalent (with {2, 3, 8}),
    then {1, 2} and {3, 4, 5} in groups1 will be merged,
    because 2 and 3 each belong to those 2 groups.
    Additionally 8 also belong to this same group.
    {3, 4, 5} is left alone, while {9, 10, 11} is a completely new set.

    The links to make this all happens is:
    (2, 3): to merge {1, 2} and {3, 4, 5}
    (3, 8): to link 8 into the merged({1, 2, 3, 4, 5})
    (9, 10) and (10, 11): to make the new group {9, 10, 11}

    Args:
      groups1: a list of sets.
      groups2: a list of sets.

    Returns:
      groups1, links, history: result of the update.
    """
    history = []
    links = []
    for g2 in groups2:
        joins = [None] * len(groups1)  # mark which one in groups1 is merged
        merged_g1 = set()  # merge them into this.
        old = None  # any elem in g2 that belong to any set in groups1 (old)
        new = []  # all elem in g2 that is new

        for e in g2:
            found = False
            for i, g1 in enumerate(groups1):
                if e not in g1:
                    continue

                found = True
                if joins[i]:
                    continue

                joins[i] = True
                merged_g1.update(g1)

                if old is not None:
                    links.append((old, e))  # link to make merging happen.
                old = e

            if not found:  # e is new!
                new.append(e)

        # now chain elems in new together.
        if old is not None and new:
            links.append((old, new[0]))
            merged_g1.update(new)

        links += chain2(new)

        new_groups1 = []
        if merged_g1:  # put the merged_g1 in first
            new_groups1.append(merged_g1)

        # put the remaining (unjoined) groups in
        new_groups1 += [g1 for j, g1 in zip(joins, groups1) if not j]

        if old is None and new:
            new_groups1 += [set(new)]

        groups1 = new_groups1
        history.append(groups1)

    return groups1, links, history


class GeometricTable(Table):
    """Abstract class representing the coefficient matrix (table) A."""

    def __init__(self, const: str, const_obj: Symbol):
        super().__init__(const)
        self.v2obj = {const: const_obj}

    def get_name(self, objs: list[Symbol]) -> list[str]:
        self.v2obj.update({o.name: o for o in objs})
        return [o.name for o in objs]

    def map2obj(self, names: list[str]) -> list[Symbol]:
        return [self.v2obj[n] for n in names]

    def get_all_eqs_and_why(self, return_quads: bool) -> Generator[Any, None, None]:
        for out in super().get_all_eqs_and_why(return_quads):
            if len(out) == 3:
                x, y, why = out
                x, y = self.map2obj([x, y])
                yield x, y, why
            if len(out) == 4:
                x, y, f, why = out
                if x == self.const:
                    continue
                x, y = self.map2obj([x, y])
                yield x, y, f, why
            if len(out) == 5:
                a, b, x, y, why = out
                a, b, x, y = self.map2obj([a, b, x, y])
                yield a, b, x, y, why


class RatioTable(GeometricTable):
    """Coefficient matrix A for log(distance)."""

    def __init__(self, const: str, const_obj: Symbol):
        super().__init__(const, const_obj)
        self.one = self.const

    def add_eq(self, l1: Length, l2: Length, dep: "Dependency") -> None:
        l1, l2 = self.get_name([l1, l2])
        return super().add_eq3(l1, l2, Coef(0), dep)

    def add_const_ratio(self, l1: Length, l2: Length, m, n, dep: "Dependency") -> None:
        l1, l2 = self.get_name([l1, l2])
        super().add_eq2(l1, l2, m, n, dep)

    def add_const_length(self, length: Length, val, dep: "Dependency") -> None:
        super().add_eq2(self.get_name([length])[0], self.one, val, 1, dep)

    def add_eqratio(
        self,
        l1: Length,
        l2: Length,
        l3: Length,
        l4: Length,
        dep: "Dependency",
    ) -> None:
        l1, l2, l3, l4 = self.get_name([l1, l2, l3, l4])
        return self.add_eq4(l1, l2, l3, l4, dep)

    def get_all_eqs_and_why(self) -> Generator[Any, None, None]:
        return super().get_all_eqs_and_why(True)


class AngleTable(GeometricTable):
    """Coefficient matrix A for slope(direction)."""

    def __init__(self, const: str, const_obj: Symbol):
        super().__init__(const, const_obj)
        self.pi = self.const

    def modulo(self, e: SumCV) -> SumCV:
        e = strip(e)
        if self.pi in e:
            e[self.pi] = e[self.pi] % Coef(1)  # why mod 1, should mod 2??
        return strip(e)

    def add_para(self, d1: Direction, d2: Direction, dep: "Dependency") -> None:
        return self.add_const_angle(d1, d2, 0, dep)

    def add_const_angle(
        self, d1: Direction, d2: Direction, ang, dep: "Dependency"
    ) -> None:
        if ang and d2._obj.num > d1._obj.num:
            d1, d2 = d2, d1
            ang = 1 - ang

        d1, d2 = self.get_name([d1, d2])

        return super().add_eq3(d1, d2, Coef(ang), dep)

    def add_eqangle(
        self,
        d1: Direction,
        d2: Direction,
        d3: Direction,
        d4: Direction,
        dep: "Dependency",
    ) -> None:
        """Add the inequality d1-d2=d3-d4."""
        # Use string as variables.
        l1, l2, l3, l4 = [d._obj.num for d in [d1, d2, d3, d4]]
        d1, d2, d3, d4 = self.get_name([d1, d2, d3, d4])
        ang1 = {d1: Coef(1), d2: Coef(-1)}
        ang2 = {d3: Coef(1), d4: Coef(-1)}

        if l2 > l1:
            ang1 = plus({self.pi: Coef(1)}, ang1)
        if l4 > l3:
            ang2 = plus({self.pi: Coef(1)}, ang2)

        ang12 = minus(ang1, ang2)
        self.record_eq(d1, d2, d3, d4)
        self.record_eq(d1, d3, d2, d4)

        expr = list(ang12.items())
        if not self.add_expr(expr):
            return []

        self.register(expr, dep)

    def get_all_eqs_and_why(self) -> Generator[Any, None, None]:
        return super().get_all_eqs_and_why(True)


class DistanceTable(GeometricTable):
    """Coefficient matrix A for position(point, line)."""

    def __init__(self, name: str = ""):
        name = name or "1:1"
        self.merged = {}
        self.ratios = set()
        super().__init__(name, None)

    def pairs(self) -> Generator[tuple[str, str], None, None]:
        l2vs = defaultdict(list)
        for v in list(self.v2e.keys()):
            if v == self.const:
                continue
            line, p = v.split(":")
            l2vs[line].append(p)

        for line, ps in l2vs.items():
            for p1, p2 in perm2(ps):
                yield line + ":" + p1, line + ":" + p2

    def name(self, line: Line, p: Point) -> str:
        v = line.name + ":" + p.name
        self.v2obj[v] = (line, p)
        return v

    def map2obj(self, names: list[str]) -> list[Point]:
        return [self.v2obj[n][1] for n in names]

    def add_cong(
        self,
        l12: Line,
        l34: Line,
        p1: Point,
        p2: Point,
        p3: Point,
        p4: Point,
        dep: "Dependency",
    ) -> None:
        """Add that distance between p1 and p2 (on l12) == p3 and p4 (on l34)."""
        if p2.num > p1.num:
            p1, p2 = p2, p1
        if p4.num > p3.num:
            p3, p4 = p4, p3

        p1 = self.name(l12, p1)
        p2 = self.name(l12, p2)
        p3 = self.name(l34, p3)
        p4 = self.name(l34, p4)
        return super().add_eq4(p1, p2, p3, p4, dep)

    def get_all_eqs_and_why(self) -> Generator[Any, None, None]:
        for x in super().get_all_eqs_and_why(True):
            yield x

        # Now we figure out all the const ratios.
        h2pairs = defaultdict(list)
        for v1, v2 in self.pairs():
            if (v1, v2) in self.merged:
                continue
            e1, e2 = self.v2e[v1], self.v2e[v2]
            e12 = minus(e1, e2)
            h12 = hashed(e12)
            h2pairs[h12].append((v1, v2, e12))

        for (_, vves1), (_, vves2) in perm2(list(h2pairs.items())):
            v1, v2, e12 = vves1[0]
            for v1_, v2_, _ in vves1[1:]:
                self.merged[(v1_, v2_)] = (v1, v2)

            v3, v4, e34 = vves2[0]
            for v3_, v4_, _ in vves2[1:]:
                self.merged[(v3_, v4_)] = (v3, v4)

            if (v1, v2, v3, v4) in self.ratios:
                continue

            d12 = div(e12, e34)
            if d12 is None or d12 > 1 or d12 < 0:
                continue

            self.ratios.add((v1, v2, v3, v4))
            self.ratios.add((v2, v1, v4, v3))

            n, d = d12.numerator, d12.denominator

            # (v1 - v2) * d = (v3 - v4) * n
            why_dict = minus(
                minus({v1: d, v2: -d}, {v3: n, v4: -n}),
                minus(mult(e12, d), mult(e34, n)),  # there is no modulo, so this is 0
            )

            v1, v2, v3, v4 = self.map2obj([v1, v2, v3, v4])
            yield v1, v2, v3, v4, abs(n), abs(d), self.why(why_dict)
