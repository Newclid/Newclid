"""Definitions of free points in a specific formation or figure."""

from newclid.jgex.clause import JGEXClause
from newclid.jgex.constructions._index import JGEXConstructionName
from newclid.jgex.definition import JGEXDefinition, SketchConstruction, v
from newclid.jgex.sketch import (
    sketch_acute_triangle,
    sketch_between,
    sketch_eq_quadrangle,
    sketch_eqdia_quadrangle,
    sketch_free,
    sketch_function_name,
    sketch_ieq_triangle,
    sketch_iso_trapezoid,
    sketch_isos,
    sketch_isquare,
    sketch_pentagon,
    sketch_quadrangle,
    sketch_r_trapezoid,
    sketch_r_triangle,
    sketch_rectangle,
    sketch_risos,
    sketch_segment,
    sketch_trapezoid,
    sketch_triangle,
    sketch_triangle12,
)

# 1 Point
FREE = JGEXDefinition(
    name=JGEXConstructionName.FREE,
    args=(v("a"),),
    rely_on_points={v("a"): ()},
    requirements=JGEXClause.from_str("")[0],
    clauses=(),
    sketches=(
        SketchConstruction(name=sketch_function_name(sketch_free.__name__), args=()),
    ),
    input_points=(),
    output_points=(v("a"),),
)

# 2 Points
SEGMENT = JGEXDefinition(
    name=JGEXConstructionName.SEGMENT,
    args=(v("a"), v("b")),
    rely_on_points={},
    requirements=JGEXClause.from_str("")[0],
    clauses=(),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_segment.__name__),
            args=(),
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b")),
)

BETWEEN = JGEXDefinition(
    name=JGEXConstructionName.BETWEEN,
    args=(v("c"), v("a"), v("b")),
    rely_on_points={},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("coll a b c, obtuse_angle a c b"),
    sketches=(
        SketchConstruction(name=sketch_function_name(sketch_between.__name__), args=()),
    ),
    input_points=(),
    output_points=(v("c"), v("a"), v("b")),
)


# 3 Points
TRIANGLE = JGEXDefinition(
    name=JGEXConstructionName.TRIANGLE,
    args=(v("a"), v("b"), v("c")),
    rely_on_points={},
    requirements=JGEXClause.from_str("")[0],
    clauses=(),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_triangle.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c")),
)

R_TRIANGLE = JGEXDefinition(
    name=JGEXConstructionName.R_TRIANGLE,
    args=(v("a"), v("b"), v("c")),
    rely_on_points={v("c"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("perp a b a c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_r_triangle.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c")),
)

ACUTE_TRIANGLE = JGEXDefinition(
    name=JGEXConstructionName.ACUTE_TRIANGLE,
    args=(v("a"), v("b"), v("c")),
    rely_on_points={},
    requirements=JGEXClause.from_str("")[0],
    clauses=(),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_acute_triangle.__name__),
            args=(),
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c")),
)


ISO_TRIANGLE = JGEXDefinition(
    name=JGEXConstructionName.ISO_TRIANGLE,
    args=(v("a"), v("b"), v("c")),
    rely_on_points={v("c"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("eqangle b a b c c b c a, cong a b a c"),
    sketches=(
        SketchConstruction(name=sketch_function_name(sketch_isos.__name__), args=()),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c")),
)


ISO_TRIANGLE0 = JGEXDefinition(
    name=JGEXConstructionName.ISO_TRIANGLE0,
    args=(v("a"), v("b"), v("c")),
    rely_on_points={v("c"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("cong a b a c"),
    sketches=(
        SketchConstruction(name=sketch_function_name(sketch_isos.__name__), args=()),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c")),
)


IEQ_TRIANGLE = JGEXDefinition(
    name=JGEXConstructionName.IEQ_TRIANGLE,
    args=(v("a"), v("b"), v("c")),
    rely_on_points={v("c"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str(
        "cong a b b c, cong b c c a; eqangle a b a c c a c b, eqangle c a c b b c b a"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_ieq_triangle.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c")),
)

TRIANGLE12 = JGEXDefinition(
    name=JGEXConstructionName.TRIANGLE12,
    args=(v("a"), v("b"), v("c")),
    rely_on_points={v("c"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("rconst a b a c 1/2"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_triangle12.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c")),
)

RISOS = JGEXDefinition(
    name=JGEXConstructionName.RISOS,
    args=(v("a"), v("b"), v("c")),
    rely_on_points={v("c"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("perp a b a c, cong a b a c; eqangle b a b c c b c a"),
    sketches=(
        SketchConstruction(name=sketch_function_name(sketch_risos.__name__), args=()),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c")),
)

TRIANGLE_CONSTRUCTIONS = [
    TRIANGLE,
    R_TRIANGLE,
    ACUTE_TRIANGLE,
    ISO_TRIANGLE,
    ISO_TRIANGLE0,
    IEQ_TRIANGLE,
    TRIANGLE12,
    RISOS,
]

# 4 Points
QUADRANGLE = JGEXDefinition(
    name=JGEXConstructionName.QUADRANGLE,
    args=(v("a"), v("b"), v("c"), v("d")),
    rely_on_points={},
    requirements=JGEXClause.from_str("")[0],
    clauses=(),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_quadrangle.__name__),
            args=(),
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c"), v("d")),
)


RECTANGLE = JGEXDefinition(
    name=JGEXConstructionName.RECTANGLE,
    args=(v("a"), v("b"), v("c"), v("d")),
    rely_on_points={v("c"): (v("a"), v("b")), v("d"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str(
        "c : perp a b b c ; d : para a b c d, para a d b c; perp a b a d, cong a b c d, cong a d b c, cong a c b d"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_rectangle.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c"), v("d")),
)


ISQUARE = JGEXDefinition(
    name=JGEXConstructionName.ISQUARE,
    args=(v("a"), v("b"), v("c"), v("d")),
    rely_on_points={v("c"): (v("a"), v("b")), v("d"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str(
        "c : perp a b b c, cong a b b c; d : para a b c d, para a d b c; perp a d d c, cong b c c d, cong c d d a, perp a c b d, cong a c b d"
    ),
    sketches=(
        SketchConstruction(name=sketch_function_name(sketch_isquare.__name__), args=()),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c"), v("d")),
)


TRAPEZOID = JGEXDefinition(
    name=JGEXConstructionName.TRAPEZOID,
    args=(v("a"), v("b"), v("c"), v("d")),
    rely_on_points={v("d"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("para a b c d"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_trapezoid.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c"), v("d")),
)

R_TRAPEZOID = JGEXDefinition(
    name=JGEXConstructionName.R_TRAPEZOID,
    args=(v("a"), v("b"), v("c"), v("d")),
    rely_on_points={v("d"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("para a b c d, perp a b a d"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_r_trapezoid.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c"), v("d")),
)


ISO_TRAPEZOID = JGEXDefinition(
    name=JGEXConstructionName.ISO_TRAPEZOID,
    args=(v("a"), v("b"), v("c"), v("d")),
    rely_on_points={v("d"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("para d c a b, cong d a b c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_iso_trapezoid.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c"), v("d")),
)


EQ_QUADRANGLE = JGEXDefinition(
    name=JGEXConstructionName.EQ_QUADRANGLE,
    args=(v("a"), v("b"), v("c"), v("d")),
    rely_on_points={v("d"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("cong d a b c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_eq_quadrangle.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c"), v("d")),
)

EQDIA_QUADRANGLE = JGEXDefinition(
    name=JGEXConstructionName.EQDIA_QUADRANGLE,
    args=(v("a"), v("b"), v("c"), v("d")),
    rely_on_points={v("d"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("cong d b a c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_eqdia_quadrangle.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c"), v("d")),
)

QUADRANGLE_CONSTRUCTIONS = [
    QUADRANGLE,
    RECTANGLE,
    ISQUARE,
    TRAPEZOID,
    R_TRAPEZOID,
    ISO_TRAPEZOID,
    EQ_QUADRANGLE,
    EQDIA_QUADRANGLE,
]


# 5 Points
PENTAGON = JGEXDefinition(
    name=JGEXConstructionName.PENTAGON,
    args=(v("a"), v("b"), v("c"), v("d"), v("e")),
    rely_on_points={},
    requirements=JGEXClause.from_str("")[0],
    clauses=(),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_pentagon.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c"), v("d"), v("e")),
)


FREE_CONSTRUCTIONS = (
    [FREE, SEGMENT, BETWEEN, PENTAGON]
    + TRIANGLE_CONSTRUCTIONS
    + QUADRANGLE_CONSTRUCTIONS
)
