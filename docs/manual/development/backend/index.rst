Backend developer guide
=======================

The Newclid backend is a FastAPI service that receives solver requests from the
frontend, stores them as Redis/RQ jobs, and exposes endpoints for status polling
and result retrieval.

The backend is intentionally thin. It owns transport, validation, queueing,
status mapping, configuration, and result normalization. It does not own the
mathematical solver logic; that lives in Newclid and the Yuclid engine.

Backend reading order
---------------------

Read :doc:`architecture` first if you are new to the backend. Then use the
module pages as reference and the guide pages when making a change.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Page group
     - Use it for
   * - :doc:`setup`
     - Running the API server, Redis, and an RQ worker locally.
   * - :doc:`architecture`
     - Understanding the whole backend flow in one pass.
   * - :doc:`modules/index`
     - Understanding what each backend module is responsible for.
   * - :doc:`guides/index`
     - Making common backend changes safely.
   * - :doc:`api_reference`
     - Connecting hand-written docs to generated API/OpenAPI references.
   * - :doc:`testing`
     - Choosing and running the right backend tests.

Backend source map
------------------

.. code-block:: text

   src/newclid_backend/
     main.py
     routers/jobs.py
     schemas.py
     queue.py
     tasks.py
     newclid_runner.py
     runner_helpers.py
     runner_models.py
     settings.py

.. toctree::
   :maxdepth: 2

   setup
   architecture
   modules/index
   guides/index
   api_reference
   testing
