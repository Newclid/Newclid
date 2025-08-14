"""Implements theorem matching functions for the Deductive Database (DD)."""

from __future__ import annotations

import collections
import itertools
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import (
    Generator,
    Iterator,
    Optional,
    TypeAlias,
    cast,
)

from newclid.justifications.justification import (
    Justification,
    RuleApplication,
    justify_dependency,
)
from newclid.predicate_types import PredicateArgument
from newclid.predicates import (
    SYMBOLIC_PREDICATES,
    Predicate,
    predicate_from_construction,
)
from newclid.predicates._index import PredicateType
from newclid.predicates.collinearity import Coll
from newclid.predicates.cyclic import Cyclic
from newclid.problem import PredicateConstruction
from newclid.proof_state import ProofState
from newclid.rule import Rule, RuleConstruction, VarName
from newclid.rule_matching.efficient_statement import (
    EfficientStatement,
    efficient_version,
    generate_permutations,
)
from newclid.rule_matching.interface import RuleMatcher
from newclid.rule_matching.permutations import generate_permutations_as_dicts

LOGGER = logging.getLogger(__name__)

Mapping: TypeAlias = dict[VarName, PredicateArgument]


class MappingMatcher(RuleMatcher):
    def __init__(self, theorem_mapper: TheoremMapper) -> None:
        self.runtime_cache_path: Optional[Path] = None
        self.theorem_mapper = theorem_mapper

    def match_theorem(self, rule: Rule, proof: ProofState) -> set[Justification]:
        conclusions = self._match_generic(rule, proof)
        valid_conclusions: set[Justification] = set()
        for conclusion_dep in conclusions:
            if proof.graph.hyper_graph.get(conclusion_dep.predicate) is not None:
                continue
            applicable = True
            for premise in justify_dependency(conclusion_dep, proof):
                if not proof.check(premise):
                    applicable = False
            if not applicable and "Pythagoras" not in rule.fullname:
                LOGGER.warning(
                    "Trying to apply theorem when symbolic checks have failed."
                    f" Check the mappings of theorem '{rule}'."
                )
                continue
            valid_conclusions.add(conclusion_dep)
        return valid_conclusions

    def _match_generic(self, rule: Rule, proof: ProofState) -> set[Justification]:
        theorem_conclusions: set[Justification] = set()
        points = [p.name for p in proof.symbols.points]

        for mapping in self.theorem_mapper.mappings(rule, points, proof=proof):
            why: list[Predicate] = []
            assert len(mapping) > 0

            applicable = True
            for premise in rule.premises:
                premise_args = tuple(mapping[arg] for arg in premise.variables)
                premise_predicate_construction = (
                    PredicateConstruction.from_predicate_type_and_args(
                        PredicateType(premise.name), premise_args
                    )
                )
                premise_predicate = predicate_from_construction(
                    premise_predicate_construction, proof.symbols.points
                )
                if premise_predicate is None:
                    if "Pythagoras" not in rule.fullname:
                        LOGGER.warning(
                            f"Trying to build invalid premise '{premise_predicate}' of theorem '{rule}'."
                        )
                    applicable = False
                    break
                if not proof.check_numerical(premise_predicate):
                    if (
                        premise_predicate.predicate_type
                        in SYMBOLIC_PREDICATE_TYPES_NAMES
                    ):
                        LOGGER.warning(
                            f"Trying match numerically false premise '{premise_predicate}' of theorem '{rule}'."
                        )
                    applicable = False
                    break
                why.append(premise_predicate)
            if not applicable:
                continue

            for conclusion in rule.conclusions:
                conclusion_args = tuple(mapping[arg] for arg in conclusion.variables)
                conclusion_predicate_construction = (
                    PredicateConstruction.from_predicate_type_and_args(
                        PredicateType(conclusion.name), conclusion_args
                    )
                )
                conclusion_predicate = predicate_from_construction(
                    conclusion_predicate_construction,
                    points_registry=proof.symbols.points,
                )
                if conclusion_predicate is None:
                    LOGGER.debug(
                        f"Trying to build invalid conclusion '{conclusion_predicate}' of theorem '{rule}'."
                    )
                    continue
                theorem_conclusions.add(
                    RuleApplication(
                        predicate=conclusion_predicate, rule=rule, premises=tuple(why)
                    )
                )

        return theorem_conclusions


class TheoremMapper(ABC):
    @abstractmethod
    def mappings(
        self,
        rule: "Rule",
        points: list[PredicateArgument],
        proof: ProofState,
    ) -> Generator[Mapping, None, None]:
        """Find valid mappings for the given rule using the given points."""


class CCMapper(TheoremMapper):
    def mappings(
        self,
        rule: "Rule",
        points: list[PredicateArgument],
        proof: ProofState,
    ) -> Generator[Mapping, None, None]:
        variables = rule.variables
        for mapping in generate_permutations_as_dicts(points, variables):
            yield mapping


class FilterMapper(TheoremMapper):
    def mappings(
        self,
        rule: "Rule",
        points: list[PredicateArgument],
        proof: ProofState,
    ) -> Generator[Mapping, None, None]:
        # Each rule will have a collection of premises P.
        # S is the set of symbolic premises, and N is the set of
        # numerical premises; they partition P.
        # What we will do is iterate over all the filtered mappings for
        # the set of premises S. That will yield a set of variables compatible
        # with the premises S. For each of those, we will generate
        # a collection of mappings that also assign free points to
        # the variables in the set of premises N.

        LOGGER.debug("FilterMapper running for rule: %s", rule.fullname)

        for circle in proof.symbols.circles:
            LOGGER.debug("Circle: %s", circle)
            for point in circle.points:
                LOGGER.debug("  Point: %s", point)

        symbolic_premises: list[RuleConstruction] = []
        numerical_premises: list[RuleConstruction] = []

        variables_in_symbolic_premises: set[VarName] = set()
        for premise in rule.premises:
            premise_predicate = premise.name
            if premise_predicate not in SYMBOLIC_PREDICATE_TYPES_NAMES:
                numerical_premises.append(premise)
            else:
                symbolic_premises.append(premise)
                variables_in_symbolic_premises.update(premise.variables)

        numerical_only_variable_names_in_theorem: set[VarName] = (
            set(rule.variables) - variables_in_symbolic_premises
        )

        predicates_by_predicate_name = predictates_by_type_name_from_hypergraph(
            proof.graph.hyper_graph
        )

        LOGGER.debug("Symbolic premises: %s", predicates_by_predicate_name)
        LOGGER.debug("Numerical premises: %s", numerical_premises)

        if not rule.allow_point_repetition and len(rule.variables) > len(points):
            LOGGER.debug(
                "Skipping theorem %s because it has more variables than points",
                rule.fullname,
            )
            yield from []
            return

        symbolic_partial_mappings: list[PartialMapping] = []
        for premise in symbolic_premises:
            predicate_to_match = premise.name
            variables = premise.variables
            predicates_of_predicate: list[Predicate] = []
            match predicate_to_match:
                case "cyclic":
                    for circle in proof.symbols.circles:
                        if len(circle.points) < len(variables):
                            continue
                        for combo in itertools.combinations(
                            circle.points, len(variables)
                        ):
                            predicates_of_predicate.append(Cyclic(points=combo))
                case "coll":
                    for line in proof.symbols.lines:
                        if len(line.points) < len(variables):
                            continue
                        for combo in itertools.combinations(
                            line.points, len(variables)
                        ):
                            assert all(hasattr(e, "num") for e in combo)
                            predicates_of_predicate.append(Coll(points=combo))
                case _:
                    predicates_of_predicate = predicates_by_predicate_name.get(
                        PredicateType(predicate_to_match), []
                    )
            LOGGER.debug(
                "Have %s predicates for predicate %s",
                len(predicates_of_predicate),
                predicate_to_match,
            )

            if len(predicates_of_predicate) == 0:
                # If there is at least one predicate that has no predicates, then
                # there is no chance we can match this rule. So, we fail fast.
                yield from []
                return
            symbolic_partial_mappings.append(
                PartialMapping(
                    variables,
                    [efficient_version(_stmt) for _stmt in predicates_of_predicate],
                )
            )

        LOGGER.debug("Symbolic partial mappings: %s", symbolic_partial_mappings)

        LOGGER.debug(
            "Mapping %s variables against %s points",
            len(rule.variables),
            len(points),
        )
        LOGGER.debug("Premises: %s", rule.premises)

        empty_mapping: list[Mapping] = [{}]
        mapping_iterator: Iterator[Mapping] = (
            iterate_mappings(
                partial_mappings=symbolic_partial_mappings,
                remaining_variables=rule.variables,
                remaining_points=set(points),
                allow_point_repetition=rule.allow_point_repetition,
            )
            if symbolic_partial_mappings
            else iter(empty_mapping)
        )

        for mapping in mapping_iterator:
            if not numerical_only_variable_names_in_theorem:
                LOGGER.debug("Yielding mapping (195): %s", mapping)
                yield mapping
            else:
                if rule.allow_point_repetition:
                    available_points = set(points)
                else:
                    available_points = set(points) - set(mapping.values())
                for mapping_final in iterate_mapping_with_complementary_assignments(
                    mapping,
                    remaining_variables_in_theorem=list(
                        numerical_only_variable_names_in_theorem
                    ),
                    points=list(available_points),
                ):
                    LOGGER.debug(
                        "Yielding mapping with complementary assignments: %s %s",
                        rule.fullname,
                        mapping_final,
                    )
                    yield mapping_final


def predictates_by_type_name_from_hypergraph(
    hyper_graph: dict[Predicate, Justification],
) -> dict[PredicateType, list[Predicate]]:
    predicates_by_predictate_name: dict[PredicateType, list[Predicate]] = (
        collections.defaultdict(list)
    )
    for predicate in hyper_graph:
        predicates_by_predictate_name[predicate.predicate_type].append(predicate)
    return predicates_by_predictate_name


def iterate_mapping_with_complementary_assignments(
    mapping: Mapping, remaining_variables_in_theorem: list[str], points: list[str]
) -> Generator[Mapping, None, None]:
    """Yields mappings with additional variable assignments.

    For a given initial mapping of variables to points, yields either:
    1. Just the input mapping if there are no remaining unmapped variables
    2. New mappings that combine the input mapping with all possible assignments
    of the remaining unmapped variables to points

    Args:
        mapping: Initial dict mapping theorem variables to point names

    Yields:
        Iterator mapping all theorem variables to point names
    """
    if not remaining_variables_in_theorem:
        yield mapping
        return

    for mapping_of_remaining_variables in generate_permutations_as_dicts(  # type: ignore
        points, remaining_variables_in_theorem
    ):
        mapping.update(mapping_of_remaining_variables)  # type: ignore
        yield mapping


SYMBOLIC_PREDICATE_TYPES_NAMES = {
    symbolic_predicate_type.value
    for symbolic_predicate_type in SYMBOLIC_PREDICATES.keys()
}


LookupDict: TypeAlias = dict[VarName, dict[PredicateArgument, set[int]]]


class PartialMapping:
    lookup_dict: LookupDict  # pyright: ignore
    predicate_name: str
    predicates: list[EfficientStatement]
    vars_to_assign: tuple[VarName, ...]
    valid_arg_permutations: list[EfficientStatement]
    partial_assignment: dict[VarName, PredicateArgument]
    permutation_idxs_compatible_with_partial_assignment: set[int]
    mapping_hash: str

    def __init__(
        self,
        vars_to_assign: tuple[VarName, ...],
        predicates: list[EfficientStatement],
        lookup_dict: LookupDict | None = None,
        valid_arg_permutations: list[EfficientStatement] | None = None,
        partial_assignment: dict[VarName, PredicateArgument] | None = None,
        permutation_idxs_compatible_with_partial_assignment: set[int] | None = None,
    ):
        predicate_predicate_names: list[str] = [e[0] for e in predicates]
        assert len(set(predicate_predicate_names)) == 1, (
            f"PartialMapping must have predicates with the same predicate, but got {predicate_predicate_names}"
        )
        self.predicate_name = predicate_predicate_names[0]

        self.predicates = predicates
        self.vars_to_assign = vars_to_assign
        self._initialize_valid_arg_permutations(lookup_dict, valid_arg_permutations)

        self.partial_assignment = partial_assignment or dict()
        if permutation_idxs_compatible_with_partial_assignment is not None:
            self.permutation_idxs_compatible_with_partial_assignment = (
                permutation_idxs_compatible_with_partial_assignment
            )

    def with_assignment(
        self, var: VarName, point: PredicateArgument
    ) -> PartialMapping | None:
        # If the variable we're considering assigning is not even in our set of variables,
        # then it will be compatible with all of our assignments.
        if var not in self.vars_to_assign:
            return self

        # If we've already assigned the variable, that is an error, because we should only
        # be assigning new variables.
        if var in self.partial_assignment:
            raise ValueError(
                f"Attempting to re-assign variable {var} to {point} with {self.partial_assignment}"
            )

        updated_permutation_idxs_compatible_with_partial_assignment = (
            self.permutation_idxs_compatible_with_partial_assignment
            & self.lookup_dict[var][point]
        )
        if not updated_permutation_idxs_compatible_with_partial_assignment:
            return None
        updated_partial_assignment = {**self.partial_assignment, var: point}
        return PartialMapping(
            vars_to_assign=self.vars_to_assign,
            predicates=self.predicates,
            lookup_dict=self.lookup_dict,
            valid_arg_permutations=self.valid_arg_permutations,
            partial_assignment=updated_partial_assignment,
            permutation_idxs_compatible_with_partial_assignment=updated_permutation_idxs_compatible_with_partial_assignment,
        )

    def _initialize_valid_arg_permutations(
        self,
        lookup_dict: LookupDict | None,
        valid_arg_permutations: list[EfficientStatement] | None,
    ):
        assert not ((lookup_dict is None) ^ (valid_arg_permutations is None))
        if lookup_dict is not None:
            self.lookup_dict = lookup_dict
            self.valid_arg_permutations = (
                valid_arg_permutations if valid_arg_permutations is not None else []
            )
            return

        self.lookup_dict: LookupDict = collections.defaultdict(
            lambda: collections.defaultdict(set)
        )
        self.valid_arg_permutations = []

        points_iterator: Iterator[EfficientStatement]

        for predicate in self.predicates:
            points_iterator = generate_permutations(predicate)

            for stmt_permutation in points_iterator:
                assert len(self.vars_to_assign) == len(stmt_permutation) - 1, (
                    f"{self.predicate_name} {self.vars_to_assign} {stmt_permutation}"
                )
                permutation_pt_names = cast(
                    tuple[PredicateArgument, ...], stmt_permutation[1:]
                )
                self.valid_arg_permutations.append(stmt_permutation)
                if (
                    _get_valid_assignment_to_predicate_if_exists(
                        self.vars_to_assign, permutation_pt_names
                    )
                    is not None
                ):
                    for var, point in zip(self.vars_to_assign, permutation_pt_names):
                        self.lookup_dict[var][point].add(
                            len(self.valid_arg_permutations) - 1
                        )
        self.permutation_idxs_compatible_with_partial_assignment = set(
            range(len(self.valid_arg_permutations))
        )
        return self.valid_arg_permutations

    def __str__(self) -> str:
        return f"PartialMapping(predicate_name={self.predicate_name}, vars_to_assign={self.vars_to_assign})"

    def __repr__(self) -> str:
        return self.__str__()


def _get_valid_assignment_to_predicate_if_exists(
    vars: tuple[VarName, ...], points: tuple[PredicateArgument, ...]
) -> tuple[PredicateArgument, ...] | None:
    assignment: dict[VarName, PredicateArgument] = {}
    for v, p in zip(vars, points):
        if v in assignment and assignment[v] != p:
            return None
        assignment[v] = p
    return tuple(assignment[v] for v in vars)


def iterate_mappings(
    partial_mappings: list[PartialMapping],
    remaining_variables: list[VarName],
    remaining_points: set[PredicateArgument],
    current_assignment: dict[VarName, PredicateArgument] | None = None,
    conclusions_yielded: set[EfficientStatement] | None = None,
    allow_point_repetition: bool = False,
) -> Iterator[dict[VarName, PredicateArgument]]:
    current_assignment = current_assignment or {}
    if not remaining_variables:
        yield current_assignment
        return

    conclusions_yielded = conclusions_yielded or set()

    var, *remaining_vars_next_level = remaining_variables

    prefix = "  " * len(current_assignment)
    LOGGER.debug("%sChecking variable %s", prefix, var)
    for pt in remaining_points:
        LOGGER.debug("%sChecking point %s", prefix, pt)

        next_partial_mappings: list[PartialMapping] = []
        for current_partial_mapping in partial_mappings:
            next_partial_mapping = current_partial_mapping.with_assignment(var, pt)
            if next_partial_mapping is None:
                # If it's none, it means there was no assignment of current_assignment + var = pt
                # that was compatible with the partial mapping, so we must backtrack from
                # this partial assignment.
                break
            else:
                next_partial_mappings.append(next_partial_mapping)

        if len(next_partial_mappings) < len(partial_mappings):
            # This means that at least one partial mapping was unsatisfied, so we go on to the next point at this level.
            continue

        # If we've gotten here, it means that {**current_assignment, var: pt} is a valid assignment
        # for all the partial mappings, so we can continue to assign the rest of the variables, using
        # this prefix.

        if allow_point_repetition:
            new_remaining_points = remaining_points
        else:
            new_remaining_points = remaining_points - {pt}

        for mapping in iterate_mappings(
            partial_mappings=next_partial_mappings,
            remaining_variables=remaining_vars_next_level,
            remaining_points=new_remaining_points,
            current_assignment={**current_assignment, var: pt},
            allow_point_repetition=allow_point_repetition,
        ):
            yield mapping
