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

    const std::vector<Segment> &LazyGeometryCache::segments() const {
        if(!m_segments.has_value()) m_segments = build_segments();

        return *m_segments;
    }

    const SegmentBuckets &LazyGeometryCache::segment_length_buckets() const {
        if(m_segment_length_buckets.has_value()) {
            return m_segment_length_buckets.value();
        }

        m_segment_length_buckets = build_segment_length_buckets();

        return *m_segment_length_buckets;
    }

    std::vector<Segment> LazyGeometryCache::build_segments() const {
        std::vector<Segment> result;
        std::size_t point_count = num_points();

        if(point_count < 2) return result;

        result.reserve(point_count * (point_count - 1) / 2);

        for(ProblemPointIndex first = 0; first < point_count; first++) {
            for(ProblemPointIndex second = first + 1; second < point_count; second++) {
                result.push_back(
                    Segment {
                        first,
                        second
                    }
                );
            }
        }

        return result;
    }

    SegmentBuckets LazyGeometryCache::build_segment_length_buckets() const {
        const std::vector<Segment> &all_segments = segments();
        
        // Build a temporary sorted list:
        //   key = squared segment length
        //   id  = index into all_segments
        //
        // The cache stores segments only once in segments(). The bucket view below
        // stores only SegmentId values pointing back into that shared segment list.
        const std::vector<KeyedId<SegmentId>> keyed_segments =
            build_sorted_keyed_ids<SegmentId>(
                all_segments.size(),
                [&](SegmentId segment_id) {
                    const Segment &segment = all_segments[segment_id];

                    return static_cast<double>(
                        SquaredDist(
                            point(segment.first),
                            point(segment.second)
                        )
                    );
                }
            );
        
        SegmentBuckets result;

        // Group segments by equal/similar squared length.
        for_each_bucket_from_sorted_keyed_ids(
            keyed_segments,
            EPS,
            [&](std::vector<SegmentId> bucket) {
                result.buckets.push_back(std::move(bucket));
            },
            2,
            "segment lengths"
        );


        return result;
    }
}
