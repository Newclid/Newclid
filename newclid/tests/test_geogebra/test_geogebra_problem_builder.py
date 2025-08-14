from pathlib import Path
from typing import NamedTuple

import pytest
from newclid.ggb.problem_builder import GeogebraProblemBuilder
from newclid.numerical.geometries import PointNum
from newclid.problem import PredicateArgument, PredicateConstruction, ProblemSetup
from newclid.symbols.points_registry import Point
from newclid.tools import pretty_basemodel_diff


class GeogebraCase(NamedTuple):
    problem_id: str
    goals: list[tuple[str, ...]]
    expected_problem: ProblemSetup


def p(name: str) -> PredicateArgument:
    return PredicateArgument(name)


CASES = [
    GeogebraCase(
        problem_id="orthocenter",
        goals=[("perp", "A", "B", "C", "D")],
        expected_problem=ProblemSetup(
            name="orthocenter",
            goals=(PredicateConstruction.from_str("perp A B C D"),),
            points=(
                Point(name=p("A"), num=PointNum(x=0.0, y=1.0)),
                Point(name=p("B"), num=PointNum(x=5.0, y=8.0)),
                Point(name=p("C"), num=PointNum(x=8.0, y=3.0)),
                Point(
                    name=p("D"), num=PointNum(x=5.869565217391305, y=4.521739130434782)
                ),
            ),
            assumptions=(
                PredicateConstruction.from_str("perp B D A C"),
                PredicateConstruction.from_str("perp A D C B"),
            ),
        ),
    ),
    GeogebraCase(
        problem_id="indirect_parallelogram",
        goals=[("para", "A", "B", "C", "E")],
        expected_problem=ProblemSetup(
            name="indirect_parallelogram",
            goals=(PredicateConstruction.from_str(("para A B C E")),),
            points=(
                Point(name=p("A"), num=PointNum(x=-11.0, y=1.0)),
                Point(name=p("B"), num=PointNum(x=-8.0, y=4.0)),
                Point(name=p("C"), num=PointNum(x=-7.0, y=1.0)),
                Point(name=p("D"), num=PointNum(x=-14.0, y=4.0)),
                Point(name=p("E"), num=PointNum(x=-4.0, y=4.0)),
            ),
            assumptions=(
                PredicateConstruction.from_str(("para B E A C")),
                PredicateConstruction.from_str(("cong D A A B")),
                PredicateConstruction.from_str(("cong E C A D")),
            ),
        ),
    ),
    GeogebraCase(
        problem_id="circumcenter_midpoint",
        goals=[("eqangle", "A", "B", "A", "F", "A", "F", "A", "C")],
        expected_problem=ProblemSetup(
            name="circumcenter_midpoint",
            goals=(PredicateConstruction.from_str(("eqangle A B A F A F A C")),),
            points=(
                Point(name=p("A"), num=PointNum(x=0.0, y=0.0)),
                Point(name=p("B"), num=PointNum(x=6.0, y=-2.0)),
                Point(name=p("C"), num=PointNum(x=4.0, y=4.0)),
                Point(name=p("D"), num=PointNum(x=3.5, y=0.5)),
                Point(name=p("E"), num=PointNum(x=3.75, y=2.25)),
                Point(
                    name=p("F"), num=PointNum(x=3.23606797749979, y=0.7639320225002102)
                ),
                Point(
                    name=p("G"),
                    num=PointNum(x=2.6832815729997472, y=-0.8944271909999159),
                ),
                Point(name=p("H"), num=PointNum(x=2.0, y=2.0)),
            ),
            assumptions=(
                PredicateConstruction.from_str(("midp E D C")),
                PredicateConstruction.from_str(("coll A B G")),
                PredicateConstruction.from_str(("coll C A H")),
                PredicateConstruction.from_str(("eqangle C A A F A F A B")),
                PredicateConstruction.from_str(("eqangle B C B F B F A B")),
                PredicateConstruction.from_str(("perp F G A B")),
                PredicateConstruction.from_str(("circle D A C B")),
                PredicateConstruction.from_str(("cong H F F G")),
            ),
        ),
    ),
    GeogebraCase(
        problem_id="tangents",
        goals=[("cong", "D", "E", "D", "F")],
        expected_problem=ProblemSetup(
            name="tangents",
            goals=(PredicateConstruction.from_str(("cong D E D F")),),
            points=(
                Point(name=p("A"), num=PointNum(x=0.0, y=0.0)),
                Point(name=p("B"), num=PointNum(x=-10.0, y=0.0)),
                Point(name=p("C"), num=PointNum(x=-10.0, y=10.0)),
                Point(name=p("D"), num=PointNum(x=15.0, y=0.0)),
                Point(
                    name=p("E"), num=PointNum(x=6.666666666666667, y=7.453559924999299)
                ),
                Point(
                    name=p("F"), num=PointNum(x=6.666666666666667, y=-7.453559924999299)
                ),
            ),
            assumptions=(
                PredicateConstruction.from_str(("circle A B E F")),
                PredicateConstruction.from_str(("cong F A A B")),
                PredicateConstruction.from_str(("cong E A A B")),
                PredicateConstruction.from_str(("perp E A D E")),
                PredicateConstruction.from_str(("perp B A B C")),
                PredicateConstruction.from_str(("perp F A D F")),
            ),
        ),
    ),
    GeogebraCase(
        problem_id="imo_2019_p6",
        goals=[("perp", "A", "T", "A", "I")],
        expected_problem=ProblemSetup(
            name="imo_2019_p6",
            goals=(PredicateConstruction.from_str(("perp A T A I")),),
            points=(
                Point(name=p("A"), num=PointNum(x=-2.53, y=-0.6522616407982262)),
                Point(name=p("B"), num=PointNum(x=-0.19, y=2.09)),
                Point(name=p("C"), num=PointNum(x=1.49, y=-0.5322616407982262)),
                Point(
                    name=p("D"),
                    num=PointNum(x=0.5375646063301677, y=0.9543662152487727),
                ),
                Point(
                    name=p("E"),
                    num=PointNum(x=-0.27477205442495484, y=-0.5849414036168816),
                ),
                Point(
                    name=p("F"),
                    num=PointNum(x=-1.0654589167739486, y=1.064043843776083),
                ),
                Point(
                    name=p("I"),
                    num=PointNum(x=-0.3046153261720751, y=0.414808199911646),
                ),
                Point(
                    name=p("P"),
                    num=PointNum(x=0.4371408618192421, y=1.0857684432946726),
                ),
                Point(
                    name=p("Q"),
                    num=PointNum(x=-0.35280299034369944, y=0.5251464426438814),
                ),
                Point(
                    name=p("R"),
                    num=PointNum(x=-1.2526300070526193, y=0.09596959582020237),
                ),
                Point(
                    name=p("T"),
                    num=PointNum(x=-2.3984371937895226, y=-0.9266371703247638),
                ),
                Point(
                    name=p("O1"),
                    num=PointNum(x=0.5899354933306867, y=0.03362753959644931),
                ),
                Point(
                    name=p("O2"),
                    num=PointNum(x=-0.3175924089544161, y=1.3123787948883356),
                ),
            ),
            assumptions=(
                PredicateConstruction.from_str(("circle I D E F")),
                PredicateConstruction.from_str(("circle I D F R")),
                PredicateConstruction.from_str(("circle I D P R")),
                PredicateConstruction.from_str(("circle O1 C E P")),
                PredicateConstruction.from_str(("circle O1 C E Q")),
                PredicateConstruction.from_str(("circle O2 B F P")),
                PredicateConstruction.from_str(("circle O2 B F Q")),
                PredicateConstruction.from_str(("coll A B F")),
                PredicateConstruction.from_str(("coll A C E")),
                PredicateConstruction.from_str(("coll A P R")),
                PredicateConstruction.from_str(("coll B C D")),
                PredicateConstruction.from_str(("coll D I T")),
                PredicateConstruction.from_str(("coll P Q T")),
                PredicateConstruction.from_str(("cong D I E I")),
                PredicateConstruction.from_str(("cong E I I P")),
                PredicateConstruction.from_str(("cong F I E I")),
                PredicateConstruction.from_str(("cong I R E I")),
                PredicateConstruction.from_str(("cyclic B F P Q")),
                PredicateConstruction.from_str(("cyclic C E P Q")),
                PredicateConstruction.from_str(("cyclic D E F R")),
                PredicateConstruction.from_str(("cyclic D F P R")),
                PredicateConstruction.from_str(("eqangle A B A I A I A C")),
                PredicateConstruction.from_str(("eqangle A C C I C I B C")),
                PredicateConstruction.from_str(("perp A C E I")),
                PredicateConstruction.from_str(("perp D R E F")),
            ),
        ),
    ),
    GeogebraCase(
        problem_id="incenter",
        goals=[("eqangle", "A", "B", "B", "D", "B", "D", "B", "C")],
        expected_problem=ProblemSetup(
            name="incenter",
            goals=(PredicateConstruction.from_str(("eqangle A B B D B D B C")),),
            points=(
                Point(name=p("A"), num=PointNum(x=0.0, y=4.0)),
                Point(name=p("B"), num=PointNum(x=-4.0, y=0.0)),
                Point(name=p("C"), num=PointNum(x=4.0, y=0.0)),
                Point(name=p("D"), num=PointNum(x=0.0, y=1.6568542494923801)),
            ),
            assumptions=(
                PredicateConstruction.from_str(("eqangle A B B D B D B C")),
                PredicateConstruction.from_str(("eqangle A C C D C D B C")),
            ),
        ),
    ),
]


@pytest.mark.parametrize(
    "geogebra_case", CASES, ids=[case.problem_id for case in CASES]
)
def test_can_build_problem_from_geogebra(geogebra_case: GeogebraCase):
    ggb_file_path = Path(__file__).parent.joinpath(
        "ggb_exports", f"{geogebra_case.problem_id}.ggb"
    )
    ggb_problem_builder = GeogebraProblemBuilder(
        ggb_file_path=ggb_file_path
    ).with_goals(
        [PredicateConstruction.from_tuple(goal) for goal in geogebra_case.goals]
    )
    problem = ggb_problem_builder.build()
    expected = geogebra_case.expected_problem
    assert problem == expected, pretty_basemodel_diff(problem, expected)
