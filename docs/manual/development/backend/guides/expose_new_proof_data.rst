Backend guide to exposing new proof data
========================================

Use this guide when Newclid produces useful data that the frontend needs to
render, inspect, or debug.

Backend proof data extension steps
----------------------------------

1. Identify the source of the data.

   Decide whether the data comes from solver run info, proof data, proof
   sections, sketch points, or exception output.

2. Extend the runner model.

   Add a field to ``NewclidRunResult`` or ``NewclidProofSections`` in
   ``runner_models.py``. Prefer structured data over strings if the frontend will
   inspect it programmatically.

3. Populate the field in ``newclid_runner.py``.

   Keep conversion logic near the existing proof conversion helpers. If the
   conversion is reusable or complex, put it in ``runner_helpers.py``.

4. Update the shared proof contract.

   Update :doc:`../../contracts/proof_result_model` so frontend and backend docs
   agree on the result shape.

5. Update frontend rendering docs.

   The frontend owner should update the proof UI documentation to explain how
   the new field is displayed.

6. Add tests.

   Add model tests and runner-helper tests. Add an integration test if the field
   must appear in the final API response.

Backend proof data design rule
------------------------------

Expose stable concepts, not raw Newclid internals. For example, exposing
``step_premise_indices`` is better than forcing the frontend to inspect internal
predicate ids and reconstruct proof dependencies itself.

Backend proof data example
--------------------------

The existing ``step_premise_indices`` field follows this pattern:

.. code-block:: text

   Newclid proof_data contains predicate ids
       ↓
   runner_helpers.py maps predicate ids to proof-step indices
       ↓
   NewclidProofSections.step_premise_indices stores lists of integers
       ↓
   frontend renders dependencies without knowing Newclid internals
