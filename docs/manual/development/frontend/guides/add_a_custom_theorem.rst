Add a custom theorem (frontend)
===============================

Custom theorems extend the prover with user-defined lemmas without touching the backend.
Each theorem is a named set of premise predicates and conclusion predicates; it is serialised to JGEX and sent to the backend alongside the problem on every proof request.

See :doc:`../modules/custom_theorems` for a reference overview of the module.

For end users: create a theorem in the UI
-----------------------------------------

1. Click the **theorem manager** button in the toolbar (book icon).
2. Enter a **name** and an optional **description**.
3. Under **Premises**, click **"Add predicate"**, pick a predicate from the dropdown (e.g. ``cong``, ``perp``), and fill in the point label arguments.
4. Repeat step 3 to add more premises.
5. Repeat the same process under **Conclusions**.
6. Click **Save**.

The theorem is stored in browser ``localStorage`` via ``TheoremStore`` and survives page reloads.
It is automatically included in the JGEX sent with every subsequent proof request — no further action is needed.

To edit a saved theorem, open the theorem manager, select the theorem from the list, make changes, and save again.
To delete it, select it and click **Delete**.

For developers: add a new predicate kind
-----------------------------------------

If the predicate you need does not appear in the dropdown, add it to the built-in catalogue.

1. Open ``src/types/theorem.ts``.

2. Add an entry to ``PREDICATE_DEFINITIONS``:

   .. code-block:: typescript

      {
        id: 'my_pred',
        label: 'My predicate',
        icon: '…',
        argCount: 4,
      }

3. If the predicate requires non-default JGEX serialisation, update ``predicateToJgex()`` in the same file.

4. Run ``npm run typecheck`` to confirm there are no type errors.

5. Verify: run ``npm run dev``, open the theorem manager, confirm the new predicate appears in the dropdown, create a theorem using it, and submit a proof to check that the theorem clause appears in the request payload.
