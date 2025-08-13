"""Random number generation."""

import numpy as np


def setup_rng(rng: np.random.Generator | int | None) -> np.random.Generator:
    if rng is None:
        return np.random.default_rng()
    if isinstance(rng, int):
        return np.random.default_rng(rng)
    return rng
