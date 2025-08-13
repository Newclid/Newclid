from __future__ import annotations

from typing import TYPE_CHECKING

from newclid.jgex.errors import PointTooCloseError, PointTooFarError
from newclid.jgex.sketch import LENGTH_UNIT
from newclid.predicate_types import PredicateArgument

if TYPE_CHECKING:
    from newclid.jgex.geometries import JGEXPoint


def ensure_not_too_close_numerical(
    newpoints: dict[PredicateArgument, JGEXPoint],
    existing_points: dict[PredicateArgument, JGEXPoint],
    tol: float = 0.01,
) -> bool:
    if len(existing_points) < 2:
        return False
    mindist = (
        sum(
            [
                sum([p.distance(p1) for p1 in existing_points.values() if p1 != p])
                for p in existing_points.values()
            ]
        )
        / len(existing_points)
        / (len(existing_points) - 1)
    )
    for new_point_name, new_point in newpoints.items():
        for existing_point_name, existing_point in existing_points.items():
            p2p_dist = new_point.distance(existing_point)
            if p2p_dist < tol * mindist:
                raise PointTooCloseError(
                    f"Point {new_point_name} is too close to {existing_point_name}"
                    f" (distance: {p2p_dist} < {tol * mindist})"
                )
    return False


def ensure_not_too_far_numerical(
    newpoints: dict[PredicateArgument, JGEXPoint],
    existing_points: dict[PredicateArgument, JGEXPoint],
    tol: float = 10.0,
) -> bool:
    if len(existing_points) < 2:
        return False
    maxdist = (
        sum(
            [
                sum([p.distance(p1) for p1 in existing_points.values() if p1 != p])
                for p in existing_points.values()
            ]
        )
        / len(existing_points)
        / (len(existing_points) - 1)
    )
    maxdist = max(maxdist, 3 * LENGTH_UNIT)
    for new_point_name, new_point in newpoints.items():
        for existing_point_name, existing_point in existing_points.items():
            p2p_dist = new_point.distance(existing_point)
            if p2p_dist > tol * maxdist:
                raise PointTooFarError(
                    f"Point {new_point_name} is too far from {existing_point_name}"
                    f" (distance: {p2p_dist} > {tol * maxdist})"
                )
    return False
