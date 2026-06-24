Yuclid guide to debugging custom rule integration
=================================================

Use this guide when a custom rule works in one layer but does not appear as a
usable Newclid deduction after the full backend/Newclid/Yuclid flow.

Yuclid integration triage order
-------------------------------

Debug the integration in the same order as the data flow:

1. Confirm the backend or caller creates the expected Newclid ``Rule`` object.
2. Confirm ``GeometricSolverBuilder.with_additional_rules`` receives it.
3. Confirm the rule is not filtered out as a standard rule already present in ``ALL_RULES``.
4. Inspect ``YuclidAdapter.precomputation_custom_rules_str``.
5. Save the generated problem file and custom rule file.
6. Run Yuclid manually with ``--input-file`` and ``--input-additional-rules-file``.
7. Check C++ rule parsing and schema validation.
8. Check ``GenericRuleMatcher`` output in ``match`` mode.
9. Check theorem candidate validation and insertion.
10. Check the returned deduction id is present in the adapter's extended rule dictionary.

Yuclid integration symptoms
---------------------------

.. list-table::
   :widths: 34 66
   :header-rows: 1

   * - Symptom
     - Likely place to check
   * - Rule never appears in Yuclid input
     - Newclid builder or Python adapter custom-rule forwarding.
   * - Yuclid rejects the custom rule file
     - Rule parser or schema validator.
   * - Rule parses but has no candidates
     - Rule plan, provider selection, mapping state, or missing cache/provider.
   * - Candidates exist but no theorem is accepted
     - Statement builder, theorem builder, degeneracy checks, or final validation.
   * - Yuclid returns a deduction but Newclid cannot map it
     - Adapter extended rule dictionary and custom rule id handling.

Yuclid manual reproduction command
----------------------------------

When possible, reduce the issue to a direct Yuclid command:

.. code-block:: bash

   yuclid --mode match \
     --input-file problem.txt \
     --input-additional-rules-file custom_rules.txt \
     --log-level debug

If the direct command fails, debug Yuclid. If the direct command succeeds but the
full Newclid run fails, debug the adapter or returned deduction mapping.
