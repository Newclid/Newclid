Yuclid guide to adding a predicate provider
===========================================

Use this guide when a custom-rule predicate needs an optimized matcher instead
of fallback enumeration.

Yuclid provider addition steps
------------------------------

1. Define the predicate shape.

   Decide the predicate name, arity, argument semantics, and how duplicate
   variables should behave.

2. Add a provider class.

   Implement the ``PredicateProvider`` interface in a focused provider such as
   ``CollProvider`` or ``ParaProvider``.

3. Implement ``estimate_extensions``.

   Return a cheap estimate of how many mappings the provider can generate from
   the current ``MappingState``. This estimate is used for planning, so it should
   be fast even if it is approximate.

4. Implement ``generate_extensions``.

   Lazily yield ``MappingExtension`` objects. Preserve variable equality and
   avoid assigning already-used problem points incorrectly.

5. Implement ``is_satisfied``.

   Check a fully bound mapping using the same predicate semantics that Yuclid
   uses elsewhere.

6. Register the provider.

   Add the provider to the registry or provider selection point used by the rule
   planner.

7. Add tests.

   Test estimates, generated mappings, duplicate-variable cases, rejected
   mappings, and at least one generic matcher integration case.

Yuclid provider review checklist
--------------------------------

Before opening the merge request, check:

- Does the provider preserve completeness?
- Does it handle repeated variables correctly?
- Does it use ``LazyGeometryCache`` instead of rebuilding global geometry?
- Does it fall back safely when no matching bucket/index exists?
- Does final theorem validation still run after provider acceptance?
