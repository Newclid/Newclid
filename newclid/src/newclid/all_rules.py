"""
Rules allow the engine to create new facts given that a list of other facts is true. They correspond to mathematical theorems.

The basic language of geometrical facts are the predicates with their arguments.

Each rule is a constant instance of :ref:`newclid.rule.Rule`.

For example in:

R00_PERPENDICULARS_GIVE_PARALLEL = Rule(
    id="r00",
    description="Perpendiculars give parallel",
    premises_txt=("perp A B C D", "perp C D E F", "ncoll A B E"),
    conclusions_txt=("para A B E F",),
)

The id being between r00-r42 means it was one of the rules used in the original AlphaGeometry.

"perp", "ncoll", and "para" are predicates defining geoemtric relations between geometric objects.

A, B, C, D, E, F are points used in the rule. Because the rule doesn't have an `allow_point_repetition` argument, each point will be considered unique for the rule application.


This file contains all the rules created through the development of Newclid.

The rules currently in use are the ones in the list DEFAULT_RULES below.
"""

from __future__ import annotations

from newclid.rule import Rule

__all__ = [
    "DEFAULT_RULES",
    "ALL_RULES",
    "DEACTIVATED_RULES",
    "TRIAGE_NO_RULE_NEEDED",
    "TRIAGE_LEAVE_RULE_OUT",
    "R00_PERPENDICULARS_GIVE_PARALLEL",
    "R01_DEFINITION_OF_CYCLIC",
    "R02_PARALLEL_FROM_INCLINATION",
    "R03_ARC_DETERMINES_INTERNAL_ANGLES",
    "R04_CONGRUENT_ANGLES_ARE_IN_A_CYCLIC",
    "R05_SAME_ARC_SAME_CHORD",
    "R06_BASE_OF_HALF_TRIANGLE",
    "R07_THALES_THEOREM_1",
    "R08_RIGHT_TRIANGLES_COMMON_ANGLE_1",
    "R09_SUM_OF_ANGLES_OF_A_TRIANGLE",
    "R10_RATIO_CANCELLATION",
    "R11_BISECTOR_THEOREM_1",
    "R12_BISECTOR_THEOREM_2",
    "R13_ISOSCELES_TRIANGLE_EQUAL_ANGLES",
    "R14_EQUAL_BASE_ANGLES_IMPLY_ISOSCELES",
    "R15_ARC_DETERMINES_INSCRIBED_ANGLES_TANGENT",
    "R16_SAME_ARC_GIVING_TANGENT",
    "R17_CENTRAL_ANGLE_VS_INSCRIBED_ANGLE_1",
    "R18_CENTRAL_ANGLE_VS_INSCRIBED_ANGLE_2",
    "R19_HYPOTENUSE_IS_DIAMETER",
    "R20_DIAMETER_IS_HYPOTENUSE",
    "R21_CYCLIC_TRAPEZOID",
    "R22_BISECTOR_CONSTRUCTION",
    "R23_BISECTOR_IS_PERPENDICULAR",
    "R24_CYCLIC_KITE",
    "R25_DIAGONALS_OF_PARALLELOGRAM_1",
    "R26_DIAGONALS_OF_PARALLELOGRAM_2",
    "R27_THALES_THEOREM_2",
    "R28_OVERLAPPING_PARALLELS",
    "R29_MIDPOINT_IS_AN_EQRATIO",
    "R30_RIGHT_TRIANGLES_COMMON_ANGLE_2",
    "R31_DENOMINATOR_CANCELLING",
    "R34_AA_SIMILARITY_OF_TRIANGLES_DIRECT",
    "R35_AA_SIMILARITY_OF_TRIANGLES_REVERSE",
    "R36_ASA_CONGRUENCE_OF_TRIANGLES_DIRECT",
    "R37_ASA_CONGRUENCE_OF_TRIANGLES_REVERSE",
    "R41_THALES_THEOREM_3",
    "R42_THALES_THEOREM_4",
    "R43_ORTHOCENTER_THEOREM",
    "R44_PAPPUS_THEOREM",
    "R45_SIMSONS_LINE_THEOREM",
    "R46_INCENTER_THEOREM",
    "R47_CIRCUMCENTER_THEOREM",
    "R48_CENTROID_THEOREM",
    "R49_RECOGNIZE_CENTER_OF_CIRCLE_CYCLIC",
    "R50_RECOGNIZE_CENTER_OF_CYCLIC_CONG",
    "R51_MIDPOINT_SPLITS_IN_TWO",
    "R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES",
    "R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES",
    "R54_DEFINITION_OF_MIDPOINT",
    "R55_MIDPOINT_CONG_PROPERTIES",
    "R56_MIDPOINT_COLL_PROPERTIES",
    "R57_PYTHAGORAS_THEOREM",
    "R58_SAME_CHORD_SAME_ARC_1",
    "R59_SAME_CHORD_SAME_ARC_2",
    "R60_SSS_SIMILARITY_OF_TRIANGLES_DIRECT",
    "R61_SSS_SIMILARITY_OF_TRIANGLES_REVERSE",
    "R62_SAS_SIMILARITY_OF_TRIANGLES_DIRECT",
    "R63_SAS_SIMILARITY_OF_TRIANGLES_REVERSE",
    "R64_SSS_CONGRUENCE_OF_TRIANGLES_DIRECT",
    "R65_SSS_CONGRUENCE_OF_TRIANGLES_REVERSE",
    "R66_SAS_CONGRUENCE_OF_TRIANGLES_DIRECT",
    "R67_SAS_CONGRUENCE_OF_TRIANGLES_REVERSE",
    "R68_SIMILARITY_WITHOUT_SCALING_DIRECT",
    "R69_SIMILARITY_WITHOUT_SCALING_REVERSE",
    "R70_PROJECTIVE_HARMONIC_CONJUGATE",
    "R71_RESOLUTION_OF_RATIOS",
    "R72_DISASSEMBLING_A_CIRCLE",
    "R73_DEFINITION_OF_CIRCLE",
    "R74_INTERSECTION_BISECTORS",
    "R76_CENTER_DIA",
    "R77_CONGRUENT_TRIANGLES_DIRECT_PROPERTIES",
    "R78_CONGRUENT_TRIANGLES_REVERSE_PROPERTIES",
    "R79_MULTIPLY_CONG_BY_ONE",
    "R80_SAME_CHORD_SAME_ARC_FOUR_POINTS_1",
    "R81_SAME_CHORD_SAME_ARC_FOUR_POINTS_2",
    "R82_PARA_OF_COLL",
    "R83_BETWEEN_CONDITION_I",
    "R84_BETWEEN_CONDITION_II",
    "R85_GENERALIZED_PYTHAGORAS_I",
    "R86_GENERALIZED_PYTHAGORAS_II",
    "R87_CIRCUMCENTER_CHARACTERIZATION_I",
    "R88_CIRCUMCENTER_CHARACTERIZATION_II",
    "R89_LENGTH_OF_MEDIAN",
    "R90_PARALLELOGRAM_LAW",
    "R91_ANGLES_OF_ISO_TRAPEZOID",
    "R92_DIAMETER_CROSSES_CENTER",
]

R00_PERPENDICULARS_GIVE_PARALLEL = Rule(
    id="r00",
    description="Perpendiculars give parallel",
    premises_txt=("perp A B C D", "perp C D E F", "ncoll A B E"),
    conclusions_txt=("para A B E F",),
)

R01_DEFINITION_OF_CYCLIC = Rule(
    id="r01",
    description="Definition of cyclic",
    premises_txt=("cong O A O B", "cong O B O C", "cong O C O D"),
    conclusions_txt=("cyclic A B C D",),
)

R02_PARALLEL_FROM_INCLINATION = Rule(
    id="r02",
    description="Parallel from inclination",
    premises_txt=("eqangle A B P Q C D P Q",),
    conclusions_txt=("para A B C D",),
)

R03_ARC_DETERMINES_INTERNAL_ANGLES = Rule(
    id="r03",
    description="Arc determines internal angles",
    premises_txt=("cyclic A B P Q",),
    conclusions_txt=(
        "eqangle P A P B Q A Q B",
        "eqangle A Q A P B Q B P",
        "eqangle A B B Q A P P Q",
        "eqangle A B A P Q B Q P",
    ),
)

R04_CONGRUENT_ANGLES_ARE_IN_A_CYCLIC = Rule(
    id="r04",
    description="Congruent angles are in a cyclic",
    premises_txt=("eqangle P A P B Q A Q B", "ncoll P Q A B"),
    conclusions_txt=("cyclic A B P Q",),
)

R05_SAME_ARC_SAME_CHORD = Rule(
    id="r05",
    description="Same arc same chord",
    premises_txt=("cyclic A B C P Q R", "eqangle C A C B R P R Q"),
    conclusions_txt=("cong A B P Q",),
)

R06_BASE_OF_HALF_TRIANGLE = Rule(
    id="r06",
    description="Base of half triangle",
    premises_txt=("midp E A B", "midp F A C"),
    conclusions_txt=("para E F B C",),
)

R07_THALES_THEOREM_1 = Rule(
    id="r07",
    description="Thales Theorem I",
    premises_txt=("para A B C D", "coll O A C", "coll O B D", "ncoll O A B"),
    conclusions_txt=(
        "simtri O A B O C D",
        "eqratio O A C A O B B D",
        "eqratio O C A C O D B D",
    ),
)

R08_RIGHT_TRIANGLES_COMMON_ANGLE_1 = Rule(
    id="r08",
    description="Right triangles common angle I",
    premises_txt=("perp A B C D", "perp E F G H", "npara A B E F"),
    conclusions_txt=("eqangle A B E F C D G H",),
)

R09_SUM_OF_ANGLES_OF_A_TRIANGLE = Rule(
    id="r09",
    description="Sum of angles of a triangle",
    premises_txt=(
        "eqangle A B C D M N P Q",
        "eqangle C D E F P Q R U",
        "npara A B E F",
    ),
    conclusions_txt=("eqangle A B E F M N R U",),
)

R10_RATIO_CANCELLATION = Rule(
    id="r10",
    description="Ratio cancellation",
    premises_txt=(
        "eqratio A B C D M N P Q",
        "eqratio C D E F P Q R U",
    ),
    conclusions_txt=("eqratio A B E F M N R U",),
)

R11_BISECTOR_THEOREM_1 = Rule(
    id="r11",
    description="Bisector theorem I",
    premises_txt=(
        "eqratio D B D C A B A C",
        "coll D B C",
        "ncoll A B C",
    ),
    conclusions_txt=("eqangle A B A D A D A C",),
)

R12_BISECTOR_THEOREM_2 = Rule(
    id="r12",
    description="Bisector theorem II",
    premises_txt=("eqangle A B A D A D A C", "coll D B C", "ncoll A B C"),
    conclusions_txt=("eqratio D B D C A B A C",),
)

R13_ISOSCELES_TRIANGLE_EQUAL_ANGLES = Rule(
    id="r13",
    description="Isosceles triangle equal angles",
    premises_txt=("cong O A O B", "ncoll O A B"),
    conclusions_txt=("eqangle O A A B A B O B",),
)

R14_EQUAL_BASE_ANGLES_IMPLY_ISOSCELES = Rule(
    id="r14",
    description="Equal base angles imply isosceles",
    premises_txt=("eqangle A O A B B A B O", "ncoll O A B"),
    conclusions_txt=("cong O A O B",),
)

R15_ARC_DETERMINES_INSCRIBED_ANGLES_TANGENT = Rule(
    id="r15",
    description="Arc determines inscribed angles (tangent)",
    premises_txt=("circle O A B C", "perp O A A X"),
    conclusions_txt=("eqangle A X A B C A C B",),
)

R16_SAME_ARC_GIVING_TANGENT = Rule(
    id="r16",
    description="Same arc giving tangent",
    premises_txt=("circle O A B C", "eqangle A X A B C A C B"),
    conclusions_txt=("perp O A A X",),
)

R17_CENTRAL_ANGLE_VS_INSCRIBED_ANGLE_1 = Rule(
    id="r17",
    description="Central angle vs inscribed angle I",
    premises_txt=("circle O A B C", "midp M B C"),
    conclusions_txt=("eqangle A B A C O B O M",),
)

R18_CENTRAL_ANGLE_VS_INSCRIBED_ANGLE_2 = Rule(
    id="r18",
    description="Central angle vs inscribed angle II",
    premises_txt=("circle O A B C", "coll M B C", "eqangle A B A C O B O M"),
    conclusions_txt=("midp M B C",),
)

R19_HYPOTENUSE_IS_DIAMETER = Rule(
    id="r19",
    description="Hypotenuse is diameter",
    premises_txt=("perp A B B C", "midp M A C"),
    conclusions_txt=("cong A M B M",),
)

R20_DIAMETER_IS_HYPOTENUSE = Rule(
    id="r20",
    description="Diameter is hypotenuse",
    premises_txt=("circle O A B C", "coll O A C"),
    conclusions_txt=("perp A B B C",),
)

R21_CYCLIC_TRAPEZOID = Rule(
    id="r21",
    description="Cyclic trapezoid",
    premises_txt=("cyclic A B C D", "para A B C D"),
    conclusions_txt=("eqangle A D C D C D C B",),
)

R22_BISECTOR_CONSTRUCTION = Rule(
    id="r22",
    description="Bisector construction",
    premises_txt=("midp M A B", "perp O M A B"),
    conclusions_txt=("cong O A O B",),
)

R23_BISECTOR_IS_PERPENDICULAR = Rule(
    id="r23",
    description="Bisector is perpendicular",
    premises_txt=("cong A P B P", "cong A Q B Q"),
    conclusions_txt=("perp A B P Q",),
)

R24_CYCLIC_KITE = Rule(
    id="r24",
    description="Cyclic kite",
    premises_txt=("cong A P B P", "cong A Q B Q", "cyclic A B P Q"),
    conclusions_txt=("perp P A A Q",),
)

R25_DIAGONALS_OF_PARALLELOGRAM_1 = Rule(
    id="r25",
    description="Diagonals of parallelogram I",
    premises_txt=("midp M A B", "midp M C D"),
    conclusions_txt=("para A C B D",),
)

R26_DIAGONALS_OF_PARALLELOGRAM_2 = Rule(
    id="r26",
    description="Diagonals of parallelogram II",
    premises_txt=("midp M A B", "para A C B D", "para A D B C", "ncoll A B C"),
    conclusions_txt=("midp M C D",),
)

R27_THALES_THEOREM_2 = Rule(
    id="r27",
    description="Thales theorem II",
    premises_txt=(
        "eqratio O A A C O B B D",
        "coll O A C",
        "coll O B D",
        "ncoll A B C",
        "sameside A O C B O D",
    ),
    conclusions_txt=("para A B C D",),
)

R28_OVERLAPPING_PARALLELS = Rule(
    id="r28",
    description="Overlapping parallels",
    premises_txt=("para A B A C",),
    conclusions_txt=("coll A B C",),
)

R29_MIDPOINT_IS_AN_EQRATIO = Rule(
    id="r29",
    description="Midpoint is an eqratio",
    premises_txt=("midp M A B", "midp N C D"),
    conclusions_txt=("eqratio M A A B N C C D",),
)

R30_RIGHT_TRIANGLES_COMMON_ANGLE_2 = Rule(
    id="r30",
    description="Right triangles common angle II",
    premises_txt=("eqangle A B P Q C D U V", "perp P Q U V"),
    conclusions_txt=("perp A B C D",),
)

R31_DENOMINATOR_CANCELLING = Rule(
    id="r31",
    description="Denominator cancelling",
    premises_txt=("eqratio A B P Q C D U V", "cong P Q U V"),
    conclusions_txt=("cong A B C D",),
)

#     R32_OLD_SSS_TRIANGLE_CONGRUENCE = Rule(
#     id="r32",
#     description="SSS Triangle congruence",
#     premises_txt=("cong A B P Q", "cong B C Q R", "cong C A R P", "ncoll A B C"),
#     conclusions_txt=("contri* A B C P Q R",),
# )
#     R33_OLD_SAS_TRIANGLE_CONGRUENCE = Rule(
#     id="r33",
#     description="SAS Triangle congruence",
#     premises_txt=("cong A B P Q", "cong B C Q R", "eqangle B A B C Q P Q R", "ncoll A B C"),
#     conclusions_txt=("contri* A B C P Q R",),
# )

R34_AA_SIMILARITY_OF_TRIANGLES_DIRECT = Rule(
    id="r34",
    description="AA Similarity of triangles (Direct)",
    premises_txt=(
        "eqangle B A B C Q P Q R",
        "eqangle C A C B R P R Q",
        "ncoll A B C",
        "sameclock A B C P Q R",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("simtri A B C P Q R",),
    allow_point_repetition=True,
)

R35_AA_SIMILARITY_OF_TRIANGLES_REVERSE = Rule(
    id="r35",
    description="AA Similarity of triangles (Reverse)",
    premises_txt=(
        "eqangle B A B C Q R Q P",
        "eqangle C A C B R Q R P",
        "ncoll A B C",
        "sameclock A B C P R Q",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("simtrir A B C P Q R",),
    allow_point_repetition=True,
)

R36_ASA_CONGRUENCE_OF_TRIANGLES_DIRECT = Rule(
    id="r36",
    description="ASA Congruence of triangles (Direct)",
    premises_txt=(
        "eqangle B A B C Q P Q R",
        "eqangle C A C B R P R Q",
        "ncoll A B C",
        "cong A B P Q",
        "sameclock A B C P Q R",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("contri A B C P Q R",),
    allow_point_repetition=True,
)

R37_ASA_CONGRUENCE_OF_TRIANGLES_REVERSE = Rule(
    id="r37",
    description="ASA Congruence of triangles (Reverse)",
    premises_txt=(
        "eqangle B A B C Q R Q P",
        "eqangle C A C B R Q R P",
        "ncoll A B C",
        "cong A B P Q",
        "sameclock A B C P R Q",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("contrir A B C P Q R",),
    allow_point_repetition=True,
)

#     R38_OLD_SSS_TRIANGLE_SIMILARITY = Rule(
#     id="r38",
#     description="SSS Triangle similarity",
#     premises_txt=("eqratio B A B C Q P Q R", "eqratio C A C B R P R Q", "ncoll A B C"),
#     conclusions_txt=("simtri* A B C P Q R",),
# )
#     R39_OLD_SAS_TRIANGLE_SIMILARITY = Rule(
#     id="r39",
#     description="SAS Triangle similarity",
#     premises_txt=("eqratio B A B C Q P Q R", "eqangle B A B C Q P Q R", "ncoll A B C"),
#     conclusions_txt=("simtri* A B C P Q R",),
# )
#     R40_OLD_SIMILARITY_NO_SCALING = Rule(
#     id="r40",
#     description="Similarity without scaling"
#     premises_txt=("eqratio B A B C Q P Q R", "eqratio C A C B R P R Q", "ncoll A B C", "cong A B P Q"),
#     conclusions_txt=("contri* A B C P Q R",),
# )

R41_THALES_THEOREM_3 = Rule(
    id="r41",
    description="Thales theorem III",
    premises_txt=(
        "para A B C D",
        "coll M A D",
        "coll N B C",
        "eqratio M A M D N B N C",
        "sameside M A D N B C",
    ),
    conclusions_txt=("para M N A B",),
)

R42_THALES_THEOREM_4 = Rule(
    id="r42",
    description="Thales theorem IV",
    premises_txt=(
        "para A B C D",
        "coll M A D",
        "coll N B C",
        "para M N A B",
        "ncoll A B C",
    ),
    conclusions_txt=("eqratio M A M D N B N C",),
)

R43_ORTHOCENTER_THEOREM = Rule(
    id="r43",
    description="Orthocenter theorem",
    premises_txt=("perp A B C D", "perp A C B D", "ncoll A B C"),
    conclusions_txt=("perp A D B C",),
)

R44_PAPPUS_THEOREM = Rule(
    id="r44",
    description="Pappus's theorem",
    premises_txt=(
        "coll A B C",
        "coll P Q R",
        "coll X A Q",
        "coll X P B",
        "coll Y A R",
        "coll Y P C",
        "coll Z B R",
        "coll Z C Q",
    ),
    conclusions_txt=("coll X Y Z",),
)

R45_SIMSONS_LINE_THEOREM = Rule(
    id="r45",
    description="Simson's line theorem",
    premises_txt=(
        "cyclic A B C P",
        "coll A L C",
        "perp P L A C",
        "coll M B C",
        "perp P M B C",
        "coll N A B",
        "perp P N A B",
    ),
    conclusions_txt=("coll L M N",),
)

R46_INCENTER_THEOREM = Rule(
    id="r46",
    description="Incenter theorem",
    premises_txt=("eqangle A B A X A X A C", "eqangle B A B X B X B C", "ncoll A B C"),
    conclusions_txt=("eqangle C B C X C X C A",),
)

R47_CIRCUMCENTER_THEOREM = Rule(
    id="r47",
    description="Circumcenter theorem",
    premises_txt=(
        "midp M A B",
        "perp X M A B",
        "midp N B C",
        "perp X N B C",
        "midp P C A",
    ),
    conclusions_txt=("perp X P C A",),
)

R48_CENTROID_THEOREM = Rule(
    id="r48",
    description="Centroid theorem",
    premises_txt=("midp M A B", "coll M X C", "midp N B C", "coll N X A", "midp P C A"),
    conclusions_txt=("coll X P B",),
)

R49_RECOGNIZE_CENTER_OF_CIRCLE_CYCLIC = Rule(
    id="r49",
    description="Recognize center of circle (cyclic)",
    premises_txt=("circle O A B C", "cyclic A B C D"),
    conclusions_txt=("cong O A O D",),
)

R50_RECOGNIZE_CENTER_OF_CYCLIC_CONG = Rule(
    id="r50",
    description="Recognize center of cyclic (cong)",
    premises_txt=("cyclic A B C D", "cong O A O B", "cong O C O D", "npara A B C D"),
    conclusions_txt=("cong O A O C",),
)

R51_MIDPOINT_SPLITS_IN_TWO = Rule(
    id="r51",
    description="Midpoint splits in two",
    premises_txt=("midp M A B",),
    conclusions_txt=("rconst M A A B 1/2",),
)

R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES = Rule(
    id="r52",
    description="Properties of similar triangles (Direct)",
    premises_txt=(
        "simtri A B C P Q R",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=(
        "eqangle B A B C Q P Q R",
        "eqangle A B A C P Q P R",
        "eqangle A C B C P R Q R",
        "eqratio B A B C Q P Q R",
        "eqratio B C A C Q R P R",
    ),
    allow_point_repetition=True,
)

R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES = Rule(
    id="r53",
    description="Properties of similar triangles (Reverse)",
    premises_txt=(
        "simtrir A B C P Q R",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=(
        "eqangle B A B C Q R Q P",
        "eqangle A B A C P R P Q",
        "eqangle A C B C Q R P R",
        "eqratio B A B C Q P Q R",
        "eqratio B C A C Q R P R",
    ),
    allow_point_repetition=True,
)

R54_DEFINITION_OF_MIDPOINT = Rule(
    id="r54",
    description="Definition of midpoint",
    premises_txt=("cong M A M B", "coll M A B"),
    conclusions_txt=("midp M A B",),
)

R55_MIDPOINT_CONG_PROPERTIES = Rule(
    id="r55",
    description="Properties of midpoint (cong)",
    premises_txt=("midp M A B",),
    conclusions_txt=("cong M A M B",),
)

R56_MIDPOINT_COLL_PROPERTIES = Rule(
    id="r56",
    description="Properties of midpoint (coll)",
    premises_txt=("midp M A B",),
    conclusions_txt=("coll M A B",),
)

R57_PYTHAGORAS_THEOREM = Rule(
    id="r57",
    description="Pythagoras theorem",
    premises_txt=("PythagoreanPremises A B C",),
    conclusions_txt=("PythagoreanConclusions A B C",),
)

R58_SAME_CHORD_SAME_ARC_1 = Rule(
    id="r58",
    description="Same chord same arc I",
    premises_txt=(
        "cyclic A B C P Q R",
        "cong A B P Q",
        "nperp A C B C",
        "sameclock C A B R P Q",
        "sameside C A B R P Q",
    ),
    conclusions_txt=("eqangle C A C B R P R Q",),
)

R59_SAME_CHORD_SAME_ARC_2 = Rule(
    id="r59",
    description="Same chord same arc II",
    premises_txt=(
        "cyclic A B C P Q R",
        "cong A B P Q",
        "nperp A C B C",
        "sameclock C B A R P Q",
        "nsameside C B A R P Q",
    ),
    conclusions_txt=("eqangle C A C B R P R Q",),
)

R60_SSS_SIMILARITY_OF_TRIANGLES_DIRECT = Rule(
    id="r60",
    description="SSS Similarity of triangles (Direct)",
    premises_txt=(
        "eqratio B A B C Q P Q R",
        "eqratio C A C B R P R Q",
        "ncoll A B C",
        "sameclock A B C P Q R",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("simtri A B C P Q R",),
    allow_point_repetition=True,
)

R61_SSS_SIMILARITY_OF_TRIANGLES_REVERSE = Rule(
    id="r61",
    description="SSS Similarity of triangles (Reverse)",
    premises_txt=(
        "eqratio B A B C Q P Q R",
        "eqratio C A C B R P R Q",
        "ncoll A B C",
        "sameclock A B C P R Q",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("simtrir A B C P Q R",),
    allow_point_repetition=True,
)

R62_SAS_SIMILARITY_OF_TRIANGLES_DIRECT = Rule(
    id="r62",
    description="SAS Similarity of triangles (Direct)",
    premises_txt=(
        "eqratio B A B C Q P Q R",
        "eqangle B A B C Q P Q R",
        "ncoll A B C",
        "sameclock A B C P Q R",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("simtri A B C P Q R",),
    allow_point_repetition=True,
)

R63_SAS_SIMILARITY_OF_TRIANGLES_REVERSE = Rule(
    id="r63",
    description="SAS Similarity of triangles (Reverse)",
    premises_txt=(
        "eqratio B A B C Q P Q R",
        "eqangle B A B C Q R Q P",
        "ncoll A B C",
        "sameclock A B C P R Q",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("simtrir A B C P Q R",),
    allow_point_repetition=True,
)

R64_SSS_CONGRUENCE_OF_TRIANGLES_DIRECT = Rule(
    id="r64",
    description="SSS Congruence of triangles (Direct)",
    premises_txt=(
        "cong A B P Q",
        "cong B C Q R",
        "cong C A R P",
        "ncoll A B C",
        "sameclock A B C P Q R",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("contri A B C P Q R",),
    allow_point_repetition=True,
)

R65_SSS_CONGRUENCE_OF_TRIANGLES_REVERSE = Rule(
    id="r65",
    description="SSS Congruence of triangles (Reverse)",
    premises_txt=(
        "cong A B P Q",
        "cong B C Q R",
        "cong C A R P",
        "ncoll A B C",
        "sameclock A B C P R Q",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("contrir A B C P Q R",),
    allow_point_repetition=True,
)

R66_SAS_CONGRUENCE_OF_TRIANGLES_DIRECT = Rule(
    id="r66",
    description="SAS Congruence of triangles (Direct)",
    premises_txt=(
        "cong A B P Q",
        "cong B C Q R",
        "eqangle B A B C Q P Q R",
        "ncoll A B C",
        "sameclock A B C P Q R",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("contri A B C P Q R",),
    allow_point_repetition=True,
)

R67_SAS_CONGRUENCE_OF_TRIANGLES_REVERSE = Rule(
    id="r67",
    description="SAS Congruence of triangles (Reverse)",
    premises_txt=(
        "cong A B P Q",
        "cong B C Q R",
        "eqangle B A B C Q R Q P",
        "ncoll A B C",
        "sameclock A B C P R Q",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("contrir A B C P Q R",),
    allow_point_repetition=True,
)

R68_SIMILARITY_WITHOUT_SCALING_DIRECT = Rule(
    id="r68",
    description="Similarity without scaling (Direct)",
    premises_txt=(
        "eqratio B A B C Q P Q R",
        "eqratio C A C B R P R Q",
        "ncoll A B C",
        "cong A B P Q",
        "sameclock A B C P Q R",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("contri A B C P Q R",),
    allow_point_repetition=True,
)

R69_SIMILARITY_WITHOUT_SCALING_REVERSE = Rule(
    id="r69",
    description="Similarity without scaling (Reverse)",
    premises_txt=(
        "eqratio B A B C Q P Q R",
        "eqratio C A C B R P R Q",
        "ncoll A B C",
        "cong A B P Q",
        "sameclock A B C P R Q",
        "diff A B C",
        "diff P Q R",
    ),
    conclusions_txt=("contrir A B C P Q R",),
    allow_point_repetition=True,
)

R70_PROJECTIVE_HARMONIC_CONJUGATE = Rule(
    id="r70",
    description="Projective harmonic conjugate",
    premises_txt=(
        "coll A L M",
        "coll A K N",
        "coll B K M",
        "coll B L N",
        "coll C M N",
        "coll D K L",
        "coll A B C D",
    ),
    conclusions_txt=("eqratio A C A D B C B D",),
)

R71_RESOLUTION_OF_RATIOS = Rule(
    id="r71",
    description="Resolution of ratios",
    premises_txt=(
        "eqratio A B A C D E D F",
        "coll A B C",
        "coll D E F",
        "sameside A B C D E F",
    ),
    conclusions_txt=("eqratio A B B C D E E F",),
)

R72_DISASSEMBLING_A_CIRCLE = Rule(
    id="r72",
    description="Disassembling a circle",
    premises_txt=("circle O A B C",),
    conclusions_txt=("cong O A O B", "cong O B O C"),
)

R73_DEFINITION_OF_CIRCLE = Rule(
    id="r73",
    description="Definition of circle",
    premises_txt=("cong O A O B", "cong O B O C"),
    conclusions_txt=("circle O A B C",),
)

R74_INTERSECTION_BISECTORS = Rule(
    id="r74",
    description="Intersection of angle bisector and perpendicular bisector",
    premises_txt=(
        "eqangle C A C D C D C B",
        "cong D A D B",
        "ncoll A B C D",
        "nperp A B C D",
    ),
    conclusions_txt=("cyclic A B C D",),
)

# R75_SEGMENT_EQUIPARTITION = Rule(
#     id="r75",
#     description="Equipartition of segments",
#     premises_txt=(
#         "eqratio A B A C D E D F",
#         "coll A B C",
#         "coll D E F",
#         "sameside A B C D E F",
#     ),
#     conclusions_txt=("eqratio A B B C D E E F",),
# )

R76_CENTER_DIA = Rule(
    id="r76",
    description="Locate midpoint of hypotenuse",
    premises_txt=("cong A M B M", "coll B M C", "perp A B A C"),
    conclusions_txt=("midp M B C",),
)

R77_CONGRUENT_TRIANGLES_DIRECT_PROPERTIES = Rule(
    id="r77",
    description="Properties of congruent triangles (Direct)",
    premises_txt=("contri A B C P Q R",),
    conclusions_txt=("simtri A B C P Q R", "cong A B P Q"),
    allow_point_repetition=True,
)

R78_CONGRUENT_TRIANGLES_REVERSE_PROPERTIES = Rule(
    id="r78",
    description="Properties of congruent triangles (Reverse)",
    premises_txt=("contrir A B C P Q R",),
    conclusions_txt=("simtrir A B C P Q R", "cong A B P Q"),
    allow_point_repetition=True,
)

R79_MULTIPLY_CONG_BY_ONE = Rule(
    id="r79",
    description="Divide congruence equation by segment",
    premises_txt=(
        "cong A B C D",
        "diff X Y",
        "diff A B",
        "diff C D",
    ),
    conclusions_txt=("eqratio A B X Y C D X Y",),
    allow_point_repetition=True,
)

R80_SAME_CHORD_SAME_ARC_FOUR_POINTS_1 = Rule(
    id="r80",
    description="Same chord same arc III",
    premises_txt=(
        "cyclic A B P Q",
        "cong A B P Q",
        "npara A P B Q",
    ),
    conclusions_txt=("eqangle P A P B P B Q B",),
)

R81_SAME_CHORD_SAME_ARC_FOUR_POINTS_2 = Rule(
    id="r81",
    description="Same chord same arc IV",
    premises_txt=(
        "cyclic A B P Q",
        "cong A B P Q",
        "sameclock A P B A P Q",
    ),
    conclusions_txt=("eqangle P A P B Q B P B",),
)

# The python engine deduces this without a rule,
# so it isn't included in `ALL_RULES`,
# but we need it for the C++ bridge.
R82_PARA_OF_COLL = Rule(
    id="r82",
    description="Parallel from collinear",
    premises_txt=("coll A B C",),
    conclusions_txt=(
        "para A B B C",
        "para A B A C",
    ),
)

R83_BETWEEN_CONDITION_I = Rule(
    id="r83",
    description="Betweeness condition I",
    premises_txt=("coll A B C", "obtuse_angle A B C"),
    conclusions_txt=("lequation 1/1 A B 1/1 B C -1/1 A C 0",),
)

R84_BETWEEN_CONDITION_II = Rule(
    id="r84",
    description="Betweeness condition II",
    premises_txt=("lequation 1/1 A B 1/1 B C -1/1 A C 0",),
    conclusions_txt=("coll A B C",),
)

R85_GENERALIZED_PYTHAGORAS_I = Rule(
    id="r85",
    description="Generalized Pythagorean theorem I",
    premises_txt=("perp A B C D",),
    conclusions_txt=(
        "lequation 1/1 A C * A C 1/1 B D * B D -1/1 A D * A D -1/1 B C * B C 0",
    ),
)

R86_GENERALIZED_PYTHAGORAS_II = Rule(
    id="r86",
    description="Generalized Pythagorean theorem II",
    premises_txt=(
        "lequation 1/1 A C * A C 1/1 B D * B D -1/1 A D * A D -1/1 B C * B C 0",
        "ncoll A B C",
    ),
    conclusions_txt=("perp A B C D",),
)

R87_CIRCUMCENTER_CHARACTERIZATION_I = Rule(
    id="r87",
    description="Characterization of circumcenter I",
    premises_txt=(
        "cong O A O C",
        "aequation 1/1 A B B C 1/1 C A A O 90o",
    ),
    conclusions_txt=("circle O A B C",),
)

R88_CIRCUMCENTER_CHARACTERIZATION_II = Rule(
    id="r88",
    description="Characterization of circumcenter II",
    premises_txt=("circle O A B C",),
    conclusions_txt=("aequation 1/1 A B B C 1/1 C A A O 90o",),
)

R89_LENGTH_OF_MEDIAN = Rule(
    id="r89",
    description="Length of a median of a triangle",
    premises_txt=(
        "midp M A B",
        "ncoll A B C",
    ),
    conclusions_txt=(
        "lequation 2/1 A M * A M -2/1 B C * B C -2/1 A C * A C 1/1 A B * A B 0",
    ),
)

R90_PARALLELOGRAM_LAW = Rule(
    id="r90",
    description="Parallelogram law",
    premises_txt=(
        "para A B C D",
        "para A D B C",
        "ncoll A B C",
    ),
    conclusions_txt=(
        "lequation 2/1 A B * A B 2/1 B C * B C -1/1 A C * A C -1/1 B D * B D 0",
    ),
)

R91_ANGLES_OF_ISO_TRAPEZOID = Rule(
    id="r91",
    description="Equal angles in an isosceles trapezoid",
    premises_txt=(
        "cong A B C D",
        "para A D B C",
        "npara A B C D",
    ),
    conclusions_txt=("eqangle C A C B B C B D",),
)

R92_DIAMETER_CROSSES_CENTER = Rule(
    id="r92",
    description="Any diameter of a circle crosses the center",
    premises_txt=(
        "midp O A B",
        "circle O A B C",
        "cyclic A B C D",
        "cong A B C D",
    ),
    conclusions_txt=("coll O C D",),
)

ALL_RULES: list[Rule] = [
    R00_PERPENDICULARS_GIVE_PARALLEL,
    R01_DEFINITION_OF_CYCLIC,
    R02_PARALLEL_FROM_INCLINATION,
    R03_ARC_DETERMINES_INTERNAL_ANGLES,
    R04_CONGRUENT_ANGLES_ARE_IN_A_CYCLIC,
    R05_SAME_ARC_SAME_CHORD,
    R06_BASE_OF_HALF_TRIANGLE,
    R07_THALES_THEOREM_1,
    R08_RIGHT_TRIANGLES_COMMON_ANGLE_1,
    R09_SUM_OF_ANGLES_OF_A_TRIANGLE,
    R10_RATIO_CANCELLATION,
    R11_BISECTOR_THEOREM_1,
    R12_BISECTOR_THEOREM_2,
    R13_ISOSCELES_TRIANGLE_EQUAL_ANGLES,
    R14_EQUAL_BASE_ANGLES_IMPLY_ISOSCELES,
    R15_ARC_DETERMINES_INSCRIBED_ANGLES_TANGENT,
    R16_SAME_ARC_GIVING_TANGENT,
    R17_CENTRAL_ANGLE_VS_INSCRIBED_ANGLE_1,
    R18_CENTRAL_ANGLE_VS_INSCRIBED_ANGLE_2,
    R19_HYPOTENUSE_IS_DIAMETER,
    R20_DIAMETER_IS_HYPOTENUSE,
    R21_CYCLIC_TRAPEZOID,
    R22_BISECTOR_CONSTRUCTION,
    R23_BISECTOR_IS_PERPENDICULAR,
    R24_CYCLIC_KITE,
    R25_DIAGONALS_OF_PARALLELOGRAM_1,
    R26_DIAGONALS_OF_PARALLELOGRAM_2,
    R27_THALES_THEOREM_2,
    R28_OVERLAPPING_PARALLELS,
    R29_MIDPOINT_IS_AN_EQRATIO,
    R30_RIGHT_TRIANGLES_COMMON_ANGLE_2,
    R31_DENOMINATOR_CANCELLING,
    R34_AA_SIMILARITY_OF_TRIANGLES_DIRECT,
    R35_AA_SIMILARITY_OF_TRIANGLES_REVERSE,
    R36_ASA_CONGRUENCE_OF_TRIANGLES_DIRECT,
    R37_ASA_CONGRUENCE_OF_TRIANGLES_REVERSE,
    R41_THALES_THEOREM_3,
    R42_THALES_THEOREM_4,
    R43_ORTHOCENTER_THEOREM,
    R44_PAPPUS_THEOREM,
    R45_SIMSONS_LINE_THEOREM,
    R46_INCENTER_THEOREM,
    R47_CIRCUMCENTER_THEOREM,
    R48_CENTROID_THEOREM,
    R49_RECOGNIZE_CENTER_OF_CIRCLE_CYCLIC,
    R50_RECOGNIZE_CENTER_OF_CYCLIC_CONG,
    R51_MIDPOINT_SPLITS_IN_TWO,
    R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES,
    R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES,
    R54_DEFINITION_OF_MIDPOINT,
    R55_MIDPOINT_CONG_PROPERTIES,
    R56_MIDPOINT_COLL_PROPERTIES,
    R57_PYTHAGORAS_THEOREM,
    R58_SAME_CHORD_SAME_ARC_1,
    R59_SAME_CHORD_SAME_ARC_2,
    R60_SSS_SIMILARITY_OF_TRIANGLES_DIRECT,
    R61_SSS_SIMILARITY_OF_TRIANGLES_REVERSE,
    R62_SAS_SIMILARITY_OF_TRIANGLES_DIRECT,
    R63_SAS_SIMILARITY_OF_TRIANGLES_REVERSE,
    R64_SSS_CONGRUENCE_OF_TRIANGLES_DIRECT,
    R65_SSS_CONGRUENCE_OF_TRIANGLES_REVERSE,
    R66_SAS_CONGRUENCE_OF_TRIANGLES_DIRECT,
    R67_SAS_CONGRUENCE_OF_TRIANGLES_REVERSE,
    R68_SIMILARITY_WITHOUT_SCALING_DIRECT,
    R69_SIMILARITY_WITHOUT_SCALING_REVERSE,
    R70_PROJECTIVE_HARMONIC_CONJUGATE,
    R71_RESOLUTION_OF_RATIOS,
    R72_DISASSEMBLING_A_CIRCLE,
    R73_DEFINITION_OF_CIRCLE,
    R74_INTERSECTION_BISECTORS,
    R76_CENTER_DIA,
    R77_CONGRUENT_TRIANGLES_DIRECT_PROPERTIES,
    R78_CONGRUENT_TRIANGLES_REVERSE_PROPERTIES,
    R79_MULTIPLY_CONG_BY_ONE,
    R80_SAME_CHORD_SAME_ARC_FOUR_POINTS_1,
    R81_SAME_CHORD_SAME_ARC_FOUR_POINTS_2,
    R82_PARA_OF_COLL,
    R83_BETWEEN_CONDITION_I,
    R84_BETWEEN_CONDITION_II,
    R85_GENERALIZED_PYTHAGORAS_I,
    R86_GENERALIZED_PYTHAGORAS_II,
    R87_CIRCUMCENTER_CHARACTERIZATION_I,
    R88_CIRCUMCENTER_CHARACTERIZATION_II,
    R89_LENGTH_OF_MEDIAN,
    R90_PARALLELOGRAM_LAW,
    R91_ANGLES_OF_ISO_TRAPEZOID,
    R92_DIAMETER_CROSSES_CENTER,
]
"""List of all rules that existed at some point in the history of Newclid"""

DEACTIVATED_RULES: set[Rule] = {
    R57_PYTHAGORAS_THEOREM,
}
"""Rules deactivated because they were problematic for current use cases."""

TRIAGE_NO_RULE_NEEDED: set[Rule] = {
    R00_PERPENDICULARS_GIVE_PARALLEL,
    R02_PARALLEL_FROM_INCLINATION,
    R08_RIGHT_TRIANGLES_COMMON_ANGLE_1,
    R09_SUM_OF_ANGLES_OF_A_TRIANGLE,
    R10_RATIO_CANCELLATION,
    R30_RIGHT_TRIANGLES_COMMON_ANGLE_2,
    R31_DENOMINATOR_CANCELLING,
    R72_DISASSEMBLING_A_CIRCLE,
    R73_DEFINITION_OF_CIRCLE,
    # R79_MULTIPLY_CONG_BY_ONE,
}
"""Rules that can be proven by the functioning of the engine and AR (no rule needed)."""

TRIAGE_LEAVE_RULE_OUT: set[Rule] = {
    R00_PERPENDICULARS_GIVE_PARALLEL,
    R01_DEFINITION_OF_CYCLIC,
    R02_PARALLEL_FROM_INCLINATION,
    R05_SAME_ARC_SAME_CHORD,
    R06_BASE_OF_HALF_TRIANGLE,
    R08_RIGHT_TRIANGLES_COMMON_ANGLE_1,
    R09_SUM_OF_ANGLES_OF_A_TRIANGLE,
    R10_RATIO_CANCELLATION,
    R13_ISOSCELES_TRIANGLE_EQUAL_ANGLES,
    R14_EQUAL_BASE_ANGLES_IMPLY_ISOSCELES,
    R15_ARC_DETERMINES_INSCRIBED_ANGLES_TANGENT,
    R16_SAME_ARC_GIVING_TANGENT,
    R17_CENTRAL_ANGLE_VS_INSCRIBED_ANGLE_1,
    R18_CENTRAL_ANGLE_VS_INSCRIBED_ANGLE_2,
    R21_CYCLIC_TRAPEZOID,
    R22_BISECTOR_CONSTRUCTION,
    R23_BISECTOR_IS_PERPENDICULAR,
    R24_CYCLIC_KITE,
    R29_MIDPOINT_IS_AN_EQRATIO,
    R30_RIGHT_TRIANGLES_COMMON_ANGLE_2,
    R31_DENOMINATOR_CANCELLING,
    R45_SIMSONS_LINE_THEOREM,
    R47_CIRCUMCENTER_THEOREM,
    R48_CENTROID_THEOREM,
    R55_MIDPOINT_CONG_PROPERTIES,
    R72_DISASSEMBLING_A_CIRCLE,
    R73_DEFINITION_OF_CIRCLE,
    R76_CENTER_DIA,
    # R79_MULTIPLY_CONG_BY_ONE,
}
"""Rules that can be proven by other rules, so are redundant."""

DEFAULT_RULES: set[Rule] = (
    set(ALL_RULES) - DEACTIVATED_RULES - TRIAGE_NO_RULE_NEEDED - TRIAGE_LEAVE_RULE_OUT
)
"""The rules effectively used on a normal run of the engine."""
