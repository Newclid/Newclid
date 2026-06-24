Yuclid guide to optimizing a generic rule
=========================================

Use this guide when a custom rule works but matching is too slow.

Yuclid optimization steps
-------------------------

1. Identify the expensive rule.

   Reproduce the issue with a focused problem and custom rule file. Prefer
   ``--mode match`` before running the full solver.

2. Inspect the predicates.

   Look for a selective positive predicate that can generate a small candidate
   set, such as equal segment length, collinearity, parallelism, or
   perpendicularity.

3. Check whether a provider exists.

   If the rule starts from a predicate handled only by the base provider, the
   matcher may enumerate many point assignments.

4. Add a provider or cache.

   Add the smallest provider/cache that turns the expensive predicate into an
   indexed generator or a cheap check-only predicate.

5. Preserve final validation.

   Optimization should reduce the search space, not bypass theorem validation.

6. Benchmark before and after.

   Record matcher time, theorem count, and whether the same accepted theorems are
   produced.

Yuclid optimization warning signs
---------------------------------

A rule likely needs optimization if:

- it has many variables and no selective indexed predicate;
- it falls back to base-provider enumeration;
- it creates many mapping extensions that are later rejected;
- it spends most time before theorem construction.
