"""Utilities for Newclid."""

from __future__ import annotations

from difflib import Differ
from fractions import Fraction
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator, Optional, Sequence, TypeVar

from pydantic import BaseModel
from pyvis.network import Network  # type: ignore

from newclid.numerical import close_enough

if TYPE_CHECKING:
    from newclid.predicates import Predicate


class InfQuotientError(Exception):
    pass


# maximum denominator for a fraction.
MAX_DENOMINATOR = 1000000

T = TypeVar("T")


def get_quotient(v: Any) -> Fraction:
    v = float(v)
    n = v
    d = 1
    while not close_enough(n, round(n)):
        d += 1
        n += v
        if d > MAX_DENOMINATOR:
            e = InfQuotientError(v)
            raise e

    n = int(round(n))
    return Fraction(n, d)


def atomize(s: str, split_by: Optional[str] = None) -> tuple[str, ...]:
    words = s.split(split_by)
    return tuple(word.strip() for word in words)


def str_to_fraction(s: str) -> Fraction:
    if "pi/" in s:
        ns, ds = s.split("pi/")
        n, d = int(ns), int(ds)
        if d < 0:
            n, d = -n, -d
        return Fraction(n % d, d)
    elif "o" in s:
        n = int(s[:-1])
        d = 180
        return Fraction(n % d, d)
    elif "/" in s:
        ns, ds = s.split("/")
        n, d = int(ns), int(ds)
        return Fraction(n, d)
    else:
        n = int(s)
        d = 1
        return Fraction(n, d)


def fraction_to_len(f: Fraction):
    return f"{f.numerator}/{f.denominator}"


def fraction_to_ratio(f: Fraction):
    return f"{f.numerator}/{f.denominator}"


def fraction_to_angle(f: Fraction):
    n, d = f.numerator, f.denominator
    return f"{n % d}pi/{d}"


def reshape(to_reshape: Sequence[T], n: int) -> Generator[tuple[T, ...], None, None]:
    assert (len(to_reshape) % n) == 0, (
        f"Sequence length {len(to_reshape)} is not a multiple of reshape divisor {n}"
    )
    for i in range(0, len(to_reshape), n):
        yield tuple(to_reshape[i : i + n])


def add_edge(net: Network, u: Any, v: Any):
    net.add_node(u)  # type: ignore
    net.add_node(v)  # type: ignore
    net.add_edge(u, v)  # type: ignore


def run_static_server(directory_to_serve: Path):
    print(f"command to run the server: python -m http.server -d {directory_to_serve}")


def boring_predicate(predicate: Predicate) -> bool:
    s = str(predicate)
    if "=" in s:
        splited = atomize(s, "=")
        return all(t == splited[0] for t in splited)
    if "≅" in s:
        a, b = atomize(s, "≅")
        return a == b
    if "has the same orientation as" in s:
        a, b = atomize(s, "has the same orientation as")
        return a == b
    return False


def point_construction_tuple(point_name: str) -> tuple[str, ...]:
    return tuple(point_name[::-1]) if len(point_name) > 1 else ("0", *point_name[::-1])


S = TypeVar("S", bound=str)


def points_by_construction_order(points: set[S]) -> list[S]:
    return sorted(list(points), key=point_construction_tuple)


def pretty_basemodel_diff(actual: BaseModel, expected: BaseModel) -> str:
    return "\n".join(
        Differ().compare(
            expected.model_dump_json(indent=2).splitlines(),
            actual.model_dump_json(indent=2).splitlines(),
        )
    )


B = TypeVar("B", bound=BaseModel)


def pretty_basemodel_list_diff(actual: list[B], expected: list[B]) -> str:
    actual_combined_lines: list[str] = []
    for item in actual:
        actual_combined_lines.extend(item.model_dump_json(indent=2).splitlines())

    expected_combined_lines: list[str] = []
    for item in expected:
        expected_combined_lines.extend(item.model_dump_json(indent=2).splitlines())

    return "\n".join(Differ().compare(expected_combined_lines, actual_combined_lines))
