class JGEXConstructionError(Exception):
    """Error during JGEX construction."""


class PointTooCloseError(JGEXConstructionError):
    """Trying to create a point that is too close to an existing point."""


class PointTooFarError(JGEXConstructionError):
    """Trying to create a point that is too far from existing points."""


class InvalidIntersectError(JGEXConstructionError):
    """Unexpected number of intersections points."""
