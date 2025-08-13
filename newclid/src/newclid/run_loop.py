"""Main loop of interactions between the agent and the proof state."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from pydantic import BaseModel

from newclid.agent import AgentStats
from newclid.rule import Rule

if TYPE_CHECKING:
    from newclid.agent.agents_interface import DeductiveAgent
    from newclid.proof_state import ProofState


class RunInfos(BaseModel):
    runtime: float
    success: bool
    steps: int
    success_per_goal: dict[str, bool]
    agent_stats: AgentStats | None = None


def run_loop(
    deductive_agent: DeductiveAgent, proof: "ProofState", rules: list[Rule]
) -> RunInfos:
    """Run DeductiveAgent until saturation or goal found."""
    for goal in proof.goals:
        if not proof.check_numerical(goal):
            raise ValueError("%s fails numerical check", goal)

    t0 = time.time()
    step = 0
    running = True
    while running:
        running = deductive_agent.step(proof=proof, rules=rules)
        step += 1

    runtime = time.time() - t0
    success_per_goal: dict[str, bool] = {}
    for goal in proof.goals:
        success_per_goal[f"{goal} succeeded"] = proof.check(goal)

    return RunInfos(
        runtime=runtime,
        success=all(success_per_goal.values()),
        success_per_goal=success_per_goal,
        steps=step,
        agent_stats=deductive_agent.get_stats(),
    )
