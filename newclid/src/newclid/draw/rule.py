from typing import List

from matplotlib.artist import Artist
from matplotlib.axes import Axes

from newclid.all_rules import (
    R03_ARC_DETERMINES_INTERNAL_ANGLES,
    R04_CONGRUENT_ANGLES_ARE_IN_A_CYCLIC,
    R11_BISECTOR_THEOREM_1,
    R12_BISECTOR_THEOREM_2,
    R13_ISOSCELES_TRIANGLE_EQUAL_ANGLES,
    R14_EQUAL_BASE_ANGLES_IMPLY_ISOSCELES,
    R19_HYPOTENUSE_IS_DIAMETER,
    R28_OVERLAPPING_PARALLELS,
    R34_AA_SIMILARITY_OF_TRIANGLES_DIRECT,
    R35_AA_SIMILARITY_OF_TRIANGLES_REVERSE,
    R41_THALES_THEOREM_3,
    R42_THALES_THEOREM_4,
    R43_ORTHOCENTER_THEOREM,
    R46_INCENTER_THEOREM,
    R49_RECOGNIZE_CENTER_OF_CIRCLE_CYCLIC,
    R50_RECOGNIZE_CENTER_OF_CYCLIC_CONG,
    R51_MIDPOINT_SPLITS_IN_TWO,
    R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES,
    R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES,
    R54_DEFINITION_OF_MIDPOINT,
    R56_MIDPOINT_COLL_PROPERTIES,
    R60_SSS_SIMILARITY_OF_TRIANGLES_DIRECT,
    R61_SSS_SIMILARITY_OF_TRIANGLES_REVERSE,
    R62_SAS_SIMILARITY_OF_TRIANGLES_DIRECT,
    R63_SAS_SIMILARITY_OF_TRIANGLES_REVERSE,
    R68_SIMILARITY_WITHOUT_SCALING_DIRECT,
    R69_SIMILARITY_WITHOUT_SCALING_REVERSE,
    R71_RESOLUTION_OF_RATIOS,
    R72_DISASSEMBLING_A_CIRCLE,
    R73_DEFINITION_OF_CIRCLE,
    R74_INTERSECTION_BISECTORS,
    R77_CONGRUENT_TRIANGLES_DIRECT_PROPERTIES,
    R78_CONGRUENT_TRIANGLES_REVERSE_PROPERTIES,
    R80_SAME_CHORD_SAME_ARC_FOUR_POINTS_1,
    R82_PARA_OF_COLL,
)
from newclid.draw.geometries import draw_arrow, draw_circle, draw_segment, draw_triangle
from newclid.draw.predicates import (
    draw_free_perpendicular_symbol,
    draw_line,
    draw_predicate,
)
from newclid.draw.theme import DrawTheme
from newclid.jgex.geometries import (
    JGEXPoint,
    line_line_intersection,
    perpendicular_bisector,
)
from newclid.justifications.justification import RuleApplication
from newclid.numerical.geometries import PointNum
from newclid.predicates import Predicate
from newclid.predicates._index import PredicateType
from newclid.predicates.circumcenter import Circumcenter
from newclid.predicates.collinearity import Coll
from newclid.predicates.equal_angles import EqAngle
from newclid.predicates.triangles_congruent import ContriClock, ContriReflect
from newclid.predicates.triangles_similar import SimtriClock, SimtriReflect
from newclid.symbols.points_registry import Point, Segment
from newclid.symbols.symbols_registry import SymbolsRegistry
from sympy import li


def draw_rule_application(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    rule_applied = application.rule

    match rule_applied.id:
        case R03_ARC_DETERMINES_INTERNAL_ANGLES.id:
            return _draw_arc_determines_internal_angles(ax, application, theme)
        case R04_CONGRUENT_ANGLES_ARE_IN_A_CYCLIC.id:
            return _draw_congruent_angles_are_in_a_cyclic(ax, application, theme)
        case R11_BISECTOR_THEOREM_1.id:
            return _draw_bisector_from_eqratio_configuration(
                ax, application, symbols, theme
            )
        case R12_BISECTOR_THEOREM_2.id:
            return _draw_bisector_gives_eqratio_configuration(
                ax, application, symbols, theme
            )
        case R13_ISOSCELES_TRIANGLE_EQUAL_ANGLES.id:
            return _draw_isosceles_triangle_angles(ax, application, symbols, theme)
        case R14_EQUAL_BASE_ANGLES_IMPLY_ISOSCELES.id:
            return _draw_isosceles_triangle_angles_reverse(
                ax, application, symbols, theme
            )
        case R19_HYPOTENUSE_IS_DIAMETER.id:
            return _draw_hypotenuse_is_diameter(ax, application, theme)
        case R28_OVERLAPPING_PARALLELS.id:
            return _draw_coll_of_para(ax, application, theme)
        case R34_AA_SIMILARITY_OF_TRIANGLES_DIRECT.id:
            return _draw_sas_similarity_of_triangles_direct(
                ax, application, symbols, theme
            )
        case R35_AA_SIMILARITY_OF_TRIANGLES_REVERSE.id:
            return _draw_sas_similarity_of_triangles_reverse(
                ax, application, symbols, theme
            )
        case R41_THALES_THEOREM_3.id:
            return _draw_thales_configuration(ax, application, symbols, theme)
        case R42_THALES_THEOREM_4.id:
            return _draw_thales_configuration_giving_eqratio(
                ax, application, symbols, theme
            )
        case R43_ORTHOCENTER_THEOREM.id:
            return _draw_orthocenter_theorem(ax, application, symbols, theme)
        case R46_INCENTER_THEOREM.id:
            return _draw_incenter_theorem(ax, application, symbols, theme)
        case R49_RECOGNIZE_CENTER_OF_CIRCLE_CYCLIC.id:
            return _draw_recognize_center_of_circle(ax, application, theme)
        case R50_RECOGNIZE_CENTER_OF_CYCLIC_CONG.id:
            return _draw_center_and_concyclics(ax, application, theme)
        case R51_MIDPOINT_SPLITS_IN_TWO.id:
            return _draw_midpoint(ax, application, theme)
        case R52_SIMILAR_TRIANGLES_DIRECT_PROPERTIES.id:
            return _draw_similar_triangles_direct_properties(ax, application, theme)
        case R53_SIMILAR_TRIANGLES_REVERSE_PROPERTIES.id:
            return _draw_similar_triangles_reverse_properties(ax, application, theme)
        case R54_DEFINITION_OF_MIDPOINT.id:
            return _draw_midpoint_consequence(ax, application, theme)
        case R56_MIDPOINT_COLL_PROPERTIES.id:
            return _draw_midpoint(ax, application, theme)
        case R60_SSS_SIMILARITY_OF_TRIANGLES_DIRECT.id:
            return _draw_sas_similarity_of_triangles_direct(
                ax, application, symbols, theme
            )
        case R61_SSS_SIMILARITY_OF_TRIANGLES_REVERSE.id:
            return _draw_sas_similarity_of_triangles_reverse(
                ax, application, symbols, theme
            )
        case R62_SAS_SIMILARITY_OF_TRIANGLES_DIRECT.id:
            return _draw_sas_similarity_of_triangles_direct(
                ax, application, symbols, theme
            )
        case R63_SAS_SIMILARITY_OF_TRIANGLES_REVERSE.id:
            return _draw_sas_similarity_of_triangles_reverse(
                ax, application, symbols, theme
            )
        case R68_SIMILARITY_WITHOUT_SCALING_DIRECT.id:
            return _draw_direct_congruence(ax, application, symbols, theme)
        case R69_SIMILARITY_WITHOUT_SCALING_REVERSE.id:
            return _draw_reverse_congruence(ax, application, symbols, theme)
        case R71_RESOLUTION_OF_RATIOS.id:
            return _draw_resolution_of_ratios(ax, application, symbols, theme)
        case R72_DISASSEMBLING_A_CIRCLE.id:
            return _draw_disassembling_a_circle(ax, application, theme)
        case R73_DEFINITION_OF_CIRCLE.id:
            return _draw_assembling_a_circle(ax, application, theme)
        case R74_INTERSECTION_BISECTORS.id:
            return _draw_intersection_bisectors(ax, application, theme)
        case R77_CONGRUENT_TRIANGLES_DIRECT_PROPERTIES.id:
            return _draw_congruent_triangles_direct_properties(ax, application, theme)
        case R78_CONGRUENT_TRIANGLES_REVERSE_PROPERTIES.id:
            return _draw_congruent_triangles_reverse_properties(ax, application, theme)
        case R80_SAME_CHORD_SAME_ARC_FOUR_POINTS_1.id:
            return _draw_same_chord_same_arc_four_points_1(ax, application, symbols, theme)
        case R82_PARA_OF_COLL.id:
            return _draw_para_of_coll(ax, application, theme)
        case _:
            print(f"Rule {rule_applied.id} not implemented for drawing.")
            return []


def _draw_arc_determines_internal_angles(
    ax: Axes, application: RuleApplication, theme: DrawTheme
) -> list[Artist]:
    if application.predicate.predicate_type != PredicateType.EQUAL_ANGLES:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    if (
        len(application.premises) < 1
        or application.premises[0].predicate_type != PredicateType.CYCLIC
    ):
        raise ValueError(
            f"Unexpected premises for rule {application.rule}: {application.premises}"
        )

    angle1 = application.predicate.angle1
    angle2 = application.predicate.angle2

    vertex1 = _one_angle_vertex(angle1)
    vertex2 = _one_angle_vertex(angle2)

    angle_edges: list[Point] = []
    for line in angle1:
        for point in line:
            if point != vertex1:
                angle_edges.append(point)

    p1 = angle_edges[0]
    p2 = angle_edges[1]

    center = _circumcenter_of_triangle((p1, p2, vertex1))
    radius = center.distance(p1.num)

    return [
        draw_circle(
            ax,
            (center.x, center.y),
            radius,
            line_color=theme.circle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex1.num,
            p1.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex1.num,
            p2.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex2.num,
            p1.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex2.num,
            p2.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
    ]


def _draw_congruent_angles_are_in_a_cyclic(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    if application.predicate.predicate_type != PredicateType.CYCLIC:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    if (
        len(application.premises) < 1
        or application.premises[0].predicate_type != PredicateType.EQUAL_ANGLES
    ):
        raise ValueError(
            f"Unexpected premises for rule {application.rule}: {application.premises}"
        )

    angle1 = application.premises[0].angle1
    angle2 = application.premises[0].angle2

    vertex1 = _one_angle_vertex(angle1)
    vertex2 = _one_angle_vertex(angle2)

    angle_edges: list[Point] = []
    for line in angle1:
        for point in line:
            if point != vertex1:
                angle_edges.append(point)

    p1 = angle_edges[0]
    p2 = angle_edges[1]

    center = _circumcenter_of_triangle((p1, p2, vertex1))
    radius = center.distance(p1.num)

    return [
        draw_circle(
            ax,
            (center.x, center.y),
            radius,
            line_color=theme.circle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex1.num,
            p1.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex1.num,
            p2.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex2.num,
            p1.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex2.num,
            p2.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
    ]


def _draw_bisector_from_eqratio_configuration(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    if len(application.premises) != 3:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    coll = application.premises[0]
    if coll.predicate_type != PredicateType.COLLINEAR:
        raise ValueError(
            f"Unexpected premise for rule {application.rule}: {application.premises[1]}"
        )
    p1, p2, p3 = coll.points
    eqangle = application.predicate
    if eqangle.predicate_type != PredicateType.EQUAL_ANGLES:
        raise ValueError(
            f"Unexpected premise for rule {application.rule}: {application.predicate}"
        )
    vertex = _get_eqangle_vertex(eqangle)
    return [
        draw_segment(
            ax,
            p1.num,
            p2.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            p2.num,
            p3.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex.num,
            p1.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex.num,
            p2.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex.num,
            p3.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
    ] + list(draw_predicate(ax, eqangle, symbols, theme=theme))


def _draw_bisector_gives_eqratio_configuration(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    coll: Coll | None = None
    for premise in application.premises:
        if premise.predicate_type == PredicateType.COLLINEAR:
            coll = premise
            break

    if coll is None:
        raise ValueError(
            f"Missing coll premise for rule {application.rule}: {application.premises}"
        )
    p1, p2, p3 = coll.points

    eqangle: EqAngle | None = None
    for premise in application.premises:
        if premise.predicate_type == PredicateType.EQUAL_ANGLES:
            eqangle = premise
            break

    if eqangle is None:
        raise ValueError(
            f"Missing eqangle premise for rule {application.rule}: {application.premises}"
        )

    vertex = _get_eqangle_vertex(eqangle)
    return [
        draw_segment(
            ax,
            p1.num,
            p2.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            p2.num,
            p3.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex.num,
            p1.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex.num,
            p2.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            vertex.num,
            p3.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
    ] + list(draw_predicate(ax, eqangle, symbols, theme=theme))


def _draw_isosceles_triangle_angles(
    ax: Axes, application: RuleApplication, symbols: SymbolsRegistry, theme: DrawTheme
) -> list[Artist]:
    vertices: List[Point] = []
    if len(application.premises) != 1:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    if application.predicate.predicate_type != PredicateType.EQUAL_ANGLES:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    eqangle = application.predicate

    for point in eqangle.angle1[0]:
        if point not in vertices:
            vertices.append(point)
    for point in eqangle.angle1[1]:
        if point not in vertices:
            vertices.append(point)

    return [
        draw_triangle(
            ax,
            vertices[0].num,
            vertices[1].num,
            vertices[2].num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
    ] + list(draw_predicate(ax, eqangle, symbols, theme=theme))


def _draw_isosceles_triangle_angles_reverse(
    ax: Axes, application: RuleApplication, symbols: SymbolsRegistry, theme: DrawTheme
) -> list[Artist]:
    vertices: List[Point] = []
    if len(application.premises) != 2:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    if application.premises[0].predicate_type != PredicateType.EQUAL_ANGLES:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    eqangle = application.premises[0]

    for point in eqangle.angle1[0]:
        if point not in vertices:
            vertices.append(point)
    for point in eqangle.angle1[1]:
        if point not in vertices:
            vertices.append(point)

    return list(draw_predicate(ax, eqangle, symbols, theme=theme)) + [
        draw_triangle(
            ax,
            vertices[0].num,
            vertices[1].num,
            vertices[2].num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
    ]


def _draw_hypotenuse_is_diameter(
    ax: Axes, application: RuleApplication, theme: DrawTheme
) -> list[Artist]:
    vertices: List[Point] = []
    corners: List[Point] = []
    if len(application.premises) != 2:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    if application.premises[0].predicate_type != PredicateType.MIDPOINT:
        raise ValueError(
            f"Unexpected premise for rule {application.rule}: {application.premises[0]}"
        )
    midpoint = application.premises[0].midpoint
    if application.premises[1].predicate_type != PredicateType.PERPENDICULAR:
        raise ValueError(
            f"Unexpected premise for rule {application.rule}: {application.premises[1]}"
        )
    for point in application.premises[1].line1:
        if point not in vertices:
            vertices.append(point)
    for point in application.premises[1].line2:
        if point not in vertices:
            vertices.append(point)
    if application.predicate.predicate_type != PredicateType.CONGRUENT:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    for point in application.predicate.segment1:
        if point != midpoint:
            corners.append(point)
    for point in application.predicate.segment2:
        if point != midpoint:
            corners.append(point)
    radius = corners[0].num.distance(midpoint.num)

    return [
        draw_triangle(
            ax,
            vertices[0].num,
            vertices[1].num,
            vertices[2].num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            midpoint.num,
            corners[0].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            midpoint.num,
            corners[1].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_circle(
            ax,
            (midpoint.num.x, midpoint.num.y),
            radius,
            line_color=theme.circle_color,
            line_width=theme.thick_line_width,
        ),
    ]


def _draw_coll_of_para(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    if application.predicate.predicate_type != PredicateType.COLLINEAR:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    return [
        draw_segment(
            ax,
            application.predicate.points[0].num,
            application.predicate.points[1].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            application.predicate.points[1].num,
            application.predicate.points[2].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
    ]


def _draw_para_of_coll(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    coll = application.premises[0]
    if coll.predicate_type != PredicateType.COLLINEAR:
        raise ValueError(f"Unexpected premises for rule {application.rule}: {coll}")
    return [
        draw_segment(
            ax,
            coll.points[0].num,
            coll.points[1].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            coll.points[1].num,
            coll.points[2].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
    ]


def _draw_thales_configuration(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    if application.predicate.predicate_type != PredicateType.PARALLEL:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    para_consequence = application.predicate
    if len(application.premises) != 5:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    if application.premises[1].predicate_type != PredicateType.COLLINEAR:
        raise ValueError(
            f"Unexpected premise 1 for rule {application.rule}: {application.premises[1]}"
        )
    coll1 = application.premises[1]
    p1, p2, p3 = coll1.points
    if application.premises[2].predicate_type != PredicateType.EQUAL_RATIOS:
        raise ValueError(
            f"Unexpected premise 2 for rule {application.rule}: {application.premises[2]}"
        )
    eqratio = application.premises[2]
    if application.premises[3].predicate_type != PredicateType.PARALLEL:
        raise ValueError(
            f"Unexpected premise 3 for rule {application.rule}: {application.premises[3]}"
        )
    para_premise = application.premises[3]

    if application.premises[0].predicate_type != PredicateType.COLLINEAR:
        raise ValueError(
            f"Unexpected premise 0 for rule {application.rule}: {application.premises[0]}"
        )
    coll2 = application.premises[0]
    q1, q2, q3 = coll2.points

    return (
        list(draw_predicate(ax, para_consequence, symbols, theme=theme))
        + list(draw_predicate(ax, eqratio, symbols, theme=theme))
        + list(draw_predicate(ax, para_premise, symbols, theme=theme))
        + [
            draw_segment(
                ax,
                p1.num,
                p2.num,
                line_color=theme.line_color,
                line_width=theme.thick_line_width,
            ),
            draw_segment(
                ax,
                p2.num,
                p3.num,
                line_color=theme.line_color,
                line_width=theme.thick_line_width,
            ),
            draw_segment(
                ax,
                q1.num,
                q2.num,
                line_color=theme.line_color,
                line_width=theme.thick_line_width,
            ),
            draw_segment(
                ax,
                q2.num,
                q3.num,
                line_color=theme.line_color,
                line_width=theme.thick_line_width,
            ),
        ]
    )


def _draw_thales_configuration_giving_eqratio(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    if application.premises[2].predicate_type != PredicateType.PARALLEL:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    para_consequence = application.premises[2]
    if len(application.premises) != 4:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    if application.premises[1].predicate_type != PredicateType.COLLINEAR:
        raise ValueError(
            f"Unexpected premise 1 for rule {application.rule}: {application.premises[1]}"
        )
    coll1 = application.premises[1]
    p1, p2, p3 = coll1.points
    if application.predicate.predicate_type != PredicateType.EQUAL_RATIOS:
        raise ValueError(
            f"Unexpected premise 2 for rule {application.rule}: {application.premises[2]}"
        )
    eqratio = application.predicate
    if application.premises[3].predicate_type != PredicateType.PARALLEL:
        raise ValueError(
            f"Unexpected premise 3 for rule {application.rule}: {application.premises[3]}"
        )
    para_premise = application.premises[3]

    if application.premises[0].predicate_type != PredicateType.COLLINEAR:
        raise ValueError(
            f"Unexpected premise 0 for rule {application.rule}: {application.premises[0]}"
        )
    coll2 = application.premises[0]
    q1, q2, q3 = coll2.points

    return (
        list(draw_predicate(ax, para_consequence, symbols, theme=theme))
        + list(draw_predicate(ax, eqratio, symbols, theme=theme))
        + list(draw_predicate(ax, para_premise, symbols, theme=theme))
        + [
            draw_segment(
                ax,
                p1.num,
                p2.num,
                line_color=theme.line_color,
                line_width=theme.thick_line_width,
            ),
            draw_segment(
                ax,
                p2.num,
                p3.num,
                line_color=theme.line_color,
                line_width=theme.thick_line_width,
            ),
            draw_segment(
                ax,
                q1.num,
                q2.num,
                line_color=theme.line_color,
                line_width=theme.thick_line_width,
            ),
            draw_segment(
                ax,
                q2.num,
                q3.num,
                line_color=theme.line_color,
                line_width=theme.thick_line_width,
            ),
        ]
    )


def _draw_orthocenter_theorem(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    perps: List[Predicate] = []
    if application.predicate.predicate_type != PredicateType.PERPENDICULAR:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    else:
        perps.append(application.predicate)
    for premise in application.premises:
        if premise.predicate_type != PredicateType.PERPENDICULAR:
            raise ValueError(
                f"Unexpected premise for rule {application.rule}: {premise}"
            )
        else:
            perps.append(premise)
    p1, p2 = application.predicate.line1
    p3, p4 = application.predicate.line2
    predicate_artists: List[Artist] = []
    for perp in perps:
        predicate_artists.extend(
            draw_predicate(ax, perp, symbols, theme=theme)  # symbols are not used here
        )

    return [
        draw_segment(
            ax,
            p1.num,
            p2.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            p1.num,
            p3.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            p1.num,
            p4.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            p2.num,
            p3.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            p2.num,
            p4.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            p3.num,
            p4.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
    ] + predicate_artists


def _draw_incenter_theorem(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    vertices: List[Point] = []

    if len(application.premises) != 3:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    if application.premises[2].predicate_type != PredicateType.N_COLLINEAR:
        raise ValueError(
            f"Unexpected premise 2 for rule {application.rule}: {application.premises[2]}"
        )
    ncoll = application.premises[2]
    for point in ncoll.points:
        if point not in vertices:
            vertices.append(point)
    if application.premises[0].predicate_type != PredicateType.EQUAL_ANGLES:
        raise ValueError(
            f"Unexpected premise 0 for rule {application.rule}: {application.premises[0]}"
        )
    eqangle1 = application.premises[0]
    if application.premises[1].predicate_type != PredicateType.EQUAL_ANGLES:
        raise ValueError(
            f"Unexpected premise 1 for rule {application.rule}: {application.premises[1]}"
        )
    eqangle2 = application.premises[1]

    if application.predicate.predicate_type != PredicateType.EQUAL_ANGLES:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    eqangle3 = application.predicate

    return (
        list(draw_predicate(ax, eqangle1, symbols, theme=theme))
        + list(draw_predicate(ax, eqangle2, symbols, theme=theme))
        + list(draw_predicate(ax, eqangle3, symbols, theme=theme))
        + [
            draw_triangle(
                ax,
                vertices[0].num,
                vertices[1].num,
                vertices[2].num,
                line_color=theme.triangle_color,
                line_width=theme.thick_line_width,
            ),
        ]
    )


def _draw_recognize_center_of_circle(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    if application.predicate.predicate_type != PredicateType.CONGRUENT:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    if len(application.premises) != 2:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    if application.premises[0].predicate_type != PredicateType.CIRCUMCENTER:
        raise ValueError(
            f"Unexpected premise for rule {application.rule}: {application.premises[0]}"
        )
    circle = application.premises[0]
    cong = application.predicate
    center = circle.center
    point1 = cong.segment1[0]
    point2 = cong.segment1[1]
    point3 = cong.segment2[0]
    point4 = cong.segment2[1]
    radius = point1.num.distance(point2.num)

    return [
        draw_circle(
            ax,
            (center.num.x, center.num.y),
            radius,
            line_color=theme.circle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            point1.num,
            point2.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            point3.num,
            point4.num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        ),
    ]


def _draw_center_and_concyclics(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    if len(application.premises) != 4:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    
    if application.premises[2].predicate_type != PredicateType.CYCLIC:
        raise ValueError(
            f"Unexpected premise 2 for rule {application.rule}: {application.premises[2]}"
        )
    
    cyclic = application.premises[2]

    if application.premises[0].predicate_type != PredicateType.CONGRUENT:
        raise ValueError(
            f"Unexpected premise 0 for rule {application.rule}: {application.premises[0]}"
        )
    
    congruent = application.premises[0]

    for point in congruent.segment1:
        if point not in cyclic.points:
            center = point
            break
    
    if len(cyclic.points) < 4:
        raise ValueError(
            f"Unexpected number of points in cyclic for rule {application.rule}: {cyclic.points}"
        )

    radius = center.num.distance(cyclic.points[0].num)

    return [
        draw_circle(
            ax,
            (center.num.x, center.num.y),
            radius,
            line_color=theme.circle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            cyclic.points[0].num,
            center.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            cyclic.points[1].num,
            center.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            cyclic.points[2].num,
            center.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            cyclic.points[3].num,
            center.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
    ]

def _draw_midpoint_consequence(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    if application.predicate.predicate_type != PredicateType.MIDPOINT:
        raise ValueError(
            f"Unexpected consequence for rule {application.rule}: {application.predicate}"
        )
    midpoint = application.predicate
    p1, p2 = midpoint.segment
    return [
        draw_segment(
            ax,
            p1.num,
            p2.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        )
    ]


def _draw_midpoint(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    if (
        len(application.premises) < 1
        or application.premises[0].predicate_type != PredicateType.MIDPOINT
    ):
        raise ValueError(
            f"Unexpected premises for rule {application.rule}: {application.premises}"
        )
    midpoint = application.premises[0]
    p1, p2 = midpoint.segment
    return [
        draw_segment(
            ax,
            p1.num,
            p2.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        )
    ]


def _draw_sas_similarity_of_triangles_reverse(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    eqangles: list[Artist] = []
    if application.predicate.predicate_type != PredicateType.SIMTRI_REFLECT:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    a, b, c = application.predicate.triangle1
    p, q, r = application.predicate.triangle2
    for application_premise in application.premises:
        if application_premise.predicate_type == PredicateType.EQUAL_ANGLES:
            artist = draw_predicate(ax, application_premise, symbols, theme=theme)
            eqangles.extend(artist)
    return [
        draw_triangle(
            ax,
            a.num,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_triangle(
            ax,
            p.num,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            a.num,
            b.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            c.num,
            a.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            p.num,
            q.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            r.num,
            p.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
    ] + eqangles


def _draw_sas_similarity_of_triangles_direct(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    eqangles: list[Artist] = []
    if application.predicate.predicate_type != PredicateType.SIMTRI_CLOCK:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    a, b, c = application.predicate.triangle1
    p, q, r = application.predicate.triangle2
    for application_premise in application.premises:
        if application_premise.predicate_type == PredicateType.EQUAL_ANGLES:
            artist = draw_predicate(ax, application_premise, symbols, theme=theme)
            eqangles.extend(artist)
    return [
        draw_triangle(
            ax,
            a.num,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_triangle(
            ax,
            p.num,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            a.num,
            b.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            c.num,
            a.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            p.num,
            q.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            r.num,
            p.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
    ] + eqangles


def _draw_similar_triangles_reverse_properties(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    simtri: SimtriReflect | None = None
    for premise in application.premises:
        if premise.predicate_type == PredicateType.SIMTRI_REFLECT:
            simtri = premise
            break

    if simtri is None:
        raise ValueError(
            f"Unexpected premises for rule {application.rule}: {application.premises}"
        )
    a, b, c = simtri.triangle1
    p, q, r = simtri.triangle2
    return [
        draw_triangle(
            ax,
            a.num,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_triangle(
            ax,
            p.num,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            a.num,
            b.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            c.num,
            a.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            p.num,
            q.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            r.num,
            p.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
    ]


def _draw_similar_triangles_direct_properties(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    simtri: SimtriClock | None = None
    for premise in application.premises:
        if premise.predicate_type == PredicateType.SIMTRI_CLOCK:
            simtri = premise
            break

    if simtri is None:
        raise ValueError(
            f"Unexpected premises for rule {application.rule}: {application.premises}"
        )
    a, b, c = simtri.triangle1
    p, q, r = simtri.triangle2
    return [
        draw_triangle(
            ax,
            a.num,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_triangle(
            ax,
            p.num,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            a.num,
            b.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            c.num,
            a.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            p.num,
            q.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            r.num,
            p.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
    ]


def _draw_resolution_of_ratios(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    if application.predicate.predicate_type != PredicateType.EQUAL_RATIOS:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    eqratio_conclusion = application.predicate

    if len(application.premises) != 4:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    if application.premises[2].predicate_type != PredicateType.EQUAL_RATIOS:
        raise ValueError(
            f"Unexpected premise for rule {application.rule}: {application.premises[0]}"
        )
    eqratio_premise = application.premises[2]

    all_segments: set[Artist] = set()
    all_segments.add(
        draw_segment(
            ax,
            eqratio_conclusion.ratio1[0][0].num,
            eqratio_conclusion.ratio1[0][1].num,
            line_color=theme.circle_color,
            line_width=theme.thick_line_width,
        )
    )
    all_segments.add(
        draw_segment(
            ax,
            eqratio_conclusion.ratio1[0][0].num,
            eqratio_conclusion.ratio1[0][1].num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        )
    )
    all_segments.add(
        draw_segment(
            ax,
            eqratio_conclusion.ratio2[0][0].num,
            eqratio_conclusion.ratio2[0][1].num,
            line_color=theme.circle_color,
            line_width=theme.thick_line_width,
        )
    )
    all_segments.add(
        draw_segment(
            ax,
            eqratio_conclusion.ratio2[0][0].num,
            eqratio_conclusion.ratio2[0][1].num,
            line_color=theme.triangle_color,
            line_width=theme.thick_line_width,
        )
    )
    all_segments.update(draw_predicate(ax, eqratio_premise, symbols, theme=theme))

    return list(all_segments)


def _draw_direct_congruence(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    eqangles: list[Artist] = []
    if application.predicate.predicate_type != PredicateType.CONTRI_CLOCK:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    a, b, c = application.predicate.triangle1
    p, q, r = application.predicate.triangle2
    for application_premise in application.premises:
        if application_premise.predicate_type == PredicateType.EQUAL_ANGLES:
            artist = draw_predicate(ax, application_premise, symbols, theme=theme)
            eqangles.extend(artist)
    return [
        draw_triangle(
            ax,
            a.num,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_triangle(
            ax,
            p.num,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            a.num,
            b.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            c.num,
            a.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            p.num,
            q.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            r.num,
            p.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
    ] + eqangles


def _draw_reverse_congruence(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    eqangles: list[Artist] = []
    if application.predicate.predicate_type != PredicateType.CONTRI_REFLECT:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    a, b, c = application.predicate.triangle1
    p, q, r = application.predicate.triangle2
    for application_premise in application.premises:
        if application_premise.predicate_type == PredicateType.EQUAL_ANGLES:
            artist = draw_predicate(ax, application_premise, symbols, theme=theme)
            eqangles.extend(artist)
    return [
        draw_triangle(
            ax,
            a.num,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_triangle(
            ax,
            p.num,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            a.num,
            b.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            c.num,
            a.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            p.num,
            q.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            r.num,
            p.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
    ] + eqangles


def _draw_disassembling_a_circle(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    circle_premise: Circumcenter | None = None
    for premise in application.premises:
        if premise.predicate_type == PredicateType.CIRCUMCENTER:
            circle_premise = premise
            break

    if (
        circle_premise is None
        or circle_premise.predicate_type != PredicateType.CIRCUMCENTER
    ):
        raise ValueError(
            f"Unexpected premises for rule {application.rule}: {application.premises}"
        )
    radius = circle_premise.center.num.distance(circle_premise.points[0].num)

    if application.predicate.predicate_type != PredicateType.CONGRUENT:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    circle_points: List[Point] = []

    for point in application.predicate.segment1:
        if point != circle_premise.center:
            circle_points.append(point)

    for point in application.predicate.segment2:
        if point != circle_premise.center:
            circle_points.append(point)

    if len(circle_points) != 2:
        raise ValueError(
            f"Unexpected number of points for congruence in rule {application.rule}: {circle_points}"
        )

    return [
        draw_circle(
            ax,
            center=(circle_premise.center.num.x, circle_premise.center.num.y),
            radius=radius,
            line_color=theme.circle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            circle_premise.center.num,
            circle_points[0].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            circle_premise.center.num,
            circle_points[1].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
    ]


def _draw_assembling_a_circle(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    if application.predicate.predicate_type != PredicateType.CIRCUMCENTER:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )

    circle_premise = application.predicate

    center = circle_premise.center
    p1, p2, p3 = circle_premise.points
    radius = center.num.distance(p1.num)

    return [
        draw_circle(
            ax,
            center=(center.num.x, center.num.y),
            radius=radius,
            line_color=theme.circle_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            center.num,
            p1.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            center.num,
            p2.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            center.num,
            p3.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
    ]


def _draw_congruent_triangles_direct_properties(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    contri: ContriClock | None = None
    for premise in application.premises:
        if premise.predicate_type == PredicateType.CONTRI_CLOCK:
            contri = premise
            break

    if contri is None:
        raise ValueError(
            f"Unexpected premises for rule {application.rule}: {application.premises}"
        )
    a, b, c = contri.triangle1
    p, q, r = contri.triangle2
    return [
        draw_triangle(
            ax,
            a.num,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_triangle(
            ax,
            p.num,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            a.num,
            b.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            c.num,
            a.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            p.num,
            q.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            r.num,
            p.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
    ]


def _draw_congruent_triangles_reverse_properties(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    contri: ContriReflect | None = None
    for premise in application.premises:
        if premise.predicate_type == PredicateType.CONTRI_REFLECT:
            contri = premise
            break

    if contri is None:
        raise ValueError(
            f"Unexpected premises for rule {application.rule}: {application.premises}"
        )
    a, b, c = contri.triangle1
    p, q, r = contri.triangle2
    return [
        draw_triangle(
            ax,
            a.num,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_triangle(
            ax,
            p.num,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            a.num,
            b.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            b.num,
            c.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            c.num,
            a.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            p.num,
            q.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            q.num,
            r.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
        draw_arrow(
            ax,
            r.num,
            p.num,
            line_color=theme.triangle_color,
            line_width=theme.thin_line_width,
        ),
    ]


def _draw_same_chord_same_arc_four_points_1(
    ax: Axes,
    application: RuleApplication,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> list[Artist]:
    if len(application.premises) != 3:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    if application.premises[0].predicate_type != PredicateType.CONGRUENT:
        raise ValueError(
            f"Unexpected premise 0 for rule {application.rule}: {application.premises[0]}"
        )
    cong = application.premises[0]

    if application.predicate.predicate_type != PredicateType.EQUAL_ANGLES:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    eqangle = application.predicate

    points: List[Point] = []
    for point in cong.segment1:
        if point not in points:
            points.append(point)

    for point in cong.segment2:
        if point not in points:
            points.append(point)

    if len(points) != 4:
        raise ValueError(
            f"Unexpected number of points for congruence in rule {application.rule}: {points}"
        )
    
    center = _circumcenter_of_triangle((points[0], points[1], points[2]))
    radius = center.distance(points[0].num)
    
    return list(draw_predicate(ax, eqangle, symbols, theme=theme)) + [
        draw_segment(
            ax,
            points[0].num,
            points[1].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_segment(
            ax,
            points[2].num,
            points[3].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_circle(
            ax,
            (center.x, center.y),
            radius,
            line_color=theme.circle_color,
            line_width=theme.thick_line_width,
        ),
    ]
    


def _draw_intersection_bisectors(
    ax: Axes,
    application: RuleApplication,
    theme: DrawTheme,
) -> list[Artist]:
    if len(application.premises) != 4:
        raise ValueError(
            f"Unexpected number of premises for rule {application.rule}: {application.premises}"
        )
    if application.predicate.predicate_type != PredicateType.CYCLIC:
        raise ValueError(
            f"Unexpected conclusion for rule {application.rule}: {application.predicate}"
        )
    cyclic = application.predicate
    if application.premises[0].predicate_type != PredicateType.CONGRUENT:
        raise ValueError(
            f"Unexpected premise for rule {application.rule}: {application.premises[0]}"
        )
    cong = application.premises[0]
    if application.premises[1].predicate_type != PredicateType.EQUAL_ANGLES:
        raise ValueError(
            f"Unexpected premise for rule {application.rule}: {application.premises[0]}"
        )
    eqangle = application.premises[1]
    for point1 in cong.segment1:
        for point2 in cong.segment2:
            if point1 == point2:
                intersection = point1
                break

    triangle = [point for point in cyclic.points if point != intersection]

    center = _circumcenter_of_triangle((triangle[0], triangle[1], triangle[2]))
    radius = center.distance(triangle[0].num)
    for point in eqangle.angle1[0]:
        if point not in cong.segment1 and point not in cong.segment2:
            vertex = point
            break

    segment = [point for point in triangle if point != vertex]
    midpoint = _midpoint_of_segment((segment[0], segment[1]))

    return [
        draw_circle(
            ax,
            (center.x, center.y),
            radius,
            line_color=theme.circle_color,
            line_width=theme.thick_line_width,
        ),
        draw_line(
            ax,
            segment[0].num,
            segment[1].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_line(
            ax,
            vertex.num,
            intersection.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_line(
            ax,
            vertex.num,
            segment[0].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_line(
            ax,
            vertex.num,
            segment[1].num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_line(
            ax,
            midpoint,
            intersection.num,
            line_color=theme.line_color,
            line_width=theme.thick_line_width,
        ),
        draw_free_perpendicular_symbol(ax, midpoint, intersection.num, theme),
    ]


# Helper functions for geometry calculation


def _one_angle_vertex(angle: tuple[Segment, Segment]) -> Point:
    pair1 = angle[0]
    pair2 = angle[1]
    vertex_set = set(pair1) & set(pair2)
    if not vertex_set:
        raise ValueError("Angle didn't establish a vertex.")
    vertex_name = vertex_set.pop()
    return vertex_name


def _get_eqangle_vertex(predicate: Predicate) -> Point:
    if predicate.predicate_type != PredicateType.EQUAL_ANGLES:
        raise ValueError(
            f"Unexpected predicate type for vertex: {predicate.predicate_type}"
        )
    angle1 = predicate.angle1
    angle2 = predicate.angle2
    vertex1 = _one_angle_vertex(angle1)
    vertex2 = _one_angle_vertex(angle2)

    if vertex1 != vertex2:
        raise ValueError("Equal angle don't have a single vertex.")

    return vertex1


def _midpoint_of_segment(segment: tuple[Point, Point]) -> PointNum:
    if len(segment) != 2:
        raise ValueError("Segment must have exactly 2 points.")

    p1, p2 = (point.num for point in segment)
    midpoint_x = (p1.x + p2.x) / 2
    midpoint_y = (p1.y + p2.y) / 2
    return PointNum(x=midpoint_x, y=midpoint_y)


def _circumcenter_of_triangle(
    triangle: tuple[Point, Point, Point],
) -> PointNum:
    if len(triangle) != 3:
        raise ValueError("Triangle must have exactly 3 points.")

    p1, p2, p3 = (point.num for point in triangle)

    jp1 = JGEXPoint(x=p1.x, y=p1.y)
    jp2 = JGEXPoint(x=p2.x, y=p2.y)
    jp3 = JGEXPoint(x=p3.x, y=p3.y)

    l12 = perpendicular_bisector(jp1, jp2)
    l23 = perpendicular_bisector(jp2, jp3)

    jgex_circumcenter = line_line_intersection(l12, l23)[0]
    circumcenter = PointNum(x=jgex_circumcenter.x, y=jgex_circumcenter.y)
    return circumcenter
