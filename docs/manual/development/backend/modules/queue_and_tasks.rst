Backend queue and tasks
=======================

The queue layer is the boundary between the HTTP server and worker execution. It
uses Redis as storage and RQ as the background-job framework.

Backend queue wrapper
---------------------

``queue.py`` creates one Redis connection and one RQ queue:

.. code-block:: text

   redis_connection = Redis.from_url(REDIS_URL)
   newclid_queue = Queue(NEWCLID_QUEUE_NAME, connection=redis_connection)

The wrapper exposes two functions:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Function
     - Responsibility
   * - ``enqueue_job``
     - Enqueue a callable with a job id, timeout, result TTL, and failure TTL.
   * - ``fetch_job``
     - Fetch an RQ job by id and return ``None`` if it does not exist.

The API route uses these helpers instead of importing RQ directly everywhere.
That keeps queue configuration in one place.

Backend task adapter
--------------------

``tasks.py`` contains the function that RQ workers execute:

.. code-block:: text

   run_newclid_job(jgex_problem, custom_theorems=None)

This function imports ``run_newclid_from_jgex`` lazily, calls it, and returns
``result.model_dump()``. It is intentionally small because the task adapter
should not contain solver logic.

Backend queue options
---------------------

The queue layer applies three operational settings when enqueueing a job:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Setting
     - Use
   * - ``job_timeout``
     - Maximum execution time enforced by RQ.
   * - ``result_ttl``
     - How long successful results are kept in Redis.
   * - ``failure_ttl``
     - How long failed job metadata is kept in Redis.

These values come from :doc:`configuration`.

Backend worker requirement
--------------------------

The API process only enqueues jobs. It does not execute queued work. A separate
RQ worker must be running with the same Redis URL and queue name:

.. code-block:: bash

   uv run rq worker newclid --url redis://localhost:6379/0

If the worker is missing, ``POST /api/jobs`` still returns ``queued``, but the
job never advances to ``running`` or a terminal status.
