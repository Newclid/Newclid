import logging
from typing import NamedTuple

import numpy as np
import pytest
from newclid.api import GeometricSolverBuilder
from newclid.deductors.sympy_ar.algebraic_manipulator import SympyARDeductor
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.justifications._index import JustificationType
from newclid.predicates import predicate_from_construction
from newclid.problem import PredicateConstruction, predicate_to_construction
from newclid.proof_justifications import goals_justifications


class ArCase(NamedTuple):
    id: str
    problem: str
    expected_ar_new_predicates: tuple[tuple[str, ...], ...]


#  ∠(BC,BX) = ∠(BY,BC), ∠(AB,BC) = ∠(BX,BY)

AR_CONSEQUENCES_USECASES: list[ArCase] = [
    ArCase(
        id="atable",
        problem="a b c = triangle a b c; x = angle_bisector x a b c; y = angle_mirror y x b c",
        expected_ar_new_predicates=(
            ("eqangle", "a", "b", "b", "x", "b", "c", "b", "y"),
            ("eqangle", "a", "b", "b", "c", "b", "x", "b", "y"),
        ),
    ),
    ArCase(
        id="ieq_triangle",
        problem="a b c = ieq_triangle a b c; x = angle_bisector x a b c; y = angle_mirror y x b a",
        expected_ar_new_predicates=(
            ("perp", "a", "c", "b", "x"),
            ("perp", "b", "c", "b", "y"),
        ),
    ),
    ArCase(
        id="on_aline",
        problem="a b = segment a b; x = free x; y = on_aline y b a x a b",
        expected_ar_new_predicates=(("para", "a", "x", "b", "y"),),
    ),
    ArCase(
        id="aconst",
        problem="a b = segment a b; c = s_angle a b c 30o; d = s_angle c b d 15o",
        expected_ar_new_predicates=(
            ("aconst", "a", "b", "b", "d", "1pi/4"),
            ("aconst", "b", "d", "a", "b", "3pi/4"),
            ("aconst", "b", "c", "a", "b", "5pi/6"),
            ("aconst", "b", "d", "b", "c", "11pi/12"),
        ),
    ),
    ArCase(
        id="rtable",
        problem="a b c = triangle a b c; d = free d; e f g = triangle e f g;"
        " h = eqratio h a b c d e f g; x y z = triangle x y z; w = eqratio w g h e f x y z",
        expected_ar_new_predicates=(
            ("eqratio", "a", "b", "c", "d", "w", "z", "x", "y"),
            ("eqratio", "a", "b", "e", "f", "c", "d", "g", "h"),
            ("eqratio", "a", "b", "w", "z", "c", "d", "x", "y"),
            ("eqratio", "e", "f", "w", "z", "g", "h", "x", "y"),
        ),
    ),
    ArCase(
        id="eqdistance",
        problem="a b = segment a b; c = eqdistance c a a b; d = eqratio d a b a c a c a",
        expected_ar_new_predicates=(
            ("cong", "a", "b", "a", "d"),
            ("cong", "a", "c", "a", "d"),
        ),
    ),
    ArCase(
        id="trisegment",
        problem="a b = segment a b; x y = trisegment x y a b",
        expected_ar_new_predicates=(
            # Congruences
            ("cong", "b", "y", "a", "x"),
            ("cong", "a", "x", "b", "y"),
            ("cong", "a", "y", "b", "x"),
            ("cong", "b", "x", "a", "y"),
            ("rconst", "a", "x", "x", "y", "1/1"),
            ("rconst", "x", "y", "a", "x", "1/1"),
            ("rconst", "b", "y", "x", "y", "1/1"),
            ("rconst", "x", "y", "b", "y", "1/1"),
            ("rconst", "b", "y", "a", "x", "1/1"),
            ("rconst", "a", "x", "b", "y", "1/1"),
            ("rconst", "a", "y", "b", "x", "1/1"),
            ("rconst", "b", "x", "a", "y", "1/1"),
            # Constant ratios
            ("rconst", "a", "b", "x", "y", "3/1"),
            ("rconst", "a", "b", "b", "y", "3/1"),
            ("rconst", "x", "y", "a", "b", "1/3"),
            ("rconst", "a", "b", "a", "x", "3/1"),
            ("rconst", "b", "y", "a", "b", "1/3"),
            ("rconst", "b", "x", "x", "y", "2/1"),
            ("rconst", "b", "x", "a", "x", "2/1"),
            ("rconst", "a", "x", "b", "x", "1/2"),
            ("rconst", "b", "x", "b", "y", "2/1"),
            ("rconst", "b", "x", "a", "b", "2/3"),
            ("rconst", "a", "b", "b", "x", "3/2"),
            ("rconst", "a", "y", "x", "y", "2/1"),
            ("rconst", "a", "y", "a", "x", "2/1"),
            ("rconst", "a", "y", "b", "y", "2/1"),
            ("rconst", "b", "y", "a", "y", "1/2"),
            ("rconst", "a", "y", "a", "b", "2/3"),
            ("rconst", "a", "b", "a", "y", "3/2"),
        ),
    ),
    ArCase(
        id="lconst",
        problem="a = free a; b = lconst b a 4; c = free c; d = eqdistance d c a b",
        expected_ar_new_predicates=(("lconst", "d", "c", "4"),),
    ),
]


# TODO: re-enable this test when AR is ran each level again
@pytest.mark.skip("Skipping for now AR is not ran each level")
@pytest.mark.parametrize(
    argnames="case",
    argvalues=AR_CONSEQUENCES_USECASES,
    ids=[case.id for case in AR_CONSEQUENCES_USECASES],
)
def test_ar_predicates_in_dependency_hypergraph(case: ArCase):
    match_logger = logging.getLogger("newclid.match_theorems")
    match_logger.setLevel(logging.INFO)

    problem = case.problem
    rng = np.random.default_rng(42)
    problem_setup = JGEXProblemBuilder(rng).with_problem_from_txt(problem).build()
    solver = GeometricSolverBuilder(rng).build(problem_setup)
    solver.run()

    expected_goals_constructions = [
        PredicateConstruction.from_tuple(tokens)
        for tokens in case.expected_ar_new_predicates
    ]
    expected_goals = [
        predicate_from_construction(
            construction, points_registry=solver.proof_state.symbols.points
        )
        for construction in expected_goals_constructions
    ]
    expected_goals = [g for g in expected_goals if g is not None]
    goal_predicates = set([g.predicate_type for g in expected_goals])
    goals_constructions = [predicate_to_construction(g) for g in expected_goals]

    try:
        all_predicates_found_by_ar = [
            stmt
            for stmt, dep in solver.proof_state.graph.hyper_graph.items()
            if dep.dependency_type == JustificationType.AR_DEDUCTION
            and stmt.predicate_type in goal_predicates
        ]
        assert set(all_predicates_found_by_ar) == set(expected_goals)

        justifications_for_expected_goals = goals_justifications(
            expected_goals, solver.proof_state
        )
        assert len(justifications_for_expected_goals) > 0
        print(solver.proof(goals_constructions=goals_constructions))
    finally:
        for stmt, justification in solver.proof_state.graph.hyper_graph.items():
            print(stmt, justification)

        ar_deductor = solver.proof_state.deductors[0]
        assert isinstance(ar_deductor, SympyARDeductor)
        print("RTABLE:")
        print(ar_deductor.rtable.inner_table.v2e.keys())  # type: ignore
        print("ATABLE:")
        print(ar_deductor.atable.inner_table.v2e.keys())  # type: ignore


def test_ar_world_hardest_problem_vertex():
    rng = np.random.default_rng(998244353)
    problem_setup = (
        JGEXProblemBuilder(rng)
        .with_problem_from_txt(
            "a b = segment a b; "
            "o = s_angle b a o 70o, s_angle a b o 120o; "
            "c = s_angle o a c 10o, s_angle o b c 160o; "
            "d = on_line d o b, on_line d c a; "
            "e = on_line e o a, on_line e c b; "
            "f = on_pline f d a b, on_line f b c; "
            "g = on_line g f a, on_line g d b "
            "? aconst c a c b 1pi/9"
        )
        .build()
    )
    success = GeometricSolverBuilder(rng).build(problem_setup).run()
    assert success


def test_ar_ratio_hallucination():
    rng = np.random.default_rng(998244353)
    problem_setup = (
        JGEXProblemBuilder(rng)
        .with_problem_from_txt(
            "a b e = triangle12 a b e; c = midpoint c a e ? cong a c a b"
        )
        .build()
    )
    success = GeometricSolverBuilder(rng).build(problem_setup).run()
    assert success
