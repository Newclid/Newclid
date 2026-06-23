Yuclid guide to debugging generic matching
==========================================

Use this guide when a custom rule parses but does not produce the expected
matches, produces too many matches, or produces candidates that final validation
rejects.

Yuclid generic matching triage
------------------------------

Debug in this order:

1. Confirm the rule file parses.
2. Confirm schema validation accepts the declared variables and predicates.
3. Check the generated ``RulePlan``.
4. Check which provider handles each predicate.
5. Inspect candidate ``MappingExtension`` objects.
6. Check ``MappingState`` rollback and used-point behavior.
7. Check check-only predicates after variables become assigned.
8. Check theorem construction and final validation.

Yuclid no matches symptom
-------------------------

If the rule produces no matches:

- verify the predicate names and argument order;
- verify that repeated variables are intentional;
- test the provider's ``is_satisfied`` method on a known valid mapping;
- check whether an indexed provider silently skipped singleton or degenerate cases;
- check whether final validation rejected all candidates.

Yuclid too many matches symptom
-------------------------------

If the rule produces too many candidates:

- check variable equality and used-point constraints;
- check whether a check-only predicate is not being applied early enough;
- check whether a provider is generating both valid and invalid aliases;
- confirm that symmetric predicates intentionally generate both orientations.

Yuclid final rejection symptom
------------------------------

If candidates are generated but rejected later, debug ``statement_builder`` and
``theorem_builder``. The provider may be locally correct while the full theorem
candidate is degenerate or duplicates an existing theorem.
