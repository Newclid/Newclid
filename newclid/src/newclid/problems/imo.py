"""JGEX problems from the International Mathematical Olympiad."""

from pydantic_core import Url

from newclid.jgex.formulation import JGEXFormulation
from newclid.problems.problem import (
    Competition,
    CompetitionIds,
    Problem,
    ProblemFormulation,
)

IMO = Competition(
    id=CompetitionIds.IMO,
    name="International Mathematical Olympiad",
    url=Url("https://www.imo-official.org/"),
)

IMO_2000_P1 = Problem(
    source=IMO,
    name="2000_p1",
    natural_language_formulation="""AB is tangent to the circles CAMN and NMBD.
M lies between C and D on the line CD, and CD is parallel to AB.
The chords NA and CM meet at P""; the chords NB and MD meet at Q.
The rays CA and DB meet at E. Prove that P E = QE.""",
    formulations=[
        ProblemFormulation(
            name="ag",
            formulation=JGEXFormulation.from_text(
                "a b = segment a b"
                "; g1 = on_tline g1 a a b"
                "; g2 = on_tline g2 b b a"
                "; m = on_circle m g1 a, on_circle m g2 b"
                "; n = on_circle n g1 a, on_circle n g2 b"
                "; c = on_pline c m a b, on_circle c g1 a"
                "; d = on_pline d m a b, on_circle d g2 b"
                "; p = on_line p a n, on_line p c d"
                "; q = on_line q b n, on_line q c d"
                "; e = on_line e a c, on_line e b d"
                " ? cong e p e q"
            ),
        )
    ],
)

IMO_2025_P2 = Problem(
    source=IMO,
    name="2025_p2",
    natural_language_formulation="""Let Ω and Γ be circles with centres Mand N, respectively, such that the radius of Ω is less than the radius of Γ.
Suppose circles Ω and Γ intersect at two distinct points A and B.
Line MN intersects Ω at C and Γ at D, such that points C, M, N and D lie on the line in that order.
Let P be the circumcentre of triangle ACD. Line AP intersects Ω again at E ≠ A.
Line AP intersects Γ again at F ≠ A.
Let H be the orthocentre of triangle PMN.
Prove that the line through H parallel to AP is tangent to the circumcircle of triangle BEF.""",
    formulations=[
        ProblemFormulation(
            name="2025_p2",
            formulation=JGEXFormulation.from_text(
                "a m n = triangle a m n"
                "; b = on_circle b m a, on_circle b n a"
                "; c = on_line c m n, on_circle c m a"
                "; d = on_line d m n, on_circle d n a"
                "; p = circle p a c d"
                "; e = on_line e a p, on_circle e m a"
                "; f = on_line f a p, on_circle f n a"
                "; h = on_tline h p m n, on_tline h m p n"
                "; o = circle o b e f"
                "; x = on_dia x o h, on_pline x h a p"
                " | w = circle w d e f"
                " ? cong o x o b"
                "; obtuse_angle c m n"
                "; obtuse_angle m n d"
            ),
        ),
    ],
)

ALL_IMO_PROBLEMS = [
    IMO_2000_P1,
    IMO_2025_P2,
]
