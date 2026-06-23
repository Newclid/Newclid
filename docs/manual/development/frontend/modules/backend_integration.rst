Frontend backend integration
============================

The backend integration layer submits proof jobs to the Newclid prover and streams status updates back into the UI.
All communication goes over HTTP to ``/api``; the Vite dev server proxies these requests to ``http://localhost:8000``.

Source files: ``src/api/backendClient.ts``, ``src/api/jobPoller.ts``, ``src/api/types.ts``

BackendClient
-------------

``src/api/backendClient.ts`` is a thin wrapper around ``fetch``:

- ``submitJob(jgex, customTheorems)`` — ``POST /api/jobs``; returns a ``SubmitJobResponse`` containing the new ``jobId``.
- ``getJobStatus(jobId)`` — ``GET /api/jobs/{id}``; returns the current ``JobStatus`` and an optional progress message.
- ``getJobResult(jobId)`` — ``GET /api/jobs/{id}/result``; returns the full ``JobResultPayload`` once the job has reached a terminal status.
- ``healthCheck()`` — ``GET /api/health``; used to verify the backend is reachable.

``ApiError`` (defined in ``types.ts``) is thrown on non-2xx responses and carries a ``retryable`` flag so the poller can distinguish transient network errors from permanent failures.

JobPoller
---------

``src/api/jobPoller.ts`` drives the polling loop after a job is submitted:

1. Polls ``getJobStatus()`` every 2 seconds.
2. Calls ``AppStore.updateJob()`` with each new status and message so the UI stays current.
3. On a terminal status (``succeeded``, ``failed``, ``timed_out``, ``cancelled``), fetches the full result with ``getJobResult()`` and stores it in ``AppStore``.
4. Retries automatically on transient network errors; stops permanently on 4xx responses.

API types
---------

``src/api/types.ts`` defines the contracts between frontend and backend:

- ``JobStatus`` — ``queued | running | succeeded | failed | timed_out | cancelled``.
- ``SubmitJobResponse`` — ``{ job_id, status }``.
- ``JobStatusResponse`` — ``{ status, message? }``.
- ``JobResultPayload`` — the full result: proof sections (``NewclidProofSections``), sketch geometry, stdout/stderr, and run metadata.
- ``NewclidProofSections`` — structured proof data: points, assumptions, proof steps, goals, and theorem references.
- ``SketchPoint`` — a named point with ``x, y`` coordinates in the user's canvas coordinate space.
