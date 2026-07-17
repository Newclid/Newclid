Backend extension guides
========================

Backend guides are task-oriented recipes. Use them when you need to change
backend behavior and want to know which modules, contracts, and tests are
normally involved.

Backend guide map
-----------------

.. list-table::
   :widths: 34 66
   :header-rows: 1

   * - Guide
     - Use it when
   * - :doc:`add_an_endpoint`
     - Adding a new HTTP route to the backend service.
   * - :doc:`extend_the_job_request`
     - Adding a new field to ``POST /api/jobs``.
   * - :doc:`extend_custom_theorems`
     - Changing custom theorem request validation or conversion.
   * - :doc:`expose_new_proof_data`
     - Returning additional solver/proof data to the frontend.
   * - :doc:`tune_job_execution`
     - Changing timeouts, TTLs, queue names, or worker behavior.
   * - :doc:`debug_job_failures`
     - Debugging queued jobs, failed jobs, and missing results.

.. toctree::
   :maxdepth: 2

   add_an_endpoint
   extend_the_job_request
   extend_custom_theorems
   expose_new_proof_data
   tune_job_execution
   debug_job_failures
