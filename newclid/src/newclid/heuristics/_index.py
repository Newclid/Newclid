from enum import Enum


class HeuristicName(str, Enum):
    LINE_INTERSECTIONS = "line_intersections"
    CENTERS = "centers"
    ANGLE_VERTICES = "angle_vertices"
    MIDPOINT = "midpoint"
    EQDISTANCE = "eqdistance"
    FOOT = "foot"
    REFLECT_ON_CENTER = "reflect_on_center"
    THREE_CIRCUMCIRCLES_FOR_EQANGLE_GOAL = "three_circumcircles_for_eqangle_goal"
