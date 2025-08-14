import itertools
from typing import Iterator, TypeVar

P = TypeVar("P")
V = TypeVar("V")


def generate_permutations_as_dicts(
    points: list[P], variables: list[V]
) -> Iterator[dict[V, P]]:
    """Generates dictionaries from permutations of 'points' mapped to 'variables'.

    This function is a Python implementation of the C++ `generate_permutations_as_dicts`.
    It behaves like Python's itertools.permutations, where each permutation
    of points is zipped with variables to form a dictionary.

    Args:
        points: A list of strings to be permuted.
        variables: A list of strings to be used as keys. The length of
                   permutations will be equal to len(variables).

    Yields:
        A dictionary where keys are from 'variables' and values are
        from a permutation of 'points'.
    """
    r = len(variables)
    for p in itertools.permutations(points, r):
        yield dict(zip(variables, p))
