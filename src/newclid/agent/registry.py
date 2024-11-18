from __future__ import annotations

from typing import Callable, Type

from newclid.agent.human_agent import HumanAgent
from newclid.agent.agents_interface import DeductiveAgent
from newclid.agent.breadth_first_search import BFSDD, BFSDDAR


class AgentRegistry:
    def __init__(self) -> None:
        self.agents = {"bfsddar": BFSDDAR, "bfsdd": BFSDD, "human": HumanAgent}

    def register(
        self,
        agent_name: str,
        agent_generator: Type[DeductiveAgent] | Callable[[], DeductiveAgent],
    ) -> None:
        if agent_name in self.agents:
            raise ValueError(
                "Agent name %s is already existing and cannot be registered."
            )
        self.agents[agent_name] = agent_generator

    def load_agent(self, agent_name: str) -> DeductiveAgent:
        return self.agents.get(agent_name)()
