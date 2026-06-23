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
