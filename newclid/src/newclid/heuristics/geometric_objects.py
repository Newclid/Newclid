import itertools
from typing import Iterable

from pydantic import BaseModel

from newclid.jgex.constructions.free import FREE_CONSTRUCTIONS
from newclid.jgex.formulation import JGEXFormulation
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.problem import PredicateConstruction

free_names = [definition.name for definition in FREE_CONSTRUCTIONS]


class LineHeuristic(BaseModel):
    points: tuple[PredicateArgument, ...]


class CircleHeuristic(BaseModel):
    points: tuple[PredicateArgument, ...]


class AngleHeuristic(BaseModel):
    line_1: tuple[PredicateArgument, PredicateArgument]
    line_2: tuple[PredicateArgument, PredicateArgument]


def read_geometric_objects_from_predicate_constructions(
    problem: JGEXFormulation,
    predicate_constructions: Iterable[PredicateConstruction],
) -> tuple[
    list[LineHeuristic],
    list[CircleHeuristic],
    list[AngleHeuristic],
    list[PredicateArgument],
]:
    """Read geometric objects from predicate constructions.

    Args:
        predicate_constructions (Iterable[StatementConstruction]): The predicate constructions to read geometric objects from.

    Returns:
        lines, circles, angles, free_points: The geometric objects read from the predicate constructions.
    """

    # Not working as information is not been stored in the symbols_registry by yuclid,
    # lines = solver.proof_state.symbols.lines.nodes_of_type(Line)
    # circles = solver.proof_state.symbols.circles.nodes_of_type(Circle)
    lines: list[LineHeuristic] = []
    circles: list[CircleHeuristic] = []
    angles: list[AngleHeuristic] = []
    free_points: list[PredicateArgument] = []

    # Gathering the lines involving free constructions
    for construction in problem.clauses:
        if construction.constructions[0].name in free_names:
            for point in construction.points:
                point_as_argument = PredicateArgument(point)
                free_points.append(point_as_argument)

    for p1, p2 in itertools.combinations(free_points, 2):
        lines.append(LineHeuristic(points=(p1, p2)))

    for stmt in predicate_constructions:
        match stmt.predicate_type:
            case PredicateType.CYCLIC:
                circles.append(CircleHeuristic(points=stmt.args))
            case PredicateType.CIRCUMCENTER:
                circles.append(CircleHeuristic(points=stmt.args))
            case PredicateType.COLLINEAR:
                lines.append(LineHeuristic(points=stmt.args))
            case PredicateType.PERPENDICULAR:
                lines.append(LineHeuristic(points=(stmt.args[0], stmt.args[1])))
                lines.append(LineHeuristic(points=(stmt.args[2], stmt.args[3])))
                angles.append(
                    AngleHeuristic(
                        line_1=(stmt.args[0], stmt.args[1]),
                        line_2=(stmt.args[2], stmt.args[3]),
                    )
                )
            case PredicateType.PARALLEL:
                lines.append(LineHeuristic(points=(stmt.args[0], stmt.args[1])))
                lines.append(LineHeuristic(points=(stmt.args[2], stmt.args[3])))
            case PredicateType.EQUAL_ANGLES:
                angles.append(
                    AngleHeuristic(
                        line_1=(stmt.args[0], stmt.args[1]),
                        line_2=(stmt.args[2], stmt.args[3]),
                    )
                )
                angles.append(
                    AngleHeuristic(
                        line_1=(stmt.args[4], stmt.args[5]),
                        line_2=(stmt.args[6], stmt.args[7]),
                    )
                )
            case _:
                pass

    merged_lines: list[LineHeuristic] = []
    skipped_lines_indexes: set[int] = set()
    for i, line1 in enumerate(lines):
        if i in skipped_lines_indexes:
            continue
        for j in range(i, len(lines)):
            have_two_points_in_common = (
                len(set(line1.points) & set(lines[j].points)) > 1
            )
            if have_two_points_in_common:
                merged_line = tuple(set(line1.points) | set(lines[j].points))
                skipped_lines_indexes.add(j)
                merged_lines.append(LineHeuristic(points=merged_line))

    merged_circles: list[CircleHeuristic] = []
    skipped_circles_indexes: set[int] = set()
    for i, circle1 in enumerate(circles):
        if i in skipped_circles_indexes:
            continue
        for j in range(i, len(circles)):
            have_three_points_in_common = (
                len(set(circle1.points) & set(circles[j].points)) > 2
            )
            if have_three_points_in_common:
                merged_circle = tuple(set(circle1.points) | set(circles[j].points))
                skipped_circles_indexes.add(j)
                merged_circles.append(CircleHeuristic(points=merged_circle))

    return merged_lines, merged_circles, angles, free_points
