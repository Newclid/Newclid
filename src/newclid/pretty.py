"""Utilities for string manipulation in the DSL."""

from newclid.predicates import Predicate
from newclid.listing import list_eqratio3


MAP_SYMBOL = {
    "C": Predicate.COLLINEAR.value,
    "X": Predicate.COLLINEAR_X.value,
    "P": Predicate.PARALLEL.value,
    "T": Predicate.PERPENDICULAR.value,
    "M": Predicate.MIDPOINT.value,
    "D": Predicate.CONGRUENT.value,
    "I": Predicate.CIRCLE.value,
    "O": Predicate.CYCLIC.value,
    "^": Predicate.EQANGLE.value,
    "/": Predicate.EQRATIO.value,
    "%": Predicate.EQRATIO.value,
    "S": Predicate.SIMILAR_TRIANGLE.value,
    "=": Predicate.CONTRI_TRIANGLE.value,
    "A": Predicate.COMPUTE_ANGLE.value,
    "R": Predicate.COMPUTE_RATIO.value,
    "Q": Predicate.FIX_C.value,
    "E": Predicate.FIX_L.value,
    "V": Predicate.FIX_B.value,
    "H": Predicate.FIX_T.value,
    "Z": Predicate.FIX_P.value,
    "Y": Predicate.IND.value,
}


def map_symbol(c: str) -> str:
    return MAP_SYMBOL[c]


def map_symbol_inv(c: str) -> str:
    return {v: k for k, v in MAP_SYMBOL.items()}[c]


def pretty2r(a: str, b: str, c: str, d: str) -> str:
    if b in (c, d):
        a, b = b, a

    if a == d:
        c, d = d, c

    return f"{a} {b} {c} {d}"


def pretty2a(a: str, b: str, c: str, d: str) -> str:
    if b in (c, d):
        a, b = b, a

    if a == d:
        c, d = d, c

    return f"{a} {b} {c} {d}"


def pretty_angle(a: str, b: str, c: str, d: str) -> str:
    if b in (c, d):
        a, b = b, a
    if a == d:
        c, d = d, c

    if a == c:
        return f"\u2220{b}{a}{d}"
    return f"\u2220({a}{b}-{c}{d})"


def pretty_nl(name: str, args: list[str]) -> str:
    """Natural lang formatting a predicate."""
    if name in [Predicate.CONSTANT_ANGLE.value, Predicate.S_ANGLE.value]:
        a, b, c, d, y = args
        return f"{pretty_angle(a, b, c, d)} = {y}"
    if name == Predicate.CONSTANT_RATIO.value:
        a, b, c, d, y = args
        return f"{a}{b}:{c}{d} = {y}"
    if name == Predicate.COMPUTE_ANGLE.value:
        a, b, c, d = args
        return f"{pretty_angle(a, b, c, d)}"
    if name in [Predicate.COLLINEAR.value, "C"]:
        return "" + ",".join(args) + " are collinear"
    if name == Predicate.COLLINEAR_X.value:
        return "" + ",".join(list(set(args))) + " are collinear"
    if name in [Predicate.CYCLIC.value, "O"]:
        return "" + ",".join(args) + " are concyclic"
    if name in [Predicate.MIDPOINT.value, "midpoint", "M"]:
        x, a, b = args
        return f"{x} is midpoint of {a}{b}"
    if name in [Predicate.EQANGLE.value, Predicate.EQANGLE6.value, "^"]:
        a, b, c, d, e, f, g, h = args
        return f"{pretty_angle(a, b, c, d)} = {pretty_angle(e, f, g, h)}"
    if name in [Predicate.EQRATIO.value, Predicate.EQRATIO6.value, "/"]:
        return _ratio_pretty(args)
    if name == Predicate.EQRATIO3.value:
        return " & ".join(_ratio_pretty(ratio) for ratio in list_eqratio3(args))
    if name in [Predicate.CONGRUENT.value, "D"]:
        a, b, c, d = args
        return f"{a}{b} = {c}{d}"
    if name in [Predicate.PERPENDICULAR.value, "T"]:
        if len(args) == 2:  # this is algebraic derivation.
            ab, cd = args  # ab = 'd( ... )'
            return f"{ab} \u27c2 {cd}"
        a, b, c, d = args
        return f"{a}{b} \u27c2 {c}{d}"
    if name in [Predicate.PARALLEL.value, "P"]:
        if len(args) == 2:  # this is algebraic derivation.
            ab, cd = args  # ab = 'd( ... )'
            return f"{ab} \u2225 {cd}"
        a, b, c, d = args
        return f"{a}{b} \u2225 {c}{d}"
    if name in [
        Predicate.SIMILAR_TRIANGLE_REFLECTED.value,
        Predicate.SIMILAR_TRIANGLE.value,
        Predicate.SIMILAR_TRIANGLE_BOTH.value,
    ]:
        a, b, c, x, y, z = args
        return f"\u0394{a}{b}{c} is similar to \u0394{x}{y}{z}"
    if name in [
        Predicate.CONTRI_TRIANGLE_REFLECTED.value,
        Predicate.CONTRI_TRIANGLE.value,
        Predicate.CONTRI_TRIANGLE_BOTH.value,
    ]:
        a, b, c, x, y, z = args
        return f"\u0394{a}{b}{c} is congruent to \u0394{x}{y}{z}"
    if name in [Predicate.CIRCLE.value, "I"]:
        o, a, b, c = args
        return f"{o} is the circumcenter of \\Delta {a}{b}{c}"
    if name == "foot":
        a, b, c, d = args
        return f"{a} is the foot of {b} on {c}{d}"
    if name == Predicate.CONSTANT_LENGTH.value:
        a, b, v = args
        return f"{a}{b} = {v}"
    raise NotImplementedError(f"Cannot write pretty name for {name}")


def _ratio_pretty(args: list[str]):
    return "{}{}:{}{} = {}{}:{}{}".format(*args)


def pretty(txt: tuple[str, ...]) -> str:
    """Pretty formating a predicate string."""
    if isinstance(txt, str):
        txt = txt.split(" ")
    name, *args = txt
    if name == Predicate.IND.value:
        return "Y " + " ".join(args)
    if name in [
        Predicate.FIX_C.value,
        Predicate.FIX_L.value,
        Predicate.FIX_B.value,
        Predicate.FIX_T.value,
        Predicate.FIX_P.value,
    ]:
        return map_symbol_inv(name) + " " + " ".join(args)
    if name == Predicate.COMPUTE_ANGLE.value:
        a, b, c, d = args
        return "A " + " ".join(args)
    if name == Predicate.COMPUTE_RATIO.value:
        a, b, c, d = args
        return "R " + " ".join(args)
    if name == Predicate.CONSTANT_ANGLE.value:
        a, b, c, d, y = args
        return f"^ {pretty2a(a, b, c, d)} {y}"
    if name == Predicate.CONSTANT_RATIO.value:
        a, b, c, d, y = args
        return f"/ {pretty2r(a, b, c, d)} {y}"
    if name == Predicate.COLLINEAR.value:
        return "C " + " ".join(args)
    if name == Predicate.COLLINEAR_X.value:
        return "X " + " ".join(args)
    if name == Predicate.CYCLIC.value:
        return "O " + " ".join(args)
    if name in [Predicate.MIDPOINT.value, "midpoint"]:
        x, a, b = args
        return f"M {x} {a} {b}"
    if name == Predicate.EQANGLE.value:
        a, b, c, d, e, f, g, h = args
        return f"^ {pretty2a(a, b, c, d)} {pretty2a(e, f, g, h)}"
    if name == Predicate.EQRATIO.value:
        a, b, c, d, e, f, g, h = args
        return f"/ {pretty2r(a, b, c, d)} {pretty2r(e, f, g, h)}"
    if name == Predicate.EQRATIO3.value:
        a, b, c, d, o, o = args
        return f"S {o} {a} {b} {o} {c} {d}"
    if name == Predicate.CONGRUENT.value:
        a, b, c, d = args
        return f"D {a} {b} {c} {d}"
    if name == Predicate.PERPENDICULAR.value:
        if len(args) == 2:  # this is algebraic derivation.
            ab, cd = args  # ab = 'd( ... )'
            return f"T {ab} {cd}"
        a, b, c, d = args
        return f"T {a} {b} {c} {d}"
    if name == Predicate.PARALLEL.value:
        if len(args) == 2:  # this is algebraic derivation.
            ab, cd = args  # ab = 'd( ... )'
            return f"P {ab} {cd}"
        a, b, c, d = args
        return f"P {a} {b} {c} {d}"
    if name in [
        Predicate.SIMILAR_TRIANGLE_REFLECTED.value,
        Predicate.SIMILAR_TRIANGLE.value,
        Predicate.SIMILAR_TRIANGLE_BOTH.value,
    ]:
        a, b, c, x, y, z = args
        return f"S {a} {b} {c} {x} {y} {z}"
    if name in [
        Predicate.CONTRI_TRIANGLE_REFLECTED.value,
        Predicate.CONTRI_TRIANGLE.value,
        Predicate.CONTRI_TRIANGLE_BOTH.value,
    ]:
        a, b, c, x, y, z = args
        return f"= {a} {b} {c} {x} {y} {z}"
    if name == Predicate.CIRCLE.value:
        o, a, b, c = args
        return f"I {o} {a} {b} {c}"
    if name == "foot":
        a, b, c, d = args
        return f"F {a} {b} {c} {d}"
    return " ".join(txt)
