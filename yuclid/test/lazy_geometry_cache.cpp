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

/**
 * @brief Equal side lengths and equal diagonal lengths of a square are grouped
 * into separate buckets.
 */
BOOST_AUTO_TEST_CASE(equal_segment_lengths_are_grouped) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 1.0, 0.0);
    add_point(problem, "C", 1.0, 1.0);
    add_point(problem, "D", 0.0, 1.0);

    LazyGeometryCache cache(problem);

    const std::vector<PointPair>& point_pairs =
        cache.point_pairs();

    const SegmentBuckets& segment_buckets =
        cache.segment_length_buckets();

    BOOST_REQUIRE_EQUAL(
            segment_buckets.buckets.size(),
            2U
            );

    const std::vector<PointPairId>& side_bucket =
        segment_buckets.buckets.at(0);

    const std::vector<PointPairId>& diagonal_bucket =
        segment_buckets.buckets.at(1);

    BOOST_CHECK_EQUAL(side_bucket.size(), 4U);
    BOOST_CHECK_EQUAL(diagonal_bucket.size(), 2U);

    const double side_length =
        segment_bucket_length(
                problem,
                point_pairs,
                side_bucket
                );

    const double diagonal_length =
        segment_bucket_length(
                problem,
                point_pairs,
                diagonal_bucket
                );

    BOOST_CHECK_EQUAL(side_length, 1.0);
    BOOST_CHECK_EQUAL(diagonal_length, 2.0);
    BOOST_CHECK_LT(side_length, diagonal_length);

    for (PointPairId point_pair_id : side_bucket) {
        BOOST_CHECK_EQUAL(
                squared_length(
                    problem,
                    point_pairs.at(point_pair_id)
                    ),
                side_length
                );
    }

    for (
            PointPairId point_pair_id :
            diagonal_bucket
        ) {
        BOOST_CHECK_EQUAL(
                squared_length(
                    problem,
                    point_pairs.at(point_pair_id)
                    ),
                diagonal_length
                );
    }
}

/**
 * @brief Segment buckets are ordered by increasing squared segment length.
 */
BOOST_AUTO_TEST_CASE(
        segment_length_buckets_are_in_ascending_order
        ) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 1.0, 0.0);
    add_point(problem, "C", 2.0, 0.0);
    add_point(problem, "D", 3.0, 0.0);

    LazyGeometryCache cache(problem);

    const std::vector<PointPair>& point_pairs =
        cache.point_pairs();

    const SegmentBuckets& segment_buckets =
        cache.segment_length_buckets();

    BOOST_REQUIRE_EQUAL(
            segment_buckets.buckets.size(),
            2U
            );

    const double first_length =
        segment_bucket_length(
                problem,
                point_pairs,
                segment_buckets.buckets.at(0)
                );

    const double second_length =
        segment_bucket_length(
                problem,
                point_pairs,
                segment_buckets.buckets.at(1)
                );

    BOOST_CHECK_EQUAL(first_length, 1.0);
    BOOST_CHECK_EQUAL(second_length, 4.0);
    BOOST_CHECK_LT(first_length, second_length);
}

/**
 * @brief A segment length occurring only once is not stored as a bucket.
 */
BOOST_AUTO_TEST_CASE(singleton_segment_lengths_are_skipped) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 1.0, 0.0);
    add_point(problem, "C", 0.0, 1.0);

    LazyGeometryCache cache(problem);

    const std::vector<PointPair>& point_pairs =
        cache.point_pairs();

    const SegmentBuckets& segment_buckets =
        cache.segment_length_buckets();

    const PointPairId ab =
        find_point_pair_id(
                point_pairs,
                0,
                1
                );

    const PointPairId ac =
        find_point_pair_id(
                point_pairs,
                0,
                2
                );

    const PointPairId bc =
        find_point_pair_id(
                point_pairs,
                1,
                2
                );

    BOOST_REQUIRE_EQUAL(
            segment_buckets.buckets.size(),
            1U
            );

    const std::vector<PointPairId>& equal_sides =
        segment_buckets.buckets.at(0);

    BOOST_REQUIRE_EQUAL(equal_sides.size(), 2U);

    BOOST_CHECK(
            contains_point_pair(equal_sides, ab)
            );

    BOOST_CHECK(
            contains_point_pair(equal_sides, ac)
            );

    BOOST_CHECK(
            !contains_point_pair(equal_sides, bc)
            );
}

/**
 * @brief Every stored segment bucket contains at least two point pairs.
 */
BOOST_AUTO_TEST_CASE(
        segment_buckets_never_contain_singletons
        ) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 1.0, 0.0);
    add_point(problem, "C", 0.0, 1.0);
    add_point(problem, "D", 2.0, 0.0);
    add_point(problem, "E", 0.0, 2.0);

    LazyGeometryCache cache(problem);

    const SegmentBuckets& segment_buckets =
        cache.segment_length_buckets();

    for (
            const std::vector<PointPairId>& bucket :
            segment_buckets.buckets
        ) {
        BOOST_CHECK_GE(bucket.size(), 2U);
    }
}

/**
 * @brief Parallel horizontal and vertical point pairs are grouped into their
 * respective orientation buckets.
 */
BOOST_AUTO_TEST_CASE(
        parallel_pairs_share_orientation_buckets
        ) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 2.0, 0.0);
    add_point(problem, "C", 0.0, 1.0);
    add_point(problem, "D", 2.0, 1.0);

    LazyGeometryCache cache(problem);

    const std::vector<PointPair>& point_pairs =
        cache.point_pairs();

    const LineOrientationBuckets& orientations =
        cache.line_orientation_buckets();

    const PointPairId ab =
        find_point_pair_id(
                point_pairs,
                0,
                1
                );

    const PointPairId ac =
        find_point_pair_id(
                point_pairs,
                0,
                2
                );

    const PointPairId bd =
        find_point_pair_id(
                point_pairs,
                1,
                3
                );

    const PointPairId cd =
        find_point_pair_id(
                point_pairs,
                2,
                3
                );

    const std::optional<std::size_t>
        first_horizontal_bucket =
        find_orientation_bucket_index(
                orientations,
                ab
                );

    const std::optional<std::size_t>
        second_horizontal_bucket =
        find_orientation_bucket_index(
                orientations,
                cd
                );

    const std::optional<std::size_t>
        first_vertical_bucket =
        find_orientation_bucket_index(
                orientations,
                ac
                );

    const std::optional<std::size_t>
        second_vertical_bucket =
        find_orientation_bucket_index(
                orientations,
                bd
                );

    BOOST_REQUIRE(
            first_horizontal_bucket.has_value()
            );

    BOOST_REQUIRE(
            second_horizontal_bucket.has_value()
            );

    BOOST_REQUIRE(
            first_vertical_bucket.has_value()
            );

    BOOST_REQUIRE(
            second_vertical_bucket.has_value()
            );

    BOOST_CHECK_EQUAL(
            *first_horizontal_bucket,
            *second_horizontal_bucket
            );

    BOOST_CHECK_EQUAL(
            *first_vertical_bucket,
            *second_vertical_bucket
            );

    BOOST_CHECK_NE(
            *first_horizontal_bucket,
            *first_vertical_bucket
            );
}

/**
 * @brief Perpendicular orientation bucket keys differ by one half-turn unit.
 */
BOOST_AUTO_TEST_CASE(
        perpendicular_orientation_keys_differ_by_half
        ) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 2.0, 0.0);
    add_point(problem, "C", 0.0, 1.0);
    add_point(problem, "D", 2.0, 1.0);

    LazyGeometryCache cache(problem);

    const std::vector<PointPair>& point_pairs =
        cache.point_pairs();

    const LineOrientationBuckets& orientations =
        cache.line_orientation_buckets();

    const PointPairId horizontal_pair =
        find_point_pair_id(
                point_pairs,
                0,
                1
                );

    const PointPairId vertical_pair =
        find_point_pair_id(
                point_pairs,
                0,
                2
                );

    const std::optional<std::size_t>
        horizontal_bucket_index =
        find_orientation_bucket_index(
                orientations,
                horizontal_pair
                );

    const std::optional<std::size_t>
        vertical_bucket_index =
        find_orientation_bucket_index(
                orientations,
                vertical_pair
                );

    BOOST_REQUIRE(
            horizontal_bucket_index.has_value()
            );

    BOOST_REQUIRE(
            vertical_bucket_index.has_value()
            );

    const double horizontal_key =
        orientations.buckets
        .at(*horizontal_bucket_index)
        .key;

    const double vertical_key =
        orientations.buckets
        .at(*vertical_bucket_index)
        .key;

    BOOST_CHECK_SMALL(
            std::abs(
                std::abs(
                    vertical_key - horizontal_key
                    ) - 0.5
                ),
            1E-12
            );
}

/**
 * @brief Every point pair appears exactly once in the ordered orientation view.
 */
BOOST_AUTO_TEST_CASE(
        orientation_buckets_cover_all_point_pairs_once
        ) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 2.0, 0.0);
    add_point(problem, "C", 0.0, 1.0);
    add_point(problem, "D", 2.0, 1.0);

    LazyGeometryCache cache(problem);

    const std::vector<PointPair>& point_pairs =
        cache.point_pairs();

    const LineOrientationBuckets& orientations =
        cache.line_orientation_buckets();

    BOOST_REQUIRE_EQUAL(
            orientations.ordered_point_pair_ids.size(),
            point_pairs.size()
            );

    const std::set<PointPairId> unique_ids(
            orientations.ordered_point_pair_ids.begin(),
            orientations.ordered_point_pair_ids.end()
            );

    BOOST_CHECK_EQUAL(
            unique_ids.size(),
            point_pairs.size()
            );

    for (
            PointPairId point_pair_id = 0;
            point_pair_id < point_pairs.size();
            ++point_pair_id
        ) {
        BOOST_CHECK_EQUAL(
                unique_ids.count(point_pair_id),
                1U
                );
    }
}

/**
 * @brief Orientation bucket ranges are contiguous and cover the complete
 * ordered-point-pair collection.
 */
BOOST_AUTO_TEST_CASE(
        orientation_bucket_ranges_are_contiguous
        ) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 2.0, 0.0);
    add_point(problem, "C", 0.0, 1.0);
    add_point(problem, "D", 2.0, 1.0);

    LazyGeometryCache cache(problem);

    const LineOrientationBuckets& orientations =
        cache.line_orientation_buckets();

    std::size_t expected_begin = 0;

    for (
            const LineOrientationBuckets::BucketRange&
            bucket :
            orientations.buckets
        ) {
        BOOST_CHECK_EQUAL(
                bucket.begin,
                expected_begin
                );

        BOOST_CHECK_LT(
                bucket.begin,
                bucket.end
                );

        BOOST_CHECK_LE(
                bucket.end,
                orientations
                .ordered_point_pair_ids
                .size()
                );

        expected_begin = bucket.end;
    }

    BOOST_CHECK_EQUAL(
            expected_begin,
            orientations
            .ordered_point_pair_ids
            .size()
            );
}

/**
 * @brief Orientation buckets are ordered by increasing representative key.
 */
BOOST_AUTO_TEST_CASE(
        orientation_bucket_keys_are_ascending
        ) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 1.0, 0.0);
    add_point(problem, "C", 1.0, 1.0);
    add_point(problem, "D", 0.0, 1.0);

    LazyGeometryCache cache(problem);

    const LineOrientationBuckets& orientations =
        cache.line_orientation_buckets();

    for (
            std::size_t bucket_index = 1;
            bucket_index < orientations.buckets.size();
            ++bucket_index
        ) {
        BOOST_CHECK_LT(
                orientations.buckets
                .at(bucket_index - 1)
                .key,
                orientations.buckets
                .at(bucket_index)
                .key
                );
    }
}

/**
 * @brief An orientation occurring only once is still represented by a
 * singleton orientation bucket.
 */
BOOST_AUTO_TEST_CASE(
        singleton_orientation_buckets_are_kept
        ) {
    Problem problem;

    add_point(problem, "A", 0.0, 0.0);
    add_point(problem, "B", 1.0, 0.0);
    add_point(problem, "C", 2.0, 1.0);

    LazyGeometryCache cache(problem);

    const LineOrientationBuckets& orientations =
        cache.line_orientation_buckets();

    BOOST_REQUIRE_EQUAL(
            orientations.buckets.size(),
            3U
            );

    for (
            const LineOrientationBuckets::BucketRange&
            bucket :
            orientations.buckets
        ) {
        BOOST_CHECK_EQUAL(
                orientation_bucket_size(bucket),
                1U
                );
    }
}

/**
 * @brief Circularly close orientations on opposite sides of the zero/one
 * boundary should belong to the same bucket.
 *
 * This is currently registered as an expected failure because orientation
 * grouping is linear and does not yet merge the first and last buckets.
 * Remove BOOST_AUTO_TEST_CASE_EXPECTED_FAILURES when the cache implementation
 * gains circular wrap-around merging.
 */
BOOST_AUTO_TEST_CASE_EXPECTED_FAILURES(
        wraparound_orientations_share_bucket,
        1
        )

    BOOST_AUTO_TEST_CASE(
            wraparound_orientations_share_bucket
            ) {
        Problem problem;

        const double orientation_offset =
            EPS / 4.0;

        const double vertical_offset =
            std::tan(
                    std::numbers::pi_v<double>
                    * orientation_offset
                    );

        add_point(
                problem,
                "A",
                0.0,
                0.0
                );

        add_point(
                problem,
                "B",
                1.0,
                vertical_offset
                );

        add_point(
                problem,
                "C",
                0.0,
                10.0
                );

        add_point(
                problem,
                "D",
                1.0,
                10.0 - vertical_offset
                );

        LazyGeometryCache cache(problem);

        const std::vector<PointPair>& point_pairs =
            cache.point_pairs();

        const LineOrientationBuckets& orientations =
            cache.line_orientation_buckets();

        const PointPairId ab =
            find_point_pair_id(
                    point_pairs,
                    0,
                    1
                    );

        const PointPairId cd =
            find_point_pair_id(
                    point_pairs,
                    2,
                    3
                    );

        const std::optional<std::size_t> ab_bucket =
            find_orientation_bucket_index(
                    orientations,
                    ab
                    );

        const std::optional<std::size_t> cd_bucket =
            find_orientation_bucket_index(
                    orientations,
                    cd
                    );

        BOOST_REQUIRE(ab_bucket.has_value());
        BOOST_REQUIRE(cd_bucket.has_value());

        BOOST_CHECK_EQUAL(
                *ab_bucket,
                *cd_bucket
                );
    }

BOOST_AUTO_TEST_SUITE_END()
