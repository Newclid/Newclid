def _gcd(x: int, y: int) -> int:
    while y:
        x, y = y, x % y
    return x


def simplify(n: int, d: int) -> tuple[int, int]:
    g = _gcd(n, d)
    return (n // g, d // g)
