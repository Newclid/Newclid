from __future__ import annotations
from newclid.defs.clause import Clause, Construction
from newclid.problem import reshape


class Definition:
    """Definitions of construction statements."""

    def __init__(
        self,
        construction: Construction,
        rely: dict[str, str],
        clause: Clause,
        basics: list[tuple[list[str], list[Construction]]],
        numerics: list[Construction],
    ):
        self.construction = construction
        self.rely = rely
        self.clause = clause
        self.basics = basics
        self.numerics = numerics

        args = set()
        for num in numerics:
            args.update(num.args)

        self.points = []
        self.args = []
        for p in self.construction.args:
            if p in args:
                self.args.append(p)
            else:
                self.points.append(p)

    @classmethod
    def from_txt_file(cls, fname: str) -> Definition:
        with open(fname, "r") as f:
            lines = f.read()
        return cls.from_string(lines)

    @classmethod
    def from_string(cls, string: str) -> list[Definition]:
        lines = string.split("\n")
        data = [cls.from_txt("\n".join(group)) for group in reshape(lines, 6)]
        return data

    @staticmethod
    def to_dict(data: list[Definition]) -> dict[str, Definition]:
        return {d.construction.name: d for d in data}

    @classmethod
    def from_txt(cls, data: str) -> Definition:
        """Load definitions from a str object."""
        statement, rely, clause, basics, numerics, _ = data.split("\n")
        basics = [] if not basics else [b.strip() for b in basics.split(";")]

        levels = []
        for bs in basics:
            if ":" in bs:
                points, bs = bs.split(":")
                points = points.strip().split()
            else:
                points = []
            if bs.strip():
                bs = [Construction.from_txt(b.strip()) for b in bs.strip().split(",")]
            else:
                bs = []
            levels.append((points, bs))

        numerics = [] if not numerics else numerics.split(", ")

        return cls(
            construction=Construction.from_txt(statement),
            rely=parse_rely(rely),
            clause=Clause.from_txt(clause),
            basics=levels,
            numerics=[Construction.from_txt(c) for c in numerics],
        )


def parse_rely(s: str) -> dict[str, str]:
    result = {}
    if not s:
        return result
    s = [x.strip() for x in s.split(",")]
    for x in s:
        a, b = x.split(":")
        a, b = a.strip().split(), b.strip().split()
        result.update({m: b for m in a})
    return result
