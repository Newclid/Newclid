Backend guide to extending the job request
==========================================

Use this guide when adding a new field to ``POST /api/jobs``.

Backend job request extension flow
----------------------------------

1. Update ``CreateJobRequest`` in ``schemas.py``.

   Add the field with a type, default value when appropriate, and a clear field
   description. Add validators if the value has constraints that can be checked
   before the job is queued.

2. Decide where the field is consumed.

   A queue-only setting belongs near ``routers/jobs.py`` or ``queue.py``. A
   solver option usually needs to be passed through ``tasks.py`` and consumed by
   ``newclid_runner.py``.

3. Pass the value through the queue boundary.

   RQ serializes arguments. Keep queued arguments JSON-like where possible:
   strings, numbers, booleans, lists, and dictionaries.

4. Update the shared contract.

   If the frontend must send the field, update
   :doc:`../../contracts/solver_job_lifecycle` or another relevant contract page.

5. Update tests.

   Add schema validation tests and route tests. If the field affects runner
   behavior, add runner or integration tests.

Backend job request example change
----------------------------------

Suppose you add a boolean ``include_debug_output`` field. The flow should look
like this:

.. code-block:: text

   schemas.CreateJobRequest.include_debug_output
       ↓
   routers/jobs.py reads request.include_debug_output
       ↓
   enqueue_job(run_newclid_job, ..., include_debug_output=...)
       ↓
   tasks.run_newclid_job forwards the option
       ↓
   newclid_runner.py changes result construction

Backend job request compatibility rule
--------------------------------------

Prefer adding optional fields with safe defaults. Existing frontend deployments
may still send the old request shape, and old clients should continue to work
unless the change intentionally breaks the API contract.
