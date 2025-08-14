"""Definitions of points defined relatively to previous constructions."""

from newclid.jgex.clause import JGEXClause
from newclid.jgex.constructions._index import JGEXConstructionName
from newclid.jgex.definition import JGEXDefinition, SketchConstruction, v
from newclid.jgex.sketch import (
    sketch_amirror,
    sketch_between_bound,
    sketch_bisect,
    sketch_circle,
    sketch_exbisect,
    sketch_excenter2,
    sketch_function_name,
    sketch_incenter2,
    sketch_line,
    sketch_midp,
    sketch_pmirror,
    sketch_reflect,
    sketch_shift,
    sketch_tline,
    sketch_trisect,
    sketch_trisegment,
)

ANGLE_BISECTOR = JGEXDefinition(
    name=JGEXConstructionName.ANGLE_BISECTOR,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str("eqangle b a b x b x b c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_bisect.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


ANGLE_MIRROR = JGEXDefinition(
    name=JGEXConstructionName.ANGLE_MIRROR,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str("eqangle b a b c b c b x"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_amirror.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


EQDISTANCE = JGEXDefinition(
    name=JGEXConstructionName.EQDISTANCE,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("diff b c")[0],
    clauses=JGEXClause.from_str("cong x a b c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_circle.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


FOOT = JGEXDefinition(
    name=JGEXConstructionName.FOOT,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str("perp x a b c, coll x b c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_tline.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_line.__name__), args=(v("b"), v("c"))
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


INCENTER = JGEXDefinition(
    name=JGEXConstructionName.INCENTER,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str(
        "x : eqangle a b a x a x a c, eqangle c a c x c x c b; eqangle b c b x b x b a"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_bisect.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_bisect.__name__),
            args=(v("b"), v("c"), v("a")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


INCENTER2 = JGEXDefinition(
    name=JGEXConstructionName.INCENTER2,
    args=(v("x"), v("y"), v("z"), v("i"), v("a"), v("b"), v("c")),
    rely_on_points={
        v("i"): (v("a"), v("b"), v("c")),
        v("x"): (v("i"), v("b"), v("c")),
        v("y"): (v("i"), v("c"), v("a")),
        v("z"): (v("i"), v("a"), v("b")),
    },
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str(
        "i : eqangle a b a i a i a c, eqangle c a c i c i c b; eqangle b c b i b i b a; x : coll x b c, perp i x b c; y : coll y c a, perp i y c a; z : coll z a b, perp i z a b; cong i x i y, cong i y i z"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_incenter2.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"), v("y"), v("z"), v("i")),
)


EXCENTER = JGEXDefinition(
    name=JGEXConstructionName.EXCENTER,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str(
        "x : eqangle a b a x a x a c, eqangle c a c x c x c b; eqangle b c b x b x b a"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_bisect.__name__),
            args=(v("b"), v("a"), v("c")),
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_exbisect.__name__),
            args=(v("b"), v("c"), v("a")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


EXCENTER2 = JGEXDefinition(
    name=JGEXConstructionName.EXCENTER2,
    args=(v("x"), v("y"), v("z"), v("i"), v("a"), v("b"), v("c")),
    rely_on_points={
        v("i"): (v("a"), v("b"), v("c")),
        v("x"): (v("i"), v("b"), v("c")),
        v("y"): (v("i"), v("c"), v("a")),
        v("z"): (v("i"), v("a"), v("b")),
    },
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str(
        "i : eqangle a b a i a i a c, eqangle c a c i c i c b; eqangle b c b i b i b a; x : coll x b c, perp i x b c; y : coll y c a, perp i y c a; z : coll z a b, perp i z a b; cong i x i y, cong i y i z"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_excenter2.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"), v("y"), v("z"), v("i")),
)


MIDPOINT = JGEXDefinition(
    name=JGEXConstructionName.MIDPOINT,
    args=(v("x"), v("a"), v("b")),
    rely_on_points={v("x"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("midp x a b"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_midp.__name__),
            args=(v("a"), v("b")),
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"),),
)


MIRROR = JGEXDefinition(
    name=JGEXConstructionName.MIRROR,
    args=(v("x"), v("a"), v("b")),
    rely_on_points={v("x"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("coll x a b, cong b a b x"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_pmirror.__name__),
            args=(v("a"), v("b")),
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"),),
)


ORTHOCENTER = JGEXDefinition(
    name=JGEXConstructionName.ORTHOCENTER,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str("perp x a b c, perp x b c a; perp x c a b"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_tline.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
        SketchConstruction(
            name=sketch_function_name(sketch_tline.__name__),
            args=(v("b"), v("c"), v("a")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


REFLECT = JGEXDefinition(
    name=JGEXConstructionName.REFLECT,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("diff b c, ncoll a b c")[0],
    clauses=JGEXClause.from_str("cong b a b x, cong c a c x; perp b c a x"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_reflect.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


SHIFT = JGEXDefinition(
    name=JGEXConstructionName.SHIFT,
    args=(v("x"), v("b"), v("c"), v("d")),
    rely_on_points={v("x"): (v("b"), v("c"), v("d"))},
    requirements=JGEXClause.from_str("diff d b")[0],
    clauses=JGEXClause.from_str("cong x b c d, cong x c b d"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_shift.__name__),
            args=(v("d"), v("c"), v("b")),
        ),
    ),
    input_points=(v("b"), v("c"), v("d")),
    output_points=(v("x"),),
)


TRISECT = JGEXDefinition(
    name=JGEXConstructionName.TRISECT,
    args=(v("x"), v("y"), v("a"), v("b"), v("c")),
    rely_on_points={
        v("x"): (v("a"), v("b"), v("c"), v("y")),
        v("y"): (v("a"), v("b"), v("c"), v("x")),
    },
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str(
        "x y : coll x a c, coll y a c, eqangle b a b x b x b y, eqangle b x b y b y b c"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_trisect.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"), v("y")),
)


TRISEGMENT = JGEXDefinition(
    name=JGEXConstructionName.TRISEGMENT,
    args=(v("x"), v("y"), v("a"), v("b")),
    rely_on_points={
        v("x"): (v("a"), v("b"), v("y")),
        v("y"): (v("a"), v("b"), v("x")),
    },
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str(
        "x y : coll x a b, coll y a b, cong x a x y, cong y x y b, rconst a x a b 1/3"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_trisegment.__name__),
            args=(v("a"), v("b")),
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"), v("y")),
)


BETWEEN_BOUND = JGEXDefinition(
    name=JGEXConstructionName.BETWEEN_BOUND,
    args=(v("x"), v("a"), v("b")),
    rely_on_points={v("x"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("coll x a b, obtuse_angle a x b"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_between_bound.__name__),
            args=(v("a"), v("b")),
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"),),
)


RELATIVE_TO_CONSTRUCTIONS = [
    ANGLE_BISECTOR,
    ANGLE_MIRROR,
    EQDISTANCE,
    FOOT,
    INCENTER,
    INCENTER2,
    EXCENTER,
    EXCENTER2,
    MIDPOINT,
    MIRROR,
    ORTHOCENTER,
    REFLECT,
    SHIFT,
    TRISECT,
    TRISEGMENT,
    BETWEEN_BOUND,
]
