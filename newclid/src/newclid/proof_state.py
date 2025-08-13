"""Implements the proof state."""

from __future__ import annotations

import logging

from numpy.random import Generator as RngGenerator

from newclid.deductors.deductor_interface import (
    Deductor,
    add_to_deductors,
    check_from_deductors,
    justify_from_deductors,
)
from newclid.justifications.justification import (
    Assumption,
    Justification,
    NumericalCheck,
)
from newclid.justifications.justify_predicates import justify_predicate
from newclid.justifications.predicates_graph import PredicatesGraph
from newclid.predicates import (
    NUMERICAL_PREDICATES,
    Predicate,
    predicate_from_construction,
)
from newclid.problem import ProblemSetup
from newclid.rng import setup_rng
from newclid.rule import Rule
from newclid.rule_matching.interface import RuleMatcher
from newclid.symbols.symbols_registry import SymbolsRegistry

LOGGER = logging.getLogger(__name__)


class ProofBuildError(Exception):
    pass


class ProofState:
    """Object representing the proof state."""

    def __init__(
        self,
        *,
        problem: ProblemSetup,
        rule_matcher: RuleMatcher,
        deductors: list[Deductor],
        rng: RngGenerator | int | None = None,
    ):
        self.problem = problem
        self._matcher = rule_matcher
        self.deductors = deductors
        self._numerical_check_cache: dict[Predicate, bool] = {}
        self.graph = PredicatesGraph()
        self.symbols = SymbolsRegistry()
        self.rng = setup_rng(rng)
        self._BLACKLIST: set[Justification] = set()

        self._add_points_to_symbols_graph()
        self._add_assumptions_to_pred_graph()
        self.goals = self._goals_from_problem()

    def match_theorem(self, rule: Rule) -> set[Justification]:
        """Match a rule to the proof state.

        Returns:
            A set of dependencies that would be added to the proof state if the rule was applied.
        """
        return self._matcher.match_theorem(rule, proof=self)

    def apply(self, justification: Justification) -> bool:
        """Add the justification to the proof dependency graph.

        Returns:
            True if the predicate is a new one, false otherwise.
        """
        if justification in self._BLACKLIST:
            return False

        if not self.check_numerical(justification.predicate):
            LOGGER.warning(
                f"Trying to add justification {justification} the conclusion of which is numerically false"
            )
            self._BLACKLIST.add(justification)
            return False

        dep_for_predicate = self.graph.hyper_graph.get(justification.predicate)
        already_proven = dep_for_predicate is not None
        if already_proven:
            return False

        self.graph.hyper_graph[justification.predicate] = justification
        justification.predicate.add(self)
        _symbols = justification.predicate.symbols(self.symbols)
        add_to_deductors(justification, self.deductors, self.symbols)
        return True

    def check(self, predicate: Predicate) -> bool:
        """Symbolically check if the predicate is currently considered True."""
        if predicate in self.graph.hyper_graph:
            return True
        if not predicate.check_numerical():
            return False
        symbolic_check = predicate.check(self)
        if symbolic_check:
            self.justify(predicate)
            return True
        if symbolic_check is None:
            deductors_check = check_from_deductors(
                predicate, self.deductors, self.symbols
            )
            if deductors_check:
                return True
        return False

    def check_numerical(self, predicate: Predicate) -> bool:
        """Check if the predicate is numerically sound."""
        if predicate in self._numerical_check_cache:
            return self._numerical_check_cache[predicate]
        res = predicate.check_numerical()
        self._numerical_check_cache[predicate] = res
        return res

    def justify(self, predicate: Predicate) -> Justification:
        justification_cached = self.graph.hyper_graph.get(predicate)
        if justification_cached is not None:
            return justification_cached

        justification = justify_predicate(predicate, self.deductors, self.symbols)
        if justification is None:
            justification = justify_from_deductors(
                predicate, self.deductors, self.symbols
            )
        if justification is None:
            raise ValueError(f"Could not justify predicate {predicate}")

        self.apply(justification)
        return justification

    def check_goals(self) -> bool:
        """Check if the goals are all symbolically checked."""
        if not self.goals:
            return False
        for goal in self.goals:
            if not self.check(goal):
                return False
        return True

    def _add_points_to_symbols_graph(self) -> None:
        for point in self.problem.points:
            self.symbols.points.add_point(point)

    def _add_assumptions_to_pred_graph(self) -> None:
        for predicate_construction in self.problem.assumptions:
            predicate = predicate_from_construction(
                predicate_construction,
                points_registry=self.symbols.points,
            )
            if predicate is None:
                raise ProofBuildError(
                    f"Assumption '{predicate_construction}' cannot be built."
                )
            if not self.check_numerical(predicate):
                raise ProofBuildError(
                    f"Assumption '{predicate_construction}' is numerically false."
                )
            dependency: Justification
            if predicate.predicate_type in NUMERICAL_PREDICATES:
                dependency = NumericalCheck(predicate=predicate)
            else:
                dependency = Assumption(predicate=predicate)
            self.apply(dependency)

    def _goals_from_problem(self) -> list[Predicate]:
        goals: list[Predicate] = []
        for goal in self.problem.goals:
            goal_predicate = predicate_from_construction(
                goal, points_registry=self.symbols.points
            )
            if goal_predicate is None:
                continue
            if not self.check_numerical(goal_predicate):
                raise ProofBuildError(f"Goal {goal} is numerically false.")
            goals.append(goal_predicate)
        return goals
