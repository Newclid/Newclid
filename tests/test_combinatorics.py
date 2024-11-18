"""Unit tests for graph_utils.py."""

import pytest_check as check

from newclid.combinatorics import (
    cross_product,
    arrangement_pairs,
    arrangement_triplets,
    arrangement_quadruplets,
    permutations_pairs,
    permutations_triplets,
    permutations_quadruplets,
)


class TestCombinationsPermutations:
    def test_cross_product(self):
        check.equal(cross_product([], [1]), [])
        check.equal(cross_product([1], []), [])
        check.equal(cross_product([1], [2]), [(1, 2)])
        check.equal(cross_product([1], [2, 3]), [(1, 2), (1, 3)])

        e1 = [1, 2, 3]
        e2 = [4, 5]
        target = [(1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)]
        check.equal(cross_product(e1, e2), target)

    def test_arrangement_pairs(self):
        check.equal(arrangement_pairs([]), [])
        check.equal(arrangement_pairs([1]), [])
        check.equal(arrangement_pairs([1, 2]), [(1, 2)])
        check.equal(arrangement_pairs([1, 2, 3]), [(1, 2), (1, 3), (2, 3)])

    def test_arrangement_triplets(self):
        check.equal(arrangement_triplets([]), [])
        check.equal(arrangement_triplets([1]), [])
        check.equal(arrangement_triplets([1, 2]), [])
        check.equal(arrangement_triplets([1, 2, 3]), [(1, 2, 3)])
        check.equal(
            arrangement_triplets([1, 2, 3, 4]),
            [(1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4)],
        )

    def test_arrangement_quadruplets(self):
        check.equal(arrangement_quadruplets([]), [])
        check.equal(arrangement_quadruplets([1]), [])
        check.equal(arrangement_quadruplets([1, 2]), [])
        check.equal(arrangement_quadruplets([1, 2, 3]), [])
        check.equal(arrangement_quadruplets([1, 2, 3, 4]), [(1, 2, 3, 4)])
        check.equal(
            arrangement_quadruplets([1, 2, 3, 4, 5]),
            [(1, 2, 3, 4), (1, 2, 3, 5), (1, 2, 4, 5), (1, 3, 4, 5), (2, 3, 4, 5)],
        )

    def test_permutations_pairs(self):
        check.equal(permutations_pairs([]), [])
        check.equal(permutations_pairs([1]), [])
        check.equal(permutations_pairs([1, 2]), [(1, 2), (2, 1)])
        check.equal(
            permutations_pairs([1, 2, 3]),
            [(1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2)],
        )

    def test_permutations_triplets(self):
        check.equal(permutations_triplets([]), [])
        check.equal(permutations_triplets([1]), [])
        check.equal(permutations_triplets([1, 2]), [])
        check.equal(
            permutations_triplets([1, 2, 3]),
            [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)],
        )
        check.equal(
            permutations_triplets([1, 2, 3, 4]),
            [
                (1, 2, 3),
                (1, 2, 4),
                (1, 3, 2),
                (1, 3, 4),
                (1, 4, 2),
                (1, 4, 3),
                (2, 1, 3),
                (2, 1, 4),
                (2, 3, 1),
                (2, 3, 4),
                (2, 4, 1),
                (2, 4, 3),
                (3, 1, 2),
                (3, 1, 4),
                (3, 2, 1),
                (3, 2, 4),
                (3, 4, 1),
                (3, 4, 2),
                (4, 1, 2),
                (4, 1, 3),
                (4, 2, 1),
                (4, 2, 3),
                (4, 3, 1),
                (4, 3, 2),
            ],
        )

    def test_permutations_quadruplets(self):
        check.equal(permutations_quadruplets([]), [])
        check.equal(permutations_quadruplets([1]), [])
        check.equal(permutations_quadruplets([1, 2]), [])
        check.equal(permutations_quadruplets([1, 2, 3]), [])
        check.equal(
            permutations_quadruplets([1, 2, 3, 4]),
            [
                (1, 2, 3, 4),
                (1, 2, 4, 3),
                (1, 3, 2, 4),
                (1, 3, 4, 2),
                (1, 4, 2, 3),
                (1, 4, 3, 2),
                (2, 1, 3, 4),
                (2, 1, 4, 3),
                (2, 3, 1, 4),
                (2, 3, 4, 1),
                (2, 4, 1, 3),
                (2, 4, 3, 1),
                (3, 1, 2, 4),
                (3, 1, 4, 2),
                (3, 2, 1, 4),
                (3, 2, 4, 1),
                (3, 4, 1, 2),
                (3, 4, 2, 1),
                (4, 1, 2, 3),
                (4, 1, 3, 2),
                (4, 2, 1, 3),
                (4, 2, 3, 1),
                (4, 3, 1, 2),
                (4, 3, 2, 1),
            ],
        )
