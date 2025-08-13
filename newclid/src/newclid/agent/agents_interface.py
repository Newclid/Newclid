"""Action / Feedback interface

Make all interactions explicit between DeductiveAgent and the Proof state to allow
for independent developpement of different kinds of DeductiveAgent.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from newclid.agent import AgentStats
    from newclid.proof_state import ProofState
    from newclid.rule import Rule


class DeductiveAgent(ABC):
    """Common interface for deductive agents"""

    @abstractmethod
    def step(self, proof: ProofState, rules: list[Rule]) -> bool:
        """Perform a single reasoning step on the given proof with given rules, and return if the agent is exausted.

        Returns:
            True if the agent is considered exausted, False otherwise.
        """

    def get_stats(self) -> AgentStats | None:
        """Get the statistics of the agent."""
        return None
