Backend API and routing
=======================

The API layer is implemented by ``main.py``, ``routers/jobs.py``, and
``schemas.py``. It owns the public HTTP contract between the frontend and the
backend.

Backend FastAPI application
---------------------------

``main.py`` creates the FastAPI app, includes the jobs router, and exposes the
health endpoint:

.. code-block:: text

   GET /api/health -> {"status": "ok"}

The health endpoint is intentionally simple. It checks that the ASGI app can
respond, not that Redis or Newclid are healthy.

Backend job endpoints
---------------------

The jobs router is mounted under ``/api/jobs`` and exposes three endpoints:

.. list-table::
   :widths: 18 34 48
   :header-rows: 1

   * - Method
     - Path
     - Responsibility
   * - ``POST``
     - ``/api/jobs``
     - Create a job id, normalize the JGEX input, serialize custom theorems, enqueue the task, and return ``queued``.
   * - ``GET``
     - ``/api/jobs/{job_id}``
     - Fetch the RQ job, map its internal status to a public status, and return a message.
   * - ``GET``
     - ``/api/jobs/{job_id}/result``
     - Return ``null`` while the job is pending, or the stored runner result for terminal states.

The detailed lifecycle contract is :doc:`../../contracts/solver_job_lifecycle`.

Backend request models
----------------------

The main request model is ``CreateJobRequest``. It currently supports only JGEX
input:

.. code-block:: json

   {
     "input_type": "jgex",
     "problem_input": "a b c = triangle a b c ? cong a b a b",
     "custom_theorems": [],
     "timeout_seconds": 120
   }

The backend strips leading and trailing whitespace from ``problem_input`` before
queueing the job. It does not parse the JGEX string in the route; parsing is
part of the worker-side runner.

Backend public status mapping
-----------------------------

``routers/jobs.py`` maps RQ statuses to public statuses:

.. list-table::
   :widths: 34 32 34
   :header-rows: 1

   * - RQ status or condition
     - Public status
     - Notes
   * - ``queued``, ``deferred``, ``scheduled``
     - ``queued``
     - Work has not started yet.
   * - ``started``
     - ``running``
     - A worker is executing the job.
   * - ``stopped``, ``canceled``
     - ``cancelled``
     - The job was interrupted by queue control.
   * - ``failed``
     - ``failed``
     - RQ marks the job as failed.
   * - ``finished`` with result status ``succeeded``
     - ``succeeded``
     - Newclid proved all goals.
   * - ``finished`` with result status ``failed``
     - ``failed``
     - Newclid finished without proving all goals or the runner caught an exception.
   * - ``finished`` with result status ``timed_out``
     - ``timed_out``
     - Reserved for runner timeout results.

Unknown or malformed states are treated as ``failed``. This is safer than
reporting success when the backend cannot understand the stored result.

Backend result endpoint behavior
--------------------------------

The result endpoint has different behavior depending on the public status:

- For ``queued`` and ``running``, it returns ``result: null`` and ``error: null``.
- For ``cancelled``, it returns ``result: null`` and an error message.
- For terminal Newclid statuses, it returns the runner dictionary from RQ.
- For malformed or missing return values, it reports a failed job with an error.

See :doc:`result_model` for the object stored inside the ``result`` field.
