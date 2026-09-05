Yuclid guide to adding a supported predicate
============================================

Use this guide when a predicate should work in custom rules end-to-end. This is
broader than :doc:`add_a_predicate_provider`: a predicate must be parseable,
schema-validated, buildable into a real ``Statement``, and either matchable or
explicitly deferred to final validation, before a custom rule using it can ever
produce a theorem.

Most geometry predicates Newclid already knows about — ``cong``, ``coll``,
``para``, ``perp``, ``eqangle``/``equal_angles``, ``eqratio``, ``cyclic``,
``circumcenter``/``circle``, ``simtri``/``simtrir``/``contri``/``contrir``,
``midp``, ``rconst``/``r2const``/``lconst``/``l2const``/``aconst``,
``sameclock``, ``obtuse_angle``, ``sameside``/``nsameside`` — are *already*
supported end-to-end this way (see the full dispatch list in
``yuclid/src/statement/statement_builder.cpp``). What is usually missing for
them is a fast provider, which is a separate, smaller task (see
:doc:`add_a_predicate_provider`). This guide is for a predicate that the
custom-rule pipeline does not accept as rule-file text at all yet.

Yuclid worked example: wiring up ``ncoll``
---------------------------------------------

A concrete, already-half-built example is negated collinearity, ``ncoll``. The
underlying engine already has a fully correct ``Statement`` subclass for it —
``Yuclid::NonCollinear`` in ``yuclid/src/statement/ncoll.hpp``/``.cpp``:

.. code-block:: cpp

   class NonCollinear : public Statement {
   public:
       NonCollinear(Point a, Point b, Point c);
       // name() returns "ncoll"
       // check_nondegen() returns
       //   !a.is_close(b) && !b.is_close(c) && !a.is_close(c)
       //   && !Collinear(a, b, c).check_equations();
       // check_equations() always returns true (numerical_only() == true,
       // so all the real work happens in check_nondegen()).
   };

``predicate_matching_metadata.hpp`` even documents ``ncoll`` by name as the
intended example for the ``CandidateFilter`` role — "the predicate does not
generate candidates, but can reject a matching state once all variables ... are
assigned" — and explicitly says "currently no parser supports those predicates
... so for now such example is not possible." Wiring it up end-to-end is a
genuinely useful, well-scoped first contribution. The same steps apply to
``npara``/``nperp`` (``Yuclid::NonParallel``/``NonPerpendicular``, already
implemented in ``npara.hpp``/``nperp.hpp``), which are in the same situation.

Yuclid supported predicate steps
------------------------------------

1. **Define the public predicate shape.** ``ncoll A B C`` — exactly 3 points,
   no legal duplicate positions (three named points that must *not* be
   collinear; letting two of them alias would make the check
   ``check_nondegen()`` returns for degenerate input, not a real answer). The
   name in the rule-file text must match the name Newclid/Yuclid already use at
   the statement boundary — here that's easy, because ``NonCollinear::name()``
   already returns ``"ncoll"``.

2. **Accept and validate the pattern in the schema validator.**
   ``yuclid/src/rules/schema_validator.cpp``'s ``validate_predicate`` is a
   flat if/else chain keyed on ``pattern.name``; every predicate not listed
   there is rejected with "Unknown rule predicate". Add a branch with the same
   if/else shape as ``coll``'s, but with ``ncoll``'s own fixed arity of 3
   (``coll`` is variadic, accepting 3 or more points; ``ncoll`` is not):

   .. code-block:: cpp

      else if (name == "ncoll") {
          valid_arity = (args_size == 3);
          expected_msg = "exactly 3";
      }

   The variable-declaration loop right below (rejecting any argument that is
   not one of ``declared_vars``) already applies to every predicate uniformly,
   so no extra work is needed there unless your predicate has a constant
   argument like ``rconst``/``lconst`` do (see the ``i == 4``/``i == 2``
   special-cases just above the loop, which exist purely to skip constant
   parsing for those two predicate families — do not copy that unless your
   predicate really does take a literal constant argument).

3. **Add statement-builder support**, in
   ``yuclid/src/statement/statement_builder.cpp``, so a concrete
   ``RuleMapping`` for the pattern can become a real ``Statement``:

   .. code-block:: cpp

      if (pattern.name == "ncoll") {
          check_arity(pattern, 3);
          statements.push_back(std::make_unique<NonCollinear>(
              mapped_point(pattern, mapping, 0),
              mapped_point(pattern, mapping, 1),
              mapped_point(pattern, mapping, 2)
          ));
          return statements;
      }

   Do not forget the ``#include "statement/ncoll.hpp"`` at the top of the file.
   This function is called both by ``theorem_builder.cpp`` (to build the final
   hypothesis/conclusion ``Statement`` objects for an accepted mapping) and by
   ``BaseProvider::is_satisfied`` (to numerically check a fully-bound
   predicate through the generic fallback path) — one implementation serves
   both.

4. **Decide the matching role**, in
   ``yuclid/src/matchers/predicate_matching_metadata.cpp``:

   .. code-block:: cpp

      {"ncoll", PredicateMatchingRole::CandidateFilter, 50},

   .. warning::
      Read this before picking ``CandidateFilter``. ``RulePlan::candidate_filters``
      (populated by ``build_rule_plan`` for exactly this role, see
      ``yuclid/src/matchers/rule_plan.cpp``) is **not currently consumed
      anywhere** in ``GenericRuleMatcher::search()``
      (``yuclid/src/matchers/generic_rule_matcher.cpp``). The search loop's
      FILTER STAGE iterates ``plan.validators`` (the ``Validator`` role), and
      its generator fallback also only tries ``plan.candidate_generators`` then
      ``plan.validators`` — never ``plan.candidate_filters``. If ``ncoll`` were
      the *only* premise of a rule, tagging it ``CandidateFilter`` today would
      mean its variables are never assigned and never checked, and ``search()``
      would throw its "Dead end reached" ``std::runtime_error``. Until someone
      extends ``search()`` to also drain ``plan.candidate_filters`` (a real,
      valuable, separate contribution — see :doc:`debug_generic_matching` for
      where that loop lives), tag a genuinely new predicate ``Validator``
      instead so ``BaseProvider`` can still enumerate it as a last-resort
      generator and check it once bound. ``CandidateFilter`` is correct to use
      *once* that search-loop gap is closed, or for a predicate that always
      appears alongside another premise that already pins down every one of
      its variables.

5. **Add cache support only if needed.** ``ncoll`` does not need one — it has
   no provider and is checked with a plain numerical ``is_satisfied`` via
   ``BaseProvider``. If your predicate does get its own provider later, shared
   geometry structures belong in ``LazyGeometryCache``, not rebuilt inside the
   provider (see :doc:`add_a_lazy_cache`).

6. **Add theorem-builder and matcher tests.** ``theorem_builder.cpp`` itself
   needs no predicate-specific change — it already calls
   ``build_statements_from_pattern`` generically — but add cases to
   ``yuclid/test/statement_builder.cpp`` (correct ``Statement`` built from a
   concrete mapping, and an arity-mismatch throw case) and
   ``yuclid/test/theorem_builder.cpp`` (the predicate as a premise, and as a
   conclusion). Then add one C++ integration case in
   ``yuclid/test/generic_rule_matcher.cpp`` or
   ``yuclid/test/custom_rule_integration_test.cpp`` building a real
   ``RuleSchema`` that uses ``ncoll`` end-to-end, plus a schema-validator test
   in ``yuclid/test/schema_validator.cpp`` for both the arity rejection and the
   undeclared-variable rejection.

   .. code-block:: bash

      cmake --build yuclid/build
      ctest --test-dir yuclid/build -R "schema_validator|statement_builder|theorem_builder|generic_rule_matcher"

Yuclid supported predicate checklist
----------------------------------------

Before considering the predicate supported, check:

- invalid arity is rejected clearly by ``schema_validator.cpp``, with a message
  naming the predicate and the expected count;
- undeclared variables are rejected by the same file's shared
  variable-declaration loop;
- ``predicate_matching_metadata.cpp`` classifies the predicate consistently
  with what ``search()`` actually consumes today — see the warning above before
  choosing ``CandidateFilter``;
- statement construction in ``statement_builder.cpp`` works for a concrete
  mapping, and throws (via ``check_arity``/``check_minimum_arity``) rather than
  silently misreading arguments for a malformed pattern;
- provider/check-only behavior preserves completeness — nothing about your
  change can cause ``search()`` to reach "Dead end reached" for a
  well-formed rule using only this predicate;
- final theorem validation still runs (it always does, for every candidate,
  regardless of predicate — see ``GenericRuleMatcher::build_valid_theorems_from_mappings``);
  do not special-case that path for your predicate;
- integration tests cover one successful custom rule using the predicate as a
  premise and one using it as a conclusion.
