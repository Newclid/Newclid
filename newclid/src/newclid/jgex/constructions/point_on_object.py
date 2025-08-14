"""Definitions of points on lines, circles, etc."""

from newclid.jgex.clause import JGEXClause
from newclid.jgex.constructions._index import JGEXConstructionName
from newclid.jgex.definition import JGEXDefinition, SketchConstruction, v
from newclid.jgex.sketch import (
    sketch_aline,
    sketch_aline0,
    sketch_bline,
    sketch_circle,
    sketch_cyclic,
    sketch_dia,
    sketch_function_name,
    sketch_line,
    sketch_pline,
    sketch_tline,
)

# Point on Line

ON_LINE = JGEXDefinition(
    name=JGEXConstructionName.ON_LINE,
    args=(v("x"), v("a"), v("b")),
    rely_on_points={v("x"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("coll x a b"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_line.__name__), args=(v("a"), v("b"))
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"),),
)

ON_PARA_LINE = JGEXDefinition(
    name=JGEXConstructionName.ON_PARA_LINE,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("diff b c, ncoll a b c")[0],
    clauses=JGEXClause.from_str("para x a b c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_pline.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)

ON_PARA_LINE0 = JGEXDefinition(
    name=JGEXConstructionName.ON_PARA_LINE0,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("diff b c")[0],
    clauses=JGEXClause.from_str("para x a b c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_pline.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)

ON_PERP_LINE = JGEXDefinition(
    name=JGEXConstructionName.ON_PERP_LINE,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("diff b c")[0],
    clauses=JGEXClause.from_str("perp x a b c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_tline.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


ON_ALINE = JGEXDefinition(
    name=JGEXConstructionName.ON_ALINE,
    args=(v("x"), v("a"), v("b"), v("c"), v("d"), v("e")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"), v("d"), v("e"))},
    requirements=JGEXClause.from_str("ncoll c d e")[0],
    clauses=JGEXClause.from_str("eqangle a x a b d c d e"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_aline.__name__),
            args=(v("e"), v("d"), v("c"), v("b"), v("a")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("d"), v("e")),
    output_points=(v("x"),),
)


ON_ALINE0 = JGEXDefinition(
    name=JGEXConstructionName.ON_ALINE0,
    args=(v("x"), v("a"), v("b"), v("c"), v("d"), v("e"), v("f"), v("g")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"), v("d"), v("e"), v("f"), v("g"))},
    requirements=JGEXClause.from_str("ncoll a b c d")[0],
    clauses=JGEXClause.from_str("eqangle a b c d e f g x"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_aline0.__name__),
            args=(v("a"), v("b"), v("c"), v("d"), v("e"), v("f"), v("g")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("d"), v("e"), v("f"), v("g")),
    output_points=(v("x"),),
)


ON_BLINE = JGEXDefinition(
    name=JGEXConstructionName.ON_BLINE,
    args=(v("x"), v("a"), v("b")),
    rely_on_points={v("x"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("cong x a x b, eqangle a x a b b a b x"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_bline.__name__), args=(v("a"), v("b"))
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"),),
)


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

ON_CIRCUM = JGEXDefinition(
    name=JGEXConstructionName.ON_CIRCUM,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str("cyclic a b c x"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_cyclic.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)

ON_DIA = JGEXDefinition(
    name=JGEXConstructionName.ON_DIA,
    args=(v("x"), v("a"), v("b")),
    rely_on_points={v("x"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("perp x a x b"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_dia.__name__), args=(v("a"), v("b"))
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"),),
)

POINT_ON_OBJECT_CONSTRUCTIONS = [
    ON_LINE,
    ON_PARA_LINE,
    ON_PARA_LINE0,
    ON_PERP_LINE,
    ON_ALINE,
    ON_ALINE0,
    ON_BLINE,
    ON_CIRCLE,
    ON_CIRCUM,
    ON_DIA,
]
