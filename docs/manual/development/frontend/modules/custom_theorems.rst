Frontend custom theorems
========================

Custom theorems let users extend the prover with domain-specific lemmas without modifying the backend.
Each theorem is defined as a list of premise predicates and a list of conclusion predicates; it is serialised to JGEX and sent to the backend alongside the problem on every proof request.

Source files: ``src/types/theorem.ts``, ``src/types/theoremValidation.ts``, ``src/ui/theoremManager.ts``

Data model
----------

Defined in ``src/types/theorem.ts``:

- ``TheoremPredicate`` — a pair of ``{ predicateId, args[] }`` where ``args`` are point labels.
- ``CustomTheorem`` — the full theorem record: ``id``, ``name``, ``description``, ``premises``, ``conclusions``, ``createdAt``.
- ``PredicateDef`` — definition of one predicate: label, icon, and the expected argument count.
- ``PREDICATE_DEFINITIONS`` — the built-in catalogue of supported predicates: ``cong``, ``para``, ``perp``, ``midp``, ``eqangle``, and others.
- ``predicateToJgex(predicate)`` — serialises a single ``TheoremPredicate`` to a JGEX clause string.

Validation
----------

``src/types/theoremValidation.ts`` validates a ``CustomTheorem`` before it is saved:
it checks that every predicate's argument count matches its ``PredicateDef`` and that all required fields are present.

Theorem manager UI
------------------

``src/ui/theoremManager.ts`` is a modal dialog for creating and editing theorems:

1. Name and description fields.
2. A visual predicate builder for premises — pick a predicate from a dropdown, then fill in the point argument inputs.
3. The same builder for conclusions.
4. Save and delete buttons; save writes to ``TheoremStore`` (``localStorage``).

To add a new predicate kind that users can pick in the theorem manager, add an entry to ``PREDICATE_DEFINITIONS`` in ``src/types/theorem.ts``.
See :doc:`../guides/add_a_custom_theorem` for the full workflow.
