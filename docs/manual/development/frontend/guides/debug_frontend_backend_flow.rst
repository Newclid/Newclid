Debug frontend-backend flow
===========================

This guide covers the most common failure modes when a proof submission is not working as expected and explains how to diagnose them.

See :doc:`../modules/backend_integration` and :doc:`../modules/jgex_emission` for background.

Check the backend is running
----------------------------

Open ``http://localhost:8000/api/health`` in the browser or run:

.. code-block:: bash

   curl http://localhost:8000/api/health

A healthy backend returns a 200 response.
A ``502 Bad Gateway`` on the ``POST /api/jobs`` request in the Network tab means the backend is not reachable — start it before submitting proofs.

Inspect network requests
------------------------

Open **DevTools → Network** and filter by ``/api``:

- **``POST /api/jobs``** — the submission request. Check the request body contains the expected JGEX string and any custom theorems. A 4xx response body will contain an error message from the backend.
- **``GET /api/jobs/{id}``** — the polling requests. The response body contains the current ``status`` and an optional ``message`` field with progress information.
- **``GET /api/jobs/{id}/result``** — fetched once when the job reaches a terminal status. The full result payload is here, including ``stdout`` and ``stderr`` from the prover.

Read the JGEX string
--------------------

The JGEX input panel in the UI shows the problem string before submission.
Copy it out and check it manually if the backend reports a parse error.

JGEX syntax basics:

- Construction lines: ``<construction> <points>`` (e.g. ``triangle A B C``)
- Goal lines: ``? <predicate> <points>`` (e.g. ``? perp A B C D``)
- Custom theorem clauses follow the same predicate syntax

Common failures
---------------

**Backend not running**
  Symptom: ``POST /api/jobs`` returns 502.
  Fix: start the backend (see the backend setup guide).

**Malformed JGEX**
  Symptom: job status is ``failed`` immediately; ``stderr`` contains a parse or resolution error.
  Fix: copy the JGEX string from the input panel and check for typos in construction names or point labels.

**Proof timeout**
  Symptom: job status is ``timed_out``.
  Fix: try a simpler problem to confirm the backend is healthy. If the backend is healthy, the problem may be too complex for the current prover configuration.

**Custom theorem conflict**
  Symptom: job fails with a predicate resolution error mentioning a theorem name.
  Fix: open the theorem manager, review the theorem's premises and conclusions for typos or incorrect argument counts, and re-save.

**Polling stops early**
  Symptom: the UI shows "running" indefinitely but no result arrives.
  Fix: check the browser console for ``ApiError`` messages from ``JobPoller``. A 4xx on a polling request stops the poller permanently — inspect the response body for the cause.

Browser console
---------------

``JobPoller`` logs each status transition to the browser console (e.g. ``job abc123: queued → running → succeeded``).
These messages appear even when DevTools is not open on the Network tab, so the console is often the fastest place to see what is happening.

To inspect ``AppStore`` state at runtime, set a breakpoint inside ``updateJob()`` in ``src/store/appStore.ts`` and trigger a proof submission.
