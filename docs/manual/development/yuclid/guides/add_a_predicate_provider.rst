Yuclid guide to adding a predicate provider
===========================================

Use this guide when a custom-rule predicate (``coll``, ``para``, ``perp``, or any
predicate you are adding yourself) should get an optimized matcher instead of
falling back to :doc:`the base provider's <../modules/predicate_providers>`
brute-force enumeration. This is the single highest-leverage place to speed up
the generic matcher: today only ``cong`` has a specialized provider
(``CongProvider``), and every other candidate-generating predicate — ``coll``,
``para``, ``perp`` — is still routed to ``BaseProvider`` by
``GenericRuleMatcher::add_providers_to_registry()`` in
``yuclid/src/matchers/generic_rule_matcher.cpp``. Predicates classified as
``Validator`` (``midp``, ``eqangle``/``equal_angles``, ``eqratio``, ``cyclic``,
``circumcenter``/``circle``, ``simtri``/``simtrir``/``contri``/``contrir``,
``rconst``/``r2const``/``lconst``/``l2const``/``aconst``, ``sameclock``,
``obtuse_angle``, ``sameside``/``nsameside`` — see
``yuclid/src/matchers/predicate_matching_metadata.cpp``) never even get a
provider slot yet; they are only checked once fully assigned. Any of these is a
legitimate target for a new provider once a rule that uses it turns out to be
slow (see :doc:`optimize_a_generic_rule`).

Yuclid provider interface you are implementing
-----------------------------------------------

Every provider implements ``Yuclid::PredicateProvider``
(``yuclid/src/matchers/predicate_provider.hpp``):

.. code-block:: cpp

   class PredicateProvider {
   public:
       virtual ~PredicateProvider() = default;

       [[nodiscard]] virtual std::size_t estimate_extensions(
           const PlannedPredicate &predicate,
           const MappingState &mapping,
           const LazyGeometryCache &cache
       ) const = 0;

       [[nodiscard]] virtual std::generator<MappingExtension> generate_extensions(
           const PlannedPredicate &predicate,
           const MappingState &mapping,
           const LazyGeometryCache &cache
       ) const = 0;

       [[nodiscard]] virtual bool is_satisfied(
           const PlannedPredicate &predicate,
           const MappingState &mapping,
           const LazyGeometryCache &cache
       ) const = 0;
   };

All three methods receive the same three things:

- ``predicate`` (a ``PlannedPredicate``, from ``yuclid/src/matchers/rule_plan.hpp``) —
  ``predicate.pattern`` is the raw ``RulePredicatePattern`` (``name`` plus the
  original ``args`` strings, in the exact order written in the rule file, with
  duplicates preserved), and ``predicate.variable_indices`` is the **deduplicated**
  list of rule-variable indices the predicate touches, in first-appearance order.
  For ``cong A B A C``, ``pattern.args`` is ``["A", "B", "A", "C"]`` but
  ``variable_indices`` is only ``[index(A), index(B), index(C)]`` — you have to
  re-derive which argument positions repeat a variable yourself (see
  ``get_predicate_local_var_indexes`` in ``cong_provider.cpp`` for a small helper
  that does this).
- ``mapping`` (a ``MappingState``, from ``yuclid/src/matchers/mapping_state.hpp``) —
  the partial variable→point assignment for the current search branch. Use
  ``mapping.is_assigned(var_idx)``, ``mapping.assigned_point_index(var_idx)``, and
  ``mapping.is_point_used(point_idx)``.
- ``cache`` (a ``LazyGeometryCache``, see :doc:`add_a_lazy_cache`) — shared,
  lazily-built geometry indexes such as ``point_pairs()`` and
  ``segment_length_buckets()``.

The three methods are used at different moments by
``GenericRuleMatcher::search()`` (``yuclid/src/matchers/generic_rule_matcher.cpp``):

.. list-table::
   :widths: 26 34 40
   :header-rows: 1

   * - Method
     - Called when
     - Contract
   * - ``estimate_extensions``
     - For every not-yet-fully-assigned ``candidate_generators`` predicate, before
       the matcher picks which one to expand next (``get_cheapest_predicate``).
     - Cheap, approximate, never used for correctness — only for ordering. Must
       still be consistent enough that a genuinely selective predicate scores
       lower than a genuinely unselective one.
   * - ``generate_extensions``
     - Once for the predicate ``get_cheapest_predicate`` picked, whose provider
       is looked up via ``m_provider_registry.get_provider(name)``.
     - A lazy ``std::generator<MappingExtension>``. Every yielded extension is
       passed to ``mapping_state.try_apply_extension(extension)``, which
       silently rejects and rolls back an extension that reassigns an
       already-used point, so it is safe (if wasteful) to over-generate, but
       it must never *skip* a mapping that could lead to a valid theorem.
   * - ``is_satisfied``
     - Once a predicate's ``variable_indices`` are *all* assigned — either
       because it is a ``Validator``-role predicate reached in the FILTER STAGE
       of ``search()``, or because ``BaseProvider::is_satisfied`` is asked to
       double-check your own predicate.
     - Pure boolean check against the fully-bound mapping. False means "prune
       this branch."

Providers are looked up by predicate name through
``PredicateProviderRegistry`` (same header): ``get_provider(name)`` returns the
registered provider for ``name``, or the mandatory fallback (always
``BaseProvider`` today) if nothing was registered.

Yuclid provider addition steps
--------------------------------

1. **Decide the predicate shape first.** Fix the name, arity, argument order,
   and which argument positions may legally repeat the same variable (e.g.
   ``cong A B A C`` — isosceles shape — vs. ``cong A B C D`` — independent
   segments). Confirm this matches what ``yuclid/src/rules/schema_validator.cpp``
   already accepts for that predicate name; if it does not exist yet at all,
   do :doc:`add_a_supported_predicate` first.

2. **Create the provider class.** Add
   ``yuclid/src/matchers/<predicate>_provider.hpp`` and ``.cpp`` next to
   ``cong_provider.hpp``/``.cpp``, deriving from ``PredicateProvider``:

   .. code-block:: cpp

      // para_provider.hpp
      #pragma once
      #include "predicate_provider.hpp"

      namespace Yuclid {
          /** Handles matching for `para A B C D` (line AB parallel to line CD). */
          class ParaProvider : public PredicateProvider {
          public:
              [[nodiscard]] std::size_t estimate_extensions(
                  const PlannedPredicate &predicate,
                  const MappingState &mapping,
                  const LazyGeometryCache &cache
              ) const override;

              [[nodiscard]] std::generator<MappingExtension> generate_extensions(
                  const PlannedPredicate &predicate,
                  const MappingState &mapping,
                  const LazyGeometryCache &cache
              ) const override;

              [[nodiscard]] bool is_satisfied(
                  const PlannedPredicate &predicate,
                  const MappingState &mapping,
                  const LazyGeometryCache &cache
              ) const override;
          };
      }

3. **Implement ``is_satisfied`` first.** It is the smallest of the three methods
   and it doubles as your numerical oracle while you write the other two. The
   simplest correct body mirrors ``CongProvider::is_satisfied``: recover the
   bound points, build the real engine ``Statement`` for this predicate, and
   call ``check_nondegen()``/``check_equations()`` (or reuse
   ``build_statements_from_pattern`` plus ``check_numerically()``, exactly what
   ``BaseProvider::is_satisfied`` does, if you do not want to depend on a
   specific ``Statement`` subclass):

   .. code-block:: cpp

      bool ParaProvider::is_satisfied(
          const PlannedPredicate &predicate,
          const MappingState &mapping,
          const LazyGeometryCache &cache
      ) const {
          assert(predicate.pattern.args.size() == 4);
          auto a = mapping.assigned_point_index(predicate.variable_indices[0]);
          auto b = mapping.assigned_point_index(predicate.variable_indices[1]);
          auto c = mapping.assigned_point_index(predicate.variable_indices[2]);
          auto d = mapping.assigned_point_index(predicate.variable_indices[3]);
          if (!a || !b || !c || !d) return false; // not fully bound: fail safe

          Parallel para_statement(
              SlopeAngle(cache.point(*a), cache.point(*b)),
              SlopeAngle(cache.point(*c), cache.point(*d))
          );
          return para_statement.check_nondegen() && para_statement.check_equations();
      }

   Note the ``predicate.variable_indices[i]`` indirection: it is only valid to
   index ``variable_indices`` by *position of first appearance*, not by literal
   argument position, once duplicate variables are involved — copy
   ``get_predicate_local_var_indexes`` from ``cong_provider.cpp`` if your
   predicate allows repeats.

4. **Implement ``generate_extensions``.** Handle each "which variables are
   already assigned" case explicitly — do not try to write one generic branch
   for all of them. ``CongProvider::generate_extensions`` in
   ``yuclid/src/matchers/cong_provider.cpp`` is the fully worked reference:
   it switches on a 4-bit mask of which of the 4 argument variables already
   have a point, and handles 0, 1, 2 (both adjacent and independent), 3, and 4
   assigned points as separate cases, plus a fast "tautology" path when the
   predicate is a pure identity (``cong A B A B``). For a new predicate you do
   not need every case on day one — start with the cheapest to implement (fully
   unassigned, and "one full side/shape known") and let the rest fall through
   to ``BaseProvider`` semantics only if you are certain that is still correct;
   otherwise a wrong ``generate_extensions`` silently drops valid theorems
   forever, so prefer *emitting more than necessary* while you flesh it out.
   For ``para``/``perp`` specifically, ``LazyGeometryCache::line_orientation_buckets()``
   (see :doc:`add_a_lazy_cache`) already groups point pairs by undirected line
   orientation, with perpendicular pairs one half-turn apart in key space — no
   provider consumes it yet, so it is the natural starting point:

   .. code-block:: cpp

      std::generator<MappingExtension> ParaProvider::generate_extensions(
          const PlannedPredicate &predicate,
          const MappingState &mapping,
          const LazyGeometryCache &cache
      ) const {
          // Case: nothing assigned yet - yield every pair of point pairs that
          // share an orientation bucket (mirrors CongProvider's 0b0000 case,
          // but keyed by line orientation instead of segment length).
          const auto &orientations = cache.line_orientation_buckets();
          const auto &pairs = cache.point_pairs();

          for (const auto &bucket : orientations.buckets) {
              for (std::size_t i = bucket.begin; i < bucket.end; ++i) {
                  for (std::size_t j = bucket.begin; j < bucket.end; ++j) {
                      if (i == j) continue;
                      const PointPair &ab = pairs[orientations.ordered_point_pair_ids[i]];
                      const PointPair &cd = pairs[orientations.ordered_point_pair_ids[j]];

                      if (mapping.is_point_used(ab.first) || mapping.is_point_used(ab.second) ||
                          mapping.is_point_used(cd.first) || mapping.is_point_used(cd.second)) continue;

                      MappingExtension ext;
                      ext.add_assignment(predicate.variable_indices[0], ab.first);
                      ext.add_assignment(predicate.variable_indices[1], ab.second);
                      ext.add_assignment(predicate.variable_indices[2], cd.first);
                      ext.add_assignment(predicate.variable_indices[3], cd.second);
                      co_yield ext;
                      // ... plus the endpoint-swapped and partially-assigned
                      // cases, following CongProvider's structure.
                  }
              }
          }
      }

   This sketch is illustrative, not a drop-in ``ParaProvider`` — it is missing
   the partially-assigned cases and the directional-swap permutations that
   ``CongProvider`` handles explicitly. Treat ``CongProvider`` as the level of
   completeness to aim for before merging.

5. **Implement ``estimate_extensions``.** It must return a ``std::size_t`` that
   is monotonically "smaller when more selective." The minimum viable version
   is ``predicate.metadata.base_cost`` plus a rough count (bucket size, or
   ``variation_with_cap`` from ``base_provider.cpp`` for a raw permutation
   count) — see ``CongProvider::estimate_extensions`` for the full bit-mask
   version with an "intersection reduction" heuristic for when an anchor point
   is already known. Getting this exactly right is less important than getting
   it in the right ballpark: it only affects which predicate ``search()`` tries
   first, never correctness.

6. **Register the provider.** In
   ``GenericRuleMatcher::add_providers_to_registry()``
   (``yuclid/src/matchers/generic_rule_matcher.cpp``):

   .. code-block:: cpp

      void GenericRuleMatcher::add_providers_to_registry() {
          // add all providers that are implemented
          m_provider_registry.register_provider("para", std::make_unique<ParaProvider>());
      }

   .. warning::
      Double-check what is registered for the predicate name you are touching.
      As of this writing, this function actually registers
      ``std::make_unique<BaseProvider>()`` for ``"cong"`` instead of
      ``CongProvider`` — ``CongProvider`` is fully implemented and unit-tested,
      but not yet wired in. Forgetting this step (or, as here, registering the
      wrong class) does not fail to compile or fail any test that does not
      specifically exercise the registry — it silently falls back to
      ``BaseProvider`` and you get correct-but-slow behavior. If you are adding
      a provider, register it here and also add a regression test like
      ``registry_routes_to_specific_provider`` in
      ``yuclid/test/provider_registry.cpp`` that asserts ``get_provider(name)``
      no longer returns the fallback instance.

7. **Add the source file to the build.** New matcher ``.cpp`` files must be
   added explicitly to ``yuclid/src/CMakeLists.txt`` (it is a hand-maintained
   list, not a glob) — see :doc:`../modules/build_and_packaging` and
   :doc:`../setup`.

8. **Add tests.** Add ``yuclid/test/<predicate>_provider.cpp`` and register it
   in the ``foreach(name ...)`` list in ``yuclid/test/CMakeLists.txt`` next to
   ``cong_provider``. Structure it like ``yuclid/test/cong_provider.cpp``:

   - a fixture that builds a small ``Problem``, a 4-ish-variable ``RuleSchema``,
     and a helper ``build_planned_pred`` that constructs a ``PlannedPredicate``
     by hand (see ``CongProviderFixture`` for the pattern);
   - ``is_satisfied`` cases: a true case, a false case, a degenerate case (e.g.
     two argument positions mapped to the same point where the predicate
     requires them distinct), and a "not fully assigned" failsafe case;
   - ``estimate_extensions`` cases for each assignment-mask you implemented,
     with the exact expected number worked out by hand in a comment (see how
     ``estimate_state_1100_length_known`` documents its arithmetic);
   - ``generate_extensions`` cases that assert both the *count* and, for at
     least one case, the *actual signatures* of yielded extensions (build a
     ``std::string`` signature like ``consume_generator`` does in
     ``cong_provider.cpp``, to catch a provider that yields the right count but
     the wrong assignments);
   - at least one duplicate-variable case (``cong A B A C`` style) proving the
     provider assigns the same point to both occurrences of the repeated
     variable;
   - one ``GenericRuleMatcher`` integration test (see
     ``yuclid/test/generic_rule_matcher.cpp``) constructing a real ``RuleSchema``
     that uses your predicate and asserting ``optimized_match()`` returns the
     expected theorem(s) — this is what actually proves the provider is wired
     into search correctly, not just correct in isolation.

   Run the suite with:

   .. code-block:: bash

      cmake --build yuclid/build
      ctest --test-dir yuclid/build -R "_provider|generic_rule_matcher"

Yuclid provider review checklist
----------------------------------

Before opening the merge request, check:

- Does the provider preserve completeness? (No case where a valid mapping is
  silently never yielded — when in doubt, over-generate and let
  ``is_satisfied``/final validation reject the rest.)
- Does it handle repeated variables correctly, both when generating (assigning
  the same point to every occurrence of a repeated variable, not conflicting
  occurrences to different points) and when the schema uses genuinely
  different variables that happen to map to the same point (should usually be
  rejected)?
- Does it use ``LazyGeometryCache`` instead of rebuilding global geometry
  inside ``generate_extensions``/``estimate_extensions``?
- Does it check ``mapping.is_point_used(...)`` before yielding, rather than
  relying only on ``try_apply_extension`` to reject conflicts? (Correct either
  way, but skipping the check makes the matcher slower for no benefit.)
- Is the provider actually registered for the predicate name in
  ``add_providers_to_registry()``, and is there a test that would fail if that
  registration line were deleted or pointed at the wrong class?
- Does final theorem validation still run after provider acceptance? (It
  always does — ``GenericRuleMatcher::build_valid_theorems_from_mappings``
  calls ``check_hypotheses_nondeg_numerically()`` and ``check_numerically()``
  on every candidate regardless of which provider produced it — but a provider
  should not be relied on as the only correctness guard.)

See also :doc:`../modules/predicate_providers` for the conceptual model, and
:doc:`optimize_a_generic_rule` for how to decide *which* predicate is worth
turning into a provider next.
