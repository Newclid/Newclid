from typing import TypeVar


T = TypeVar("T")


def list_eqratio3(points: list[T]) -> list[list[T]]:
    a, b, c, d, m, n = points
    ratios = [
        [m, a, m, c, n, b, n, d],
        [a, m, a, c, b, n, b, d],
        [c, m, c, a, d, n, d, b],
    ]
    if m == n:
        ratios.append([m, a, m, c, a, b, c, d])
    return ratios
