Backend configuration
=====================

Backend configuration lives in ``settings.py`` and is read from environment
variables. Defaults are safe for local development.

Backend environment variables
-----------------------------

.. list-table::
   :widths: 30 24 46
   :header-rows: 1

   * - Variable
     - Default
     - Meaning
   * - ``REDIS_URL``
     - ``redis://localhost:6379/0``
     - Redis-compatible server used by RQ.
   * - ``NEWCLID_QUEUE_NAME``
     - ``newclid``
     - Queue name used by the API and worker.
   * - ``DEFAULT_JOB_TIMEOUT_SECONDS``
     - ``120``
     - Default RQ job timeout when the request does not override it.
   * - ``RESULT_TTL_SECONDS``
     - ``3600``
     - How long successful job results remain in Redis.
   * - ``FAILURE_TTL_SECONDS``
     - ``3600``
     - How long failed job metadata remains in Redis.
   * - ``NEWCLID_COMMAND``
     - ``newclid``
     - Reserved command setting from earlier subprocess-based runner designs. The current runner calls Newclid in process.
   * - ``MAX_OUTPUT_CHARS``
     - ``200000``
     - Maximum stored output length for proof text and tracebacks.

Backend API and worker consistency
----------------------------------

The API server and RQ worker must use the same values for:

- ``REDIS_URL``;
- ``NEWCLID_QUEUE_NAME``;
- Python environment and installed Newclid version.

If these differ, jobs may be enqueued in one queue while workers listen to a
different queue, or workers may fail because the expected package versions are
not installed.

Backend timeout configuration
-----------------------------

``timeout_seconds`` can be provided per job request and is passed to RQ as the
job timeout. The default is ``DEFAULT_JOB_TIMEOUT_SECONDS``.

Be careful when increasing timeouts. Longer jobs keep worker processes busy for
longer and delay all jobs behind them in the same queue.

Backend output-size configuration
---------------------------------

``MAX_OUTPUT_CHARS`` prevents very large proof text or tracebacks from being
stored without bound. Truncation keeps the end of the output because the end of
a traceback usually contains the most useful error message.
