from newclid.ggb.read_commands import (
    GGBCommand,
    GGBMidpointCommand,
    GGBReadCommandType,
)
from newclid.ggb.read_elements import GGBConic, GGBLine
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.problem import PredicateConstruction


def commands_to_newclid_assumptions(
    commands: list[GGBCommand], lines: dict[str, GGBLine], conics: dict[str, GGBConic]
) -> list[PredicateConstruction]:
    assumptions: list[PredicateConstruction] = []
    for command in commands:
        assumptions.extend(_command_to_newclid_assumptions(command, lines, conics))
    return assumptions


def _command_to_newclid_assumptions(
    command: GGBCommand, lines: dict[str, GGBLine], conics: dict[str, GGBConic]
) -> list[PredicateConstruction]:
    match command.construction_type:
        case GGBReadCommandType.Midpoint:
            return _midpoint_command_assumption(command)
        case (
            GGBReadCommandType.Line
            | GGBReadCommandType.Intersect
            | GGBReadCommandType.AddPointOn
            | GGBReadCommandType.Circle
            | GGBReadCommandType.Circumcircle
            | GGBReadCommandType.Eqdistance
            | GGBReadCommandType.Center
            | GGBReadCommandType.OrthogonalLine
            | GGBReadCommandType.ParallelLine
            | GGBReadCommandType.AngularBisectorPoints
            | GGBReadCommandType.AngularBisector
            | GGBReadCommandType.TangentOnCircle
            | GGBReadCommandType.TangentOutsideCircle
        ):
            return []
    raise NotImplementedError(f"Unknown command: {command}")


def _midpoint_command_assumption(
    command: GGBMidpointCommand,
) -> list[PredicateConstruction]:
    return [
        PredicateConstruction.from_predicate_type_and_args(
            PredicateType.MIDPOINT,
            (
                PredicateArgument(command.midpoint),
                PredicateArgument(command.point_a),
                PredicateArgument(command.point_b),
            ),
        )
    ]
