from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar, Union

from newclid.predicates import Predicate

if TYPE_CHECKING:
    from newclid.geometry import Symbol, Point, Angle, Ratio


@dataclass
class Statement:
    """One predicate applied to a set of points and values."""

    predicate: Predicate
    args: tuple["Point" | "Ratio" | "Angle" | int | str, ...]

    def __post_init__(self):
        self.predicate = Predicate(self.predicate)
        self.hash_tuple = hash_statement(self.name, self.args)

    def translate(self, mapping: dict[str, str]) -> Statement:
        args = [mapping[a] if a in mapping else a for a in self.args]
        return Statement(self.name, tuple(args))

    @property
    def name(self):
        return self.predicate.value

    def __str__(self) -> str:
        return name_and_arguments_to_str(self.name, self.args, " ")

    def __hash__(self) -> tuple[str, ...]:
        return hash(self.hash_tuple)

    @classmethod
    def from_txt(cls, data: str) -> Statement:
        data = data.split(" ")
        return Statement(data[0], tuple(data[1:]))


def name_and_arguments_to_str(
    name: str, args: list[str | int | "Symbol"], join: str
) -> list[str]:
    return join.join([name] + _arguments_to_str(args))


def hash_statement(name: str, args: list["Point" | "Ratio" | int]):
    return hash_statement_str(name, [_symbol_to_txt(p) for p in args])


def hash_statement_str(name: Union[str, Predicate], args: list[str]) -> tuple[str, ...]:
    """Return a tuple unique to name and args upto arg permutation equivariant."""
    try:
        predicate = Predicate(name)
    except ValueError:
        return (name, *args)
    if isinstance(name, Predicate):
        name = predicate.value
    if predicate is Predicate.EQANGLE6:
        name = Predicate.EQANGLE.value
    if predicate is Predicate.EQRATIO6:
        name = Predicate.EQRATIO.value
    return PREDICATE_TO_HASH[predicate](name, args)


def _symbol_to_txt(symbol: "Point" | "Ratio" | int | str):
    if isinstance(symbol, str):
        return symbol
    if isinstance(symbol, int):
        return str(symbol)
    return symbol.name


def _arguments_to_str(args: list[str | int | "Symbol"]) -> list[str]:
    args_str = []
    for arg in args:
        if isinstance(arg, (int, str, float)):
            args_str.append(str(arg))
        else:
            args_str.append(arg.name)
    return args_str


P = TypeVar("P")


def _hash_unordered_set_of_points(name: str, args: list[P]) -> tuple[str | P]:
    return (name,) + tuple(sorted(list(set(args))))


def _hash_unordered_set_of_points_with_value(
    name: str, args: list[P]
) -> tuple[str | P]:
    return _hash_unordered_set_of_points(name, args[:-1]) + (args[-1],)


def _hash_ordered_list_of_points(name: str, args: list[P]) -> tuple[str | P]:
    return (name,) + tuple(args)


def _hash_point_then_set_of_points(name: str, args: list[P]) -> tuple[str | P]:
    return (name, args[0]) + tuple(sorted(args[1:]))


def _hashed_unordered_two_lines_points(
    name: str, args: tuple[P, P, P, P]
) -> tuple[str, P, P, P, P]:
    a, b, c, d = args

    a, b = sorted([a, b])
    c, d = sorted([c, d])
    (a, b), (c, d) = sorted([(a, b), (c, d)])

    return (name, a, b, c, d)


def _hash_ordered_two_lines_with_value(
    name: str, args: tuple[P, P, P, P, P]
) -> tuple[str, P, P, P, P, P]:
    a, b, c, d, y = args
    a, b = sorted([a, b])
    c, d = sorted([c, d])
    return name, a, b, c, d, y


def _hash_point_and_line(name: str, args: tuple[P, P, P]) -> tuple[str, P, P, P]:
    a, b, c = args
    b, c = sorted([b, c])
    return (name, a, b, c)


def _hash_two_times_two_unorded_lines(
    name: str, args: tuple[P, P, P, P, P, P, P, P]
) -> tuple[str, P, P, P, P, P, P, P, P]:
    a, b, c, d, e, f, g, h = args
    a, b = sorted([a, b])
    c, d = sorted([c, d])
    e, f = sorted([e, f])
    g, h = sorted([g, h])
    # res = []
    # for i in range(2):
    #     for j in range(2):
    #         if i == 0:
    #             _a, _b, _e, _f, _c, _d, _g, _h = c, d, g, h, a, b, e, f
    #         else:
    #             _a, _b, _e, _f, _c, _d, _g, _h = a, b, e, f, c, d, g, h
    #         if j == 0:
    #             _a, _b, _c, _d, _e, _f, _g, _h = _e, _f, _g, _h, _a, _b, _c, _d
    #         res.append(deepcopy((_a, _b, _c, _d, _e, _f, _g, _h)))
    if tuple(sorted([a, b, e, f])) > tuple(sorted([c, d, g, h])):
        a, b, e, f, c, d, g, h = c, d, g, h, a, b, e, f
    if (a, b, c, d) > (e, f, g, h):
        a, b, c, d, e, f, g, h = e, f, g, h, a, b, c, d

    return (name,) + (a, b, c, d, e, f, g, h)


def _hash_triangle(
    name: str, args: tuple[P, P, P, P, P, P]
) -> tuple[str, P, P, P, P, P, P]:
    a, b, c, x, y, z = args
    (a, x), (b, y), (c, z) = sorted([(a, x), (b, y), (c, z)], key=sorted)
    (a, b, c), (x, y, z) = sorted([(a, b, c), (x, y, z)], key=sorted)
    return (name, a, b, c, x, y, z)


def _hash_eqratio_3(
    name: str, args: tuple[P, P, P, P, P, P]
) -> tuple[str, P, P, P, P, P, P]:
    a, b, c, d, o, o = args
    (a, c), (b, d) = sorted([(a, c), (b, d)], key=sorted)
    (a, b), (c, d) = sorted([(a, b), (c, d)], key=sorted)
    return (name, a, b, c, d, o, o)


PREDICATE_TO_HASH = {
    Predicate.PARALLEL: _hashed_unordered_two_lines_points,
    Predicate.CONGRUENT: _hashed_unordered_two_lines_points,
    Predicate.CONGRUENT_2: _hashed_unordered_two_lines_points,
    Predicate.PERPENDICULAR: _hashed_unordered_two_lines_points,
    Predicate.COLLINEAR_X: _hashed_unordered_two_lines_points,
    Predicate.NON_PARALLEL: _hashed_unordered_two_lines_points,
    Predicate.NON_PERPENDICULAR: _hashed_unordered_two_lines_points,
    Predicate.COLLINEAR: _hash_unordered_set_of_points,
    Predicate.CYCLIC: _hash_unordered_set_of_points,
    Predicate.NON_COLLINEAR: _hash_unordered_set_of_points,
    Predicate.DIFFERENT: _hash_unordered_set_of_points,
    Predicate.CIRCLE: _hash_point_then_set_of_points,
    Predicate.MIDPOINT: _hash_point_and_line,
    Predicate.CONSTANT_ANGLE: _hash_ordered_two_lines_with_value,
    Predicate.CONSTANT_RATIO: _hash_ordered_two_lines_with_value,
    Predicate.CONSTANT_LENGTH: _hash_unordered_set_of_points_with_value,
    Predicate.EQANGLE: _hash_two_times_two_unorded_lines,
    Predicate.EQRATIO: _hash_two_times_two_unorded_lines,
    Predicate.EQANGLE6: _hash_two_times_two_unorded_lines,
    Predicate.EQRATIO6: _hash_two_times_two_unorded_lines,
    Predicate.SAMESIDE: _hash_ordered_list_of_points,
    Predicate.S_ANGLE: _hash_ordered_list_of_points,
    Predicate.SIMILAR_TRIANGLE: _hash_triangle,
    Predicate.SIMILAR_TRIANGLE_REFLECTED: _hash_triangle,
    Predicate.SIMILAR_TRIANGLE_BOTH: _hash_triangle,
    Predicate.CONTRI_TRIANGLE: _hash_triangle,
    Predicate.CONTRI_TRIANGLE_REFLECTED: _hash_triangle,
    Predicate.CONTRI_TRIANGLE_BOTH: _hash_triangle,
    Predicate.EQRATIO3: _hash_eqratio_3,
}


def angle_to_num_den(angle: "Angle" | str) -> tuple[int, int]:
    name = angle
    if not isinstance(angle, str):
        name = angle.name
    num, den = name.split("pi/")
    return int(num), int(den)


def ratio_to_num_den(ratio: "Ratio" | str) -> tuple[int, int]:
    name = ratio
    if not isinstance(ratio, str):
        name = ratio.name
    num, den = name.split("/")
    return int(num), int(den)
