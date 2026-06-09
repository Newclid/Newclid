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

    /**
     * Point pairs grouped by undirected line orientation.
     *
     * The actual PointPair objects are stored once in LazyGeometryCache::point_pairs().
     * This cache view stores an ordered list of PointPairId values plus bucket ranges
     * into that ordered list.
     *
     * A bucket's key is the representative orientation of all point pairs in that
     * bucket. Orientation is undirected: AB and BA represent the same line orientation.
     */
    struct LineOrientationBuckets {
        struct BucketRange {
            double key;
            std::size_t begin;
            std::size_t end;
        };

        std::vector<PointPairId> ordered_point_pair_ids;
        std::vector<BucketRange> buckets;
    };
}
