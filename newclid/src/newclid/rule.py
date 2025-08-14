"""Define the Rule as used in Newclid.

Rules represent theorems of geometry that are considered as axioms in the proof.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, NewType, Self

import yaml
from pydantic import BaseModel, ConfigDict, model_validator

from newclid.justifications._index import JustificationType
from newclid.predicates import Predicate
from newclid.tools import atomize

VarName = NewType("VarName", str)


class RuleConstruction(BaseModel):
    """A construction in a rule."""

    name: str
    """Name of the construction."""
    variables: tuple[VarName, ...]
    """Input variable names."""


class RuleApplication(BaseModel):
    """A rule application."""

    predicate: Predicate
    """The predicate justified by the rule."""

    rule: Rule
    """The rule applied."""
    premises: tuple[Predicate, ...]
    """The premises of the rule."""

    dependency_type: Literal[JustificationType.RULE_APPLICATION] = (
        JustificationType.RULE_APPLICATION
    )

    @model_validator(mode="after")
    def canonicalize(self) -> Self:
        self.premises = tuple(sorted(set(self.premises), key=lambda x: repr(x)))
        return self

    def __str__(self) -> str:
        premises_txt = ", ".join(str(premise) for premise in self.premises)
        return f"{premises_txt} =({self.rule.id})> {self.predicate}"

    def __hash__(self) -> int:
        return hash(self.predicate)


class Rule(BaseModel):
    """Deduction rule."""

    model_config = ConfigDict(frozen=True)

    id: str
    """Unique permanent identifier for the rule."""
    description: str
    """Descriptive name for the rule."""
    premises_txt: tuple[str, ...]
    """Tuple of predicates representing the hypothesis of the rule."""
    conclusions_txt: tuple[str, ...]
    """Tuple of predicates representing the conclusions of the rule."""
    allow_point_repetition: bool = False
    """Whether the same point can correspond to different variables in the rule presentation."""

    @property
    def premises(self) -> list[RuleConstruction]:
        premises: list[RuleConstruction] = []
        for p in self.premises_txt:
            name, *args = atomize(p)
            premises.append(
                RuleConstruction(name=name, variables=tuple(VarName(a) for a in args))
            )
        return premises

    @property
    def conclusions(self) -> list[RuleConstruction]:
        conclusions: list[RuleConstruction] = []
        for c in self.conclusions_txt:
            name, *args = atomize(c)
            conclusions.append(
                RuleConstruction(name=name, variables=tuple(VarName(a) for a in args))
            )
        return conclusions

    @property
    def fullname(self) -> str:
        return f"{self.id} {self.description}"

    @property
    def variables(self) -> list[VarName]:
        variable_names: set[VarName] = set()
        for p in self.premises + self.conclusions:
            for x in p.variables:
                if str.isalpha(x[0]):
                    variable_names.add(x)
        return list(variable_names)

    def __str__(self) -> str:
        premises_txt = ", ".join(premise for premise in self.premises_txt)
        conclusions_txt = ", ".join(conclusion for conclusion in self.conclusions_txt)
        return f"{premises_txt} => {conclusions_txt}"

    def __hash__(self) -> int:
        return hash(self.id)


def rules_from_file(file_path: Path) -> list[Rule]:
    """Load deduction rule from a file."""
    match file_path.suffix:
        case ".yaml":
            return _rules_from_yaml(file_path.read_text())
        case ".txt":
            return rules_from_txt(file_path.read_text())
        case _:
            raise ValueError(f"Unsupported file extension: {file_path.suffix}")


def _rules_from_yaml(yaml_content: str) -> list[Rule]:
    """Load deduction rule from a yaml object."""
    return [Rule.model_validate(rule) for rule in yaml.safe_load(yaml_content)]


def rules_from_txt(text: str) -> list[Rule]:
    """Load deduction rule from a txt object."""
    description = ""
    res: list[Rule] = []
    for i, s in enumerate(atomize(text, "\n")):
        if "=>" in s:
            res.append(_rule_from_string(s, description or f"rule of line {i}"))
            description = ""
        else:
            description = s
    return res


def _rule_from_string(s: str, description: str = "") -> Rule:
    premises, conclusions = atomize(s, "=>")
    id, description = description.split(" ", 1)
    return Rule(
        id=id,
        description=description,
        premises_txt=atomize(premises, ","),
        conclusions_txt=atomize(conclusions, ","),
    )
