Testing strategy
================

Each package in the workspace (see :doc:`repository_layout`) owns its own test
suite, in the layer that makes sense for its language and its distance from
the core solver logic. This page gives the overview; :doc:`yuclid/testing`
goes into the Yuclid-specific detail (which C++ test file protects which
matcher module, and how to pick a regression test for a matcher change).

Test layers
-----------

.. list-table::
   :widths: 24 20 56
   :header-rows: 1

   * - Layer
     - Framework
     - What it covers
   * - ``yuclid/test/``
     - Boost.Test, run via CTest
     - C++ unit and integration tests for the engine: numeric/algebraic
       primitives, the problem parser, the generic rule matcher and its
       parser/schema/mapping/provider/cache components, and a C++-level
       custom-rule integration test. Also holds the ``.txt`` problem fixtures
       these tests and ad hoc stress runs use (``imo_ag_30/``,
       ``ratio_only/``, ``no_crash/``, ``simple/``).
   * - ``yuclid/tests/``
     - pytest
     - Python integration tests that exercise the built ``py_yuclid`` package
       end to end, i.e. calling the real ``yuclid`` executable through
       ``YuclidAdapter``/``OmniMatcher`` rather than mocking it. Covers
       custom-rule round trips (``test_custom_rule_integration.py``) and a
       full example problem solved through Yuclid
       (``test_harmonic_euclid.py``).
   * - ``newclid/tests/``
     - pytest
     - The main solver test suite: problem parsing (JGEX and GeoGebra),
       individual rule/predicate behavior, algebraic reasoning, deductive
       agents, heuristics, proof writing/dependencies, drawing, and the CLI.
       Most tests build a solver through ``GeometricSolverBuilder`` without
       forcing a backend, so they run against whichever ``RuleMatcher`` the
       environment resolves (Yuclid if ``py_yuclid`` is installed, the
       pure-Python fallback otherwise). A few tests, such as
       ``test_individual_rules.py``, use
       ``pytest.importorskip("py_yuclid.yuclid_adapter")`` to test Yuclid-only
       behavior and are skipped when Yuclid is not installed.
   * - ``ncdgen/tests/``
     - pytest
     - Tests for the diagram-generation tool, covering its CLI, generation
       configuration, auxiliary-point discriminators, diagram generation, and
       double-checking logic.

Running the tests
-----------------

From the repository root, after ``uv sync``:

.. code-block:: bash

   # Whole Python workspace (newclid, ncdgen, yuclid Python integration tests)
   uv run pytest

   # One package only
   uv run pytest newclid/tests
   uv run pytest ncdgen/tests
   uv run pytest yuclid/tests

   # C++ engine tests
   cmake -S yuclid -B yuclid/build
   cmake --build yuclid/build
   ctest --test-dir yuclid/build --output-on-failure

Because this is a uv workspace, ``uv run pytest`` from the root collects tests
from every member package in one run; scope it to a single ``tests/``
directory while iterating on one package. ``yuclid/tests`` (Python) requires a
built ``yuclid`` executable/``py_yuclid`` extension, so run the CMake build
first if you are working on the C++ engine and want the Python integration
tests to reflect your changes.

Continuous integration mirrors this split: a dedicated workflow builds and
``ctest``\ s the C++ engine on Linux, macOS, and Windows (on every push to
``main`` and on pull requests touching ``yuclid/**``), while a separate
workflow runs ``pytest`` across the Python workspace on every push, after
``pre-commit`` checks.

Choosing where to add a test
----------------------------

.. list-table::
   :widths: 34 66
   :header-rows: 1

   * - Change
     - Where to add coverage
   * - New or changed C++ matcher/parser/provider/cache behavior
     - ``yuclid/test/`` (see :doc:`yuclid/testing` for the file-by-file map).
   * - New or changed Python adapter behavior
       (``yuclid_adapter.py``, ``omni_matcher.py``)
     - ``yuclid/tests/test_custom_rule_integration.py`` or a new focused test
       in ``yuclid/tests/``.
   * - New or changed rule, predicate, deductor, or proof-writing behavior
     - ``newclid/tests/``.
   * - New or changed diagram-generation behavior
     - ``ncdgen/tests/``.
   * - A behavior that must hold regardless of backend
     - Add or extend a backend-agnostic ``newclid/tests/`` test (one that
       builds the solver without forcing a ``RuleMatcher``), plus a
       Yuclid-specific regression in ``yuclid/test/`` or ``yuclid/tests/`` if
       the failure mode is Yuclid-specific (e.g. a provider pruning bug that a
       pure-Python matcher would not hit).

As with the Yuclid-specific rule in :doc:`yuclid/testing`, prefer the smallest
test that proves a behavior, and add an integration test only for flows that
genuinely cross a package boundary (Python calling the compiled engine, or the
CLI driving the full solver).
