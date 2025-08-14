import numpy as np

from newclid.jgex.geometries import JGEXPoint


def ang_of(tail: JGEXPoint, head: JGEXPoint) -> float:
    vector = head - tail
    arctan = np.arctan2(vector.y, vector.x) % (2 * np.pi)
    return arctan


def ang_between(tail: JGEXPoint, head1: JGEXPoint, head2: JGEXPoint) -> float:
    """
    the slid angle from tail->head1 to tail->head2 controlled between [-np.pi, np.pi)
    """
    ang1 = ang_of(tail, head1)
    ang2 = ang_of(tail, head2)
    diff = ang2 - ang1
    return diff % (2 * np.pi)
