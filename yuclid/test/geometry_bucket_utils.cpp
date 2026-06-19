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

BOOST_AUTO_TEST_SUITE_END()
