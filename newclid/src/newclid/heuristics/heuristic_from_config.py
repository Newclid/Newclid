from typing import Annotated

from pydantic import Field

from newclid.heuristics._index import HeuristicName
from newclid.heuristics._interface import Heuristic
from newclid.heuristics.angle_vertices import (
    AngleVerticesHeuristic,
    AngleVerticesHeuristicConfig,
)
from newclid.heuristics.centers_of_cyclic import (
    CentersOfCyclicHeuristic,
    CentersOfCyclicHeuristicConfig,
)
from newclid.heuristics.circumcircles_for_eqangle import (
    ThreeCircumcirclesForEqangleGoalHeuristic,
    ThreeCircumcirclesForEqangleGoalHeuristicConfig,
)
from newclid.heuristics.foots_on_lines import FootHeuristic, FootHeuristicConfig
from newclid.heuristics.line_intersections import (
    LineIntersectionsHeuristic,
    LineIntersectionsHeuristicConfig,
)
from newclid.heuristics.midpoint import MidpointHeuristic, MidpointHeuristicConfig
from newclid.heuristics.reflect_on_center import (
    ReflectOnCenterHeuristic,
    ReflectOnCenterHeuristicConfig,
)
from newclid.heuristics.transfer_distances import (
    TransferDistancesHeuristic,
    TransferDistancesHeuristicConfig,
)

HeuristicConfig = Annotated[
    MidpointHeuristicConfig
    | LineIntersectionsHeuristicConfig
    | TransferDistancesHeuristicConfig
    | AngleVerticesHeuristicConfig
    | ReflectOnCenterHeuristicConfig
    | CentersOfCyclicHeuristicConfig
    | ThreeCircumcirclesForEqangleGoalHeuristicConfig
    | FootHeuristicConfig,
    Field(discriminator="heuristic_name"),
]


def heuristic_from_name(name: HeuristicName) -> Heuristic:
    return heuristic_from_config(config_from_name(name))


def config_from_name(name: HeuristicName) -> HeuristicConfig:
    match name:
        case HeuristicName.MIDPOINT:
            return MidpointHeuristicConfig()
        case HeuristicName.LINE_INTERSECTIONS:
            return LineIntersectionsHeuristicConfig()
        case HeuristicName.EQDISTANCE:
            return TransferDistancesHeuristicConfig()
        case HeuristicName.ANGLE_VERTICES:
            return AngleVerticesHeuristicConfig()
        case HeuristicName.THREE_CIRCUMCIRCLES_FOR_EQANGLE_GOAL:
            return ThreeCircumcirclesForEqangleGoalHeuristicConfig()
        case HeuristicName.REFLECT_ON_CENTER:
            return ReflectOnCenterHeuristicConfig()
        case HeuristicName.CENTERS:
            return CentersOfCyclicHeuristicConfig()
        case HeuristicName.FOOT:
            return FootHeuristicConfig()
    raise ValueError(f"Unknown heuristic: {name}")


def heuristic_from_config(
    heuritic_config: HeuristicConfig,
) -> Heuristic:
    match heuritic_config.heuristic_name:
        case HeuristicName.MIDPOINT:
            return MidpointHeuristic()
        case HeuristicName.LINE_INTERSECTIONS:
            return LineIntersectionsHeuristic()
        case HeuristicName.EQDISTANCE:
            return TransferDistancesHeuristic()
        case HeuristicName.ANGLE_VERTICES:
            return AngleVerticesHeuristic()
        case HeuristicName.THREE_CIRCUMCIRCLES_FOR_EQANGLE_GOAL:
            return ThreeCircumcirclesForEqangleGoalHeuristic()
        case HeuristicName.REFLECT_ON_CENTER:
            return ReflectOnCenterHeuristic()
        case HeuristicName.CENTERS:
            return CentersOfCyclicHeuristic()
        case HeuristicName.FOOT:
            return FootHeuristic()
    raise ValueError(f"Unknown heuristic: {heuritic_config.heuristic_name}")
