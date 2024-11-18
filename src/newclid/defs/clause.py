from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class ArgType(Enum):
    POINT = "Point"
    RATIO = "Ratio"
    Angle = "Angle"
    Length = "Length"


@dataclass
class Construction:
    """One predicate applied to a set of points and values."""

    name: str
    args: tuple[str]
    args_types: tuple[ArgType]

    def __post_init__(self):
        self.hash_tuple = (self.name, *self.args)

    def translate(self, mapping: dict[str, str]) -> Construction:
        args = [mapping[a] if a in mapping else a for a in self.args]
        return Construction(self.name, tuple(args), self.args_types)

    def __str__(self) -> str:
        return " ".join(self.hash_tuple)

    def __hash__(self) -> tuple[str, ...]:
        return hash(self.hash_tuple)

    @classmethod
    def from_txt(cls, data: str) -> Construction:
        data = data.split(" ")
        name = data[0]

        args_names = []
        args_types = []
        for args_str in data[1:]:
            arg_type = ArgType.POINT
            if ":" in args_str:
                args_str, arg_type = args_str.split(":")
            args_names.append(args_str)
            args_types.append(ArgType(arg_type))

        return Construction(
            name=name, args=tuple(args_names), args_types=tuple(args_types)
        )


class Clause:
    """One clause to define one or multiple points through one or more constructions."""

    def __init__(self, points: list[str], constructions: list[Construction]):
        self.points = []
        self.nums = []

        for p in points:
            num = None
            if isinstance(p, str) and "@" in p:
                p, num = p.split("@")
                x, y = num.split("_")
                num = float(x), float(y)
            self.points.append(p)
            self.nums.append(num)

        self.constructions = constructions

    def translate(self, mapping: dict[str, str]) -> Clause:
        points0 = []
        for p in self.points:
            pcount = len(mapping) + 1
            name = chr(96 + pcount)
            if name > "z":  # pcount = 26 -> name = 'z'
                name = chr(97 + (pcount - 1) % 26) + str((pcount - 1) // 26)

            p0 = mapping.get(p, name)
            mapping[p] = p0
            points0.append(p0)
        return Clause(points0, [c.translate(mapping) for c in self.constructions])

    def add(self, name: str, args: list[str]) -> None:
        self.constructions.append(Construction(name, args))

    def __str__(self) -> str:
        return (
            " ".join(self.points)
            + " = "
            + ", ".join(str(c) for c in self.constructions)
        )

    @classmethod
    def from_txt(cls, data: str) -> Clause:
        if data == " =":
            return Clause([], [])
        points, statements = data.split(" = ")
        return Clause(
            points.split(" "),
            [Construction.from_txt(c) for c in statements.split(", ")],
        )
