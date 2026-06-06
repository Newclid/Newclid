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
        [[nodiscard]] const std::vector<Segment> &segments() const;

        /**
         * Returns segments grouped by equal/similar length.
         *
         * The buckets store SegmentId values pointing into segments(), so
         * segment data is stored once and combinations are generated on demand.
         */
        [[nodiscard]] const SegmentBuckets &segment_length_buckets() const;

    private:
        [[nodiscard]] std::vector<Segment> build_segments() const;
        [[nodiscard]] SegmentBuckets build_segment_length_buckets() const;

        const Problem* m_problem;

        // Lazily initialized by segments().
        mutable std::optional<std::vector<Segment>> m_segments;

        // Lazily initialized by segment_length_buckets().
        mutable std::optional<SegmentBuckets> m_segment_length_buckets;
    };
}
