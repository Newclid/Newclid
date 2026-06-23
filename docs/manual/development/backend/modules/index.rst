Backend modules
===============

The backend module pages describe what each backend component is and how it
fits into the job lifecycle. These pages are reference material, not step-by-step
guides.

Backend module map
------------------

.. list-table::
   :widths: 34 66
   :header-rows: 1

   * - Module page
     - What it explains
   * - :doc:`api`
     - FastAPI app, job routes, request schemas, status mapping, and result endpoint behavior.
   * - :doc:`queue_and_tasks`
     - Redis/RQ queue wrapper and the worker task adapter.
   * - :doc:`runner`
     - JGEX parsing, Newclid solver invocation, proof conversion, and error handling.
   * - :doc:`result_model`
     - Pydantic models returned by the runner and consumed by the frontend.
   * - :doc:`custom_theorems`
     - Request validation and conversion of custom theorem payloads into Newclid rules.
   * - :doc:`configuration`
     - Environment variables and operational settings.

.. toctree::
   :maxdepth: 2

   api
   queue_and_tasks
   runner
   result_model
   custom_theorems
   configuration
