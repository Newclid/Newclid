"""Definitions of points that directly satisfy a predicate."""

from newclid.jgex.clause import JGEXClause
from newclid.jgex.constructions._index import JGEXConstructionName
from newclid.jgex.definition import JGEXDefinition, SketchConstruction, v
from newclid.jgex.sketch import (
    sketch_aconst,
    sketch_contri,
    sketch_contrir,
    sketch_eqangle2,
    sketch_eqangle3,
    sketch_eqratio,
    sketch_eqratio6,
    sketch_function_name,
    sketch_l2const,
    sketch_lconst,
    sketch_r2const,
    sketch_rconst,
    sketch_rconst2,
    sketch_s_angle,
    sketch_simtri,
    sketch_simtrir,
)

# Angles

ACONST = JGEXDefinition(
    name=JGEXConstructionName.ACONST,
    args=(v("a"), v("b"), v("c"), v("x"), v("r")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("aconst a b c x r"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_aconst.__name__),
            args=(v("a"), v("b"), v("c"), v("r")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


S_ANGLE = JGEXDefinition(
    name=JGEXConstructionName.S_ANGLE,
    args=(v("a"), v("b"), v("x"), v("y")),
    rely_on_points={v("x"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("aconst a b b x y"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_s_angle.__name__),
            args=(v("a"), v("b"), v("y")),
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"),),
)


EQANGLE2 = JGEXDefinition(
    name=JGEXConstructionName.EQANGLE2,
    args=(v("x"), v("a"), v("b"), v("c")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str("eqangle a b a x c x c b"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_eqangle2.__name__),
            args=(v("a"), v("b"), v("c")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)

EQANGLE3 = JGEXDefinition(
    name=JGEXConstructionName.EQANGLE3,
    args=(v("x"), v("a"), v("b"), v("d"), v("e"), v("f")),
    rely_on_points={v("x"): (v("a"), v("b"), v("d"), v("e"), v("f"))},
    requirements=JGEXClause.from_str("ncoll d e f, diff a b, diff d e, diff e f")[0],
    clauses=JGEXClause.from_str("eqangle x a x b d e d f"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_eqangle3.__name__),
            args=(v("a"), v("b"), v("d"), v("e"), v("f")),
        ),
    ),
    input_points=(v("a"), v("b"), v("d"), v("e"), v("f")),
    output_points=(v("x"),),
)


# Ratios


RCONST = JGEXDefinition(
    name=JGEXConstructionName.RCONST,
    args=(v("a"), v("b"), v("c"), v("x"), v("r")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("rconst a b c x r"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_rconst.__name__),
            args=(v("a"), v("b"), v("c"), v("r")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)


RCONST2 = JGEXDefinition(
    name=JGEXConstructionName.RCONST2,
    args=(v("x"), v("a"), v("b"), v("r")),
    rely_on_points={v("x"): (v("a"), v("b"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("rconst x a x b r"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_rconst2.__name__),
            args=(v("a"), v("b"), v("r")),
        ),
    ),
    input_points=(v("a"), v("b")),
    output_points=(v("x"),),
)

R2CONST = JGEXDefinition(
    name=JGEXConstructionName.R2CONST,
    args=(v("a"), v("b"), v("c"), v("x"), v("r")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"))},
    requirements=JGEXClause.from_str("diff a b")[0],
    clauses=JGEXClause.from_str("r2const a b c x r"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_r2const.__name__),
            args=(v("a"), v("b"), v("c"), v("r")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c")),
    output_points=(v("x"),),
)

EQRATIO = JGEXDefinition(
    name=JGEXConstructionName.EQRATIO,
    args=(v("x"), v("a"), v("b"), v("c"), v("d"), v("e"), v("f"), v("g")),
    rely_on_points={v("x"): (v("a"), v("b"), v("c"), v("d"), v("e"), v("f"), v("g"))},
    requirements=JGEXClause.from_str("diff a b, diff c d, diff e f")[0],
    clauses=JGEXClause.from_str("eqratio a b c d e f g x"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_eqratio.__name__),
            args=(v("a"), v("b"), v("c"), v("d"), v("e"), v("f"), v("g")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("d"), v("e"), v("f"), v("g")),
    output_points=(v("x"),),
)

EQRATIO6 = JGEXDefinition(
    name=JGEXConstructionName.EQRATIO6,
    args=(v("x"), v("a"), v("c"), v("e"), v("f"), v("g"), v("h")),
    rely_on_points={v("x"): (v("a"), v("c"), v("e"), v("f"), v("g"), v("h"))},
    requirements=JGEXClause.from_str("diff e f, diff g h")[0],
    clauses=JGEXClause.from_str("eqratio a x c x e f g h"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_eqratio6.__name__),
            args=(v("a"), v("c"), v("e"), v("f"), v("g"), v("h")),
        ),
    ),
    input_points=(v("a"), v("c"), v("e"), v("f"), v("g"), v("h")),
    output_points=(v("x"),),
)


# Lengths

LCONST = JGEXDefinition(
    name=JGEXConstructionName.LCONST,
    args=(v("x"), v("a"), v("l")),
    rely_on_points={v("a"): (v("x"),)},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("lconst x a l"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_lconst.__name__), args=(v("a"), v("l"))
        ),
    ),
    input_points=(v("a"),),
    output_points=(v("x"),),
)


L2CONST = JGEXDefinition(
    name=JGEXConstructionName.L2CONST,
    args=(v("x"), v("a"), v("l")),
    rely_on_points={v("a"): (v("x"),)},
    requirements=JGEXClause.from_str("")[0],
    clauses=JGEXClause.from_str("l2const x a l"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_l2const.__name__),
            args=(v("a"), v("l")),
        ),
    ),
    input_points=(v("a"),),
    output_points=(v("x"),),
)

# Similar triangles


SIMTRI = JGEXDefinition(
    name=JGEXConstructionName.SIMTRI,
    args=(v("r"), v("a"), v("b"), v("c"), v("p"), v("q")),
    rely_on_points={v("r"): (v("a"), v("b"), v("c"), v("p"), v("q"))},
    requirements=JGEXClause.from_str("ncoll a b c, diff p q")[0],
    clauses=JGEXClause.from_str("simtri a b c p q r"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_simtri.__name__),
            args=(v("a"), v("b"), v("c"), v("p"), v("q")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("p"), v("q")),
    output_points=(v("r"),),
)


SIMTRIR = JGEXDefinition(
    name=JGEXConstructionName.SIMTRIR,
    args=(v("r"), v("a"), v("b"), v("c"), v("p"), v("q")),
    rely_on_points={v("r"): (v("a"), v("b"), v("c"), v("p"), v("q"))},
    requirements=JGEXClause.from_str("ncoll a b c, diff p q")[0],
    clauses=JGEXClause.from_str("simtrir a b c p q r"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_simtrir.__name__),
            args=(v("a"), v("b"), v("c"), v("p"), v("q")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("p"), v("q")),
    output_points=(v("r"),),
)


CONTRI = JGEXDefinition(
    name=JGEXConstructionName.CONTRI,
    args=(v("q"), v("r"), v("a"), v("b"), v("c"), v("p")),
    rely_on_points={
        v("q"): (v("a"), v("b"), v("c"), v("p")),
        v("r"): (v("a"), v("b"), v("c"), v("p"), v("q")),
    },
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str("contri a b c p q r"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_contri.__name__),
            args=(v("a"), v("b"), v("c"), v("p")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("p")),
    output_points=(v("q"), v("r")),
)


CONTRIR = JGEXDefinition(
    name=JGEXConstructionName.CONTRIR,
    args=(v("q"), v("r"), v("a"), v("b"), v("c"), v("p")),
    rely_on_points={
        v("q"): (v("a"), v("b"), v("c"), v("p")),
        v("r"): (v("a"), v("b"), v("c"), v("p"), v("q")),
    },
    requirements=JGEXClause.from_str("ncoll a b c")[0],
    clauses=JGEXClause.from_str("contrir a b c p q r"),
    sketches=(
        SketchConstruction(
            name=sketch_function_name(sketch_contrir.__name__),
            args=(v("a"), v("b"), v("c"), v("p")),
        ),
    ),
    input_points=(v("a"), v("b"), v("c"), v("p")),
    output_points=(v("q"), v("r")),
)

PREDICATE_PRESCRIPTIONS = [
    ACONST,
    S_ANGLE,
    EQANGLE2,
    EQANGLE3,
    RCONST,
    RCONST2,
    R2CONST,
    EQRATIO,
    EQRATIO6,
    LCONST,
    L2CONST,
    SIMTRI,
    SIMTRIR,
    CONTRI,
    CONTRIR,
]
