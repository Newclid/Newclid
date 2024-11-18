from newclid.agent.breadth_first_search import BFSDDAR

import pytest
import pytest_check as check

from newclid.api import GeometricSolverBuilder
from tests.fixtures import build_until_works


def test_ar_world_hardest_problem_vertex():
    solver = build_until_works(
        GeometricSolverBuilder()
        .load_problem_from_txt(
            "a b = segment a b; "
            "o = s_angle b a o 70o, s_angle a b o 120o; "
            "c = s_angle o a c 10o, s_angle o b c 160o; "
            "d = on_line d o b, on_line d c a; "
            "e = on_line e o a, on_line e c b; "
            "f = on_pline f d a b, on_line f b c; "
            "g = on_line g f a, on_line g d b "
            "? aconst c b c a 1pi/9"
        )
        .with_deductive_agent(BFSDDAR())
    )

    success = solver.run()
    check.is_true(success)


@pytest.mark.xfail
def test_ar_ratio_hallucination():
    solver = build_until_works(
        GeometricSolverBuilder()
        .load_problem_from_txt(
            "a b e = triangle12 a b e; c = midpoint c a e ? cong a c a b"
        )
        .with_deductive_agent(BFSDDAR())
    )

    success = solver.run()
    check.is_true(success)
