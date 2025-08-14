import logging

import numpy as np
from newclid.api import GeometricSolverBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder

LOGGER = logging.getLogger(__name__)


def test_can_write_partial_proof():
    problem_txt = (
        "a b c = triangle a b c"
        "; d = angle_bisector d b a c"
        "; e = on_aline e d a d c b, on_line e a c"
        "; f = on_aline f d a d b c, on_line f a b"
        "; x = on_bline x b c, on_line x a c"
        "; o1 = circle o1 a d c"
        "; o2 = circle o2 e x d"
        "; y = on_line y e f, on_line y b c"
        " ? eqangle c x b c b c b x"
        "; coll o1 o2 y"
    )
    rng = np.random.default_rng(42)
    problem_builder = JGEXProblemBuilder(rng=rng).with_problem_from_txt(problem_txt)
    solver = GeometricSolverBuilder(rng=rng).build(problem_builder.build())
    solver.run()
    assert solver.run_infos is not None
    assert solver.run_infos.success_per_goal["∠(BC,BX) = ∠(CX,BC) succeeded"]
    assert not solver.run_infos.success_per_goal["O₁, O₂, Y are collinear succeeded"]
    partial_proof = solver.proof()
    LOGGER.debug(partial_proof)
    assert "∠(BC,BX) = ∠(CX,BC) : Proved [C0]" in partial_proof
    assert "O₁, O₂, Y are collinear : Could not prove" in partial_proof


def test_circle_merge_is_written():
    problem_txt = (
        "a b c = triangle a b c"
        "; m = midpoint m a b"
        "; n = midpoint n b c"
        "; p = midpoint p a c"
        "; f1 = foot f1 a b c"
        "; f2 = foot f2 b a c"
        "; f3 = foot f3 c a b"
        " ? cyclic m n p f1 f2 f3"
    )
    rng = np.random.default_rng(42)
    problem_builder = JGEXProblemBuilder(rng=rng).with_problem_from_txt(problem_txt)
    solver = GeometricSolverBuilder(rng=rng).build(problem_builder.build())
    success = solver.run()
    assert success
    assert solver.run_infos is not None
    partial_proof = solver.proof()
    LOGGER.debug(partial_proof)
    assert "Circle merge" in partial_proof
