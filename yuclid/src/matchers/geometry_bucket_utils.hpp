#pragma once

#include <algorithm>
#include <cstddef>
#include <utility>
#include <vector>

#include <boost/log/trivial.hpp>

namespace Yuclid {

    /**
     * Temporary helper object used while building geometry buckets.
     *
     * key:
     *   Numeric value used for sorting/grouping.
     *
     * id:
     *   Index into the cache-owned geometry list.
     *
     * Examples:
     *   SegmentId   -> index into LazyGeometryCache::segments()
     *   AngleId     -> index into LazyGeometryCache::angles()
     *   TriangleId  -> index into LazyGeometryCache::triangles()
     */
    template <typename Id>
    struct KeyedId {
        double key;
        Id id;
    };

    /**
     * Builds a sorted temporary list of geometry IDs ordered by their numeric key.
     *
     * The cache owns the real geometry objects. This function stores only IDs,
     * not copies of the geometry objects.
     *
     * Example:
     *   sort_ids_by_key<SegmentId>(
     *       segments.size(),
     *       [&](SegmentId id) { return squared_length_of_segment(id); }
     *   )
     *
     * Result:
     *   [{key=3.0, id=2}, {key=5.0, id=0}, {key=5.0, id=3}, ...]
     */
    template <typename Id, typename KeyFn>
    std::vector<KeyedId<Id>> generate_sorted_keyed_ids(
        std::size_t id_count,
        KeyFn key_for_id
    ) {
        std::vector<KeyedId<Id>> keyed_ids;
        keyed_ids.reserve(id_count);

        for (std::size_t raw_id = 0; raw_id < id_count; raw_id++) {
            const Id id = static_cast<Id>(raw_id);

            keyed_ids.push_back(KeyedId<Id>{
                .key = static_cast<double>(key_for_id(id)),
                .id = id,
            });
        }

        std::sort(
            keyed_ids.begin(),
            keyed_ids.end(),
            [](const KeyedId<Id> &left, const KeyedId<Id> &right) {
                return left.key < right.key;
            }
        );

        return keyed_ids;
    }

    /**
     * Builds stored ID buckets from an already sorted keyed-ID list.
     *
     * This follows the same tolerance style as the current TheoremMatcher:
     *
     *   - compare each key with the previous key
     *   - keep adding to the same bucket while:
     *       key < last_key + tolerance
     *   - warn if the bucket drifts more than 10x tolerance from its start
     *
     * The warning matches the old matcher behavior. It does not split or skip
     * the bucket, because doing so would change matching behavior.
     *
     * add_bucket receives a completed std::vector<Id>.
     */
    template <typename Id, typename AddBucketFn>
    void build_buckets_from_sorted_keyed_ids(
        const std::vector<KeyedId<Id>> &sorted_ids,
        double tolerance,
        AddBucketFn add_bucket,
        std::size_t min_bucket_size = 1,
        const char *debug_name = "geometry ids",
        double drift_warning_factor = 10.0
    ) {
        if (sorted_ids.empty()) {
            return;
        }

        auto emit_bucket = [&](std::size_t begin, std::size_t end) {
            const std::size_t bucket_size = end - begin;

            if (bucket_size < min_bucket_size) {
                return;
            }

            std::vector<Id> bucket;
            bucket.reserve(bucket_size);

            for (std::size_t i = begin; i < end; i++) {
                bucket.push_back(sorted_ids[i].id);
            }

            add_bucket(std::move(bucket));
        };

        std::size_t start_bucket_index = 0;
        double start_bucket_key = sorted_ids[0].key;
        double last_key = start_bucket_key;

        for (std::size_t index = 1; index < sorted_ids.size(); index++) {
            const double key = sorted_ids[index].key;

            if (key < last_key + tolerance) {
                if (key >= start_bucket_key + drift_warning_factor * tolerance) {
                    BOOST_LOG_TRIVIAL(warning)
                        << "While bucketing " << debug_name
                        << ": bucket tolerance "
                        << drift_warning_factor
                        << "x overflow";
                }
            } else {
                emit_bucket(start_bucket_index, index);

                start_bucket_index = index;
                start_bucket_key = key;
            }

            last_key = key;
        }

        emit_bucket(start_bucket_index, sorted_ids.size());
    }

    /**
     * Iterates over all unique unordered pairs inside one stored ID bucket.
     *
     * Example:
     *   bucket = [0, 3, 5]
     *
     * pair_fn receives:
     *   (0, 3)
     *   (0, 5)
     *   (3, 5)
     */
    template <typename Id, typename PairFn>
    void for_each_unordered_pair(
        const std::vector<Id> &bucket,
        PairFn pair_fn
    ) {
        for (std::size_t i = 0; i < bucket.size(); i++) {
            for (std::size_t j = i + 1; j < bucket.size(); j++) {
                pair_fn(bucket[i], bucket[j]);
            }
        }
    }
}
