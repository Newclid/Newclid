Backend guide to tuning job execution
=====================================

Use this guide when changing job timeouts, queue names, Redis settings, result
retention, or worker behavior.

Backend execution settings
--------------------------

The main settings are documented in :doc:`../modules/configuration`:

- ``REDIS_URL``;
- ``NEWCLID_QUEUE_NAME``;
- ``DEFAULT_JOB_TIMEOUT_SECONDS``;
- ``RESULT_TTL_SECONDS``;
- ``FAILURE_TTL_SECONDS``;
- ``MAX_OUTPUT_CHARS``.

Backend timeout tuning
----------------------

Increasing ``DEFAULT_JOB_TIMEOUT_SECONDS`` or per-request ``timeout_seconds`` can
help long-running problems finish, but it also means each worker can be occupied
for longer. If jobs are queued behind each other, increasing timeouts may make
the system feel slower.

Before increasing the timeout, check whether the solver work can be optimized or
whether more worker processes should be started.

Backend result retention tuning
-------------------------------

``RESULT_TTL_SECONDS`` and ``FAILURE_TTL_SECONDS`` control how long RQ keeps job
results in Redis. Longer TTLs make it easier for the frontend to fetch old
results, but they increase Redis memory usage.

Choose TTLs based on how the UI behaves:

- short-lived interactive sessions can use shorter TTLs;
- demos or debugging environments may benefit from longer TTLs;
- production deployments should monitor Redis memory usage.

Backend queue-name tuning
-------------------------

The API and worker must use the same queue name. If you change
``NEWCLID_QUEUE_NAME``, update worker startup commands and deployment
configuration at the same time.

Backend worker scaling
----------------------

RQ workers process jobs from the queue. To increase parallelism, start more
worker processes. Make sure the host has enough CPU and memory for multiple
simultaneous Newclid runs.

Backend tuning test checklist
-----------------------------

After changing execution settings, test:

1. ``POST /api/jobs`` returns a queued job.
2. The worker receives and starts the job.
3. ``GET /api/jobs/{job_id}`` moves from ``queued`` to ``running`` to a terminal status.
4. ``GET /api/jobs/{job_id}/result`` returns the expected stored result.
5. Old results expire according to the configured TTL.
