Frontend testing
================

The frontend uses `Vitest <https://vitest.dev>`_ with a ``jsdom`` environment.
Tests live under ``frontend/tests/`` and are split into two projects: ``unit`` and ``integration``.

Test layout
-----------

.. code-block:: text

   tests/
   ├── unit/
   │   ├── api/          # BackendClient, JobPoller, API types
   │   ├── construction/ # Construction catalogue entries
   │   ├── render/       # Renderer
   │   ├── theorem/      # TheoremStore, validation, predicates
   │   └── ui/           # Toolbar, proof panel, notifications, …
   └── integration/
       └── submissionLifecycle.test.ts  # End-to-end job submit → poll → result

Unit tests cover individual modules in isolation; integration tests exercise the full job lifecycle with a mocked HTTP layer.

Running the tests
-----------------

.. code-block:: bash

   # All tests (watch mode)
   npm test

   # All tests (single run)
   npm run test:run

   # Unit tests only
   npm run test:unit

   # Integration tests only
   npm run test:integration

   # Coverage report (output to frontend/coverage/)
   npm run test:coverage

Writing tests
-------------

Add new test files under ``tests/unit/`` or ``tests/integration/`` following the existing directory structure.
The ``jsdom`` environment is available in both projects, so DOM manipulation works out of the box.

The geometry layer (``src/geometry/``) has no DOM dependency and is straightforward to unit-test with plain assertions.
For modules that interact with the DOM, use the helpers in ``src/ui/dom.ts`` to create elements and assert on their state.
