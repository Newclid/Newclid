Yuclid custom rule testing
==========================

Yuclid custom-rule tests should be grouped by the boundary they protect. Use the
smallest test that proves the behavior, then add integration tests for full
custom-rule flows.

Yuclid parser and schema tests
------------------------------

Parser and schema tests should cover:

- valid custom rule files;
- invalid or missing rule sections;
- duplicate or undeclared variables;
- malformed predicate lines;
- multiple schemas in one rule file.

Relevant tests include:

.. code-block:: text

   yuclid/test/rule_parser.cpp
   yuclid/test/schema_validator.cpp

Yuclid builder tests
--------------------

Builder tests should cover predicate-to-statement conversion and theorem
candidate construction from mappings.

Relevant tests include:

.. code-block:: text

   yuclid/test/statement_builder.cpp
   yuclid/test/theorem_builder.cpp

Yuclid matcher state tests
--------------------------

State tests should cover mapping application, rollback, used-point tracking, and
filter tracking.

Relevant tests include:

.. code-block:: text

   yuclid/test/mapping_state.cpp
   yuclid/test/filter_state.cpp
   yuclid/test/rule_plan.cpp

Yuclid provider and cache tests
-------------------------------

Provider/cache tests should cover generated candidates, fully bound checks,
cache bucket contents, duplicate-variable behavior, and fallback behavior.

Relevant tests include:

.. code-block:: text

   yuclid/test/base_provider.cpp
   yuclid/test/cong_provider.cpp
   yuclid/test/lazy_geometry_cache.cpp
   yuclid/test/geometry_bucket_utils.cpp
   yuclid/test/provider_registry.cpp

Yuclid integration tests
------------------------

Integration tests should prove that a custom rule can travel through the matcher
and produce usable deductions.

Relevant tests include:

.. code-block:: text

   yuclid/test/generic_rule_matcher.cpp
   yuclid/test/custom_rule_integration_test.cpp
   yuclid/tests/test_custom_rule_integration.py

Yuclid test commands
--------------------

A typical C++ test flow is:

.. code-block:: bash

   cmake --build yuclid/build
   ctest --test-dir yuclid/build

For focused debugging, run the specific Boost.Test binary or the specific Python
integration test used by the project.

Yuclid testing rule
-------------------

When changing matcher internals, test both correctness and performance-relevant
behavior. A change that preserves theorem count but explodes candidate generation
can still break interactive use.
