Yuclid guide to debugging generic matching
==========================================

Use this guide when a custom rule parses but does not produce the expected
matches, produces too many matches, or produces candidates that final
validation rejects. It walks the same path
``GenericRuleMatcher::optimized_match()`` (``yuclid/src/matchers/generic_rule_matcher.cpp``)
takes internally, so you can localize a bug to one stage instead of guessing.

Yuclid fastest way to reproduce
-----------------------------------

Two reproduction paths, cheapest first:

- **A C++ unit test**, if you can express the rule as a ``RuleSchema`` in code.
  This is the fastest inner loop — no process spawn, no file I/O, a debugger
  attaches directly. Follow the pattern in ``yuclid/test/generic_rule_matcher.cpp``:

  .. code-block:: cpp

     Problem prob;
     (void) prob.add_point("A", 0.0, 0.0);
     (void) prob.add_point("B", 1.0, 0.0);
     // ... enough points to make the rule matchable

     RuleSchema schema;
     schema.id = "debug_rule";
     schema.variables = {"X", "Y", "Z"};
     schema.hypotheses.push_back({"coll", {"X", "Y", "Z"}});
     schema.conclusions.push_back({"cong", {"X", "Y", "X", "Z"}});

     std::vector<RuleSchema> rules = {schema};
     GenericRuleMatcher matcher(&prob, rules);
     std::vector<Theorem> results = matcher.optimized_match();

- **The Yuclid CLI**, if the bug only shows up with a real rule file or you do
  not yet know the minimal ``Problem``:

  .. code-block:: bash

     yuclid --mode match \
       --input-file problem.txt \
       --input-additional-rules-file custom_rules.txt \
       --log-level debug

  ``--mode match`` skips DDAR proof search, so any candidate the generic
  matcher accepts shows up directly. ``--log-level debug`` surfaces the
  ``BOOST_LOG_TRIVIAL(warning)`` lines ``optimized_match()`` already emits when
  it skips a schema entirely — schema validation failure, "insufficient number
  of points in problem," unsupported predicates, or a per-schema exception —
  which is the fastest way to rule out steps 1–3 below without instrumenting
  anything yourself.

Yuclid generic matching triage
------------------------------

Debug in this order, matching the stages inside ``optimized_match()``:

1. **Confirm the rule file parses.** ``parser/rule_parser.cpp``'s
   ``parse_rule_schemas`` throws ``std::runtime_error`` on the first structural
   problem (duplicate variable, unknown ``require``/``conclude``/``end``
   action, missing ``end``) — a parse failure means no ``RuleSchema`` is
   produced at all, so nothing downstream runs.

2. **Confirm schema validation accepts it.**
   ``rules/schema_validator.cpp``'s ``validate_schema`` checks arity per
   predicate name and that every non-constant argument is a declared variable.
   A validation failure is logged as a warning and the whole schema is
   skipped — silently, from the caller's point of view, unless you are
   watching the log. If your rule "does nothing," this is the single most
   common cause; check ``--log-level debug`` output first.

3. **Check the generated ``RulePlan``.**
   ``matchers/rule_plan.cpp``'s ``build_rule_plan`` sorts every hypothesis and
   conclusion into one of ``candidate_generators``, ``candidate_filters``,
   ``validators``, or ``unsupported_predicates``, based on
   ``predicate_matching_metadata.cpp``. Any predicate landing in
   ``unsupported_predicates`` causes ``optimized_match()`` to skip the whole
   schema (again, only visible as a warning log). Check
   ``planned.variable_indices`` too if the predicate has repeated variables
   (e.g. ``cong A B A C``) — it is deduplicated to first-appearance order, so
   an off-by-one there silently maps the wrong point to the wrong variable.

   .. warning::
      ``candidate_filters`` (the ``CandidateFilter`` role) is populated by
      ``build_rule_plan`` but **not read anywhere** in ``search()`` today. A
      predicate tagged ``CandidateFilter`` is neither used to generate
      candidates nor checked as a filter — if it is the only premise
      constraining some variable, that variable is never assigned and
      ``search()`` throws "Dead end reached: All predicates evaluated, but the
      mapping is incomplete." If you hit that exact error, check whether one
      of the rule's predicates was classified ``CandidateFilter`` (see
      :doc:`add_a_supported_predicate` for the same trap from the predicate
      side).

4. **Check which provider handles each predicate.**
   ``GenericRuleMatcher::add_providers_to_registry()`` is the only place
   provider registration happens; ``PredicateProviderRegistry::get_provider``
   silently returns the fallback ``BaseProvider`` for anything not registered
   there — there is no error or warning for "no specific provider," because
   that is the expected/common case. If a predicate you expect to be fast is
   actually still running through ``BaseProvider``, matching will still be
   *correct*, just slow (see :doc:`optimize_a_generic_rule`) — this step is
   about correctness bugs specific to a provider implementation, not speed.

5. **Inspect candidate ``MappingExtension`` objects.** Temporarily log or
   step through ``generate_extensions()`` for the suspect predicate/provider
   pair (identified in step 4). Confirm the assignments it yields use
   ``predicate.variable_indices[i]`` — indexed by *first-appearance position*,
   not raw argument position — as their variable index, and confirm point
   indices come from ``cache.point_pairs()``/other cache structures rather
   than being invented.

6. **Check ``MappingState`` rollback and used-point behavior.**
   ``search()`` calls ``mapping_state.try_apply_extension(extension)``, which
   is all-or-nothing: if any single assignment in the extension targets an
   already-used point, the whole extension is rejected and any partial
   assignments from it are rolled back automatically
   (``mapping_state.cpp``). Re-assigning the same variable to the same point
   it already holds is treated as a no-op success, not a conflict — so a
   provider yielding a redundant assignment for an already-bound variable is
   harmless, just wasted work. A search-level bug here almost always looks
   like variables staying ``UNASSIGNED_POINT`` (check
   ``mapping.is_assigned(var_idx)``) when they should not, or a point that
   should be free reporting ``is_point_used() == true`` after a rollback that
   did not actually happen (check the ``MappingStateSnapshot``/``rollback``
   pairing around your new code).

7. **Check check-only (``Validator``-role) predicates once their variables are
   assigned.** ``search()``'s FILTER STAGE loop (top of the function) walks
   ``plan.validators`` **linearly**, in schema order — unlike
   ``candidate_generators``, these are *not* cost-sorted, and a predicate is
   only checked once every one of its ``variable_indices`` happens to already
   be bound by something else. If a filter is failing (or, more subtly,
   passing when it should not), confirm ``FilterState::is_used``/``mark_used``
   bookkeeping: a filter already marked used earlier in the same DFS branch is
   skipped on the next call, and ``filter_state.rollback(filter_snapshot)``
   must run on every return path out of ``search()`` (it does, in current
   code, but a naive edit to add an early return can easily break this).

8. **Check theorem construction and final validation.**
   ``theorem_builder.cpp``'s ``build_theorem_from_rule_schema`` turns a
   complete ``RuleMapping`` into hypothesis/conclusion ``Statement`` objects
   via ``statement_builder.cpp``. Then
   ``build_valid_theorems_from_mappings`` calls, in order,
   ``check_hypotheses_nondeg_numerically()`` and ``check_numerically()`` — a
   candidate that is locally consistent for every individual predicate can
   still be rejected here (e.g. two points the rule treats as distinct turn
   out numerically equal in this problem instance, making a hypothesis
   degenerate).

Yuclid no matches symptom
-------------------------

If the rule produces no matches:

- check the log first (see the reproduction section) — a validation failure
  or an unsupported predicate skips the schema silently otherwise;
- verify the predicate names and argument order against
  ``schema_validator.cpp``'s expected arity table;
- verify that repeated variables are intentional, and that any provider
  involved re-derives repeated-argument positions correctly (see
  ``get_predicate_local_var_indexes`` in ``cong_provider.cpp`` for the
  reference technique) rather than assuming ``variable_indices`` lines up
  1:1 with ``pattern.args``;
- test the provider's ``is_satisfied`` directly, in a unit test, on a mapping
  you already know by hand should be accepted — this isolates "the provider's
  predicate logic is wrong" from "the mapping never reached ``is_satisfied``";
- check whether an indexed provider silently skips singleton or degenerate
  cases that are actually valid here — e.g. ``CongProvider``'s "tautology"
  fast path only triggers for a genuine identity pattern like
  ``cong A B A B``; a near-identity pattern that does not match that exact
  shape falls through to the bucket-based cases instead, which may behave
  differently than you expect for a length-0 or singleton segment;
- check whether a predicate got classified ``CandidateFilter`` (see step 3
  above) instead of ``Validator``;
- check whether final validation rejected every candidate (step 8) rather
  than none being generated at all — these look identical from the outside
  (empty result vector) but need different fixes.

Yuclid too many matches symptom
--------------------------------

If the rule produces too many candidates:

- check variable equality: a provider that does not enforce
  "same variable ⇒ same point, different variable ⇒ different point" (the
  ``check_var_equality`` pattern in ``cong_provider.cpp``) will happily
  generate mappings that collapse two supposedly-independent rule variables
  onto the same problem point, or split one repeated variable across two
  points;
- check whether a ``Validator``-role filter is not being applied as early as
  it could be — remember the FILTER STAGE is linear in schema order, so a
  cheap, highly restrictive filter placed after several expensive
  ``candidate_generators`` steps still only prunes *after* all of those
  branches are already explored;
- check whether a provider is generating both valid and invalid orientations
  of a symmetric predicate — e.g. ``cong``'s brute-force case intentionally
  yields all 4 directional permutations of two matched segments
  (``swap_state`` in ``cong_provider.cpp``'s ``0b0000`` branch); confirm this
  is what the *rule* actually wants, not an accidental duplication;
- confirm symmetric predicates are supposed to generate both orientations for
  your rule specifically — a rule that only cares about one orientation needs
  an explicit filter or a different predicate order, not a provider change.

Yuclid final rejection symptom
-------------------------------

If candidates are generated but rejected later, debug ``statement_builder.cpp``
and ``theorem_builder.cpp`` next. The provider may be locally correct — every
individual predicate it touches is genuinely satisfiable — while the complete
theorem candidate is still degenerate (``check_hypotheses_nondeg_numerically()``
fails) or numerically false as a whole
(``check_numerically()`` fails). Reproduce with the smallest ``Problem`` that
still triggers it, print the built ``Statement`` objects' ``args()``/``print()``
output, and check them against the rule's premises/conclusions by hand before
assuming the provider is at fault.

See :doc:`optimize_a_generic_rule` if matching is correct but slow, and
:doc:`debug_custom_rule_integration` if matching is correct in isolation (via
the CLI or a C++ test) but the rule still does not show up as a usable
deduction once called through Newclid.
