from enum import Enum

"""
Definitions are used in the translation of a problem to a JGEX string to create the coordinates of the points and add the hypothesis predicates to the problem. They correspond to geometric constructions.

Each definition is an instance of the JGEXDefinition class, and it receives the following arguments:

- `name`: The name of the construction, which is the syntax for using it in the JGEX string.
- `args`: The points that the construction requires as arguments, in the order to be declared in the JGEX string.
- `rely_on_points`: Registers the logical dependency between one or many output points and other arguments of the construction.
- `requirements`: A list of numerical predicates that must be satisfied by the input points for the construction to be attempted.
- `clauses`: The list of predicate hypothesis that will be added to the problem by the definition.
- `sketches`: The name of the sketch function called by the definition with its arguments, which creates coordinates for the points given by the definition.
- `input_points`: The previously existing points that the construction requires as input.
- `output_points`: The points that the construction will create as output.

For example in:

ON_CIRCLE = JGEXDefinition(
    name=JGEXConstructionName.ON_CIRCLE,
    args=(v("x"), v("o"), v("a")),
    rely_on_points={v("x"): (v("o"), v("a"))},
    requirements=JGEXClause.from_str("diff o a")[0],
    clauses=JGEXClause.from_str("cong o x o a"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_circle.__name__),
            args=(v("o"), v("o"), v("a")),
        ),
    ),
    input_points=(v("o"), v("a")),
    output_points=(v("x"),),
)

The name, to be found in the JGEXConstructionName enum below, is on_circle. The args are x, o, a (typed as variables).

As x is the output point, and o, a, are input points, the definition would occur in a JGEX string as:

    x = on_circle x o a

o, a should be defined beforehand. The requirement says the engine will check if o, a are distinct points before attempting the construction. If succeeded, the clauses say the hypothesis

    cong o x o a

will be added to the problem.

To get the coordinates of x, the sketch function sketch_circle will be called with the arguments o, o, a.


This file contains the JGEXConstructionName class, which lists all the definitions that can be currently used, separated by categories. The left hand side gives the name of the instance of the definition in the code, while the right hand side gives the syntax to be used in the JGEX string.
"""


class JGEXConstructionName(str, Enum):
    # Free constructions
    FREE = "free"
    SEGMENT = "segment"
    BETWEEN = "between"
    TRIANGLE = "triangle"
    R_TRIANGLE = "r_triangle"
    ACUTE_TRIANGLE = "acute_triangle"
    ISO_TRIANGLE = "iso_triangle"
    ISO_TRIANGLE0 = "iso_triangle0"
    IEQ_TRIANGLE = "ieq_triangle"
    RISOS = "risos"
    TRIANGLE12 = "triangle12"
    QUADRANGLE = "quadrangle"
    RECTANGLE = "rectangle"
    ISQUARE = "isquare"
    TRAPEZOID = "trapezoid"
    R_TRAPEZOID = "r_trapezoid"
    ISO_TRAPEZOID = "iso_trapezoid"
    EQ_QUADRANGLE = "eq_quadrangle"
    EQDIA_QUADRANGLE = "eqdia_quadrangle"
    PENTAGON = "pentagon"

    # Point on object constructions
    ON_LINE = "on_line"
    ON_PARA_LINE = "on_pline"
    ON_PARA_LINE0 = "on_pline0"
    ON_PERP_LINE = "on_tline"
    ON_ALINE = "on_aline"
    ON_ALINE0 = "on_aline0"
    ON_BLINE = "on_bline"
    ON_CIRCLE = "on_circle"
    ON_CIRCUM = "on_circum"
    ON_DIA = "on_dia"

    # Intersection constructions
    INTERSECTION_LINE_LINE = "intersection_ll"
    INTERSECTION_LINE_PARA = "intersection_lp"
    INTERSECTION_PARA_PARA = "intersection_pp"
    INTERSECTION_LINE_PERP = "intersection_lt"
    INTERSECTION_PERP_PERP = "intersection_tt"
    INTERSECTION_LINE_CIRCLE = "intersection_lc"
    INTERSECTION_CIRCLE_CIRCLE = "intersection_cc"

    # Tangent constructions
    TANGENT = "tangent"
    LINE_CIRCLE_TANGENT = "lc_tangent"
    CIRCLE_CIRCLE_TANGENT = "cc_tangent"
    CIRCLE_CIRCLE_ITANGENT = "cc_itangent"

    # Relative to other constructions
    ANGLE_BISECTOR = "angle_bisector"
    ANGLE_MIRROR = "angle_mirror"
    EQDISTANCE = "eqdistance"
    FOOT = "foot"
    INCENTER = "incenter"
    INCENTER2 = "incenter2"
    EXCENTER = "excenter"
    EXCENTER2 = "excenter2"
    MIDPOINT = "midpoint"
    MIRROR = "mirror"
    ORTHOCENTER = "orthocenter"
    REFLECT = "reflect"
    SHIFT = "shift"
    TRISECT = "trisect"
    TRISEGMENT = "trisegment"
    BETWEEN_BOUND = "between_bound"

    # Complete figure constructions
    ISO_TRIANGLE_VERTEX = "iso_triangle_vertex"
    ISO_TRIANGLE_VERTEX_ANGLE = "iso_triangle_vertex_angle"
    EQ_TRIANGLE = "eq_triangle"
    ISO_TRAPEZOID2 = "iso_trapezoid2"
    PARALLELOGRAM = "parallelogram"
    SQUARE = "square"
    CIRCLE = "circle"
    CIRCUMCENTER = "circumcenter"
    PSQUARE = "psquare"
    NSQUARE = "nsquare"
    CENTROID = "centroid"

    # Predicate prescriptions
    ACONST = "aconst"
    S_ANGLE = "s_angle"
    EQANGLE2 = "eqangle2"
    EQANGLE3 = "eqangle3"
    RCONST = "rconst"
    RCONST2 = "rconst2"
    R2CONST = "r2const"
    EQRATIO = "eqratio"
    EQRATIO6 = "eqratio6"
    LCONST = "lconst"
    L2CONST = "l2const"
    SIMTRI = "simtri"
    SIMTRIR = "simtrir"
    CONTRI = "contri"
    CONTRIR = "contrir"

    # Problem specific constructions
    TWOL1C = "2l1c"
    E5128 = "e5128"
    THREEPEQ = "3peq"
    TEST_R20 = "test_r20"
    TEST_R25 = "test_r25"
    NINEPOINTS = "ninepoints"
