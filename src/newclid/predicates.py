from enum import Enum


class Predicate(Enum):
    COLLINEAR = "coll"
    """coll A B C - True if the 3 (or more) points in the arguments are collinear."""
    COLLINEAR_X = "collx"
    PARALLEL = "para"
    """para A B C D - True if the line AB is parallel to the line CD."""
    PERPENDICULAR = "perp"
    """perp A B C D - True if the line AB is perpendicular to the line CD. A perp statement will add the corresponding 90-degree angle statement as well."""
    MIDPOINT = "midp"
    """midp M A B - True if the M is the midpoint of the segment AB. Can be equivalent to coll M A B + cong A M B M."""
    CONGRUENT = "cong"
    """cong A B C D - True if segments AB and CD are congruent."""
    CONGRUENT_2 = "cong2"
    CIRCLE = "circle"
    """circle O A B C - True if O is the center of the circle through A, B, and C (circumcenter of triangle ABC). Can be equivalent to cong O A O B + cong O A O C, and equivalent pairs of congruences."""
    CYCLIC = "cyclic"
    """cyclic A B C D - True if the 4 (or more) points in the arguments lie on the same circle."""
    EQANGLE = "eqangle"
    """eqangle A B C D E F G H - True if one can rigidly move the crossing of lines AB and CD to get on top of the crossing of EF and GH, respectively (no reflections allowed). In particular, eqangle A B C D C D A B is only true if AB is perpendicular to CD."""
    EQANGLE6 = "eqangle6"
    EQRATIO = "eqratio"
    """eqratio A B C D E F G H - True if AB/CD=EF/GH, as ratios between lengths of segments."""
    EQRATIO6 = "eqratio6"
    EQRATIO3 = "eqratio3"
    """eqratio3 A B C D M N - True in an instance of Thales theorem which has AB//MN//CD. It adds the corresponding eqratios to MA/MC=NB/ND, AM/AC=BN/BD, and MC/AC=ND/BD. See _add_eqratio3 in adder.py."""
    EQRATIO4 = "eqratio4"
    SIMILAR_TRIANGLE = "simtri"
    """simtri A B C P Q R - True if triangles ABC and PQR are similar under orientation-preserving transformations taking A to P, B to Q and C to R. It is equivalent to the three eqangle and eqratio predicates on the corresponding angles and sides."""
    SIMILAR_TRIANGLE_REFLECTED = "simtri2"
    """simtri2 A B C P Q R - True if triangle ABC is similar to a reflection of triangle PQR under orientation-preserving transformations taking A to the reflection of P, B to the reflection of Q and C to the reflection of R. It is equivalent to the three eqangle and eqratio predicates on the corresponding angles and sides."""
    SIMILAR_TRIANGLE_BOTH = "simtri*"
    """simtri* A B C P Q R - True if either simtri A B C P Q R or simtri2 A B C P Q R is true."""
    CONTRI_TRIANGLE = "contri"
    """contri A B C P Q R - True if triangles ABC and PQR are congruent under orientation-preserving transformations taking A to P, B to Q and C to R. It is equivalent to the three eqangle and cong predicates on the corresponding angles and sides."""
    CONTRI_TRIANGLE_REFLECTED = "contri2"
    """contri2 A B C P Q R - True if triangle ABC is congruent to a reflection of triangle PQR under orientation-preserving transformations taking A to the reflection of P, B to the reflection of Q and C to the reflection of R. It is equivalent to the three eqangle and cong predicates on the corresponding angles and sides."""
    CONTRI_TRIANGLE_BOTH = "contri*"
    """contri* A B C P Q R - True if either contri A B C P Q R or contri2 A B C P Q R is true."""
    CONSTANT_ANGLE = "aconst"
    """aconst A B C D r - True if the angle needed to go from line AB to line CD, around the intersection point, on the clockwise direction is r, in radians. The syntax of y should be a fraction of pi, as 2pi/3 for an angle of 120 degrees."""
    CONSTANT_RATIO = "rconst"
    """rconst A B C D r - True if AB/CD=r, r should be given with numerator and denominator separated by /, as in 2/3."""
    CONSTANT_LENGTH = "lconst"
    """rconst A B l - True if AB=l, l should be given as a float."""
    COMPUTE_ANGLE = "acompute"
    COMPUTE_RATIO = "rcompute"
    S_ANGLE = "s_angle"
    """s_angle A B C y - True if the angle ABC, with vertex at B and going counter clockwise from A to C, is y in degrees. The syntax of y should be as 123o for an angle of 123 degrees."""
    # Numericals
    SAMESIDE = "sameside"
    DIFFERENT = "diff"
    """diff A B - True is points A and B are NOT the same. It can only be numerically checked."""
    NON_COLLINEAR = "ncoll"
    """ncoll A B C - True if all the 3 (or more) points on the arguments do NOT lie on the same line. It can only be numerically checked."""
    NON_PARALLEL = "npara"
    """npara A B C D - True if lines AB and CD are NOT parallel. It can only be numerically checked (the check uses the angular coefficient of the equations of the lines)."""
    NON_PERPENDICULAR = "nperp"
    """nperp A B C D - True if lines AB and CD are NOT perpendicular."""
    # Fix_x ? What is that ?
    FIX_L = "fixl"
    FIX_C = "fixc"
    FIX_B = "fixb"
    FIX_T = "fixt"
    FIX_P = "fixp"
    # What is that also ?
    IND = "ind"
    INCI = "inci"


NUMERICAL_PREDICATES = (
    Predicate.NON_COLLINEAR,
    Predicate.NON_PARALLEL,
    Predicate.NON_PERPENDICULAR,
    Predicate.DIFFERENT,
    Predicate.SAMESIDE,
)
