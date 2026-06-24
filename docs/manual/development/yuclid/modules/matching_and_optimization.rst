Yuclid matching and optimization
================================

The generic matcher is designed to stay complete while avoiding the worst cases
of brute-force enumeration. Optimization comes from planning, provider estimates,
lazy caches, and early pruning.

Yuclid search optimization flow
-------------------------------

.. code-block:: text

   choose planned predicate
      -> estimate provider extensions
      -> generate candidate mapping extensions
      -> apply extension to MappingState
      -> run available check-only predicates
      -> backtrack on rejection
      -> build theorem when mapping is complete

Yuclid selective predicates
---------------------------

A selective predicate is a predicate that can generate a small candidate set from
geometry. ``cong`` is the first optimized provider because equal-length segment
buckets are much smaller than all point quadruples.

Yuclid check-only pruning
-------------------------

Some predicates are useful even if they cannot generate candidates yet. Once
their variables are assigned, they can reject the current mapping immediately.
This avoids building theorem candidates that will fail later.

Yuclid fallback cost
--------------------

Fallback enumeration keeps the matcher complete, but it can become expensive
when a rule has many variables and no selective positive predicate. If a rule is
slow, first identify which predicate could provide a selective index, then add a
provider or cache for that predicate.

Yuclid optimization safety rule
-------------------------------

An optimization must not skip valid mappings. Provider estimates may be
heuristic, but ``generate_extensions`` and ``is_satisfied`` must preserve the
semantics of the predicate. Final theorem validation remains required even after
provider checks pass.
