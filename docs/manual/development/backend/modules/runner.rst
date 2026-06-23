Backend runner
==============

The runner layer is the only backend layer that calls Newclid directly. It is
implemented by ``newclid_runner.py`` and helper code in ``runner_helpers.py`` and
``runner_models.py``.

Backend runner entry point
--------------------------

The main entry point is:

.. code-block:: text

   run_newclid_from_jgex(jgex_problem, custom_theorems=None)

It returns a ``NewclidRunResult`` model, not a FastAPI response. This makes the
runner testable without HTTP, Redis, or RQ.

Backend runner execution steps
------------------------------

The runner performs these steps:

.. code-block:: text

   JGEXProblemBuilder().with_problem_from_txt(jgex_problem).build()
       ↓
   GeometricSolverBuilder()
       ↓
   optionally add custom Rule objects
       ↓
   build solver from problem setup
       ↓
   solver.run()
       ↓
   convert proof state into proof_data
       ↓
   write proof text and proof sections
       ↓
   build sketch points
       ↓
   return NewclidRunResult

Backend JGEX parsing boundary
-----------------------------

The API route does not parse JGEX. JGEX parsing happens inside the runner with
``JGEXProblemBuilder``. This is important for error handling: malformed JGEX is
reported as a failed solver job rather than as a synchronous API validation
error.

Backend proof conversion
------------------------

When the solver succeeds, the runner builds proof data from the solver state and
then produces two frontend-facing proof forms:

- ``proof_text``: full human-readable proof text from ``write_proof``.
- ``proof_sections``: structured proof sections from ``write_proof_sections``.

The runner also builds ``sketch_points`` from the proof data points so the
frontend can draw the final solver sketch.

Backend runner failure behavior
-------------------------------

The runner catches exceptions and converts them into ``NewclidRunResult`` with
``status="failed"``. The exception message is put into ``message`` and the
truncated traceback is put into ``stderr``.

If the solver runs without raising an exception but does not prove all goals,
the runner also returns ``status="failed"`` with the message:

.. code-block:: text

   Newclid finished, but did not prove all goals.

This distinction is useful for debugging but both cases are public failed jobs.

Backend output truncation
-------------------------

Long output is truncated by keeping the last ``MAX_OUTPUT_CHARS`` characters.
This is used for proof text and exception tracebacks so Redis does not store
unbounded output.
