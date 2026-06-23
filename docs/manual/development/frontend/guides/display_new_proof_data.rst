Display new proof data
======================

The backend returns a ``JobResultPayload`` that the frontend stores in ``AppStore`` and renders in the proof panel and on the canvas.
This guide covers how to surface a new field from the backend result — whether as text in the proof panel or as a visual element on the canvas.

See :doc:`../modules/backend_integration`, :doc:`../modules/proof_ui`, and :doc:`../modules/rendering` for background.

Steps
-----

1. **Extend the type definition**

   If the backend sends a new field that is not yet modelled, add it to the relevant type in ``src/api/types.ts``:

   - ``JobResultPayload`` — for top-level result fields.
   - ``NewclidProofSections`` — for fields inside the structured proof (steps, goals, assumptions, etc.).

   Mark new fields as optional (``field?: Type``) if they may be absent on older backend versions.

2. **Store the data**

   ``JobPoller`` already passes the full result object to ``AppStore.updateJob()``, so the new field will be available in ``AppStore.jobs.get(jobId).result`` with no changes to the polling logic.

   If the field needs preprocessing before storage (e.g. parsing a string into a structured value), do that transformation inside ``JobPoller`` before calling ``updateJob()``.

3. **Show it in the proof panel**

   Open ``src/ui/proofPanel.ts`` and locate the render function for the relevant part of the UI (job status, proof steps, or proof metadata).
   Use the DOM helpers from ``src/ui/dom.ts`` to create and append elements:

   .. code-block:: typescript

      const el = dom.div({ className: 'proof-extra' });
      el.textContent = result.my_new_field ?? '';
      container.appendChild(el);

4. **Show it on the canvas** (if visual)

   If the new field contains geometry (points, segments, angles), draw it in the proof sketch:

   a. Parse any JGEX-encoded geometry using ``parseJgexGeometry()`` in ``src/emit/jgexParser.ts``.
   b. Open ``src/render/renderer.ts`` and add drawing calls to the Canvas 2D section of ``draw()``.
      The Canvas context and ``Viewport`` are already available there for coordinate transforms.

5. **Verify**

   Run ``npm run dev``, submit a proof job, and confirm that the new data appears correctly.
   Also run ``npm run typecheck`` to catch any type mismatches.
