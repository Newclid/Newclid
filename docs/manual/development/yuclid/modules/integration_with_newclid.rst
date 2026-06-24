Yuclid integration with Newclid
===============================

The Newclid/Yuclid integration lets Newclid register additional rules and lets
Yuclid return deductions that reference those custom rules.

Yuclid adapter custom rules
---------------------------

The Python ``YuclidAdapter`` stores optional custom rules for the current run. If
custom rules are present, the adapter writes them to a temporary file and passes
that file to the Yuclid executable with ``--input-additional-rules-file``.

Yuclid adapter rule serialization
---------------------------------

Each Newclid ``Rule`` is serialized into the Yuclid custom rule format:

.. code-block:: text

   rule <id> <variables...>
   require <predicate> <args...>
   conclude <predicate> <args...>
   end

The adapter writes only the transport format. Yuclid still parses and validates
the rule file on the C++ side.

Yuclid deduction mapping back to Newclid
----------------------------------------

When Yuclid returns a rule deduction, the adapter uses an extended rule lookup:
standard Yuclid-backed rules plus the custom rules for this run. That allows
custom-rule deductions to become normal Newclid cached rule deductions.

Yuclid related Newclid API changes
----------------------------------

The Newclid solver builder can register additional rules. It forwards rules that
are not part of the standard rule library to the Yuclid adapter. Proof section
signatures are also exposed so downstream consumers can identify construction,
step, and goal predicates more easily.

Yuclid solver-builder boundary
------------------------------

Newclid exposes custom rules through ``GeometricSolverBuilder``. The
``with_additional_rules`` method merges additional rules into the builder's rule
list while preserving existing rules by id. If a new rule has the same id as an
already registered rule, the duplicate is skipped instead of replacing the
existing definition.

When the solver is built, Newclid compares the active rule list against
``ALL_RULES``. Rules that are not part of the complete standard library are
considered custom for this run. Those rules are stored on the Yuclid adapter so
they can be forwarded to the C++ executable.

This split matters because Newclid may still run with a mixture of standard and
custom rules. Only the non-standard rules need to be serialized as a custom rule
file for Yuclid.

Yuclid temporary-file boundary
------------------------------

The adapter writes two separate temporary files before launching Yuclid:

.. list-table::
   :widths: 32 68
   :header-rows: 1

   * - Temporary file
     - Contents
   * - ``problem_<problem_name>.txt``
     - The normal Yuclid problem setup generated from the Newclid problem.
   * - ``custom_rules_<problem_name>.txt``
     - Runtime custom rule schemas written in Yuclid's ``rule`` / ``require`` / ``conclude`` / ``end`` format.

When custom rules are present, the adapter adds this CLI argument:

.. code-block:: bash

   --input-additional-rules-file custom_rules_<problem_name>.txt

If no custom rules are present, the argument is omitted and Yuclid behaves like
the normal standard-rule matcher.

Yuclid adapter serialization details
------------------------------------

The adapter serializes each Newclid ``Rule`` into a compact text format:

.. code-block:: text

   rule <rule_id> <sorted variables>
   require <premise predicate name> <premise variables>
   conclude <conclusion predicate name> <conclusion variables>
   end

The adapter does not perform C++ matcher validation. It only writes the transport
format. The C++ ``rule_parser`` and ``schema_validator`` still validate the file
before matching begins.

Sorting variables makes the rule header deterministic, which helps debugging and
keeps generated custom-rule files stable across runs. The premise and conclusion
lines preserve the rule's predicate order.

Yuclid returned deduction mapping
---------------------------------

Yuclid returns deductions using rule ids. For standard Yuclid-backed rules, the
adapter already has ``ID_TO_YUCLID_RULE``. Custom rules are added to a copy of
that dictionary for the current run:

.. code-block:: text

   id_to_yuclid_extended = ID_TO_YUCLID_RULE + custom rule ids

When a returned deduction references a custom rule id, the adapter can now build
a normal Newclid ``CachedRuleDeduction`` using the original custom ``Rule``
object. This is what makes custom-rule deductions look like normal proof
deductions once they return to Newclid.

Yuclid proof-data signatures
----------------------------

The Newclid proof-writing changes expose extra predicate signatures for
constructions, proof steps, and goals. These signatures help downstream code
identify the predicate behind a proof line without reparsing the human-readable
proof text.

The signatures are especially useful for frontend/backend proof visualization:
text can still be shown to users, while structured signatures can be used to
highlight or connect proof objects programmatically.

Yuclid integration debugging order
----------------------------------

For integration bugs, debug in this order:

1. Check that the custom rule reaches ``GeometricSolverBuilder.with_additional_rules``.
2. Check that the rule is not filtered out as a standard rule.
3. Print or inspect ``YuclidAdapter.precomputation_custom_rules_str``.
4. Re-run Yuclid manually with the generated problem file and custom rule file.
5. Check whether C++ parsing and schema validation accept the rule.
6. Check whether ``GenericRuleMatcher`` produces theorem candidates.
7. Check whether final theorem validation rejects those candidates.
8. Check whether the returned deduction id exists in the extended rule dictionary.
