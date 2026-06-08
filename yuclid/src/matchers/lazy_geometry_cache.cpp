#include "matchers/lazy_geometry_cache.hpp"

#include <utility>
#include <vector>

#include "matchers/geometry_bucket_utils.hpp"
#include "numbers/add_circle.hpp"
#include "numbers/util.hpp"
#include "problem.hpp"
#include "type/slope_angle.hpp"
#include "type/squared_dist.hpp"

namespace Yuclid {

    namespace {

        /**
         * Computes the numeric bucket key for the line through two points.
         *
         * SlopeAngle gives the orientation of the line, ignoring the finite segment
         * length. Converting it to AddCircle<double> normalizes that orientation
         * modulo pi, so opposite point orders such as AB and BA represent the same
         * line orientation.
         *
         * The returned number is used for sorting/grouping. Keys that differ by 0.5
         * represent perpendicular line orientations.
         */
        double line_orientation_key(Point first, Point second) {
            const SlopeAngle slope_angle(first, second);
            const AddCircle<double> orientation =
                static_cast<AddCircle<double>>(slope_angle);

            return orientation.number();
        }
    }

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

    const LineOrientationBuckets &LazyGeometryCache::line_orientation_buckets() const {
        if(!m_line_orientation_buckets.has_value()) {
            m_line_orientation_buckets = build_line_orientation_buckets();
        }

        return *m_line_orientation_buckets;
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
            [&](std::vector<PointPairId> bucket, [[maybe_unused]] double bucket_key) {
                result.buckets.push_back(std::move(bucket));
            },
            2,
            "segment lengths"
        );


        return result;
    }

    LineOrientationBuckets LazyGeometryCache::build_line_orientation_buckets() const {
        const std::vector<PointPair> &all_point_pairs = point_pairs();

        // Build a temporary sorted list:
        //   key = undirected line orientation of the point pair
        //   id  = index into all_point_pairs
        //
        // The base PointPair list is stored once by point_pairs(). This cache view
        // only stores PointPairId values, interpreting each pair as the line through
        // its two points.
        const std::vector<KeyedId<PointPairId>> keyed_point_pairs =
        build_sorted_keyed_ids<PointPairId>(
            all_point_pairs.size(),
            [&](PointPairId point_pair_id) {
                const PointPair &point_pair = all_point_pairs[point_pair_id];

                return line_orientation_key(
                    point(point_pair.first),
                    point(point_pair.second)
                );
            }
        );
        
        LineOrientationBuckets result;
        result.ordered_point_pair_ids.reserve(keyed_point_pairs.size());

        // Group point pairs by equal/similar line orientation.
        for_each_bucket_from_sorted_keyed_ids(
            keyed_point_pairs,
            EPS,
            [&](std::vector<PointPairId> bucket, double bucket_key) {
                const std::size_t begin = result.ordered_point_pair_ids.size();

                for (PointPairId point_pair_id : bucket) {
                    result.ordered_point_pair_ids.push_back(point_pair_id);
                }

                const std::size_t end = result.ordered_point_pair_ids.size();

                result.buckets.push_back(LineOrientationBuckets::BucketRange{
                    .key = bucket_key,
                    .begin = begin,
                    .end = end,
                });
            },
            1,
            "line orientations"
        );

        return result;
    }
}
