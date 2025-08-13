from __future__ import annotations

import collections
import json
import logging
import os
import subprocess
import tempfile
import time
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Annotated, Literal

from newclid.agent.follow_deductions import (
    ARPremiseConstruction,
    CachedARDeduction,
    CachedDeduction,
    CachedNumericalCheckDeduction,
    CachedReflexivityDeduction,
    CachedRuleDeduction,
    DeductionProvider,
    DeductionType,
)
from newclid.all_rules import (
    R03_ARC_DETERMINES_INTERNAL_ANGLES,
    R04_CONGRUENT_ANGLES_ARE_IN_A_CYCLIC,
    R11_BISECTOR_THEOREM_1,
    R12_BISECTOR_THEOREM_2,
    R13_ISOSCELES_TRIANGLE_EQUAL_ANGLES,
    R14_EQUAL_BASE_ANGLES_IMPLY_ISOSCELES,
    R19_HYPOTENUSE_IS_DIAMETER,
    R28_OVERLAPPING_PARALLELS,
    R34_AA_SIMILARITY_OF_TRIANGLES_DIRECT,
    R35_AA_SIMILARITY_OF_TRIANGLES_REVERSE,
    R41_THALES_THEOREM_3,
    R42_THALES_THEOREM_4,
    R43_ORTHOCENTER_THEOREM,
    R46_INCENTER_THEOREM,
    R49_RECOGNIZE_CENTER_OF_CIRCLE_CYCLIC,
    R50_RECOGNIZE_CENTER_OF_CYCLIC_CONG,
    R51_MIDPOINT_SPLITS_IN_TWO,
    R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES,
    R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES,
    R54_DEFINITION_OF_MIDPOINT,
    R55_MIDPOINT_CONG_PROPERTIES,
    R56_MIDPOINT_COLL_PROPERTIES,
    R60_SSS_SIMILARITY_OF_TRIANGLES_DIRECT,
    R61_SSS_SIMILARITY_OF_TRIANGLES_REVERSE,
    R62_SAS_SIMILARITY_OF_TRIANGLES_DIRECT,
    R63_SAS_SIMILARITY_OF_TRIANGLES_REVERSE,
    R68_SIMILARITY_WITHOUT_SCALING_DIRECT,
    R69_SIMILARITY_WITHOUT_SCALING_REVERSE,
    R71_RESOLUTION_OF_RATIOS,
    R72_DISASSEMBLING_A_CIRCLE,
    R73_DEFINITION_OF_CIRCLE,
    R74_INTERSECTION_BISECTORS,
    R77_CONGRUENT_TRIANGLES_DIRECT_PROPERTIES,
    R78_CONGRUENT_TRIANGLES_REVERSE_PROPERTIES,
    R80_SAME_CHORD_SAME_ARC_FOUR_POINTS_1,
    R82_PARA_OF_COLL,
    R91_ANGLES_OF_ISO_TRAPEZOID,
)
from newclid.deductors import ARReason
from newclid.deductors.deductor_interface import ARCoefficient
from newclid.predicate_types import PredicateArgument
from newclid.predicates import NUMERICAL_PREDICATES
from newclid.predicates._index import PredicateType
from newclid.problem import PredicateConstruction, ProblemSetup
from newclid.rule import Rule
from pydantic import BaseModel, Field

LOGGER = logging.getLogger(__name__)


class YuclidError(Exception):
    pass


if "UV_PROJECT_ENVIRONMENT" not in os.environ:
    # If we don't have a custom project environment set, then we use the one in
    # .venv at the root of the repository.
    YUCLID_PATH = Path(__file__).parents[3] / ".venv/bin/yuclid"
else:
    # If we do have a custom project environment set, then we use the one in the
    # environment variable. This is used in the docker setup, where we are running
    # uv sync in the docker newclid folder, but the build files are written to
    # the environment on the SSD.
    YUCLID_PATH = (  # pyright: ignore
        Path(os.environ["UV_PROJECT_ENVIRONMENT"]) / "bin/yuclid"
    )

# We need to keep this here to fail fast. There's no way to use this module
# without having the binary installed.
if not YUCLID_PATH.is_file():
    raise YuclidError(
        f"yuclid binary not found at {YUCLID_PATH}. "
        "Run `uv sync --reinstall` to install it."
    )


class YuclidStatus(str, Enum):
    SOLVED = "solved"
    SATURATED = "saturated"


class YuclidOutput(BaseModel):
    status: YuclidStatus
    all_deductions: list[HEDeduction]
    deductions_for_goal: list[HEDeduction]


class YuclidAdapter(DeductionProvider):
    def __init__(self, problem_name: str = "noname"):
        self.problem_name = problem_name
        self._precomputed_all_deductions: list[CachedDeduction] = []
        self._precomputed_deductions_for_goal: list[CachedDeduction] = []
        self._precomputed_rule_deductions: dict[Rule, list[CachedRuleDeduction]] = (
            collections.defaultdict(list)
        )
        self._precomputed_ar_deductions: list[CachedARDeduction] = []
        self._precomputed_numerical_checks: list[CachedNumericalCheckDeduction] = []
        self._precomputed_reflexivities: list[CachedReflexivityDeduction] = []
        self._precomputation_input: list[str] | None = None
        self.goals: list[PredicateConstruction] = []

    @property
    def precomputation_input_str(self) -> str:
        if self._precomputation_input is None:
            raise ValueError("Precomputation input is not set.")
        return "\n".join(self._precomputation_input)

    def ordered_deductions_for_problem(
        self, problem: ProblemSetup
    ) -> list[CachedDeduction]:
        if self._precomputation_input is None:
            self._precompute(problem)
        if not problem.goals:
            return self._precomputed_all_deductions
        return self._precomputed_deductions_for_goal

    def rule_matches(
        self, rule: Rule, problem: ProblemSetup
    ) -> list[CachedRuleDeduction]:
        if self._precomputation_input is None:
            self._precompute(problem)
        return self._precomputed_rule_deductions[rule]

    def ar_deductions(self, problem: ProblemSetup) -> list[CachedARDeduction]:
        if self._precomputation_input is None:
            self._precompute(problem)
        return self._precomputed_ar_deductions

    def _precompute(self, problem: ProblemSetup) -> None:
        self._precomputation_input = _write_yuclid_setup(problem)
        yuclid_output = self._run_yuclid()

        for he_deduction in yuclid_output.all_deductions:
            deduction: CachedDeduction
            match he_deduction.deduction_type:
                case DeductionType.RULE:
                    if he_deduction.newclid_rule in {
                        HESpecificRule.IGNORE.value,
                        HESpecificRule.BY_CONSTRUCTION.value,
                    }:
                        continue
                    deduction = he_deduction.to_cached_application()
                    rule = ID_TO_YUCLID_RULE[he_deduction.newclid_rule]
                    self._precomputed_rule_deductions[rule].append(deduction)
                case DeductionType.AR:
                    deduction = he_deduction.to_cached_application()
                    self._precomputed_ar_deductions.append(deduction)
                case DeductionType.NUM:
                    deduction = he_deduction.to_cached_application()
                    self._precomputed_numerical_checks.append(deduction)
                case DeductionType.REFLEXIVITY:
                    deduction = he_deduction.to_cached_application()
                    self._precomputed_reflexivities.append(deduction)
            self._precomputed_all_deductions.append(deduction)
            if he_deduction in yuclid_output.deductions_for_goal:
                self._precomputed_deductions_for_goal.append(deduction)

    def _run_yuclid(self) -> YuclidOutput:
        t0 = time.perf_counter()
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file_path = Path(temp_dir) / f"problem_{self.problem_name}.txt"
            input_file_path.write_text(self.precomputation_input_str)
            command = [
                YUCLID_PATH.as_posix(),
                "--mode",
                "ddar",
                "--disable-ar-dist",
                "--disable-ar-squared",
                "--disable-eqn-statements",
                "--disable-ar-sin",
                "--use-json",
                "--log-level",
                "warning",
                "--input-file",
                str(input_file_path),
            ]
            cmd_joined = " ".join(command)
            LOGGER.debug(
                f"Running yuclid on {input_file_path}. Setup:\n{self.precomputation_input_str}"
            )
            try:
                # Run the binary with the input file
                result = subprocess.run(
                    command, capture_output=True, text=True, check=True
                )

            except subprocess.CalledProcessError as e:
                error_msg = (
                    f"yuclid execution failed: {e}.\nCommand: {cmd_joined}\n"
                    f"Setup:\n{self.precomputation_input_str}\nStderr:\n{e.stderr}"
                )
                LOGGER.error(error_msg)
                raise YuclidError(error_msg) from e

            try:
                he_output = YuclidOutput.model_validate_json(result.stdout)
            except json.JSONDecodeError as e:
                error_msg = (
                    f"yuclid JSON output parsing and validation failed: {e}.\nCommand: {cmd_joined}\n"
                    f"Setup:\n{self.precomputation_input_str}\nStdout:\n{result.stdout}"
                )
                LOGGER.error(error_msg)
                raise YuclidError(error_msg) from e

        run_time = time.perf_counter() - t0
        LOGGER.info(
            f"Ran yuclid in {run_time:.2f}s. "
            f"Precomputed {len(he_output.all_deductions)} deductions,"
            f" {len(he_output.deductions_for_goal)} for goal."
        )
        return he_output

    def reset(self) -> None:
        self._precomputed_all_deductions = []
        self._precomputed_deductions_for_goal = []
        self._precomputed_rule_deductions = collections.defaultdict(list)
        self._precomputed_ar_deductions = []
        self._precomputation_input = None
        self.goals = []


class HEConstruction(BaseModel):
    name: str
    points: tuple[PredicateArgument, ...]

    def to_newclid(self) -> PredicateConstruction:
        return PredicateConstruction.from_predicate_type_and_args(
            PredicateType(self.name), self.points
        )


class HESpecificRule(str, Enum):
    IGNORE = "ignore"
    BY_CONSTRUCTION = "By construction"


class HERuleApplication(BaseModel):
    deduction_type: Literal[DeductionType.RULE] = DeductionType.RULE
    point_deps: list[str]
    newclid_rule: str
    assumptions: list[HEConstruction]
    assertions: list[HEConstruction]

    def to_cached_application(self) -> CachedRuleDeduction:
        premises = tuple(assumption.to_newclid() for assumption in self.assumptions)
        conclusions = tuple(assertion.to_newclid() for assertion in self.assertions)
        rule = ID_TO_YUCLID_RULE[self.newclid_rule]

        return CachedRuleDeduction(
            deduction_type=DeductionType.RULE,
            rule=rule,
            premises=premises,
            conclusions=conclusions,
            point_deps=self.point_deps,
        )


class HEARReason(str, Enum):
    ANGLE_CHASING = "angle chasing"
    RATIO_CHASING = "ratio chasing"


HEAR_REASON_TO_AR_REASON: dict[HEARReason, ARReason] = {
    HEARReason.ANGLE_CHASING: ARReason.ANGLE_CHASING,
    HEARReason.RATIO_CHASING: ARReason.RATIO_CHASING,
}


class HEARonstruction(BaseModel):
    name: str
    points: tuple[PredicateArgument, ...]
    coeff: Fraction
    lhs_terms: dict[str, Fraction]

    def to_newclid(self) -> ARPremiseConstruction:
        return ARPremiseConstruction(
            predicate_construction=PredicateConstruction.from_predicate_type_and_args(
                PredicateType(self.name), self.points
            ),
            coefficient=ARCoefficient(
                coeff=self.coeff,
                lhs_terms=self.lhs_terms,
            ),
        )


class HEARApplication(BaseModel):
    deduction_type: Literal[DeductionType.AR] = DeductionType.AR
    point_deps: list[str]
    ar_reason: HEARReason
    assumptions: list[HEARonstruction]
    assertions: list[HEConstruction]

    def to_cached_application(self) -> CachedARDeduction:
        premises = tuple(assumption.to_newclid() for assumption in self.assumptions)
        conclusions = tuple(assertion.to_newclid() for assertion in self.assertions)
        return CachedARDeduction(
            deduction_type=DeductionType.AR,
            ar_reason=HEAR_REASON_TO_AR_REASON[self.ar_reason],
            premises=premises,
            conclusions=conclusions,
            point_deps=self.point_deps,
        )


class HENumericalCheck(BaseModel):
    deduction_type: Literal[DeductionType.NUM] = DeductionType.NUM
    assertions: list[HEConstruction]

    def to_cached_application(self) -> CachedNumericalCheckDeduction:
        return CachedNumericalCheckDeduction(
            deduction_type=DeductionType.NUM,
            conclusions=tuple(assertion.to_newclid() for assertion in self.assertions),
        )


class HEReflexivity(BaseModel):
    deduction_type: Literal[DeductionType.REFLEXIVITY] = DeductionType.REFLEXIVITY
    assertions: list[HEConstruction]

    def to_cached_application(self) -> CachedReflexivityDeduction:
        return CachedReflexivityDeduction(
            deduction_type=DeductionType.REFLEXIVITY,
            conclusions=tuple(assertion.to_newclid() for assertion in self.assertions),
        )


HEDeduction = Annotated[
    HERuleApplication | HEARApplication | HENumericalCheck | HEReflexivity,
    Field(discriminator="deduction_type"),
]


def _write_yuclid_setup(problem: ProblemSetup) -> list[str]:
    setup_lines: list[str] = []
    for pt in problem.points:
        setup_lines.append(f"point {pt.name} {pt.num.x} {pt.num.y}")
    for assumption in problem.assumptions:
        if assumption.predicate_type in NUMERICAL_PREDICATES:
            continue
        setup_lines.append(f"assume {_predicate_to_yuclid(assumption)}")
    for goal in problem.goals:
        setup_lines.append(f"prove {_predicate_to_yuclid(goal)}")
    return setup_lines


def _predicate_to_yuclid(predicate: PredicateConstruction) -> str:
    predicate_name = predicate.predicate_type.value
    args_txts: list[str] = []
    for arg in predicate.args:
        if "pi/" in arg:
            args_txts.append(arg.replace("pi/", "/"))
        else:
            args_txts.append(arg)
    return f"{predicate_name} {' '.join(args_txts)}"


YUCLID_RULES: set[Rule] = {
    R03_ARC_DETERMINES_INTERNAL_ANGLES,
    R04_CONGRUENT_ANGLES_ARE_IN_A_CYCLIC,
    R11_BISECTOR_THEOREM_1,
    R12_BISECTOR_THEOREM_2,
    R13_ISOSCELES_TRIANGLE_EQUAL_ANGLES,
    R14_EQUAL_BASE_ANGLES_IMPLY_ISOSCELES,
    R19_HYPOTENUSE_IS_DIAMETER,
    R28_OVERLAPPING_PARALLELS,
    R34_AA_SIMILARITY_OF_TRIANGLES_DIRECT,
    R35_AA_SIMILARITY_OF_TRIANGLES_REVERSE,
    R41_THALES_THEOREM_3,
    R42_THALES_THEOREM_4,
    R43_ORTHOCENTER_THEOREM,
    R46_INCENTER_THEOREM,
    R49_RECOGNIZE_CENTER_OF_CIRCLE_CYCLIC,
    R50_RECOGNIZE_CENTER_OF_CYCLIC_CONG,
    R51_MIDPOINT_SPLITS_IN_TWO,
    R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES,
    R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES,
    R54_DEFINITION_OF_MIDPOINT,
    R55_MIDPOINT_CONG_PROPERTIES,
    R56_MIDPOINT_COLL_PROPERTIES,
    R60_SSS_SIMILARITY_OF_TRIANGLES_DIRECT,
    R61_SSS_SIMILARITY_OF_TRIANGLES_REVERSE,
    R62_SAS_SIMILARITY_OF_TRIANGLES_DIRECT,
    R63_SAS_SIMILARITY_OF_TRIANGLES_REVERSE,
    R68_SIMILARITY_WITHOUT_SCALING_DIRECT,
    R69_SIMILARITY_WITHOUT_SCALING_REVERSE,
    R71_RESOLUTION_OF_RATIOS,
    R72_DISASSEMBLING_A_CIRCLE,
    R73_DEFINITION_OF_CIRCLE,
    R74_INTERSECTION_BISECTORS,
    R77_CONGRUENT_TRIANGLES_DIRECT_PROPERTIES,
    R78_CONGRUENT_TRIANGLES_REVERSE_PROPERTIES,
    R80_SAME_CHORD_SAME_ARC_FOUR_POINTS_1,
    R82_PARA_OF_COLL,
    R91_ANGLES_OF_ISO_TRAPEZOID,
}

ID_TO_YUCLID_RULE: dict[str, Rule] = {rule.id: rule for rule in YUCLID_RULES}
