#pragma once
#include <cstddef>
#include <optional>
#include <vector>

#include "matchers/geometry_cache_types.hpp"
#include "matchers/matching_types.hpp"
#include "type/point.hpp"

namespace Yuclid {
    class Problem;

    /**
     * Lazy read-only cache of geometry data derived from one Problem.
     *
     * The cache does not own or modify the Problem. It builds derived data
     * only when it is first requested, then reuses it for later calls.
     */
    class LazyGeometryCache {
    public:
        explicit LazyGeometryCache(const Problem &problem);

        [[nodiscard]] std::size_t num_points() const;

        [[nodiscard]] Point point(ProblemPointIndex index) const;

        /**
         * Returns all unordered point pairs in the problem.
         *
         * Example for points 0, 1, 2:
         *   (0, 1), (0, 2), (1, 2)
         *
         * Built lazily on first use.
         */
        [[nodiscard]] const std::vector<PointPair> &point_pairs() const;

        /**
         * Returns point pairs grouped by equal/similar segment length.
         *
         * Each PointPair is interpreted as a finite segment for this cache view.
         * Buckets store PointPairId values pointing into point_pairs(), so point-pair
         * data is stored once and combinations are generated on demand.
         */
        [[nodiscard]] const SegmentBuckets &segment_length_buckets() const;

        /**
         * Returns point pairs grouped by undirected line orientation.
         *
         * Each PointPair is interpreted as the line through its two points for this
         * cache view. Buckets store PointPairId values pointing into point_pairs().
         *
         * This is intended for para/perp providers:
         *   - para uses point pairs with matching orientation
         *   - perp uses point pairs whose orientation differs by 90 degrees
         */
        [[nodiscard]] const LineOrientationBuckets &line_orientation_buckets() const;

    private:
        [[nodiscard]] std::vector<PointPair> build_point_pairs() const;
        [[nodiscard]] SegmentBuckets build_segment_length_buckets() const;
        [[nodiscard]] LineOrientationBuckets build_line_orientation_buckets() const;

        const Problem* m_problem;

        // Lazily initialized by point_pairs().
        mutable std::optional<std::vector<PointPair>> m_point_pairs;

        // Lazily initialized by segment_length_buckets().
        mutable std::optional<SegmentBuckets> m_segment_length_buckets;

        // Lazily initialized by line_orientation_buckets().
        mutable std::optional<LineOrientationBuckets> m_line_orientation_buckets;
    };
}
