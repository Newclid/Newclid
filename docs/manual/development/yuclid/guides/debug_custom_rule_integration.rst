Yuclid guide to debugging custom rule integration
=================================================

Use this guide when a custom rule works in one layer — say, matching correctly
in a direct Yuclid run — but does not appear as a usable Newclid deduction
after the full round trip from your Python code through Yuclid and back. This
repository ships the engine only: there is no built-in web application here.
"The calling application" below means whatever Python code constructs a
``GeometricSolverBuilder`` and calls ``with_additional_rules`` — that may be a
script, a test, or a separate downstream project such as Viewclid, which
consumes Newclid/Yuclid as an external, decoupled dependency rather than as
part of this codebase.

Yuclid integration triage order
-------------------------------

Debug the integration in the same order as the data flow (see
:doc:`../modules/integration_with_newclid` for the full design rationale
behind each step):

1. **Confirm the calling application's code actually creates the expected
   Newclid ``Rule`` object** (``newclid.rule.Rule``, with ``id``,
   ``premises_txt``, ``conclusions_txt``) — not just a rule-shaped dictionary
   or string. See ``yuclid/tests/test_custom_rule_integration.py`` for a
   minimal working example of constructing one.

2. **Confirm ``GeometricSolverBuilder.with_additional_rules(...)`` receives
   it**, in ``newclid/src/newclid/api.py``. This method merges rules into the
   builder's rule list by id and skips (with a logged warning) any new rule
   whose id already matches an existing one — a silent no-op if you reused an
   id by accident.

3. **Confirm the rule is not filtered out as a standard rule.** At
   ``.build()`` time, ``api.py`` computes
   ``custom_rules = [r for r in self.rules if r not in ALL_RULES]``
   (``newclid/src/newclid/all_rules.py`` defines ``ALL_RULES``) and only that
   filtered list is forwarded to the Yuclid adapter. A rule is dropped from
   this custom-rule forwarding only if it compares equal to something already
   in ``ALL_RULES`` — in practice this means double check you are not
   accidentally reusing an id (or an otherwise-equal ``Rule``) that already
   exists in the standard library.

4. **Inspect ``YuclidAdapter.precomputation_custom_rules_str``**
   (``yuclid/python/py_yuclid/yuclid_adapter.py``). This property serializes
   every rule in ``self.custom_rules`` through ``_write_custom_rule_setup``
   into Yuclid's ``rule``/``require``/``conclude``/``end`` text format, with
   variables sorted for determinism. Print or log this string directly —
   it is exactly what reaches the C++ side.

5. **Save the generated problem file and custom rule file.**
   ``YuclidAdapter._run_yuclid`` writes both to a temporary directory
   (``problem_<name>.txt`` and ``custom_rules_<name>.txt``) before invoking the
   ``yuclid`` binary; copy them out of the temp directory before it is cleaned
   up (or just reconstruct them from the strings you inspected in step 4 plus
   ``precomputation_input_str``).

6. **Run Yuclid manually** with the saved files:

   .. code-block:: bash

      yuclid --mode match \
        --input-file problem.txt \
        --input-additional-rules-file custom_rules.txt \
        --log-level debug

   This is the split point: if this command already fails or misbehaves, the
   bug is entirely inside Yuclid (continue with steps 7–9, or see
   :doc:`debug_generic_matching`). If it succeeds and produces the expected
   theorem, the bug is in the Python adapter boundary (steps 1–5 above, or
   step 10 below).

7. **Check C++ rule parsing and schema validation** — see
   :doc:`debug_generic_matching`'s triage steps 1–2 for the same check in more
   detail. A parser or validator rejection here means the *text* the adapter
   generated is malformed, even though the Python ``Rule`` object looked fine.

8. **Check ``GenericRuleMatcher`` output in ``--mode match``** — see
   :doc:`debug_generic_matching` in full for this stage.

9. **Check theorem candidate validation and insertion** — same reference,
   final-rejection section.

10. **Check that the returned deduction id is present in the adapter's
    extended rule dictionary.** ``YuclidAdapter._precompute`` builds
    ``id_to_yuclid_extended`` as a copy of ``ID_TO_YUCLID_RULE`` plus every
    rule in ``self.custom_rules`` keyed by its own ``rule.id``. If Yuclid's
    JSON output names a rule id that is not a key in this dictionary — most
    often because the id used at serialization time (step 4) does not match
    the id the rule object carries in Python — ``to_cached_application`` will
    raise a ``KeyError`` when the deduction is converted back.

Yuclid integration symptoms
---------------------------

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Symptom
     - Likely place to check
   * - Rule never appears in the generated custom-rule text at all
     - Step 2 (id already present, silently skipped) or step 3 (rule equals
       something already in ``ALL_RULES``).
   * - ``YuclidAdapter.precomputation_custom_rules_str`` is right, but Yuclid
       rejects the custom rule file
     - Step 7 — rule parser or schema validator; compare the printed text
       byte-for-byte against the ``rule``/``require``/``conclude``/``end``
       grammar in ``parser/rule_parser.cpp``.
   * - Rule parses but has no candidates
     - Step 8 — rule plan, provider selection, mapping state, or a missing
       cache/provider; see :doc:`debug_generic_matching` in full.
   * - Candidates exist but no theorem is accepted
     - Step 9 — statement builder, theorem builder, degeneracy checks, or
       final validation.
   * - Yuclid returns a deduction but the calling application raises a
       ``KeyError``/cannot map it back to a ``Rule``
     - Step 10 — the adapter's extended rule dictionary and custom-rule id
       handling; check for an id mismatch between serialization and lookup.

Yuclid manual reproduction command
-----------------------------------

When possible, reduce the issue to the direct Yuclid command from step 6
before touching any Python:

.. code-block:: bash

   yuclid --mode match \
     --input-file problem.txt \
     --input-additional-rules-file custom_rules.txt \
     --log-level debug

If the direct command fails, the bug is in Yuclid — continue with
:doc:`debug_generic_matching`. If the direct command succeeds but the full
run through the calling application still fails, the bug is specific to the
Python/C++ boundary — focus on ``YuclidAdapter`` (steps 1–5 and 10 above)
rather than the matcher itself.
