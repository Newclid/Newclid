Backend testing
===============

Backend tests are split into unit tests and integration tests. Use the smallest
test level that proves the behavior you changed.

Backend unit tests
------------------

Unit tests live under:

.. code-block:: text

   tests/unit/

They cover logic that can run without a real Redis server or a full worker. The
current unit test areas include:

.. list-table::
   :widths: 36 64
   :header-rows: 1

   * - Test area
     - What it should verify
   * - Health endpoint
     - The FastAPI app responds to ``/api/health``.
   * - Job routes
     - Route behavior, public statuses, messages, and unknown job handling with mocked queue behavior.
   * - Schemas
     - Request validation, custom theorem validation, duplicate names, and predicate-line cleanup.
   * - Queue wrapper
     - Enqueue and fetch behavior with controlled/mocked queue state.
   * - Runner helpers
     - Output truncation, custom rule conversion, and proof dependency index construction.
   * - Runner models
     - Pydantic model validation, especially sketch point validation.
   * - Tasks
     - The RQ task adapter returns a serializable dictionary.

Run backend unit tests with:

.. code-block:: bash

   uv run pytest tests/unit

Backend integration tests
-------------------------

Integration tests live under:

.. code-block:: text

   tests/integration/

They cover behavior that needs multiple real components, such as Redis/RQ or a
real Newclid runner call. The current integration test areas include:

.. list-table::
   :widths: 36 64
   :header-rows: 1

   * - Test area
     - What it should verify
   * - API job lifecycle
     - A submitted job can move through the expected API lifecycle.
   * - Newclid runner integration
     - The runner can parse a real JGEX problem and produce a result model.
   * - Redis/RQ behavior
     - Jobs can be enqueued and processed through the real queue.
   * - Unknown jobs
     - Missing job ids return the expected API error behavior.

Run integration tests with:

.. code-block:: bash

   uv run pytest tests/integration

Backend test selection rule
---------------------------

Use this rule when adding tests:

.. list-table::
   :widths: 34 66
   :header-rows: 1

   * - Change type
     - Test expectation
   * - Pydantic schema change
     - Unit tests in ``tests/unit/test_schemas.py`` or a focused schema validation file.
   * - Route behavior change
     - Unit route test, plus integration test if Redis/RQ behavior changes.
   * - Queue configuration change
     - Unit test for wrapper behavior and integration test with Redis/RQ.
   * - Runner output change
     - Runner helper/model tests and at least one runner integration test.
   * - Full job lifecycle change
     - Integration test that submits a job and reads the final result.

Backend CI expectation
----------------------

For normal backend changes, run:

.. code-block:: bash

   uv sync --extra test
   uv run pytest tests/unit

For queue, worker, Redis, runner, or full API lifecycle changes, also run:

.. code-block:: bash

   uv run pytest tests/integration
