import logging

import numpy as np
import pytest
from newclid.all_rules import (
    R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES,
    R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES,
    R77_CONGRUENT_TRIANGLES_DIRECT_PROPERTIES,
    R78_CONGRUENT_TRIANGLES_REVERSE_PROPERTIES,
)
from newclid.api import GeometricSolverBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


TEST_CASES = [
    (
        "simtri_no_rep",
        R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES,
        "a b c = triangle a b c; p q = segment p q; r = simtri r a b c p q ? eqangle b a b c q p q r; eqangle a b a c p q p r; eqangle a c b c p r q r; eqratio b a b c q p q r; eqratio b c a c q r p r",
    ),
    (
        "simtri_a=p",
        R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES,
        "a b c = triangle a b c; q = free q; r = simtri r a b c a q ? eqangle b a b c q a q r; eqangle a b a c a q a r; eqangle a c b c a r q r; eqratio b a b c q a q r; eqratio b c a c q r a r",
    ),
    (
        "simtri_a=q",
        R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES,
        "a b c = triangle a b c; p =free p; r = simtri r a b c p a ? eqangle b a b c a p a r; eqangle a b a c p a p r; eqangle a c b c p r a r; eqratio b a b c a p a r; eqratio b c a c a r p r",
    ),
    (
        "simtri_a=r",
        R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES,
        "a b c = triangle a b c; q = free q; p = simtri p b c a q a ? eqangle b a b c q p q a; eqangle a b a c p q p a; eqangle a c b c p a q a; eqratio b a b c q p q a; eqratio b c a c q a p a",
    ),
    (
        "simtri_a=q_b=r",
        R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES,
        "a b c = triangle a b c; p = simtri p b c a a b ? eqangle b a b c a p a b; eqangle a b a c p a p b; eqangle a c b c p b a b; eqratio b a b c a p a b; eqratio b c a c a b p b",
    ),
    (
        "simtrir_no_rep",
        R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES,
        "a b c = triangle a b c; p q = segment p q; r = simtrir r a b c p q ? eqangle b a b c q r q p; eqangle a b a c p r p q; eqangle a c b c q r p r; eqratio b a b c q p q r; eqratio b c a c q r p r",
    ),
    (
        "simtrir_a=p",
        R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES,
        "a b c = triangle a b c; q = free q; r = simtrir r a b c a q ? eqangle b a b c q r q a; eqangle a b a c a r a q; eqangle a c b c q r a r; eqratio b a b c q a q r; eqratio b c a c q r a r",
    ),
    (
        "simtrir_a=p_b=q",
        R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES,
        "a b c = triangle a b c; r = simtrir r a b c a b ? eqangle b a b c b r b a; eqangle a b a c a r a b; eqangle a c b c b r a r; eqratio b a b c b a b r; eqratio b c a c b r a r",
    ),
    (
        "contri_no_rep",
        R77_CONGRUENT_TRIANGLES_DIRECT_PROPERTIES,
        "a b c = triangle a b c; p = free p; q r = contri q r a b c p ? simtri a b c p q r; cong a b p q",
    ),
    (
        "contri_a=p",
        R77_CONGRUENT_TRIANGLES_DIRECT_PROPERTIES,
        "a b c = triangle a b c; q r = contri q r a b c a ? simtri a b c a q r; cong a b a q",
    ),
    (
        "contrir_no_rep",
        R78_CONGRUENT_TRIANGLES_REVERSE_PROPERTIES,
        "a b c = triangle a b c; p = free p; q r = contrir q r a b c p ? simtrir a b c p q r; cong a b p q",
    ),
    (
        "contrir_a=p",
        R78_CONGRUENT_TRIANGLES_REVERSE_PROPERTIES,
        "a b c = triangle a b c; q r = contrir q r a b c a ? simtrir a b c a q r; cong a b a q",
    ),
]

TEST_CASE_NAMES = [rule[0] for rule in TEST_CASES]
assert len(TEST_CASE_NAMES) == len(set(TEST_CASE_NAMES)), (
    "There are duplicate case names"
)


@pytest.mark.parametrize("case_name", TEST_CASE_NAMES)
def test_triangle_case(case_name: str):
    _, rule, problem_txt = TEST_CASES[TEST_CASE_NAMES.index(case_name)]
    LOGGER.info(f"Testing case {case_name} with problem {problem_txt} and rule {rule}")
    rng = np.random.default_rng(123)
    solver_builder = GeometricSolverBuilder(rng=rng).with_rules([rule])
    problem_builder = JGEXProblemBuilder(rng=rng).with_problem_from_txt(problem_txt)
    solver = solver_builder.build(problem_builder.build())
    success = solver.run()
    assert success
