Yuclid guide to adding a lazy cache
===================================

Use this guide when multiple providers would need the same precomputed
geometry, or when one provider would otherwise recompute expensive data
repeatedly across search branches. Everything lives on
``Yuclid::LazyGeometryCache`` (``yuclid/src/matchers/lazy_geometry_cache.hpp``/
``.cpp``), backed by the shared bucket-building helpers in
``yuclid/src/matchers/geometry_bucket_utils.hpp`` and the plain data types in
``yuclid/src/matchers/geometry_cache_types.hpp``.

Yuclid cache shape today
------------------------

``LazyGeometryCache`` wraps one ``Problem`` and exposes:

.. code-block:: cpp

   class LazyGeometryCache {
   public:
       explicit LazyGeometryCache(const Problem &problem);

       [[nodiscard]] std::size_t num_points() const;
       [[nodiscard]] Point point(ProblemPointIndex index) const;
       [[nodiscard]] const std::vector<PointPair> &point_pairs() const;
       [[nodiscard]] const SegmentBuckets &segment_length_buckets() const;
       [[nodiscard]] const LineOrientationBuckets &line_orientation_buckets() const;
   private:
       mutable std::optional<std::vector<PointPair>> m_point_pairs;
       mutable std::optional<SegmentBuckets> m_segment_length_buckets;
       mutable std::optional<LineOrientationBuckets> m_line_orientation_buckets;
   };

Every accessor follows the same "lazy getter" shape: check the ``mutable
std::optional`` member, build it once if empty, return a reference. This is
the pattern you copy for a new cache view. Two views already exist as worked
examples:

- ``segment_length_buckets()`` — powers ``CongProvider``. Groups
  ``point_pairs()`` by squared segment length.
- ``line_orientation_buckets()`` — built for ``para``/``perp``, but **no
  provider consumes it yet** (see :doc:`add_a_predicate_provider`). It groups
  point pairs by undirected line orientation (``AB`` and ``BA`` are the same
  orientation); pairs whose orientation differs by exactly half a turn
  (0.5 in ``AddCircle<double>`` units) are perpendicular. Its bucket type is
  slightly different from ``SegmentBuckets`` — instead of one
  ``std::vector<std::vector<PointPairId>>``, it stores one flat
  ``ordered_point_pair_ids`` list plus ``BucketRange{key, begin, end}`` windows
  into it, which avoids allocating one vector per bucket. Pick whichever shape
  fits your data better; nothing requires new caches to match either one
  exactly.

Both views are built through the same two generic helpers in
``geometry_bucket_utils.hpp``:

.. code-block:: cpp

   // 1. Compute one double-valued "key" per item, keep the item id.
   template <typename Id, typename KeyFn>
   std::vector<KeyedId<Id>> build_sorted_keyed_ids(
       std::size_t object_count,
       KeyFn key_for_id
   );

   // 2. Walk the sorted keys and group consecutive ones within `tolerance`.
   template <typename Id, typename AddBucketFn>
   void for_each_bucket_from_sorted_keyed_ids(
       const std::vector<KeyedId<Id>> &sorted_ids,
       double tolerance,
       AddBucketFn add_bucket,
       std::size_t min_bucket_size = 1,
       const char *debug_name = "geometry ids",
       double drift_warning_factor = 10.0
   );

``build_segment_length_buckets()`` is the shortest real example of using both:

.. code-block:: cpp

   SegmentBuckets LazyGeometryCache::build_segment_length_buckets() const {
       const std::vector<PointPair> &all_point_pairs = point_pairs();

       const std::vector<KeyedId<PointPairId>> keyed_segments =
           build_sorted_keyed_ids<PointPairId>(
               all_point_pairs.size(),
               [&](PointPairId segment_id) {
                   const PointPair &segment = all_point_pairs[segment_id];
                   return static_cast<double>(
                       SquaredDist(point(segment.first), point(segment.second))
                   );
               }
           );

       SegmentBuckets result;
       for_each_bucket_from_sorted_keyed_ids(
           keyed_segments, EPS,
           [&](std::vector<PointPairId> bucket, double) {
               result.buckets.push_back(std::move(bucket));
           },
           2, "segment lengths"
       );
       return result;
   }

``min_bucket_size = 2`` here means singleton buckets (a length that occurs only
once) are dropped, because a single segment can never form an equal-length
*pair*. Whether your new cache should drop singletons depends on what the
consuming provider needs — decide this deliberately and document it, the way
this function's comment does.

Yuclid lazy cache addition steps
-----------------------------------

1. **Identify the repeated computation** a provider needs. Good next
   candidates, per the predicate-role table in
   ``predicate_matching_metadata.cpp``, are collinearity groups (for a future
   ``coll`` provider) and cyclic/circle groups (for ``cyclic``/``circumcenter``).
   Perpendicular/parallel direction lookup is *already built* —
   ``line_orientation_buckets()`` — it just needs a provider.

2. **Add the plain data type(s)** to ``geometry_cache_types.hpp``, next to
   ``PointPair``/``SegmentBuckets``/``LineOrientationBuckets``. Keep them
   independent of any one provider — they should answer a reusable geometry
   question ("which point pairs share a length/orientation/whatever"), not
   encode a specific predicate's search policy. Storing ``PointPairId``
   indices into the existing ``point_pairs()`` list (rather than copying
   ``PointPair``/``Point`` values into every bucket) keeps memory bounded and
   is the convention every existing cache view follows.

3. **Add a private ``build_*()`` method and a public lazy getter** to
   ``LazyGeometryCache``, following the ``m_segment_length_buckets``/
   ``segment_length_buckets()`` pair exactly: an ``mutable std::optional<T>``
   member, and a getter that builds-if-empty then returns a ``const T&``.

4. **Build from stable problem data only.** Use ``ProblemPointIndex`` values
   and ``point(index)`` coordinates — never store raw temporary ``Point``
   copies tied to one search branch, and never key off anything from
   ``MappingState`` (the cache is built once per ``Problem`` and reused across
   every rule and every search branch; see ``GenericRuleMatcher::optimized_match``
   constructing exactly one ``LazyGeometryCache`` before its rule loop).

5. **Beware "same direction" versus "same line."** A tempting shortcut for a
   future ``coll`` cache is to reuse ``line_orientation_buckets()`` — but that
   groups pairs with the same *direction*, which is necessary but not
   sufficient for three points to be collinear: two parallel-but-distinct
   lines share an orientation bucket. A real collinearity cache needs a key
   that also captures the line's offset/intercept (or an explicit
   points-on-this-line index), not slope alone. This is exactly the kind of
   subtlety a cache's own unit tests should pin down before any provider
   relies on it.

6. **Use the cache from a provider.** The cache never drives search itself;
   it is inert data. A provider's ``generate_extensions``/``estimate_extensions``
   requests the relevant view and turns it into ``MappingExtension`` objects (see
   :doc:`add_a_predicate_provider`).

7. **Add the source file to the build** if you split the new cache into its
   own translation unit — ``yuclid/src/CMakeLists.txt`` lists matcher sources
   explicitly (see :doc:`../modules/build_and_packaging`). If you are only
   adding methods to the existing ``lazy_geometry_cache.cpp``, nothing to add.

8. **Add tests** in ``yuclid/test/lazy_geometry_cache.cpp`` (or a new test file
   registered in ``yuclid/test/CMakeLists.txt``). Follow the structure already
   there — see ``yuclid/test/lazy_geometry_cache.cpp`` for the exact patterns
   to copy:

   - an empty-problem case (``cache.num_points() == 0``, every view empty);
   - a single-point case (no pairs at all);
   - a "repeated access reuses cached storage" case, asserting
     ``&first_call_result == &second_call_result`` — this is what actually
     proves the getter is lazy-and-cached rather than rebuilding every call;
   - grouping correctness (equal keys land in the same bucket, e.g.
     ``equal_segment_lengths_are_grouped``);
   - ordering (buckets come out in ascending key order);
   - a singleton-handling case matching whatever ``min_bucket_size`` you chose;
   - at least one test that exercises a *provider* consuming the new cache, so
     a bucketing regression is caught even if the low-level cache test still
     passes by coincidence.

   .. code-block:: bash

      cmake --build yuclid/build
      ctest --test-dir yuclid/build -R "lazy_geometry_cache|geometry_bucket_utils"

Yuclid lazy cache design rule
-----------------------------

A cache should speed up candidate generation without changing matcher
semantics. If adding a cache changes which theorem candidates get accepted,
treat that as a matcher bug unless the previous behavior was demonstrably
incorrect — cache buckets are an optimization layer, not a source of truth.
Final theorem validation (``check_hypotheses_nondeg_numerically()`` and
``check_numerically()`` in ``GenericRuleMatcher::build_valid_theorems_from_mappings``)
still runs on every candidate a cache-backed provider produces; see
:doc:`../modules/lazy_geometry_cache` for the fuller design rationale
(ownership split between cache and provider, why construction is lazy, and why
buckets are not proof by themselves).
