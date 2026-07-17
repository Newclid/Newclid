Backend architecture
====================

The backend is an asynchronous job service around Newclid. Its job is to accept
solver requests quickly, move expensive solver work out of the HTTP request
path, and return normalized proof results that the frontend can render.

Backend architecture in one diagram
-----------------------------------

.. code-block:: text

   POST /api/jobs
        │
        ▼
   CreateJobRequest validation
        │
        ▼
   routers/jobs.py creates a UUID job id
        │
        ▼
   queue.py enqueues run_newclid_job in Redis/RQ
        │
        ▼
   RQ worker executes tasks.py
        │
        ▼
   newclid_runner.py parses JGEX and runs Newclid
        │
        ▼
   runner_models.py normalizes the result
        │
        ▼
   RQ stores return value in Redis
        │
        ▼
   GET /api/jobs/{job_id}
   GET /api/jobs/{job_id}/result

Backend layers
--------------

.. list-table::
   :widths: 25 35 40
   :header-rows: 1

   * - Layer
     - Main files
     - Responsibility
   * - HTTP layer
     - ``main.py``, ``routers/jobs.py``, ``schemas.py``
     - FastAPI app, request validation, public responses, and status mapping.
   * - Queue layer
     - ``queue.py``, ``tasks.py``
     - Redis/RQ connection, enqueue options, and worker task adapter.
   * - Runner layer
     - ``newclid_runner.py``, ``runner_helpers.py``, ``runner_models.py``
     - Build a Newclid problem, run the solver, convert proof data, and return a stable result model.
   * - Configuration layer
     - ``settings.py``
     - Environment variables for Redis, queue names, timeouts, TTLs, and output limits.

Backend status model
--------------------

The backend has two status layers:

- **RQ status**: the internal queue status, such as ``queued``, ``started``, ``finished``, or ``failed``.
- **Public job status**: the frontend-facing status, such as ``queued``, ``running``, ``succeeded``, ``failed``, ``timed_out``, or ``cancelled``.

The public status is the one documented in :doc:`../contracts/solver_job_lifecycle`.
The mapping lives in ``routers/jobs.py`` because it is part of the HTTP contract,
not part of the runner.

Backend result path
-------------------

The worker returns a plain dictionary to RQ. That dictionary comes from
``NewclidRunResult.model_dump()``. The API then exposes it inside the
``result`` field of ``JobResultResponse``.

This means the result model has two boundaries:

1. The runner boundary, where internal Python objects are converted into
   Pydantic models.
2. The HTTP boundary, where FastAPI serializes those models as JSON.

Backend design decisions
------------------------

The backend follows five important rules:

.. list-table::
   :widths: 28 72
   :header-rows: 1

   * - Rule
     - Reason
   * - Do not run Newclid inside the request handler.
     - Solver runs can be slow; HTTP requests should remain responsive.
   * - Keep the queue adapter small.
     - RQ should call one simple task function, and the solver logic should stay testable without RQ.
   * - Validate public input with Pydantic.
     - Invalid requests should fail before they create queued work.
   * - Normalize solver output once.
     - The frontend should receive stable fields even if Newclid internals change.
   * - Keep shared contracts outside area docs.
     - Frontend and backend pages should link to the same contract pages instead of duplicating them.

Backend extension points
------------------------

Most backend changes fall into one of these categories:

- Add or modify an HTTP endpoint: start with :doc:`guides/add_an_endpoint`.
- Extend the job request: start with :doc:`guides/extend_the_job_request`.
- Add new proof data to the frontend result: start with :doc:`guides/expose_new_proof_data`.
- Change queue timeouts, TTLs, or worker behavior: start with :doc:`guides/tune_job_execution`.
