import logging

import numpy as np
import pytest
from newclid.all_rules import (
    ALL_RULES,
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
)
from newclid.api import GeometricSolverBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.rule import Rule

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


PROBLEM_FOR_RULE: dict[Rule, str] = {
    R00_PERPENDICULARS_GIVE_PARALLEL: "a = free a; b = free b; c = free c; d = on_tline d c a b; e = free e; f = on_tline f e c d ? para a b e f",
    R01_DEFINITION_OF_CYCLIC: "o = free o; a = free a; b = eqdistance b o o a; c = eqdistance c o o b; d = eqdistance d o o c ? cyclic a b c d",
    R02_PARALLEL_FROM_INCLINATION: "p = free p; q = free q; a = free a; b = free b; c = free c; d = on_aline0 d p q a b p q c ? para a b c d",
    R03_ARC_DETERMINES_INTERNAL_ANGLES: "a = free a; b = free b; p = free p; q = on_circum q a b p ? eqangle p a p b q a q b; eqangle a q a p b q b p; eqangle a b b q a p p q; eqangle a b a p q b q p",
    R04_CONGRUENT_ANGLES_ARE_IN_A_CYCLIC: "a = free a; b = free b; q = free q; p = eqangle3 p a b q a b ? cyclic a b p q",
    R05_SAME_ARC_SAME_CHORD: "a = free a; b = free b; c = free c; p = on_circum p a b c; r = on_circum r a b c; q = on_circum q a b c, on_aline q r p b c a ? cong a b p q",
    R06_BASE_OF_HALF_TRIANGLE: "a = free a; b = free b; c = free c; e = midpoint e a b; f = midpoint f a c ? para e f b c",
    R07_THALES_THEOREM_1: "a = free a; b = free b; c = free c; d = on_pline d c a b; o = on_line o a c, on_line o b d ? eqratio o a o c o b o d; eqratio o a c a o b b d; eqratio o c a c o d b d",
    R08_RIGHT_TRIANGLES_COMMON_ANGLE_1: "a = free a; b = free b; c = free c; d = on_tline d c a b; e = free e; f = free f; g = free g; h = on_tline h g e f ? eqangle a b e f c d g h",
    R09_SUM_OF_ANGLES_OF_A_TRIANGLE: "c = free c; d = free d; p = free p; q = free q; a = free a; b = free b; m = free m; n = on_aline0 n c d a b p q m; e = free e; f = free f; r = free r; u = on_aline0 u c d e f p q r ? eqangle a b e f m n r u",
    R10_RATIO_CANCELLATION: "a = free a; b = free b; c = free c; d = free d; m = free m; n = free n; p = free p; q = eqratio q a b c d m n p; e = free e; f = free f; r = free r; u = eqratio u c d e f p q r ? eqratio a b e f m n r u",
    R11_BISECTOR_THEOREM_1: "a = free a; b = free b; c = free c; d = eqratio6 d b c a b a c, on_line d b c ? eqangle a b a d a d a c",
    R12_BISECTOR_THEOREM_2: "a = free a; b = free b; d = free d; c = on_line c b d, on_aline c a d d a b ? eqratio d b d c a b a c",
    R13_ISOSCELES_TRIANGLE_EQUAL_ANGLES: "o = free o; a = free a; b = eqdistance b o o a ? eqangle o a a b a b o b",
    R14_EQUAL_BASE_ANGLES_IMPLY_ISOSCELES: "a = free a; b = free b; o = iso_triangle_vertex_angle o a b ? cong o a o b",
    R15_ARC_DETERMINES_INSCRIBED_ANGLES_TANGENT: "a = free a; b = free b; c = free c; o = circle o a b c; x = on_tline x a a o ? eqangle a x a b c a c b",
    R16_SAME_ARC_GIVING_TANGENT: "a = free a; b = free b; c = free c; o = circle o a b c; x = on_aline x a b a c b ? perp o a a x",
    R17_CENTRAL_ANGLE_VS_INSCRIBED_ANGLE_1: "a = free a; b = free b; c = free c; o = circle o a b c; m = midpoint m b c ? eqangle a b a c o b o m",
    R18_CENTRAL_ANGLE_VS_INSCRIBED_ANGLE_2: "a = free a; b = free b; c = free c; o = circle o a b c; m = on_line m b c, on_aline m o b c a b ? midp m b c",
    R19_HYPOTENUSE_IS_DIAMETER: "a = free a; b = free b; c = on_tline c b b a; m = midpoint m a c ? cong a m b m",
    R20_DIAMETER_IS_HYPOTENUSE: "o a b c = test_r20 o a b c ? perp a b b c",
    R21_CYCLIC_TRAPEZOID: "a = free a; b = free b; c = free c; d = on_pline d c a b, on_circum d a b c ? eqangle a d c d c d c b",
    R22_BISECTOR_CONSTRUCTION: "a = free a; b = free b; m = midpoint m a b; o = on_tline o m a b ? cong o a o b",
    R23_BISECTOR_IS_PERPENDICULAR: "a = free a; p = free p; q = free q; b = eqdistance b p a p, eqdistance b q a q ? perp a b p q",
    R24_CYCLIC_KITE: "a = free a; b = free b; p = iso_triangle_vertex p a b; q = iso_triangle_vertex q a b, on_circum q a b p ? perp p a a q",
    R25_DIAGONALS_OF_PARALLELOGRAM_1: "a b c d m = test_r25 a b c d m ? para a c b d",
    R26_DIAGONALS_OF_PARALLELOGRAM_2: "a = free a; b = free b; c = free c; d = on_pline d b a c, on_pline d a b c; m = midpoint m a b ? midp m c d",
    R27_THALES_THEOREM_2: "o = free o; a = free a; b = free b; c = on_line c a o; d = eqratio d o a a c o b b, on_line d o b ? para a b c d",
    R28_OVERLAPPING_PARALLELS: "a = free a; b = free b; c = on_pline0 c a b a ? coll a b c",
    R29_MIDPOINT_IS_AN_EQRATIO: "a = free a; b = free b; c = free c; d = free d; m = midpoint m a b; n = midpoint n c d ? eqratio m a a b n c c d",
    R30_RIGHT_TRIANGLES_COMMON_ANGLE_2: "p = free p; q = free q; u = free u; v = on_tline v u p q; a = free a; b = free b; c = free c; d = on_aline0 d p q a b u v c ? perp a b c d",
    R31_DENOMINATOR_CANCELLING: "p = free p; q = free q; u = free u; v = eqdistance v u p q; a = free a; b = free b; c = free c; d = eqratio d p q a b u v c ? cong a b c d",
    R34_AA_SIMILARITY_OF_TRIANGLES_DIRECT: "a = free a; b = free b; c = free c; q = free q; r = free r; p = on_aline p q r a b c, on_aline p r q a c b ? simtri a b c p q r",
    R35_AA_SIMILARITY_OF_TRIANGLES_REVERSE: "a b c = triangle a b c; q r = segment q r; p = on_aline p q r c b a , on_aline p r q b c a ? simtrir a b c p q r",
    R36_ASA_CONGRUENCE_OF_TRIANGLES_DIRECT: "a = free a; b = free b; p = free p; q = eqdistance q p a b; r = free r; c = on_aline c b a r q p, eqangle3 c a b r p q ? contri a b c p q r",
    R37_ASA_CONGRUENCE_OF_TRIANGLES_REVERSE: "a = free a; b = free b; p = free p; q = eqdistance q p a b; r = free r; c = on_aline c b a p q r, eqangle3 c a b r q p ? contrir a b c p q r",
    R41_THALES_THEOREM_3: "a = free a; b = free b; c = free c; d = on_pline d c a b; n = on_line n b c; m = eqratio6 m a d n b n c, on_line m a d ? para m n a b",
    R42_THALES_THEOREM_4: "a = free a; b = free b; c = free c; d = on_pline d c a b; m = on_line m a d; n = on_line n b c, on_pline n m a b ? eqratio m a m d n b n c",
    R43_ORTHOCENTER_THEOREM: "a b c = triangle a b c; d = on_tline d c a b, on_tline d b a c ? perp a d b c",
    R44_PAPPUS_THEOREM: "a b = segment a b; c = on_line c a b; p q = segment p q; r = on_line r p q; x = on_line x a q, on_line x p b; y = on_line y a r, on_line y p c; z = on_line z b r, on_line z c q ? coll x y z",
    R45_SIMSONS_LINE_THEOREM: "a b c = triangle a b c; p = on_circum p a b c; l = on_line l a c, on_tline l p a c; m = on_line m b c, on_tline m p b c; n = on_line n a b, on_tline n p a b ? coll l m n",
    R46_INCENTER_THEOREM: "a b c = triangle a b c; x = angle_bisector x b a c, angle_bisector x a b c ? eqangle c b c x c x c a",
    R47_CIRCUMCENTER_THEOREM: "a b c = triangle a b c; m = midpoint m a b; n = midpoint n b c; p = midpoint p c a; x = on_tline x m a b, on_tline x n b c ? perp x p c a",
    R48_CENTROID_THEOREM: "a b c = triangle a b c; m = midpoint m a b; n = midpoint n b c; p = midpoint p c a; x = on_line x m c, on_line x n a ? coll x p b",
    R49_RECOGNIZE_CENTER_OF_CIRCLE_CYCLIC: "a b c = triangle a b c; o = circle o a b c; d = on_circum d a b c ? cong o a o d",
    R50_RECOGNIZE_CENTER_OF_CYCLIC_CONG: "a = free a; b = free b; c = free c; d = on_circum d a b c; o = on_bline o a b, on_bline o c d ? cong o a o c",
    R51_MIDPOINT_SPLITS_IN_TWO: "a b = segment a b; m = midpoint m a b ? rconst m a a b 1/2",
    R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES: "a b c = triangle a b c; p q = segment p q; r = simtri r a b c p q ? eqangle b a b c q p q r; eqangle a b a c p q p r; eqangle a c b c p r q r; eqratio b a b c q p q r; eqratio b c a c q r p r",
    R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES: "a b c = triangle a b c; p q = segment p q; r = simtrir r a b c p q ? eqangle b a b c q r q p; eqangle a b a c p r p q; eqangle a c b c q r p r; eqratio b a b c q p q r; eqratio b c a c q r p r",
    R54_DEFINITION_OF_MIDPOINT: "a b = segment a b; m = on_line m a b, on_bline m a b ? midp m a b",
    R55_MIDPOINT_CONG_PROPERTIES: "a b = segment a b; m = midpoint m a b ? cong m a m b",
    R56_MIDPOINT_COLL_PROPERTIES: "a b = segment a b; m = midpoint m a b ? coll m a b",
    # R57_PYTHAGORAS_THEOREM: "a = free a; b = lconst b a 4; c = on_tline c b a b, lconst c b 3 ? lconst a c 5", TODO: Fix it and split it into two rules for forward and backward
    R58_SAME_CHORD_SAME_ARC_1: "a = free a; b = free b; c = free c; p = on_circum p a b c; q = on_circum q b c p, eqdistance q p a b; r = on_circum r c p q ? sameclock c a b r p q; sameside c a b r p q; eqangle c a c b r p r q",
    R59_SAME_CHORD_SAME_ARC_2: "a = free a; b = free b; c = free c; p = on_circum p a b c; q = on_circum q b c p, eqdistance q p a b; r = on_circum r c p q ? sameclock c b a r p q; nsameside c b a r p q; eqangle c a c b r p r q",
    R60_SSS_SIMILARITY_OF_TRIANGLES_DIRECT: "a b c = triangle a b c; p q = segment p q; r = eqratio r b a b c q p q, eqratio6 r p q c a c b ?  sameclock a b c p q r; simtri a b c p q r",
    R61_SSS_SIMILARITY_OF_TRIANGLES_REVERSE: "a b c = triangle a b c; p q = segment p q; r = eqratio r b a b c q p q, eqratio6 r p q c a c b ? sameclock a b c p r q; simtrir a b c p q r",
    R62_SAS_SIMILARITY_OF_TRIANGLES_DIRECT: "a b c = triangle a b c; p q = segment p q; r = eqratio r b a b c q p q, on_aline0 r b a b c q p q ? sameclock a b c p q r; simtri a b c p q r",
    R63_SAS_SIMILARITY_OF_TRIANGLES_REVERSE: "a b c = triangle a b c; p q = segment p q; r = eqratio r b a b c q p q, on_aline0 r b c b a q p q ? sameclock a b c p r q; simtrir a b c p q r",
    R64_SSS_CONGRUENCE_OF_TRIANGLES_DIRECT: "a b c = triangle a b c; p = free p; q = eqdistance q p a b; r = eqdistance r q b c, eqdistance r p a c ? sameclock a b c p q r; contri a b c p q r",
    R65_SSS_CONGRUENCE_OF_TRIANGLES_REVERSE: "a b c = triangle a b c; p = free p; q = eqdistance q p a b; r = eqdistance r q b c, eqdistance r p a c ? sameclock a b c p r q; contrir a b c p q r",
    R66_SAS_CONGRUENCE_OF_TRIANGLES_DIRECT: "a b c = triangle a b c; p = free p; q = eqdistance q p a b; r = eqdistance r q b c, on_aline0 r b a b c q p q ? sameclock a b c p q r; contri a b c p q r",
    R67_SAS_CONGRUENCE_OF_TRIANGLES_REVERSE: "a b c = triangle a b c; p = free p; q = eqdistance q p a b; r = eqdistance r q b c, on_aline0 r b c b a q p q ? sameclock a b c p r q; contrir a b c p q r",
    R68_SIMILARITY_WITHOUT_SCALING_DIRECT: "a b c = triangle a b c; p = free p; q = eqdistance q p a b; r = eqratio r b a b c q p q, eqratio6 r p q c a c b ? sameclock a b c p q r; contri a b c p q r",
    R69_SIMILARITY_WITHOUT_SCALING_REVERSE: "a b c = triangle a b c; p = free p; q = eqdistance q p a b; r = eqratio r b a b c q p q, eqratio6 r p q c a c b ? sameclock a b c p r q; contrir a b c p q r",
    R70_PROJECTIVE_HARMONIC_CONJUGATE: "a b = segment a b; c = on_line c a b; l = free l; m = on_line m a l; n = on_line n l b, on_line n m c; k = on_line k a n, on_line k b m; d = on_line d a b, on_line d k l ? eqratio a c a d b c b d",
    R71_RESOLUTION_OF_RATIOS: "a b = segment a b; c = on_line c a b; d e = segment d e; f = on_line f d e, eqratio f a b a c d e d ? eqratio a b b c d e e f",
    R72_DISASSEMBLING_A_CIRCLE: "a = free a; b = free b; c = free c; o = circle o a b c ? cong o a o b; cong o b o c",
    R73_DEFINITION_OF_CIRCLE: "o a = segment o a; b = eqdistance b o o a; c = eqdistance c o o b ? circle o a b c",
    R74_INTERSECTION_BISECTORS: "a b c = triangle a b c; d = on_bline d a b, angle_bisector d a c b ? cyclic a b c d",
    R76_CENTER_DIA: "a b = segment a b; c = on_tline c a a b; m = on_bline m a b, on_line m b c ? midp m b c",
    R77_CONGRUENT_TRIANGLES_DIRECT_PROPERTIES: "a b c = triangle a b c; p = free p; q r = contri q r a b c p ? simtri a b c p q r; cong a b p q",
    R78_CONGRUENT_TRIANGLES_REVERSE_PROPERTIES: "a b c = triangle a b c; p = free p; q r = contrir q r a b c p ? simtrir a b c p q r; cong a b p q",
    R79_MULTIPLY_CONG_BY_ONE: "a b = segment a b; c = free c; d = eqdistance d c a b; x y = segment x y ? eqratio a b x y c d x y",
    R80_SAME_CHORD_SAME_ARC_FOUR_POINTS_1: "p b = segment p b; a = free a; q = on_circum q a p b, eqdistance q p a b ? sameclock a p b a q p; eqangle p a p b p b q b",
    R81_SAME_CHORD_SAME_ARC_FOUR_POINTS_2: "p b = segment p b; a = free a; q = on_circum q a p b, eqdistance q p a b ? sameclock a p b a p q; eqangle p a p b q b p b",
    R82_PARA_OF_COLL: "a b = segment a b; c = on_line c a b ? para a b b c; para a b a c",
    R83_BETWEEN_CONDITION_I: "c a b = between c a b ? lequation 1/1 a c 1/1 c b -1/1 a b 0/1",
    # R84_BETWEEN_CONDITION_II:
    R85_GENERALIZED_PYTHAGORAS_I: "a b = segment a b; c = free c; d = on_tline d c a b ? lequation 1/1 a c * a c 1/1 b d * b d -1/1 a d * a d -1/1 b c * b c 0",
    # R86_GENERALIZED_PYTHAGORAS_II:
    # R87_CIRCUMCENTER_CHARACTERIZATION_I:
    R88_CIRCUMCENTER_CHARACTERIZATION_II: "a b c = triangle a b c; o = circle o a b c ? aequation 1/1 A B B C 1/1 C A A O 90o",
    R89_LENGTH_OF_MEDIAN: "a b c = triangle a b c; m = midpoint m a b ? lequation 2/1 A M * A M -2/1 B C * B C -2/1 A C * A C 1/1 A B * A B 0",
    R90_PARALLELOGRAM_LAW: "a b = segment a b; c = free c; d = on_pline d c a b, on_pline d a b c ? lequation 2/1 A B * A B 2/1 B C * B C -1/1 A C * A C -1/1 B D * B D 0",
    R91_ANGLES_OF_ISO_TRAPEZOID: "a b = segment a b; c = free a; d = on_pline d a b c, eqdistance d c a b ? eqangle c a c b b c b d",
}


EXTRA_RULES = {
    # C++ engine matches only some of combinatorial versions.
    # Need to get closure using `cyclic`
    # to ensure that the version in the problem is proved.
    R80_SAME_CHORD_SAME_ARC_FOUR_POINTS_1: [
        R03_ARC_DETERMINES_INTERNAL_ANGLES,
        R04_CONGRUENT_ANGLES_ARE_IN_A_CYCLIC,
    ],
    # C++ engine assume `simtri` instead of `eqratio`s
    R68_SIMILARITY_WITHOUT_SCALING_DIRECT: [R60_SSS_SIMILARITY_OF_TRIANGLES_DIRECT],
    # C++ engine assume `simtri` instead of `eqratio`s
    R69_SIMILARITY_WITHOUT_SCALING_REVERSE: [R61_SSS_SIMILARITY_OF_TRIANGLES_REVERSE],
}


@pytest.mark.parametrize("rule", ALL_RULES, ids=[r.id for r in ALL_RULES])
def test_rule(rule: Rule):
    """
    Test that all rules from `ALL_RULES` are solvable by the rules reported by `Yuclid`.
    """
    if rule not in PROBLEM_FOR_RULE:
        pytest.skip(f"No problem for rule {rule.fullname}")

    YUCLID_RULES: list[Rule] = pytest.importorskip(
        "py_yuclid.yuclid_adapter"
    ).YUCLID_RULES

    if rule in (
        R44_PAPPUS_THEOREM,
        R70_PROJECTIVE_HARMONIC_CONJUGATE,
        R83_BETWEEN_CONDITION_I,
        R84_BETWEEN_CONDITION_II,
        R85_GENERALIZED_PYTHAGORAS_I,
        R86_GENERALIZED_PYTHAGORAS_II,
        R87_CIRCUMCENTER_CHARACTERIZATION_I,
        R88_CIRCUMCENTER_CHARACTERIZATION_II,
        R89_LENGTH_OF_MEDIAN,
        R90_PARALLELOGRAM_LAW,
    ):
        pytest.skip(f"Rule {rule.fullname} not matched yet")
    rules: list[Rule] = []
    if rule in EXTRA_RULES:
        rules = EXTRA_RULES[rule] + [rule]
    elif rule in YUCLID_RULES:
        rules = [rule]
    else:
        rules = list(YUCLID_RULES)
    problem_txt = PROBLEM_FOR_RULE[rule]

    LOGGER.info(f"Testing rule {rule} with problem {problem_txt}")
    rng = np.random.default_rng(123)
    solver_builder = GeometricSolverBuilder(rng=rng).with_rules(rules)
    problem_builder = JGEXProblemBuilder(rng=rng).with_problem_from_txt(problem_txt)
    solver = solver_builder.build(problem_builder.build())
    success = solver.run()
    assert success
