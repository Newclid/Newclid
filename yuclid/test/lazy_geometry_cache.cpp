#define BOOST_TEST_MODULE lazy_geometry_cache_test

#include <boost/test/unit_test.hpp>

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <numbers>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

#include "matchers/geometry_cache_types.hpp"
#include "matchers/lazy_geometry_cache.hpp"
#include "numbers/util.hpp"
#include "problem.hpp"
#include "type/point.hpp"
#include "type/squared_dist.hpp"

using namespace Yuclid;

namespace {

    /**
     * Adds a point while explicitly consuming the [[nodiscard]] return value.
     */
    void add_point(
        Problem& problem,
        const std::string& name,
        double x,
        double y
    ) {
        static_cast<void>(
            problem.add_point(name, x, y)
        );
    }

    /**
     * Finds the ID of an unordered point pair in the cache's canonical pair
     * collection.
     */
    PointPairId find_point_pair_id(
        const std::vector<PointPair>& point_pairs,
        ProblemPointIndex first,
        ProblemPointIndex second
    ) {
        for (
            PointPairId point_pair_id = 0;
            point_pair_id < point_pairs.size();
            ++point_pair_id
        ) {
            const PointPair& point_pair =
                point_pairs.at(point_pair_id);

            if (
                point_pair.first == first
                && point_pair.second == second
            ) {
                return point_pair_id;
            }
        }

        throw std::runtime_error(
            "Expected point pair was not found"
        );
    }

    /**
     * Returns whether a segment bucket contains the requested point-pair ID.
     */
    bool contains_point_pair(
        const std::vector<PointPairId>& bucket,
        PointPairId point_pair_id
    ) {
        return std::find(
            bucket.begin(),
            bucket.end(),
            point_pair_id
        ) != bucket.end();
    }

    /**
     * Calculates the squared length represented by a point pair.
     */
    double squared_length(
        const Problem& problem,
        const PointPair& point_pair
    ) {
        return static_cast<double>(
            SquaredDist(
                problem.point_at(point_pair.first),
                problem.point_at(point_pair.second)
            )
        );
    }

    /**
     * Calculates the representative squared length of a non-empty segment
     * bucket.
     */
    double segment_bucket_length(
        const Problem& problem,
        const std::vector<PointPair>& point_pairs,
        const std::vector<PointPairId>& bucket
    ) {
        if (bucket.empty()) {
            throw std::runtime_error(
                "Cannot inspect an empty segment bucket"
            );
        }

        return squared_length(
            problem,
            point_pairs.at(bucket.front())
        );
    }

    /**
     * Finds the orientation bucket containing one point-pair ID.
     */
    std::optional<std::size_t>
    find_orientation_bucket_index(
        const LineOrientationBuckets& orientation_buckets,
        PointPairId point_pair_id
    ) {
        for (
            std::size_t bucket_index = 0;
            bucket_index
                < orientation_buckets.buckets.size();
            ++bucket_index
        ) {
            const LineOrientationBuckets::BucketRange&
                bucket =
                    orientation_buckets.buckets.at(
                        bucket_index
                    );

            for (
                std::size_t ordered_index = bucket.begin;
                ordered_index < bucket.end;
                ++ordered_index
            ) {
                if (
                    orientation_buckets
                        .ordered_point_pair_ids
                        .at(ordered_index)
                    == point_pair_id
                ) {
                    return bucket_index;
                }
            }
        }

        return std::nullopt;
    }

    /**
     * Returns the number of point pairs represented by one orientation bucket.
     */
    std::size_t orientation_bucket_size(
        const LineOrientationBuckets::BucketRange& bucket
    ) {
        return bucket.end - bucket.begin;
    }

}  // namespace

BOOST_AUTO_TEST_SUITE(lazy_geometry_cache_suite)

/**
 * @brief An empty problem has no points, point pairs, or geometry buckets.
 */
BOOST_AUTO_TEST_CASE(empty_problem_produces_empty_cache_views) {
    Problem problem;
    LazyGeometryCache cache(problem);

    BOOST_CHECK_EQUAL(cache.num_points(), 0U);
    BOOST_CHECK(cache.point_pairs().empty());

    BOOST_CHECK(
        cache.segment_length_buckets()
            .buckets
            .empty()
    );

    BOOST_CHECK(
        cache.line_orientation_buckets()
            .ordered_point_pair_ids
            .empty()
    );

    BOOST_CHECK(
        cache.line_orientation_buckets()
            .buckets
            .empty()
    );
}

/**
 * @brief A one-point problem has no unordered point pairs.
 */
BOOST_AUTO_TEST_CASE(single_point_produces_no_point_pairs) {
    Problem problem;

    add_point(
        problem,
        "A",
        0.0,
        0.0
    );

    LazyGeometryCache cache(problem);

    BOOST_CHECK_EQUAL(cache.num_points(), 1U);
    BOOST_CHECK(cache.point_pairs().empty());

    BOOST_CHECK(
        cache.segment_length_buckets()
            .buckets
            .empty()
    );

    BOOST_CHECK(
        cache.line_orientation_buckets()
            .buckets
            .empty()
    );
}

/**
 * @brief Point access returns the corresponding point from the source Problem.
 */
BOOST_AUTO_TEST_CASE(point_access_uses_source_problem) {
    Problem problem;

    add_point(
        problem,
        "A",
        1.5,
        -2.0
    );

    add_point(
        problem,
        "B",
        4.0,
        3.0
    );

    LazyGeometryCache cache(problem);

    BOOST_CHECK_EQUAL(cache.num_points(), 2U);

    const Point first = cache.point(0);
    const Point second = cache.point(1);

    BOOST_CHECK_EQUAL(first.get(), 0U);
    BOOST_CHECK_EQUAL(first.name(), "A");
    BOOST_CHECK_EQUAL(first.x(), 1.5);
    BOOST_CHECK_EQUAL(first.y(), -2.0);

    BOOST_CHECK_EQUAL(second.get(), 1U);
    BOOST_CHECK_EQUAL(second.name(), "B");
    BOOST_CHECK_EQUAL(second.x(), 4.0);
    BOOST_CHECK_EQUAL(second.y(), 3.0);

    BOOST_CHECK_THROW(
        static_cast<void>(cache.point(2)),
        std::runtime_error
    );
}

/**
 * @brief Point pairs contain every unordered pair exactly once and in
 * lexicographic point-index order.
 */
BOOST_AUTO_TEST_CASE(
    point_pairs_have_expected_count_and_order
) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 1.0, 0.0);
    add_point(problem, "C", 0.0, 1.0);
    add_point(problem, "D", 1.0, 1.0);

    LazyGeometryCache cache(problem);

    const std::vector<PointPair>& point_pairs =
        cache.point_pairs();

    BOOST_REQUIRE_EQUAL(point_pairs.size(), 6U);

    BOOST_CHECK_EQUAL(point_pairs.at(0).first, 0U);
    BOOST_CHECK_EQUAL(point_pairs.at(0).second, 1U);

    BOOST_CHECK_EQUAL(point_pairs.at(1).first, 0U);
    BOOST_CHECK_EQUAL(point_pairs.at(1).second, 2U);

    BOOST_CHECK_EQUAL(point_pairs.at(2).first, 0U);
    BOOST_CHECK_EQUAL(point_pairs.at(2).second, 3U);

    BOOST_CHECK_EQUAL(point_pairs.at(3).first, 1U);
    BOOST_CHECK_EQUAL(point_pairs.at(3).second, 2U);

    BOOST_CHECK_EQUAL(point_pairs.at(4).first, 1U);
    BOOST_CHECK_EQUAL(point_pairs.at(4).second, 3U);

    BOOST_CHECK_EQUAL(point_pairs.at(5).first, 2U);
    BOOST_CHECK_EQUAL(point_pairs.at(5).second, 3U);

    for (const PointPair& point_pair : point_pairs) {
        BOOST_CHECK_LT(
            point_pair.first,
            point_pair.second
        );
    }
}

/**
 * @brief Three points produce n(n-1)/2 unordered pairs.
 */
BOOST_AUTO_TEST_CASE(point_pair_count_matches_combination_count) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 1.0, 0.0);
    add_point(problem, "C", 0.0, 1.0);
    add_point(problem, "D", 1.0, 1.0);
    add_point(problem, "E", 2.0, 2.0);

    LazyGeometryCache cache(problem);

    constexpr std::size_t point_count = 5;
    constexpr std::size_t expected_pair_count =
        point_count * (point_count - 1) / 2;

    BOOST_CHECK_EQUAL(
        cache.point_pairs().size(),
        expected_pair_count
    );
}

/**
 * @brief Repeated accessor calls return the same cached storage.
 */
BOOST_AUTO_TEST_CASE(repeated_access_reuses_cached_views) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 1.0, 0.0);
    add_point(problem, "C", 0.0, 1.0);

    LazyGeometryCache cache(problem);

    const std::vector<PointPair>& first_pairs =
        cache.point_pairs();

    const std::vector<PointPair>& second_pairs =
        cache.point_pairs();

    BOOST_CHECK(
        &first_pairs == &second_pairs
    );

    const SegmentBuckets& first_segment_buckets =
        cache.segment_length_buckets();

    const SegmentBuckets& second_segment_buckets =
        cache.segment_length_buckets();

    BOOST_CHECK(
        &first_segment_buckets
        == &second_segment_buckets
    );

    const LineOrientationBuckets&
        first_orientation_buckets =
            cache.line_orientation_buckets();

    const LineOrientationBuckets&
        second_orientation_buckets =
            cache.line_orientation_buckets();

    BOOST_CHECK(
        &first_orientation_buckets
        == &second_orientation_buckets
    );
}

BOOST_AUTO_TEST_SUITE_END()
