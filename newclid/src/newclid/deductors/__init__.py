"""Deductors are alternative ways to get deductions from other sources than rules and symbols merges.

The main example of deductor is the algebraic reasoning, which is used to get deductions from angle chasing and ratio chasing.
"""

from enum import Enum


class ARReason(str, Enum):
    ANGLE_CHASING = "Angle Chasing"
    RATIO_CHASING = "Ratio Chasing"
