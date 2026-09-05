Yuclid guide to optimizing a generic rule
=========================================

Use this guide when a custom rule parses, matches correctly, but is too slow —
usually because one of its predicates falls back to
``BaseProvider``'s permutation enumeration (see
``yuclid/src/matchers/base_provider.cpp``) instead of an indexed provider.

Yuclid optimization steps
--------------------------

1. **Reproduce with the smallest possible input.** Save the exact problem and
   custom-rule file that are slow, then run Yuclid directly instead of through
   the full Python/Newclid stack:

   .. code-block:: bash

      yuclid --mode match \
        --input-file problem.txt \
        --input-additional-rules-file custom_rules.txt \
        --log-level debug

   ``--mode match`` runs only the matching path (no DDAR proof search on top),
   which isolates whether the cost is in candidate generation or elsewhere.
   Trim the problem down to the fewest points/constructions that still
   reproduce the slowdown — every provider's cost scales with
   ``cache.num_points()``, so a smaller problem both reproduces faster and
   makes the next steps' estimates easier to verify by hand.

2. **Find which predicate is expensive.** Look at the rule's premises in the
   order ``build_rule_plan`` (``yuclid/src/matchers/rule_plan.cpp``) would sort
   them into ``candidate_generators`` versus ``validators`` versus
   ``unsupported_predicates``. A predicate lands in ``candidate_generators``
   only if ``predicate_matching_metadata.cpp`` classifies it
   ``CandidateGenerator`` — currently just ``coll``, ``cong``, ``para``,
   ``perp``. Everything else (``eqangle``, ``midp``, ``cyclic``, ``simtri``,
   ``eqratio``, ``rconst``, and friends) is ``Validator``-role and is only
   evaluated once every variable it touches is already bound by some other
   predicate — or, if no ``candidate_generators`` predicate remains unassigned,
   it gets tried as a *fallback generator* too, via
   ``GenericRuleMatcher::get_cheapest_predicate`` falling through to
   ``plan.validators`` in ``search()``. In both fallback cases the actual
   provider doing the work is ``BaseProvider``, unless you have added one (see
   :doc:`add_a_predicate_provider`).

3. **Check whether a real provider exists for that predicate name**, in
   ``GenericRuleMatcher::add_providers_to_registry()``
   (``yuclid/src/matchers/generic_rule_matcher.cpp``). Only predicates
   explicitly ``register_provider("name", ...)``'d there get anything other
   than ``BaseProvider``. As of this writing that function registers a
   provider only for ``"cong"`` (and, confusingly, registers ``BaseProvider``
   there rather than the fully-implemented ``CongProvider`` — check the
   current source before assuming ``cong`` is actually fast in your build).
   ``coll``, ``para``, and ``perp`` are tagged ``CandidateGenerator`` but have
   no registered provider at all yet, so they *look* selective in the rule
   plan but still enumerate permutations through ``BaseProvider``.

4. **Estimate the blowup by hand.** ``BaseProvider::estimate_extensions``
   returns ``base_cost + P(free_points, unassigned_vars)`` (a partial
   permutation count, see ``variation_with_cap`` in ``base_provider.cpp``,
   capped at 100,000,000). If a predicate has 3+ still-unassigned variables and
   your problem has more than a handful of points, this number gets large
   fast — a rule whose first predicate to expand has 4 unassigned variables
   over 20 points is already ``P(20,4) = 116,280`` branches for *that one
   predicate alone*, before recursing into the rest of the rule.

5. **Add the smallest provider or cache that helps**, per
   :doc:`add_a_predicate_provider` / :doc:`add_a_lazy_cache`. You do not need
   to handle every assignment-state case immediately — even handling just the
   "all variables of this predicate are free" and "one full sub-shape is
   already known" cases (the cheapest cases to implement, and usually the ones
   actually hit first in a DFS search) can turn an ``O(n^k)`` enumeration into
   a bucket lookup. Compare against ``CongProvider``'s case-by-case structure
   in ``yuclid/src/matchers/cong_provider.cpp`` for the shape a complete
   provider takes.

6. **Preserve final validation — do not bypass it.** Optimization changes
   *how* candidates are generated, never *which* candidates are ultimately
   accepted. ``GenericRuleMatcher::build_valid_theorems_from_mappings`` still
   calls ``check_hypotheses_nondeg_numerically()`` and ``check_numerically()``
   on every mapping your provider produces, regardless of how it was
   generated. If a provider needs to reject a mapping early for performance,
   it must do so only when the predicate makes it *definitely* impossible
   (wrong segment length, wrong bucket, violates a duplicate-variable
   equality) — never based on a guess about the rest of the rule.

7. **Benchmark before and after, on the same input.** ``yuclid/test/cong_provider.cpp``'s
   ``run_comparison`` helper is a good template: it calls both
   ``estimate_extensions`` and a full consumption of ``generate_extensions``
   and logs both numbers via ``BOOST_TEST_MESSAGE`` (visible with
   ``ctest --test-dir yuclid/build -R cong_provider -V``), so you can compare
   "predicted branch count" against "actual yielded extensions" across
   several point configurations (a small grid, a large grid, an irregular
   layout — see ``setup_geometry``/``setup_large_grid``/``setup_irregular_geometry``
   in that file). At the whole-rule level, compare wall-clock time for
   ``--mode match`` and confirm the *same* set of accepted theorems comes out
   before and after — a faster matcher that silently drops or duplicates
   theorems is a regression, not an optimization.

Yuclid optimization warning signs
-----------------------------------

A rule likely needs optimization if:

- it has 3+ variables and its only ``CandidateGenerator``-role predicate is
  one that has no registered provider yet (``coll``, ``para``, ``perp`` today —
  double-check ``cong`` too, see step 3);
- ``--log-level debug`` (or a quick instrumented run) shows
  ``get_cheapest_predicate`` repeatedly selecting a ``Validator``-role
  predicate as a fallback generator, i.e. the rule has no selective
  ``CandidateGenerator`` predicate at all;
- it creates many mapping extensions that ``try_apply_extension`` or a later
  filter/validator immediately rejects — a sign that ``estimate_extensions``
  is picking the wrong predicate to expand first, or that a provider is not
  pruning based on information it already has;
- most wall-clock time is spent before any theorem is ever handed to
  ``build_valid_theorems_from_mappings`` — i.e. the cost is in search, not in
  theorem construction or validation.

See :doc:`debug_generic_matching` if the rule is not just slow but is also
producing the wrong candidates, and :doc:`../modules/matching_and_optimization`
for the broader design rationale behind the search loop.
