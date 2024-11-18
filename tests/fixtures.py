from newclid.api import GeometricSolver, GeometricSolverBuilder
from newclid.numerical.distances import PointTooCloseError, PointTooFarError


def build_until_works(
    builder: GeometricSolverBuilder, max_attempts: int = 100
) -> GeometricSolver:
    solver = None
    attemps = 0
    err = None
    while solver is None and attemps < max_attempts:
        attemps += 1
        try:
            solver = builder.build()
        except (PointTooFarError, PointTooCloseError) as err:
            solver = None
            err = err

    if solver is None:
        raise Exception("Failed to build after %s attempts", max_attempts) from err

    return solver
