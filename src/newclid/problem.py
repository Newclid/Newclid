"""Implements objects to represent problems, theorems, proofs, traceback."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from newclid.defs.clause import Clause, Construction
from newclid.statements.statement import Statement
from newclid.predicates import Predicate

import newclid.pretty as pt

from newclid.ratios import simplify

if TYPE_CHECKING:
    from newclid.dependencies.dependency import Dependency
    from newclid.defs.definition import Definition


CONSTRUCTION_RULE = "c0"


def reshape(list_to_reshape: list[Any], n: int = 1) -> list[list[Any]]:
    assert len(list_to_reshape) % n == 0
    columns = [[] for i in range(n)]
    for i, x in enumerate(list_to_reshape):
        columns[i % n].append(x)
    return zip(*columns)


class Problem:
    """Describe one problem to solve."""

    def __init__(self, url: str, clauses: list["Clause"], goals: list["Construction"]):
        self.url = url
        self.clauses = clauses
        self.goals = goals

    def copy(self) -> Problem:
        return Problem(self.url, list(self.clauses), list(self.goals))

    def translate(self) -> Problem:  # to single-char point names
        """Translate point names into alphabetical."""
        mapping = {}
        clauses = []

        for clause in self.clauses:
            clauses.append(clause.translate(mapping))

        self.goals = [goal.translate(mapping) for goal in self.goals]

        p = Problem(self.url, clauses, self.goals)
        return p

    def __str__(self) -> str:
        return "; ".join([str(c) for c in self.clauses]) + (
            " ? " + "; ".join(str(goal) for goal in self.goals) if self.goals else ""
        )

    @classmethod
    def from_txt_file(cls, fname: str, to_dict: bool = False, translate: bool = True):
        """Load a problem from a text file."""
        with open(fname, "r") as f:
            lines = f.read().split("\n")

        lines = [line for line in lines if line]
        data = [
            cls.from_txt(url + "\n" + problem, translate)
            for (url, problem) in reshape(lines, 2)
        ]
        if to_dict:
            return cls.to_dict(data)
        return data

    @classmethod
    def from_txt(cls, data: str, translate: bool = True) -> Problem:
        """Load a problem from a str object."""
        url = ""
        if "\n" in data:
            url, data = data.split("\n")

        if " ? " in data:
            clauses_str, goals_str = data.split(" ? ")
        else:
            clauses_str, goals_str = data, None

        problem = Problem(
            url=url,
            clauses=[Clause.from_txt(c) for c in clauses_str.split("; ")],
            goals=[Construction.from_txt(g) for g in goals_str.split("; ")]
            if goals_str
            else [],
        )
        if translate:
            return problem.translate()
        return problem

    @classmethod
    def to_dict(cls, data: list[Problem]) -> dict[str, Problem]:
        return {p.url: p for p in data}


def setup_str_from_problem(
    problem: Problem, definitions: dict[str, "Definition"]
) -> str:
    """Construct the <theorem_premises> string from Problem object."""
    ref = 0

    string = []
    for clause in problem.clauses:
        group = {}
        p2deps = defaultdict(list)
        for c in clause.constructions:
            cdef = definitions[c.name]

            if len(c.args) != len(cdef.construction.args):
                assert len(c.args) + len(clause.points) == len(cdef.construction.args)
                c.args = clause.points + c.args

            mapping = dict(zip(cdef.construction.args, c.args))
            for points, bs in cdef.basics:
                points = tuple([mapping[x] for x in points])
                for p in points:
                    group[p] = points

                for b in bs:
                    args = [mapping[a] for a in b.args]
                    name = b.name
                    if b.name in [
                        Predicate.S_ANGLE.value,
                        Predicate.CONSTANT_ANGLE.value,
                    ]:
                        x, y, z, v = args
                        name = Predicate.CONSTANT_ANGLE.value
                        v = int(v)

                        if v < 0:
                            v = -v
                            x, z = z, x

                        m, n = simplify(int(v), 180)
                        args = [y, z, y, x, f"{m}pi/{n}"]

                    basic = Statement(name, tuple(args))
                    p2deps[points].append(basic.hash_tuple)

        for k, v in p2deps.items():
            p2deps[k] = sort_deps(v)

        points = clause.points
        while points:
            p = points[0]
            gr = group[p]
            points = [x for x in points if x not in gr]

            deps_str = []
            for dep in p2deps[gr]:
                ref_str = "{:02}".format(ref)
                dep_str = pt.pretty(dep)

                if dep[0] == Predicate.CONSTANT_ANGLE.value:
                    m, n = map(int, dep[-1].split("pi/"))
                    mn = f"{m}. pi / {n}."
                    dep_str = " ".join(dep_str.split()[:-1] + [mn])

                deps_str.append(dep_str + " " + ref_str)
                ref += 1

            string.append(" ".join(gr) + " : " + " ".join(deps_str))

    string = "{S} " + " ; ".join([s.strip() for s in string])
    string += " ? " + "; ".join(pt.pretty(goal.hash_tuple) for goal in problem.goals)
    return string


def compare_fn(dep: "Dependency") -> tuple["Dependency", str]:
    return (dep, pt.pretty(dep))


def sort_deps(deps: list["Dependency"]) -> list["Dependency"]:
    return sorted(deps, key=compare_fn)
