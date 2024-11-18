ATOM = 1e-12
NLOGATOM = 12


def close_enough(a: float, b: float, tol: float = ATOM) -> bool:
    return abs(a - b) < tol
