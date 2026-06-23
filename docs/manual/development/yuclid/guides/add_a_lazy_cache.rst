Yuclid guide to adding a lazy cache
===================================

Use this guide when multiple providers need the same precomputed geometry, or
when one provider would otherwise recompute expensive data repeatedly.

Yuclid lazy cache addition steps
--------------------------------

1. Identify the repeated computation.

   Examples include collinearity groups, line direction buckets, perpendicular
   direction lookup, or cyclic groups.

2. Add cache data types.

   Put shared cache structs and aliases near the existing geometry cache types.
   Keep them independent of one specific provider when possible.

3. Add a lazy getter.

   The getter should build the cache on first use and then return the stored
   value on later calls.

4. Build from stable problem data.

   Use problem point indices and normalized geometric keys. Avoid storing raw
   temporary objects that depend on a search branch.

5. Use the cache from providers.

   Provider code should request the cache and generate extensions from it.

6. Add tests.

   Test the cache contents, lazy behavior, and at least one provider using the
   cache.

Yuclid lazy cache design rule
-----------------------------

A cache should speed up candidate generation without changing matcher semantics.
If adding a cache changes accepted theorem candidates, treat that as a matcher
bug unless the previous behavior was explicitly incorrect.
