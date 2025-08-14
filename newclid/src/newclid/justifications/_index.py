from enum import Enum


class JustificationType(str, Enum):
    ASSUMPTION = "Assumption"
    NUMERICAL_CHECK = "Numerical Check"
    RULE_APPLICATION = "Rule Application"
    AR_DEDUCTION = "AR Deduction"
    CIRCLE_MERGE = "Circle Merge"
    LINE_MERGE = "Line Merge"
    DIRECT_CONSEQUENCE = "Direct Consequence"
    REFLEXIVITY = "Reflexivity"


class JustificationError(Exception):
    """Exception raised when a justification is not possible."""
