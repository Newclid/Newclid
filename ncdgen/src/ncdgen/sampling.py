import itertools
from typing import Iterable, Iterator, TypeVar

from numpy.random import Generator as RngGenerator

T = TypeVar("T")


def sample_from_pmf(pmf: dict[T, float], rng: RngGenerator) -> T:
    """Sample from a probability mass function.

    Args:
        pmf: A dictionary mapping each possible outcome to its probability.

    Returns:
        A random outcome from the probability mass function.
    """
    items = list(pmf.items())
    keys = [k for k, _ in items]
    probs = [p for _, p in items]
    # Use absolute difference comparison for floating point
    assert abs(sum(probs) - 1.0) < 1e-6, f"pmf must sum to 1, got {items}"
    return rng.choice(keys, p=probs, size=1)[0]  # type: ignore


def sample_order_from_pmf(pmf: dict[T, float], rng: RngGenerator) -> list[T]:
    """Sample a random order from a probability mass function without replacement.

    Args:
        pmf: A dictionary mapping each possible outcome to its probability.

    Returns:
        A list containing all outcomes in random order.
    """
    assert len(pmf) > 0

    if len(pmf) == 1:
        return list(pmf.keys())
    else:
        # Sample one item
        item = sample_from_pmf(pmf, rng)

        # Remove sampled item and renormalize remaining probabilities
        remaining_pmf = {k: v for k, v in pmf.items() if k != item}
        prob_sum = sum(remaining_pmf.values())
        assert prob_sum > 0
        remaining_pmf = {k: v / prob_sum for k, v in remaining_pmf.items()}

        # Recursively sample remaining items
        return [item] + sample_order_from_pmf(remaining_pmf, rng)


def combinations_in_random_order(
    iterable: Iterable[T], r: int, rng: RngGenerator
) -> Iterator[tuple[T, ...]]:
    """Sample random combinations of r elements from an iterable.

    Args:
        iterable: The iterable to sample from.
        r: The number of elements to sample.
        rng: The random number generator to use.
    """
    combinations = list(itertools.combinations(iterable, r))
    shuffled_combinations: list[tuple[T, ...]] = rng.permutation(combinations)  # type: ignore
    yield from shuffled_combinations
