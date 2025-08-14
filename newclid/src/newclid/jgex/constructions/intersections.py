"""Definitions of points at the intersection/tangent of lines and circles."""

from newclid.jgex.clause import JGEXClause
from newclid.jgex.constructions._index import JGEXConstructionName
from newclid.jgex.definition import JGEXDefinition, SketchConstruction, v
from newclid.jgex.sketch import (
    sketch_cc_itangent,
    sketch_cc_tangent,
    sketch_circle,
    sketch_function_name,
    sketch_line,
    sketch_pline,
    sketch_tangent,
    sketch_tline,
)

# Line Intersections

INTERSECTION_LINE_LINE = JGEXDefinition(
    name=JGEXConstructionName.INTERSECTION_LINE_LINE,
    args=(v("x"), v("a"), v("b"), v("c"), v("d")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"), v("d"))},
    requirements=JGEXClause.from_str("npara a b c d, ncoll a b c d")[0],
    clauses=JGEXClause.from_str("x : coll x a b, coll x c d"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_line.__name__), args=(v("a"), v("b"))
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_line.__name__), args=(v("c"), v("d"))
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("d")),
    output_points=(v("x"),),
)

INTERSECTION_LINE_PARA = JGEXDefinition(
    name=JGEXConstructionName.INTERSECTION_LINE_PARA,
    args=(v("x"), v("a"), v("b"), v("c"), v("m"), v("n")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"), v("m"), v("n"))},
    requirements=JGEXClause.from_str("npara m n a b, ncoll a b c, ncoll c m n")[0],
    clauses=JGEXClause.from_str("x : coll x a b, para c x m n"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_line.__name__), args=(v("a"), v("b"))
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_pline.__name__),
            args=(v("c"), v("m"), v("n")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("m"), v("n")),
    output_points=(v("x"),),
)

INTERSECTION_PARA_PARA = JGEXDefinition(
    name=JGEXConstructionName.INTERSECTION_PARA_PARA,
    args=(v("x"), v("a"), v("b"), v("c"), v("d"), v("e"), v("f")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"), v("d"), v("e"), v("f"))},
    requirements=JGEXClause.from_str("diff a d, npara b c e f")[0],
    clauses=JGEXClause.from_str("x : para x a b c, para x d e f"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_pline.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_pline.__name__),
            args=(v("d"), v("e"), v("f")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("d"), v("e"), v("f")),
    output_points=(v("x"),),
)


INTERSECTION_LINE_PERP = JGEXDefinition(
    name=JGEXConstructionName.INTERSECTION_LINE_PERP,
    args=(v("x"), v("a"), v("b"), v("c"), v("d"), v("e")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"), v("d"), v("e"))},
    requirements=JGEXClause.from_str("ncoll a b c, nperp a b d e")[0],
    clauses=JGEXClause.from_str("x : coll x a b, perp x c d e"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_line.__name__), args=(v("a"), v("b"))
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_tline.__name__),
            args=(v("c"), v("d"), v("e")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("d"), v("e")),
    output_points=(v("x"),),
)

INTERSECTION_PERP_PERP = JGEXDefinition(
    name=JGEXConstructionName.INTERSECTION_PERP_PERP,
    args=(v("x"), v("a"), v("b"), v("c"), v("d"), v("e"), v("f")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"), v("d"), v("e"), v("f"))},
    requirements=JGEXClause.from_str("diff a d, npara b c e f")[0],
    clauses=JGEXClause.from_str("x : perp x a b c, perp x d e f"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_tline.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_tline.__name__),
            args=(v("d"), v("e"), v("f")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("d"), v("e"), v("f")),
    output_points=(v("x"),),
)

# Circle Intersections

INTERSECTION_LINE_CIRCLE = JGEXDefinition(
    name=JGEXConstructionName.INTERSECTION_LINE_CIRCLE,
    args=(v("x"), v("a"), v("o"), v("b")),
    rely_on_points={v("x"): (v("a"), v("o"), v("b"))},
    requirements=JGEXClause.from_str("diff a b, diff o b, nperp b o b a")[0],
    clauses=JGEXClause.from_str("x : coll x a b, cong o b o x"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_line.__name__), args=(v("b"), v("a"))
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_circle.__name__),
            args=(v("o"), v("o"), v("b")),
        ),
    ),
    input_points=(v("a"), v("o"), v("b")),
    output_points=(v("x"),),
)

INTERSECTION_CIRCLE_CIRCLE = JGEXDefinition(
    name=JGEXConstructionName.INTERSECTION_CIRCLE_CIRCLE,
    args=(v("x"), v("o"), v("w"), v("a")),
    rely_on_points={v("x"): (v("o"), v("w"), v("a"))},
    requirements=JGEXClause.from_str("ncoll o w a")[0],
    clauses=JGEXClause.from_str("x : cong o a o x, cong w a w x"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_circle.__name__),
            args=(v("o"), v("o"), v("a")),
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_circle.__name__),
            args=(v("w"), v("w"), v("a")),
        ),
    ),
    input_points=(v("o"), v("w"), v("a")),
    output_points=(v("x"),),
)

# Tangents

TANGENT = JGEXDefinition(
    name=JGEXConstructionName.TANGENT,
    args=(v("x"), v("y"), v("a"), v("o"), v("b")),
    rely_on_points={
        v("x"): (v("o"), v("a"), v("b")),
        v("y"): (v("o"), v("a"), v("b")),
    },
    requirements=JGEXClause.from_str("diff o a, diff o b, diff a b")[0],
    clauses=JGEXClause.from_str(
        "x : cong o x o b, perp a x o x; y : cong o y o b, perp a y o y"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_tangent.__name__),
            args=(v("a"), v("o"), v("b")),
        ),
    ),
    input_points=(v("a"), v("o"), v("b")),
    output_points=(v("x"), v("y")),
)

LINE_CIRCLE_TANGENT = JGEXDefinition(
    name=JGEXConstructionName.LINE_CIRCLE_TANGENT,
    args=(v("x"), v("a"), v("o")),
    rely_on_points={v("x"): (v("a"), v("o"))},
    requirements=JGEXClause.from_str("diff a o")[0],
    clauses=JGEXClause.from_str("x : perp a x a o"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_tline.__name__),
            args=(v("a"), v("a"), v("o")),
        ),
    ),
    input_points=(v("a"), v("o")),
    output_points=(v("x"),),
)


CIRCLE_CIRCLE_TANGENT = JGEXDefinition(
    name=JGEXConstructionName.CIRCLE_CIRCLE_TANGENT,
    args=(v("x"), v("y"), v("z"), v("i"), v("o"), v("a"), v("w"), v("b")),
    rely_on_points={
        v("x"): (v("o"), v("a"), v("w"), v("b"), v("y")),
        v("y"): (v("o"), v("a"), v("w"), v("b"), v("x")),
        v("z"): (v("o"), v("a"), v("w"), v("b"), v("i")),
        v("i"): (v("o"), v("a"), v("w"), v("b"), v("z")),
    },
    requirements=JGEXClause.from_str("diff o a, diff w b, diff o w")[0],
    clauses=JGEXClause.from_str(
        "x y : cong o x o a, cong w y w b, perp x o x y, perp y w y x; z i : cong o z o a, cong w i w b, perp z o z i, perp i w i z"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_cc_tangent.__name__),
            args=(v("o"), v("a"), v("w"), v("b")),
        ),
    ),
    input_points=(v("o"), v("a"), v("w"), v("b")),
    output_points=(v("x"), v("y"), v("z"), v("i")),
)


CIRCLE_CIRCLE_ITANGENT = JGEXDefinition(
    name=JGEXConstructionName.CIRCLE_CIRCLE_ITANGENT,
    args=(v("x"), v("y"), v("z"), v("i"), v("o"), v("a"), v("w"), v("b")),
    rely_on_points={
        v("x"): (v("o"), v("a"), v("w"), v("b"), v("y")),
        v("y"): (v("o"), v("a"), v("w"), v("b"), v("x")),
        v("z"): (v("o"), v("a"), v("w"), v("b"), v("i")),
        v("i"): (v("o"), v("a"), v("w"), v("b"), v("z")),
    },
    requirements=JGEXClause.from_str("diff o a, diff w b, diff o w")[0],
    clauses=JGEXClause.from_str(
        "x y : cong o x o a, cong w y w b, perp x o x y, perp y w y x; z i : cong o z o a, cong w i w b, perp z o z i, perp i w i z"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_cc_itangent.__name__),
            args=(v("o"), v("a"), v("w"), v("b")),
        ),
    ),
    input_points=(v("o"), v("a"), v("w"), v("b")),
    output_points=(v("x"), v("y"), v("z"), v("i")),
)


INTERSECTION_CONSTRUCTIONS = [
    INTERSECTION_LINE_LINE,
    INTERSECTION_LINE_PARA,
    INTERSECTION_PARA_PARA,
    INTERSECTION_LINE_PERP,
    INTERSECTION_PERP_PERP,
    INTERSECTION_LINE_CIRCLE,
    INTERSECTION_CIRCLE_CIRCLE,
    TANGENT,
    LINE_CIRCLE_TANGENT,
    CIRCLE_CIRCLE_TANGENT,
    CIRCLE_CIRCLE_ITANGENT,
]
