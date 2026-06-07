#include "matchers/lazy_geometry_cache.hpp"

#include <algorithm>
#include <utility>
#include <vector>

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
        struct KeyedSegment {
            double key;
            SegmentId segment_id;
        };

        const std::vector<Segment> &all_segments = segments();

        std::vector<KeyedSegment> keyed_segments;
        keyed_segments.reserve(all_segments.size());
        
        // Compute one numeric key per object.
        // Here:
        //   object = Segment
        //   key    = squared length of the segment
        for(SegmentId segment_id = 0; segment_id < all_segments.size(); segment_id++) {
            const Segment &segment = all_segments[segment_id];

            const double length_key = static_cast<double>(
                SquaredDist(
                    point(segment.first),
                    point(segment.second)
                )
            );

            keyed_segments.push_back(KeyedSegment{
                .key = length_key,
                .segment_id = segment_id,
            });
        }

        std::sort(
            keyed_segments.begin(),
            keyed_segments.end(),
            [](const KeyedSegment &left, const KeyedSegment &right) {
                return left.key < right.key;
            }
        );

        SegmentBuckets result;

        // Scan sorted keys and split them into buckets.
        for(std::size_t start = 0; start < keyed_segments.size();) {
            std::size_t end = start + 1;

            // TODO: align this tolerance with existing TheoremMatcher numeric bucket logic.
            while (
                end < keyed_segments.size() &&
                keyed_segments[end].key <= keyed_segments[start].key + EPS
            ) {
                ++end;
            }

            std::vector<SegmentId> bucket;
            bucket.reserve(end - start);

            // Store only IDs into the shared segment list.
            // Do not store Segment copies and do not store segment pairs/combinations.
            for (std::size_t i = start; i < end; ++i) {
                bucket.push_back(keyed_segments[i].segment_id);
            }
            
            if (bucket.size() >= 2) {
                result.buckets.push_back(std::move(bucket));
            }

            start = end;
        }

        return result;
    }
}
