Testing strategy
================

The generic rule matcher is tested at two levels: C++ unit and integration
tests for the engine itself, and Python integration tests for the adapter
that connects it to Newclid.

.. list-table::
   :widths: 25 20 55
   :header-rows: 1

   * - Suite
     - Framework
     - Covers
   * - ``yuclid/test/``
     - Boost.Test, via CTest
     - The C++ engine: the rule parser and schema validator, the generic
       matcher's search loop and mapping/filter state, predicate providers,
       the lazy geometry cache, and theorem/statement construction.
   * - ``yuclid/tests/``
     - pytest
     - The compiled engine end to end through ``py_yuclid``: custom-rule
       round trips (``test_custom_rule_integration.py``) and a full example
       problem solved through Yuclid (``test_harmonic_euclid.py``).

Running the tests
-----------------

.. code-block:: bash

   # Python integration tests
   uv run pytest yuclid/tests

   # C++ engine tests
   cmake -S yuclid -B yuclid/build
   cmake --build yuclid/build
   ctest --test-dir yuclid/build --output-on-failure

Build Yuclid first if you want the Python integration tests in
``yuclid/tests/`` to reflect a C++ change — they exercise the compiled
``yuclid`` executable, not the source directly.

Continuous integration mirrors this split: a dedicated workflow builds and
``ctest``\ s the C++ engine on Linux, macOS, and Windows, on every push to
``main`` and on pull requests touching ``yuclid/**``.

See :doc:`yuclid/testing` for a file-by-file map of which test protects
which matcher component, and how to pick a regression test for a change.
