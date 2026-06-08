#pragma once

#include <cstddef>
#include <vector>

#include "matchers/matching_types.hpp"

namespace Yuclid {
    /**
     * Unordered pair of problem point indices.
     *
     * This is the neutral base object stored by LazyGeometryCache. Different cache
     * views can interpret the same point pair differently:
     *   - as a finite segment for length buckets
     *   - as a line through two points for orientation/parallelism buckets
     */
    struct PointPair {
        ProblemPointIndex first;
        ProblemPointIndex second;
    };

    using PointPairId = std::size_t;

    /**
     * Buckets of point pairs grouped by equal/similar segment length.
     *
     * The buckets store PointPairId values pointing into LazyGeometryCache::point_pairs().
     * This avoids duplicating point-pair data or precomputing all equal-length
     * combinations.
     */
    struct SegmentBuckets {
        std::vector<std::vector<PointPairId>> buckets;
    };
}
