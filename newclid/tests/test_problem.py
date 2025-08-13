"""Tests manipulations of NcProblem."""

from typing import NamedTuple

import pytest
from newclid.numerical.geometries import PointNum
from newclid.predicate_types import PredicateArgument
from newclid.problem import (
    PredicateConstruction,
    ProblemSetup,
    filter_points_from_nc_problem,
    rename_points_in_nc_problem,
)
from newclid.symbols.points_registry import Point
from newclid.tools import pretty_basemodel_diff


def p(name: str) -> PredicateArgument:
    return PredicateArgument(name)


# A base problem for tests
BASE_PROBLEM = ProblemSetup(
    points=(
        Point(name=p("A"), num=PointNum(x=0, y=0)),
        Point(name=p("B"), num=PointNum(x=1, y=0)),
        Point(name=p("C"), num=PointNum(x=0, y=1)),
        Point(name=p("D"), num=PointNum(x=1, y=1)),
    ),
    assumptions=(
        PredicateConstruction.from_str("coll A B D"),
        PredicateConstruction.from_str("coll A B C D"),
    ),
    goals=(
        PredicateConstruction.from_str("coll B A C"),
        PredicateConstruction.from_str("coll B A D"),
    ),
)


class RenameCase(NamedTuple):
    name: str
    nc_problem: ProblemSetup
    mapping: dict[PredicateArgument, PredicateArgument]
    expected: ProblemSetup | Exception


RENAME_CASES = [
    RenameCase(
        name="Renaming one point",
        nc_problem=BASE_PROBLEM,
        mapping={p("A"): p("X")},
        expected=ProblemSetup(
            points=(
                Point(name=p("B"), num=PointNum(x=1, y=0)),
                Point(name=p("C"), num=PointNum(x=0, y=1)),
                Point(name=p("D"), num=PointNum(x=1, y=1)),
                Point(name=p("X"), num=PointNum(x=0, y=0)),
            ),
            assumptions=(
                PredicateConstruction.from_str("coll X B D"),
                PredicateConstruction.from_str("coll X B C D"),
            ),
            goals=(
                PredicateConstruction.from_str("coll B X C"),
                PredicateConstruction.from_str("coll B X D"),
            ),
        ),
    ),
    RenameCase(
        name="Renaming multiple points",
        nc_problem=BASE_PROBLEM,
        mapping={p("A"): p("X"), p("B"): p("Y")},
        expected=ProblemSetup(
            points=(
                Point(name=p("C"), num=PointNum(x=0, y=1)),
                Point(name=p("D"), num=PointNum(x=1, y=1)),
                Point(name=p("X"), num=PointNum(x=0, y=0)),
                Point(name=p("Y"), num=PointNum(x=1, y=0)),
            ),
            assumptions=(
                PredicateConstruction.from_str("coll X Y D"),
                PredicateConstruction.from_str("coll X Y C D"),
            ),
            goals=(
                PredicateConstruction.from_str("coll Y X C"),
                PredicateConstruction.from_str("coll Y X D"),
            ),
        ),
    ),
    RenameCase(
        name="Swapping two points",
        nc_problem=BASE_PROBLEM,
        mapping={p("A"): p("B"), p("B"): p("A")},
        expected=ProblemSetup(
            points=(
                Point(name=p("A"), num=PointNum(x=1, y=0)),
                Point(name=p("B"), num=PointNum(x=0, y=0)),
                Point(name=p("C"), num=PointNum(x=0, y=1)),
                Point(name=p("D"), num=PointNum(x=1, y=1)),
            ),
            assumptions=(
                PredicateConstruction.from_str("coll B A D"),
                PredicateConstruction.from_str("coll B A C D"),
            ),
            goals=(
                PredicateConstruction.from_str("coll A B C"),
                PredicateConstruction.from_str("coll A B D"),
            ),
        ),
    ),
    RenameCase(
        name="Empty mapping, no changes expected",
        nc_problem=BASE_PROBLEM,
        mapping={},
        expected=BASE_PROBLEM,
    ),
    RenameCase(
        name="Mapping a non-existent point, should raise ValueError",
        nc_problem=BASE_PROBLEM,
        mapping={p("Z"): p("X")},
        expected=ValueError(),
    ),
    RenameCase(
        name="Colliding a point to an existing point, should raise ValueError",
        nc_problem=BASE_PROBLEM,
        mapping={p("A"): p("B")},
        expected=ValueError(),
    ),
]


@pytest.mark.parametrize(
    "case",
    RENAME_CASES,
    ids=[c.name for c in RENAME_CASES],
)
def test_rename_points_in_nc_problem(case: RenameCase):
    """Test renaming points in an NcProblem."""
    if not isinstance(case.expected, ProblemSetup):
        with pytest.raises(case.expected.__class__):
            rename_points_in_nc_problem(case.nc_problem, case.mapping)
        return

    actual_problem = rename_points_in_nc_problem(case.nc_problem, case.mapping)
    assert actual_problem == case.expected, pretty_basemodel_diff(
        actual_problem, case.expected
    )


class FilterCase(NamedTuple):
    name: str
    nc_problem: ProblemSetup
    points_to_keep: list[PredicateArgument]
    expected: ProblemSetup | Exception


FILTER_CASES = [
    FilterCase(
        name="Keeping a subset of points",
        nc_problem=BASE_PROBLEM,
        points_to_keep=[p("A"), p("B"), p("D")],
        expected=ProblemSetup(
            points=(
                Point(name=p("A"), num=PointNum(x=0, y=0)),
                Point(name=p("B"), num=PointNum(x=1, y=0)),
                Point(name=p("D"), num=PointNum(x=1, y=1)),
            ),
            assumptions=(PredicateConstruction.from_str("coll A B D"),),
            goals=(PredicateConstruction.from_str("coll B A D"),),
        ),
    ),
    FilterCase(
        name="Keeping all points",
        nc_problem=BASE_PROBLEM,
        points_to_keep=[p("A"), p("B"), p("C"), p("D")],
        expected=BASE_PROBLEM,
    ),
    FilterCase(
        name="Keeping no points should raise ValueError",
        nc_problem=BASE_PROBLEM,
        points_to_keep=[],
        expected=ValueError(),
    ),
    FilterCase(
        name="Keeping points not in the problem should raise ValueError",
        nc_problem=BASE_PROBLEM,
        points_to_keep=[p("A"), p("Z")],
        expected=ValueError(),
    ),
]


@pytest.mark.parametrize(
    "case",
    FILTER_CASES,
    ids=[c.name for c in FILTER_CASES],
)
def test_filter_points_from_nc_problem(case: FilterCase):
    """Test filtering points from an NcProblem."""
    if not isinstance(case.expected, ProblemSetup):
        with pytest.raises(case.expected.__class__):
            filter_points_from_nc_problem(case.nc_problem, case.points_to_keep)
        return

    actual_problem = filter_points_from_nc_problem(case.nc_problem, case.points_to_keep)
    assert actual_problem == case.expected, pretty_basemodel_diff(
        actual_problem, case.expected
    )
