from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from newclid.justifications.justification import Justification
from newclid.rule import Rule

if TYPE_CHECKING:
    from newclid.proof_state import ProofState


class RuleMatcher(ABC):
    @abstractmethod
    def match_theorem(self, rule: Rule, proof: ProofState) -> set[Justification]:
        """Match all dependencies created by the given rule given the existing dependency graph."""
