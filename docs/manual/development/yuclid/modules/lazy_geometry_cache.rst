Yuclid lazy geometry cache
==========================

The lazy geometry cache stores geometry indexes used by predicate providers. It
exists so providers can reuse expensive computations instead of rebuilding them
for every predicate and every search branch.

Yuclid cache responsibilities
-----------------------------

The cache should:

- expose problem points by stable point index;
- build point pairs once;
- build segment length buckets only when requested;
- keep bucket/index data reusable across providers;
- avoid changing matcher semantics.

Yuclid segment length buckets
-----------------------------

The congruence provider uses segment length buckets. Each bucket groups point
pairs that have the same squared distance within Yuclid's numeric tolerance.
This lets ``cong`` matching search equal-length segments directly.

Yuclid cache design rule
------------------------

Providers should ask the cache for geometry indexes. They should not recompute
large global structures inside ``generate_extensions``. This keeps provider code
simpler and makes future predicates share the same cached data.

Yuclid future cache candidates
------------------------------

Good future cache additions include:

- collinearity groups for ``coll`` and ``ncoll``;
- line direction buckets for ``para``;
- perpendicular direction lookup for ``perp``;
- circle or cyclic groups if cyclic predicates become indexed.

Yuclid point-pair index
-----------------------

Many providers reason about pairs of problem points. The cache gives those pairs
stable integer ids so buckets can store lightweight ids instead of repeatedly
copying point pairs.

.. code-block:: text

   point_pairs()[pair_id] -> (point_index_1, point_index_2)

This is useful for ``cong`` because a segment-length bucket can store a list of
``PointPairId`` values. The provider can then recover the actual endpoints only
for candidate pairs it needs to inspect.

Yuclid lazy segment bucket construction
---------------------------------------

Segment length buckets are built from all unordered point pairs. Each pair is
assigned to a bucket according to squared distance. Providers can then ask:

.. code-block:: text

   Which point pairs have the same segment length as this known segment?

This changes ``cong`` matching from broad point enumeration into bucket lookup.
For a problem with many points, that difference is the main reason the optimized
matcher can stay interactive.

Yuclid why the cache is lazy
----------------------------

The matcher should not precompute every possible geometry index for every run.
Different custom rules use different predicates. A rule with only congruence
constraints does not need collinearity groups; a future rule with only parallel
constraints may not need segment length buckets.

Lazy construction gives this behavior:

.. code-block:: text

   provider requests index
       ↓
   cache builds it once if missing
       ↓
   all later providers/search branches reuse it

That keeps startup work proportional to the predicates actually used by custom
rules.

Yuclid cache ownership rule
---------------------------

The cache owns reusable geometry indexes. Providers own predicate-specific logic.
This means:

- the cache may group point pairs by length;
- the ``cong`` provider decides how to use those groups for ``cong A B C D``;
- the cache may later group points by line identity;
- a future ``coll`` provider decides how to use those line groups for collinearity.

Do not put predicate-specific search policy into the cache. The cache should
answer reusable geometry questions, not know how to match whole rule schemas.

Yuclid cache and final validation
---------------------------------

Cache buckets are an optimization. They should not be treated as proof by
themselves. Numeric tolerance, degeneracy, and theorem validity are still checked
later through provider satisfaction checks and final theorem validation.

For example, a segment length bucket can tell ``CongProvider`` which segment
pairs are worth trying. The resulting congruence statement should still be
checked before the candidate theorem is accepted.

Yuclid cache extension checklist
--------------------------------

When adding a new cache:

1. Define the reusable geometry data type.
2. Add a lazy getter to ``LazyGeometryCache``.
3. Build the cache from the problem points only once.
4. Keep the data independent from one specific rule schema.
5. Add focused cache tests for bucket contents and edge cases.
6. Update the provider that consumes the cache.
7. Add matcher tests showing that the cache-backed provider preserves theorem output.
