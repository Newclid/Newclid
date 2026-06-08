#include "matchers/lazy_geometry_cache.hpp"

#include <utility>
#include <vector>

#include "matchers/geometry_bucket_utils.hpp"
#include "numbers/util.hpp"
#include "problem.hpp"
#include "type/squared_dist.hpp"

namespace Yuclid {
    LazyGeometryCache::LazyGeometryCache(const Problem &problem)
        : m_problem(&problem)
    {}
    
    std::size_t LazyGeometryCache::num_points() const {
        return m_problem->num_points();
    }

    Point LazyGeometryCache::point(ProblemPointIndex index) const {
        return m_problem->point_at(index);
    }

    const std::vector<PointPair> &LazyGeometryCache::point_pairs() const {
        if(!m_point_pairs.has_value()) m_point_pairs = build_point_pairs();

        return *m_point_pairs;
    }

    const SegmentBuckets &LazyGeometryCache::segment_length_buckets() const {
        if(m_segment_length_buckets.has_value()) {
            return m_segment_length_buckets.value();
        }

        m_segment_length_buckets = build_segment_length_buckets();

        return *m_segment_length_buckets;
    }

    std::vector<PointPair> LazyGeometryCache::build_point_pairs() const {
        std::vector<PointPair> result;
        std::size_t point_count = num_points();

        if(point_count < 2) return result;

        result.reserve(point_count * (point_count - 1) / 2);

        for(ProblemPointIndex first = 0; first < point_count; first++) {
            for(ProblemPointIndex second = first + 1; second < point_count; second++) {
                result.push_back(
                    PointPair {
                        first,
                        second
                    }
                );
            }
        }

        return result;
    }

    SegmentBuckets LazyGeometryCache::build_segment_length_buckets() const {
        const std::vector<PointPair> &all_point_pairs = point_pairs();
        
        /* Build a temporary sorted list:
         *   key = squared distance between the two points in the pair
         *   id  = index into all_point_pairs
         *
         * The base PointPair list is stored once by point_pairs(). This bucket view
         * stores only PointPairId values, so it does not duplicate point-pair data or
         * precompute equal-length segment combinations.
         */
        const std::vector<KeyedId<PointPairId>> keyed_segments =
            build_sorted_keyed_ids<PointPairId>(
                all_point_pairs.size(),
                [&](PointPairId segment_id) {
                    const PointPair &segment = all_point_pairs[segment_id];

                    return static_cast<double>(
                        SquaredDist(
                            point(segment.first),
                            point(segment.second)
                        )
                    );
                }
            );
        
        SegmentBuckets result;

        // Group point pairs by equal/similar segment length. Singleton buckets are
        // skipped because they cannot produce equal-length segment pairs.
        for_each_bucket_from_sorted_keyed_ids(
            keyed_segments,
            EPS,
            [&](std::vector<PointPairId> bucket) {
                result.buckets.push_back(std::move(bucket));
            },
            2,
            "segment lengths"
        );


        return result;
    }
}
