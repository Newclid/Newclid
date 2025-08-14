"""Numerical representation of geometric objects in Newclid."""

ATOM = 1e-7
REL_TOL = 0.001


def close_enough(a: float, b: float) -> bool:
    return abs(a - b) < 4 * ATOM or abs(a - b) / max(abs(a), abs(b)) < REL_TOL


def nearly_zero(a: float) -> bool:
    return abs(a) < 2 * ATOM


def sign(a: float) -> int:
    return 0 if nearly_zero(a) else (1 if a > 0 else -1)
