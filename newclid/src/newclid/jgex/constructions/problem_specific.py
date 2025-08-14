"""Definitions made for specific problems."""

from newclid.jgex.clause import JGEXClause
from newclid.jgex.constructions._index import JGEXConstructionName
from newclid.jgex.definition import JGEXDefinition, SketchConstruction, v
from newclid.jgex.sketch import (
    sketch_2l1c,
    sketch_3peq,
    sketch_e5128,
    sketch_function_name,
    sketch_ninepoints,
    sketch_test_r20,
    sketch_test_r25,
)

TWOL1C = JGEXDefinition(
    name=JGEXConstructionName.TWOL1C,
    args=(v("x"), v("y"), v("z"), v("i"), v("a"), v("b"), v("c"), v("o")),
    rely_on_points={
        v("x"): (v("a"), v("b"), v("c"), v("o"), v("y"), v("z"), v("i")),
        v("y"): (v("a"), v("b"), v("c"), v("o"), v("x"), v("z"), v("i")),
        v("z"): (v("a"), v("b"), v("c"), v("o"), v("x"), v("y"), v("i")),
        v("i"): (v("a"), v("b"), v("c"), v("o"), v("x"), v("y"), v("z")),
    },
    requirements=JGEXClause.from_str("cong o a o b, ncoll a b c")[0],
    clauses=JGEXClause.from_str(
        "x y z i : coll x a c, coll y b c, cong o a o z, coll i o z, cong i x i y, cong i y i z, perp i x a c, perp i y b c"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_2l1c.__name__),
            args=(v("a"), v("b"), v("c"), v("o")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("o")),
    output_points=(v("x"), v("y"), v("z"), v("i")),
)


E5128 = JGEXDefinition(
    name=JGEXConstructionName.E5128,
    args=(v("x"), v("y"), v("a"), v("b"), v("c"), v("d")),
    rely_on_points={
        v("x"): (v("a"), v("b"), v("c"), v("d"), v("y")),
        v("y"): (v("a"), v("b"), v("c"), v("d"), v("x")),
    },
    requirements=JGEXClause.from_str("cong c b c d, perp b c b a")[0],
    clauses=JGEXClause.from_str(
        "x y : cong c b c x, coll y a b, coll x y d, eqangle a b a d x a x y"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_e5128.__name__),
            args=(v("a"), v("b"), v("c"), v("d")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("d")),
    output_points=(v("x"), v("y")),
)

THREEPEQ = JGEXDefinition(
    name=JGEXConstructionName.THREEPEQ,
    args=(v("x"), v("y"), v("z"), v("a"), v("b"), v("c")),
    rely_on_points={
        v("z"): (v("b"), v("c")),
        v("x"): (v("a"), v("b"), v("c"), v("z"), v("y")),
        v("y"): (v("a"), v("b"), v("c"), v("z"), v("x")),
    },
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str(
        "z : coll z b c ; x y : coll x a b, coll y a c, coll x y z, cong z x z y"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_3peq.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"), v("y"), v("z")),
)


TEST_R20 = JGEXDefinition(
    name=JGEXConstructionName.TEST_R20,
    args=(v("o"), v("a"), v("b"), v("c")),
    rely_on_points={
        v("b"): (v("a"), v("c")),
        v("o"): (v("a"), v("b"), v("c")),
    },
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("circle o a b c, coll o a c"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_test_r20.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("o"), v("a"), v("b"), v("c")),
)


TEST_R25 = JGEXDefinition(
    name=JGEXConstructionName.TEST_R25,
    args=(v("a"), v("b"), v("c"), v("d"), v("m")),
    rely_on_points={v("m"): (v("a"), v("b"), v("c"), v("d"))},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("midp m a b, midp m c d"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_test_r25.__name__), args=()
        ),
    ),
    input_points=(),
    output_points=(v("a"), v("b"), v("c"), v("d"), v("m")),
)

PROBLEM_SPECIFIC_CONSTRUCTIONS = [
    TWOL1C,
    E5128,
    THREEPEQ,
    TEST_R20,
    TEST_R25,
]
NINEPOINTS = JGEXDefinition(
    name=JGEXConstructionName.NINEPOINTS,
    args=(v("x"), v("y"), v("z"), v("i"), v("a"), v("b"), v("c")),
    rely_on_points={
        v("x"): (v("b"), v("c")),
        v("y"): (v("c"), v("a")),
        v("z"): (v("a"), v("b")),
        v("i"): (v("x"), v("y"), v("z")),
    },
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str(
        "x : coll x b c, cong x b x c; y : coll y c a, cong y c y a; z : coll z a b, cong z a z b; i : cong i x i y, cong i y i z"
    ),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_ninepoints.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"), v("y"), v("z"), v("i")),
)
