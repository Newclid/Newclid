from enum import Enum


class PredicateType(str, Enum):
    DIFFERENT = "diff"
    MIDPOINT = "midp"
    COLLINEAR = "coll"
    N_COLLINEAR = "ncoll"

    PERPENDICULAR = "perp"
    N_PERPENDICULAR = "nperp"

    PARALLEL = "para"
    N_PARALLEL = "npara"

    CIRCUMCENTER = "circle"
    CYCLIC = "cyclic"

    CONSTANT_ANGLE = "aconst"
    A_COMPUTE = "acompute"
    OBTUSE_ANGLE = "obtuse_angle"

    EQUAL_ANGLES = "eqangle"

    CONSTANT_LENGTH = "lconst"
    L_COMPUTE = "lcompute"
    SQUARED_CONSTANT_LENGTH = "l2const"

    CONGRUENT = "cong"
    CONSTANT_RATIO = "rconst"
    R_COMPUTE = "rcompute"
    SQUARED_CONSTANT_RATIO = "r2const"

    EQUAL_RATIOS = "eqratio"

    SIMTRI_CLOCK = "simtri"
    SIMTRI_REFLECT = "simtrir"

    CONTRI_CLOCK = "contri"
    CONTRI_REFLECT = "contrir"

    SAME_CLOCK = "sameclock"
    SAME_SIDE = "sameside"
    N_SAME_SIDE = "nsameside"

    PYTHAGOREAN_PREMISES = "pythagorean_premises"
    PYTHAGOREAN_CONCLUSIONS = "pythagorean_conclusions"

    LENGTH_EQUATION = "lequation"
    ANGLE_EQUATION = "aequation"
