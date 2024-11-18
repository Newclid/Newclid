from __future__ import annotations
from typing import Optional
from newclid.defs.clause import Construction
from newclid.predicates import Predicate


class Theorem:
    """Deduction rule."""

    def __init__(self, premise: list[Construction], conclusion: list[Construction]):
        if len(conclusion) != 1:
            raise ValueError("Cannot have more or less than one conclusion")
        self.name = "_".join([p.name for p in premise + conclusion])
        self.rule_name: Optional[str] = None
        self.premises = premise
        self.is_arg_reduce = False
        self.conclusion = conclusion[0]

        if self.conclusion.name in [
            Predicate.EQRATIO3.value,
            Predicate.MIDPOINT.value,
            Predicate.CONTRI_TRIANGLE.value,
            Predicate.SIMILAR_TRIANGLE.value,
            Predicate.CONTRI_TRIANGLE_REFLECTED.value,
            Predicate.SIMILAR_TRIANGLE_REFLECTED.value,
            Predicate.SIMILAR_TRIANGLE_BOTH.value,
            Predicate.CONTRI_TRIANGLE_BOTH.value,
        ]:
            return

        prem_args = set(sum([list(premise.args) for premise in self.premises], []))
        con_args = set(self.conclusion.args)
        if len(prem_args) <= len(con_args):
            self.is_arg_reduce = True

    def __str__(self) -> str:
        premises_txt = ", ".join([str(premise) for premise in self.premises])
        conclusion_txt = ", ".join([str(self.conclusion)])
        return f"{premises_txt} => {conclusion_txt}"

    @classmethod
    def from_txt_file(cls, fname: str) -> list[Theorem]:
        with open(fname, "r") as f:
            theorems = f.read()
        return cls.from_string(theorems)

    @classmethod
    def from_string(cls, string: str) -> list[Theorem]:
        """Load deduction rule from a str object."""
        theorems = string.split("\n")
        theorems = [line for line in theorems if line and not line.startswith("#")]
        theorems = [cls.from_txt(line) for line in theorems]

        for i, th in enumerate(theorems):
            th.rule_name = "r{:02}".format(i)

        return theorems

    @staticmethod
    def to_dict(theorems: list[Theorem]):
        result = {}
        for t in theorems:
            if t.name in result:
                t.name += "_"
            result[t.rule_name] = t
        return result

    @classmethod
    def from_txt(cls, data: str) -> Theorem:
        premises, conclusion = data.split(" => ")
        premises = premises.split(", ")
        conclusion = conclusion.split(", ")
        return Theorem(
            premise=[Construction.from_txt(p) for p in premises],
            conclusion=[Construction.from_txt(c) for c in conclusion],
        )
