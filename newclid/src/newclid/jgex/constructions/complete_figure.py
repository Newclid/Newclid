"""Definitions that will add points in order to complete a geometric figure"""

from newclid.jgex.clause import JGEXClause
from newclid.jgex.constructions._index import JGEXConstructionName
from newclid.jgex.definition import JGEXDefinition, SketchConstruction, v
from newclid.jgex.sketch import (
    sketch_bline,
    sketch_centroid,
    sketch_circle,
    sketch_function_name,
    sketch_isosvertex,
    sketch_pline,
    sketch_rotaten90,
    sketch_rotatep90,
    sketch_square,
)

ISO_TRIANGLE_VERTEX = JGEXDefinition(
    name=JGEXConstructionName.ISO_TRIANGLE_VERTEX,
    args=(v("x"), v("b"), v("c")),
    rely_on_points={v("x"): (v("b"), v("c"))},
    requirements=JGEXClause.from_str("diff b c")[0],
    clauses=JGEXClause.from_str("cong x b x c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_isosvertex.__name__),
            args=(v("b"), v("c")),
        ),
    ),
    input_points=(v("b"), v("c")),
    output_points=(v("x"),),
)
ISO_TRIANGLE_VERTEX_ANGLE = JGEXDefinition(
    name=JGEXConstructionName.ISO_TRIANGLE_VERTEX_ANGLE,
    args=(v("x"), v("b"), v("c")),
    rely_on_points={v("x"): (v("b"), v("c"))},
    requirements=JGEXClause.from_str("diff b c")[0],
    clauses=JGEXClause.from_str("eqangle x b b c b c x c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_isosvertex.__name__),
            args=(v("b"), v("c")),
        ),
    ),
    input_points=(v("b"), v("c")),
    output_points=(v("x"),),
)

EQ_TRIANGLE = JGEXDefinition(
    name=JGEXConstructionName.EQ_TRIANGLE,
    args=(v("x"), v("b"), v("c")),
    rely_on_points={v("x"): (v("b"), v("c"))},
    requirements=JGEXClause.from_str("diff b c")[0],
    clauses=JGEXClause.from_str(
        "cong x b b c, cong b c c x; eqangle b x b c c b c x, eqangle x c x b b x b c"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_circle.__name__),
            args=(v("b"), v("b"), v("c")),
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_circle.__name__),
            args=(v("c"), v("b"), v("c")),
        ),
    ),
    input_points=(v("b"), v("c")),
    output_points=(v("x"),),
)

ISO_TRAPEZOID2 = JGEXDefinition(
    name=JGEXConstructionName.ISO_TRAPEZOID2,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str("cong x b a c, cong x a b c"),
    sketches=(
        SketchConstruction(name="iso_trapezoid2", args=(v("a"), v("b"), v("c"))),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)

PARALLELOGRAM = JGEXDefinition(
    name=JGEXConstructionName.PARALLELOGRAM,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str(
        "para a b c x, para a x b c; cong a b c x, cong a x b c"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_pline.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_pline.__name__),
            args=(v("c"), v("a"), v("b")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)

SQUARE = JGEXDefinition(
    name=JGEXConstructionName.SQUARE,
    args=(v("x"), v("y"), v("a"), v("b")),
    rely_on_points={v("x"): (v("a"), v("b")), v("y"): (v("a"), v("b"), v("x"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str(
        "x : perp a b b x, cong a b b x; y : para a b x y, para a y b x; perp a y y x, cong b x x y, cong x y y a, perp a x b y, cong a x b y"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_square.__name__), args=(v("a"), v("b"))
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"), v("y")),
)


CIRCLE = JGEXDefinition(
    name=JGEXConstructionName.CIRCLE,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str("circle x a b c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_bline.__name__), args=(v("a"), v("b"))
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_bline.__name__), args=(v("a"), v("c"))
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)

CIRCUMCENTER = JGEXDefinition(
    name=JGEXConstructionName.CIRCUMCENTER,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str("cong x a x b, cong x b x c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_bline.__name__), args=(v("a"), v("b"))
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_bline.__name__), args=(v("a"), v("c"))
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)

PSQUARE = JGEXDefinition(
    name=JGEXConstructionName.PSQUARE,
    args=(v("x"), v("a"), v("b")),
    rely_on_points={v("x"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("cong x a a b, perp x a a b"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_rotatep90.__name__), args=(v("a"), v("b"))
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"),),
)


NSQUARE = JGEXDefinition(
    name=JGEXConstructionName.NSQUARE,
    args=(v("x"), v("a"), v("b")),
    rely_on_points={v("x"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("cong x a a b, perp x a a b"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_rotaten90.__name__),
            args=(v("a"), v("b")),
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"),),
)

CENTROID = JGEXDefinition(
    name=JGEXConstructionName.CENTROID,
    args=(v("x"), v("y"), v("z"), v("i"), v("a"), v("b"), v("c")),
    rely_on_points={
        v("x"): (v("b"), v("c")),
        v("y"): (v("c"), v("a")),
        v("z"): (v("a"), v("b")),
        v("i"): (v("a"), v("x"), v("b"), v("y")),
    },
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str(
        "x : coll x b c, cong x b x c; y : coll y c a, cong y c y a; z : coll z a b, cong z a z b; i : coll a x i, coll b y i; coll c z i"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_centroid.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


COMPLETE_FORM_CONSTRUCTIONS = [
    ISO_TRIANGLE_VERTEX,
    ISO_TRIANGLE_VERTEX_ANGLE,
    EQ_TRIANGLE,
    ISO_TRAPEZOID2,
    PARALLELOGRAM,
    SQUARE,
    CIRCLE,
    CIRCUMCENTER,
    PSQUARE,
    NSQUARE,
    CENTROID,
]
