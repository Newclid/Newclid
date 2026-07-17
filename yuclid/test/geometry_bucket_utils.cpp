#define BOOST_TEST_MODULE geometry_bucket_utils_test

#include <boost/test/unit_test.hpp>

#include <algorithm>
#include <cstddef>
#include <utility>
#include <vector>

#include "matchers/geometry_bucket_utils.hpp"

using namespace Yuclid;

namespace {

    using TestId = std::size_t;

    struct CapturedBucket {
        std::vector<TestId> ids;
        double key;
    };

    std::vector<CapturedBucket> collect_buckets(
        const std::vector<KeyedId<TestId>>& sorted_ids,
        double tolerance,
        std::size_t minimum_bucket_size = 1,
        double drift_warning_factor = 10.0
    ) {
        std::vector<CapturedBucket> buckets;

        for_each_bucket_from_sorted_keyed_ids(
            sorted_ids,
            tolerance,
            [&](std::vector<TestId> ids, double key) {
                buckets.push_back(
                    CapturedBucket{
                        .ids = std::move(ids),
                        .key = key,
                    }
                );
            },
            minimum_bucket_size,
            "test geometry IDs",
            drift_warning_factor
        );

        return buckets;
    }

}  // namespace

BOOST_AUTO_TEST_SUITE(geometry_bucket_utils_suite)

/**
 * @brief Building keyed IDs for an empty collection returns an empty result
 * without evaluating the key function.
 */
BOOST_AUTO_TEST_CASE(
    empty_collection_produces_no_keyed_ids
) {
    std::size_t key_function_calls = 0;

    const std::vector<KeyedId<TestId>> keyed_ids =
        build_sorted_keyed_ids<TestId>(
            0,
            [&](TestId) {
                ++key_function_calls;
                return 0.0;
            }
        );

    BOOST_CHECK(keyed_ids.empty());
    BOOST_CHECK_EQUAL(key_function_calls, 0U);
}

/**
 * @brief Every object ID is included and ordered by its computed key.
 */
BOOST_AUTO_TEST_CASE(
    keyed_ids_are_sorted_by_numeric_key
) {
    const std::vector<double> keys{
        4.0,
        1.5,
        3.0,
        2.0,
    };

    std::size_t key_function_calls = 0;

    const std::vector<KeyedId<TestId>> keyed_ids =
        build_sorted_keyed_ids<TestId>(
            keys.size(),
            [&](TestId id) {
                ++key_function_calls;
                return keys.at(id);
            }
        );

    BOOST_REQUIRE_EQUAL(keyed_ids.size(), 4U);
    BOOST_CHECK_EQUAL(key_function_calls, 4U);

    BOOST_CHECK_EQUAL(keyed_ids.at(0).id, 1U);
    BOOST_CHECK_EQUAL(keyed_ids.at(0).key, 1.5);

    BOOST_CHECK_EQUAL(keyed_ids.at(1).id, 3U);
    BOOST_CHECK_EQUAL(keyed_ids.at(1).key, 2.0);

    BOOST_CHECK_EQUAL(keyed_ids.at(2).id, 2U);
    BOOST_CHECK_EQUAL(keyed_ids.at(2).key, 3.0);

    BOOST_CHECK_EQUAL(keyed_ids.at(3).id, 0U);
    BOOST_CHECK_EQUAL(keyed_ids.at(3).key, 4.0);
}

/**
 * @brief Sorting preserves the association between every ID and its key.
 */
BOOST_AUTO_TEST_CASE(
    sorting_preserves_id_to_key_association
) {
    const std::vector<double> original_keys{
        8.0,
        -2.0,
        5.5,
        0.0,
    };

    const std::vector<KeyedId<TestId>> keyed_ids =
        build_sorted_keyed_ids<TestId>(
            original_keys.size(),
            [&](TestId id) {
                return original_keys.at(id);
            }
        );

    for (const KeyedId<TestId>& keyed_id : keyed_ids) {
        BOOST_CHECK_EQUAL(
            keyed_id.key,
            original_keys.at(keyed_id.id)
        );
    }
}

/**
 * @brief IDs with equal keys are all retained.
 *
 * std::sort does not promise a particular order for equal keys, so the test
 * verifies membership rather than depending on an arbitrary tie order.
 */
BOOST_AUTO_TEST_CASE(
    equal_keys_keep_all_ids
) {
    const std::vector<double> keys{
        2.0,
        1.0,
        1.0,
        3.0,
    };

    const std::vector<KeyedId<TestId>> keyed_ids =
        build_sorted_keyed_ids<TestId>(
            keys.size(),
            [&](TestId id) {
                return keys.at(id);
            }
        );

    BOOST_REQUIRE_EQUAL(keyed_ids.size(), 4U);

    BOOST_CHECK_EQUAL(keyed_ids.at(0).key, 1.0);
    BOOST_CHECK_EQUAL(keyed_ids.at(1).key, 1.0);

    std::vector<TestId> equal_key_ids{
        keyed_ids.at(0).id,
        keyed_ids.at(1).id,
    };

    std::sort(
        equal_key_ids.begin(),
        equal_key_ids.end()
    );

    BOOST_REQUIRE_EQUAL(equal_key_ids.size(), 2U);
    BOOST_CHECK_EQUAL(equal_key_ids.at(0), 1U);
    BOOST_CHECK_EQUAL(equal_key_ids.at(1), 2U);

    BOOST_CHECK_EQUAL(keyed_ids.at(2).key, 2.0);
    BOOST_CHECK_EQUAL(keyed_ids.at(3).key, 3.0);
}

/**
 * @brief Empty input produces no bucket callbacks.
 */
BOOST_AUTO_TEST_CASE(
    empty_keyed_ids_produce_no_buckets
) {
    const std::vector<CapturedBucket> buckets =
        collect_buckets(
            {},
            0.1
        );

    BOOST_CHECK(buckets.empty());
}

/**
 * @brief Consecutive keys closer than the tolerance are grouped together.
 */
BOOST_AUTO_TEST_CASE(
    nearby_keys_are_grouped
) {
    const std::vector<KeyedId<TestId>> sorted_ids{
        {.key = 1.00, .id = 10},
        {.key = 1.05, .id = 11},
        {.key = 1.30, .id = 12},
        {.key = 1.35, .id = 13},
    };

    const std::vector<CapturedBucket> buckets =
        collect_buckets(
            sorted_ids,
            0.1
        );

    BOOST_REQUIRE_EQUAL(buckets.size(), 2U);

    BOOST_CHECK_EQUAL(buckets.at(0).key, 1.00);
    BOOST_REQUIRE_EQUAL(
        buckets.at(0).ids.size(),
        2U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(0).ids.at(0),
        10U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(0).ids.at(1),
        11U
    );

    BOOST_CHECK_EQUAL(buckets.at(1).key, 1.30);
    BOOST_REQUIRE_EQUAL(
        buckets.at(1).ids.size(),
        2U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(1).ids.at(0),
        12U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(1).ids.at(1),
        13U
    );
}

/**
 * @brief A difference exactly equal to the tolerance begins a new bucket.
 *
 * The implementation uses a strict comparison:
 *     key < last_key + tolerance
 */
BOOST_AUTO_TEST_CASE(
    exact_tolerance_boundary_starts_new_bucket
) {
    const std::vector<KeyedId<TestId>> sorted_ids{
        {.key = 0.0, .id = 0},
        {.key = 0.1, .id = 1},
    };

    const std::vector<CapturedBucket> buckets =
        collect_buckets(
            sorted_ids,
            0.1
        );

    BOOST_REQUIRE_EQUAL(buckets.size(), 2U);

    BOOST_REQUIRE_EQUAL(
        buckets.at(0).ids.size(),
        1U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(0).ids.at(0),
        0U
    );

    BOOST_REQUIRE_EQUAL(
        buckets.at(1).ids.size(),
        1U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(1).ids.at(0),
        1U
    );
}

/**
 * @brief The representative key is taken from the first element in the bucket.
 */
BOOST_AUTO_TEST_CASE(
    bucket_uses_first_key_as_representative
) {
    const std::vector<KeyedId<TestId>> sorted_ids{
        {.key = 5.00, .id = 0},
        {.key = 5.04, .id = 1},
        {.key = 5.08, .id = 2},
    };

    const std::vector<CapturedBucket> buckets =
        collect_buckets(
            sorted_ids,
            0.1
        );

    BOOST_REQUIRE_EQUAL(buckets.size(), 1U);
    BOOST_CHECK_EQUAL(buckets.at(0).key, 5.00);
}

/**
 * @brief Buckets smaller than the configured minimum size are omitted.
 */
BOOST_AUTO_TEST_CASE(
    minimum_bucket_size_filters_small_buckets
) {
    const std::vector<KeyedId<TestId>> sorted_ids{
        {.key = 1.00, .id = 0},
        {.key = 1.05, .id = 1},
        {.key = 2.00, .id = 2},
    };

    const std::vector<CapturedBucket> buckets =
        collect_buckets(
            sorted_ids,
            0.1,
            2
        );

    BOOST_REQUIRE_EQUAL(buckets.size(), 1U);

    BOOST_REQUIRE_EQUAL(
        buckets.at(0).ids.size(),
        2U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(0).ids.at(0),
        0U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(0).ids.at(1),
        1U
    );
}

/**
 * @brief A final qualifying bucket is emitted when iteration ends.
 */
BOOST_AUTO_TEST_CASE(
    final_bucket_is_emitted
) {
    const std::vector<KeyedId<TestId>> sorted_ids{
        {.key = 0.0, .id = 0},
        {.key = 1.0, .id = 1},
        {.key = 1.05, .id = 2},
    };

    const std::vector<CapturedBucket> buckets =
        collect_buckets(
            sorted_ids,
            0.1,
            2
        );

    BOOST_REQUIRE_EQUAL(buckets.size(), 1U);

    BOOST_CHECK_EQUAL(buckets.at(0).key, 1.0);
    BOOST_REQUIRE_EQUAL(
        buckets.at(0).ids.size(),
        2U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(0).ids.at(0),
        1U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(0).ids.at(1),
        2U
    );
}

/**
 * @brief Bucketing compares each value to the previous value, allowing a
 * chain of close values to remain in one bucket.
 *
 * This also executes the drift-warning path. The warning does not split or
 * discard the bucket.
 */
BOOST_AUTO_TEST_CASE(
    chained_nearby_keys_remain_in_one_bucket
) {
    const std::vector<KeyedId<TestId>> sorted_ids{
        {.key = 0.00, .id = 0},
        {.key = 0.09, .id = 1},
        {.key = 0.18, .id = 2},
    };

    const std::vector<CapturedBucket> buckets =
        collect_buckets(
            sorted_ids,
            0.1,
            1,
            1.5
        );

    BOOST_REQUIRE_EQUAL(buckets.size(), 1U);

    BOOST_REQUIRE_EQUAL(
        buckets.at(0).ids.size(),
        3U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(0).ids.at(0),
        0U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(0).ids.at(1),
        1U
    );
    BOOST_CHECK_EQUAL(
        buckets.at(0).ids.at(2),
        2U
    );
}

/**
 * @brief Empty and single-element collections contain no unordered pairs.
 */
BOOST_AUTO_TEST_CASE(
    fewer_than_two_values_produce_no_pairs
) {
    std::size_t callback_count = 0;

    for_each_unordered_pair(
        std::vector<int>{},
        [&](int, int) {
            ++callback_count;
        }
    );

    for_each_unordered_pair(
        std::vector<int>{42},
        [&](int, int) {
            ++callback_count;
        }
    );

    BOOST_CHECK_EQUAL(callback_count, 0U);
}

/**
 * @brief Three values produce all three unique unordered pairs.
 */
BOOST_AUTO_TEST_CASE(
    three_values_produce_all_unordered_pairs
) {
    const std::vector<int> values{
        10,
        20,
        30,
    };

    std::vector<std::pair<int, int>> pairs;

    for_each_unordered_pair(
        values,
        [&](int first, int second) {
            pairs.emplace_back(first, second);
        }
    );

    BOOST_REQUIRE_EQUAL(pairs.size(), 3U);

    BOOST_CHECK_EQUAL(pairs.at(0).first, 10);
    BOOST_CHECK_EQUAL(pairs.at(0).second, 20);

    BOOST_CHECK_EQUAL(pairs.at(1).first, 10);
    BOOST_CHECK_EQUAL(pairs.at(1).second, 30);

    BOOST_CHECK_EQUAL(pairs.at(2).first, 20);
    BOOST_CHECK_EQUAL(pairs.at(2).second, 30);
}

/**
 * @brief Four values produce n(n-1)/2 pairs without reversed duplicates.
 */
BOOST_AUTO_TEST_CASE(
    pair_count_matches_combination_count
) {
    const std::vector<int> values{
        1,
        2,
        3,
        4,
    };

    std::vector<std::pair<int, int>> pairs;

    for_each_unordered_pair(
        values,
        [&](int first, int second) {
            pairs.emplace_back(first, second);
        }
    );

    constexpr std::size_t expected_pair_count =
        4U * 3U / 2U;

    BOOST_REQUIRE_EQUAL(
        pairs.size(),
        expected_pair_count
    );

    BOOST_CHECK_EQUAL(pairs.at(0).first, 1);
    BOOST_CHECK_EQUAL(pairs.at(0).second, 2);

    BOOST_CHECK_EQUAL(pairs.at(1).first, 1);
    BOOST_CHECK_EQUAL(pairs.at(1).second, 3);

    BOOST_CHECK_EQUAL(pairs.at(2).first, 1);
    BOOST_CHECK_EQUAL(pairs.at(2).second, 4);

    BOOST_CHECK_EQUAL(pairs.at(3).first, 2);
    BOOST_CHECK_EQUAL(pairs.at(3).second, 3);

    BOOST_CHECK_EQUAL(pairs.at(4).first, 2);
    BOOST_CHECK_EQUAL(pairs.at(4).second, 4);

    BOOST_CHECK_EQUAL(pairs.at(5).first, 3);
    BOOST_CHECK_EQUAL(pairs.at(5).second, 4);
}

/**
 * @brief Pairing is based on distinct positions, even when values are equal.
 */
BOOST_AUTO_TEST_CASE(
    duplicate_values_still_produce_positional_pairs
) {
    const std::vector<int> values{
        5,
        5,
        5,
    };

    std::size_t callback_count = 0;

    for_each_unordered_pair(
        values,
        [&](int first, int second) {
            BOOST_CHECK_EQUAL(first, 5);
            BOOST_CHECK_EQUAL(second, 5);
            ++callback_count;
        }
    );

    BOOST_CHECK_EQUAL(callback_count, 3U);
}

BOOST_AUTO_TEST_SUITE_END()
