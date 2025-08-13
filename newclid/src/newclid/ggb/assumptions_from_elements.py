from typing import cast

from newclid.ggb.read_elements import GGBConic, GGBLine
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.problem import PredicateConstruction


def elements_to_newclid_assumptions(
    lines: dict[str, GGBLine], conics: dict[str, GGBConic]
) -> list[PredicateConstruction]:
    assumptions: list[PredicateConstruction] = []
    for line in lines.values():
        assumptions.extend(_line_to_newclid_assumptions(line))
    for conic in conics.values():
        assumptions.extend(_conic_to_newclid_assumptions(conic))
    return assumptions


def _line_to_newclid_assumptions(line: GGBLine) -> list[PredicateConstruction]:
    assumptions: list[PredicateConstruction] = []
    if len(line.points) <= 1:
        return assumptions
    for i in range(len(line.points) - 2):
        coll_points = line.points[i : i + 3]
        new_predicate = PredicateConstruction.from_predicate_type_and_args(
            PredicateType.COLLINEAR, cast(tuple[PredicateArgument, ...], coll_points)
        )
        assumptions.append(new_predicate)
    return assumptions


def _conic_to_newclid_assumptions(conic: GGBConic) -> list[PredicateConstruction]:
    cong_predicates: list[PredicateConstruction] = []
    center_predicates: list[PredicateConstruction] = []
    cyclic_predicates: list[PredicateConstruction] = []
    if len(conic.points) <= 2:
        if conic.radius is None or conic.center is None:
            return []
        else:
            radius_points = [conic.radius[0], conic.radius[1]]
            for point in conic.points:
                args = [point, conic.center, *radius_points]
                if len(set(args)) > 2:
                    new_predicate = PredicateConstruction.from_predicate_type_and_args(
                        PredicateType.CONGRUENT,
                        cast(tuple[PredicateArgument, ...], args),
                    )
                    cong_predicates.append(new_predicate)

            return cong_predicates

    elif conic.center is not None:
        for i in range(0, len(conic.points) - 2):
            args = [
                conic.center,
                conic.points[i],
                conic.points[i + 1],
                conic.points[i + 2],
            ]
            center_predicates.append(
                PredicateConstruction.from_predicate_type_and_args(
                    PredicateType.CIRCUMCENTER,
                    cast(tuple[PredicateArgument, ...], args),
                )
            )
        if conic.radius is not None:
            radius_points = [conic.radius[0], conic.radius[1]]
            for point in conic.points:
                args = [point, conic.center, *radius_points]
                if set(args[:2]) == set(args[2:]):
                    # Avoid trivial cong A B B A
                    continue
                new_predicate = PredicateConstruction.from_predicate_type_and_args(
                    PredicateType.CONGRUENT,
                    cast(tuple[PredicateArgument, ...], args),
                )
                cong_predicates.append(new_predicate)

        if len(conic.points) > 3:
            for i in range(0, len(conic.points) - 3):
                args = [
                    conic.points[i],
                    conic.points[i + 1],
                    conic.points[i + 2],
                    conic.points[i + 3],
                ]
                cyclic_predicates.append(
                    PredicateConstruction.from_predicate_type_and_args(
                        PredicateType.CYCLIC,
                        cast(tuple[PredicateArgument, ...], args),
                    )
                )
    return cong_predicates + center_predicates + cyclic_predicates
