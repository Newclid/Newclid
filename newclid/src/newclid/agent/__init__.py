"""Interface and implementations of Deductive Agents."""

from typing import Annotated

from pydantic import Field

from newclid.agent.ddarn import DDARNStats
from newclid.agent.follow_deductions import FollowDeductionsStats

AgentStats = Annotated[
    DDARNStats | FollowDeductionsStats, Field(discriminator="agent_type")
]
