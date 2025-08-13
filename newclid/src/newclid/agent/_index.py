from enum import Enum


class AgentName(str, Enum):
    DDARN = "ddarn"
    HUMAN_AGENT = "human_agent"
    FOLLOW_DEDUCTIONS = "follow_deductions"
