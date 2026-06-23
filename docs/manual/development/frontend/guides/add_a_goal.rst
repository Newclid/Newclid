Add a goal
==========

A goal is a JGEX predicate that the Newclid prover must prove.
Goals are part of the JGEX problem string sent to the backend — they are not canvas objects.

See :doc:`../modules/jgex_emission` and :doc:`../modules/proof_ui` for background.

Option A: type the goal directly
---------------------------------

The JGEX input panel accepts a raw JGEX string.
Prefix any clause with ``?`` to mark it as a goal:

.. code-block:: text

   ? perp A B C D

Multiple goals can appear in the same JGEX string, one per line.
Submit the job and the backend will attempt to prove each goal.

Option B: use the proof-by-points panel
-----------------------------------------

1. Click **"Proof by points"** in the toolbar.
2. Select a predicate from the dropdown (e.g. ``perp``, ``cong``, ``para``).
3. Click canvas points one by one to fill the predicate arguments.
4. The panel assembles the JGEX goal clause automatically and adds it to the problem string.
5. Submit the job.

This option is useful when the point labels are not yet known and the user prefers to select them visually.

Option C: add a new predicate kind (developer task)
----------------------------------------------------

If the goal requires a predicate that does not yet appear in the dropdown, add it to the built-in catalogue.

1. Open ``src/types/theorem.ts``.

2. Add an entry to ``PREDICATE_DEFINITIONS``:

   .. code-block:: typescript

      {
        id: 'my_pred',
        label: 'My predicate',
        icon: '…',
        argCount: 4,   // number of point arguments
      }

3. If the predicate needs non-default JGEX serialisation, update ``predicateToJgex()`` in the same file.

4. The new predicate will appear automatically in:

   - The proof-by-points panel predicate dropdown.
   - The theorem manager predicate picker (see :doc:`add_a_custom_theorem`).

5. Verify: run ``npm run dev``, open the proof-by-points panel, confirm the predicate appears, submit a proof, and check that ``NewclidProofSections.goals`` in the result contains the expected clause.
