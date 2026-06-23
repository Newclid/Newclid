Backend guide to extending custom theorems
==========================================

Use this guide when changing the custom theorem payload or how backend custom
theorems are converted into Newclid rules.

Backend custom theorem extension steps
--------------------------------------

1. Update the shared contract.

   Start with :doc:`../../contracts/custom_theorem_contract` so frontend and
   backend owners agree on the public shape.

2. Update ``CustomTheoremRequest`` in ``schemas.py``.

   Add or change Pydantic fields and validators. Keep API validation focused on
   transport-level checks such as required fields, lengths, duplicates, and
   single-line predicate strings.

3. Update helper conversion.

   Change ``_build_custom_rule_fields`` in ``runner_helpers.py`` if the new field
   affects the arguments used to construct a Newclid ``Rule``.

4. Update runner integration.

   Change ``_build_custom_rules`` in ``newclid_runner.py`` only if the conversion
   into ``Rule`` objects changes.

5. Add tests.

   Add schema tests for validation, helper tests for conversion, and at least one
   runner/API test if the change affects actual solving.

Backend custom theorem non-goals
--------------------------------

The backend should not duplicate Newclid's rule parser. It should validate the
shape of the request and convert fields into the form Newclid expects. Predicate
semantics and generic rule matching belong in Newclid/Yuclid.

Backend custom theorem failure modes
------------------------------------

When debugging custom theorem failures, separate these cases:

- API validation failed before enqueueing.
- Runner conversion failed while constructing ``Rule`` objects.
- Newclid accepted the rule but the rule did not help prove the goal.
- Yuclid generic matching accepted the rule but produced no useful theorem candidates.

Only the first case should normally return a synchronous HTTP validation error.
The other cases are job results.
