Backend guide to debugging job failures
=======================================

Use this guide when submitted jobs stay queued, fail unexpectedly, or return no
usable proof result.

Backend failure triage order
----------------------------

Debug jobs in this order:

1. Check whether the API server is running.
2. Check whether Redis is reachable.
3. Check whether an RQ worker is listening to the correct queue.
4. Check the public job status.
5. Fetch the job result.
6. Inspect the runner ``message`` and ``stderr`` fields.
7. Reproduce the runner call directly in a test or Python shell.

Backend queued forever symptom
------------------------------

If a job remains ``queued`` forever, the most common causes are:

- no RQ worker is running;
- the worker listens to a different queue name;
- the worker uses a different Redis URL;
- the worker process cannot import ``newclid_backend.tasks``.

Check the worker command:

.. code-block:: bash

   uv run rq worker newclid --url redis://localhost:6379/0

The queue name must match ``NEWCLID_QUEUE_NAME``.

Backend immediate enqueue failure symptom
-----------------------------------------

If ``POST /api/jobs`` returns ``503``, the route could not enqueue the job. Check
that Redis is running and that ``REDIS_URL`` is correct.

A quick Redis check is:

.. code-block:: bash

   redis-cli ping

Backend failed result symptom
-----------------------------

If the job reaches ``failed``, fetch the result endpoint:

.. code-block:: bash

   curl http://127.0.0.1:8000/api/jobs/<job_id>/result

Then inspect:

- ``result.message`` for the high-level failure reason;
- ``result.stderr`` for a runner traceback;
- ``error`` for the API-level error summary.

Backend solver did not prove goals symptom
------------------------------------------

If the message is:

.. code-block:: text

   Newclid finished, but did not prove all goals.

then the backend and worker probably worked correctly. The issue is likely the
JGEX problem, the selected goal, missing assumptions, missing rules, or solver
completeness for that case.

Backend exception traceback symptom
-----------------------------------

If ``stderr`` contains a traceback, reproduce the runner directly:

.. code-block:: python

   from newclid_backend.newclid_runner import run_newclid_from_jgex

   result = run_newclid_from_jgex("a b c = triangle a b c ? cong a b a b")
   print(result.status)
   print(result.message)
   print(result.stderr)

This bypasses FastAPI, Redis, and RQ. If the direct call fails, debug the runner
or Newclid input. If the direct call succeeds, debug queue and worker setup.
