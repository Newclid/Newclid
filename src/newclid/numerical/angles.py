from typing import TYPE_CHECKING

from newclid._lazy_loading import lazy_import

if TYPE_CHECKING:
    import numpy
    from newclid.numerical.geometries import PointNum

np: "numpy" = lazy_import("numpy")


def ang_of(tail: "PointNum", head: "PointNum") -> float:
    vector = head - tail
    arctan = np.arctan2(vector.y, vector.x) % (2 * np.pi)
    return arctan


def ang_between(tail: "PointNum", head1: "PointNum", head2: "PointNum") -> float:
    ang1 = ang_of(tail, head1)
    ang2 = ang_of(tail, head2)
    diff = ang1 - ang2
    # return diff % (2*np.pi)
    if diff > np.pi:
        # if diff - np.pi > ATOM:
        return diff - 2 * np.pi
    if diff < -np.pi:
        # if -np.pi - diff > ATOM:
        return 2 * np.pi + diff
    return diff
