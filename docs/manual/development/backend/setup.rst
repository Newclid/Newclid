Backend setup
=============

This page explains how to run the backend locally. The backend needs two
long-running processes: the FastAPI server and an RQ worker. It also needs a
Redis-compatible server for queue storage.

Backend setup prerequisites
---------------------------

You need:

- Python 3.11 or newer.
- ``uv`` for dependency management.
- A Redis-compatible server such as Redis or Valkey.
- The Newclid package available in the same Python environment as the backend.

Backend dependency installation
-------------------------------

From the backend package directory, install the runtime and test dependencies:

.. code-block:: bash

   uv sync --extra test

The backend package declares FastAPI, redis-py, RQ, and Uvicorn as runtime
dependencies. The test extra adds pytest and HTTPX.

Backend Redis setup
-------------------

The default Redis URL is:

.. code-block:: text

   redis://localhost:6379/0

The easiest local setup is Docker:

.. code-block:: bash

   docker run --rm -p 6379:6379 redis:7

Verify that Redis responds:

.. code-block:: bash

   redis-cli ping

Expected output:

.. code-block:: text

   PONG

Backend API server
------------------

Start the FastAPI app with Uvicorn:

.. code-block:: bash

   uv run uvicorn newclid_backend.main:app --reload

The local API is then available at:

.. code-block:: text

   http://127.0.0.1:8000

Check the health endpoint:

.. code-block:: bash

   curl http://127.0.0.1:8000/api/health

Expected response:

.. code-block:: json

   {"status":"ok"}

Backend RQ worker
-----------------

Start an RQ worker in a second terminal:

.. code-block:: bash

   uv run rq worker newclid --url redis://localhost:6379/0

The worker must use the same queue name and Redis URL as the API server. If the
API server is running but no worker is running, submitted jobs remain queued.

Backend smoke test
------------------

Submit a small JGEX problem:

.. code-block:: bash

   curl -X POST http://127.0.0.1:8000/api/jobs \
     -H 'Content-Type: application/json' \
     -d '{
       "input_type": "jgex",
       "problem_input": "a b c = triangle a b c ? cong a b a b"
     }'

The response contains a job id:

.. code-block:: json

   {"job_id":"...","status":"queued"}

Poll the job status:

.. code-block:: bash

   curl http://127.0.0.1:8000/api/jobs/<job_id>

Fetch the final result:

.. code-block:: bash

   curl http://127.0.0.1:8000/api/jobs/<job_id>/result

See :doc:`../contracts/solver_job_lifecycle` for the public status model.
