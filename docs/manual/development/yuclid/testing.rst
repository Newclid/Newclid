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

Yuclid changed-test map
-----------------------

The custom-rule work added many tests, but each group protects a specific part
of the pipeline. Use this map when deciding where to add a regression test.

.. list-table::
   :widths: 38 62
   :header-rows: 1

   * - Test file
     - What it protects
   * - ``yuclid/test/rule_parser.cpp``
     - Custom rule file syntax: ``rule``, ``require``, ``conclude``, ``end``, and multiple schemas.
   * - ``yuclid/test/schema_validator.cpp``
     - Rule schema validation: declared variables, duplicate variables, missing sections, and invalid predicate patterns.
   * - ``yuclid/test/statement_builder.cpp``
     - Conversion from predicate patterns plus mappings into Yuclid statement objects.
   * - ``yuclid/test/theorem_builder.cpp``
     - Construction of theorem candidates from a rule schema and a complete mapping.
   * - ``yuclid/test/mapping_state.cpp``
     - Variable-to-point assignments, used-point tracking, snapshots, rollback, and mapping consistency.
   * - ``yuclid/test/filter_state.cpp``
     - Check-only/filter predicate tracking and rollback behavior.
   * - ``yuclid/test/rule_plan.cpp``
     - Rule planning, predicate ordering metadata, and variable-index preparation.
   * - ``yuclid/test/provider_registry.cpp``
     - Predicate-name dispatch to the correct provider or fallback provider.
   * - ``yuclid/test/base_provider.cpp``
     - Fallback enumeration and satisfaction checking for predicates without a specialized provider.
   * - ``yuclid/test/cong_provider.cpp``
     - Optimized congruence candidate generation, assigned-state cases, alias handling, and fully bound checks.
   * - ``yuclid/test/lazy_geometry_cache.cpp``
     - Lazy point-pair and geometry-bucket construction.
   * - ``yuclid/test/geometry_bucket_utils.cpp``
     - Geometry bucket grouping utilities and tolerance-sensitive bucketing behavior.
   * - ``yuclid/test/generic_rule_matcher.cpp``
     - End-to-end matching of parsed/planned schemas against a problem.
   * - ``yuclid/test/custom_rule_integration_test.cpp``
     - C++ integration path from custom schema to matched theorem candidates.
   * - ``yuclid/tests/test_custom_rule_integration.py``
     - Python/Newclid/Yuclid boundary: custom rules passed through the adapter and returned as usable deductions.

Yuclid regression-test selection
--------------------------------

Use these rules when choosing where to add a test:

.. list-table::
   :widths: 34 66
   :header-rows: 1

   * - Change
     - Test expectation
   * - Rule syntax or validation change
     - Add parser/schema validator tests.
   * - New predicate statement support
     - Add statement builder tests and theorem builder tests.
   * - Mapping or rollback change
     - Add mapping/filter state tests and a generic matcher regression.
   * - New provider or provider optimization
     - Add provider-specific tests for every assigned-variable case it handles.
   * - New lazy cache
     - Add cache tests plus at least one provider/matcher test that consumes it.
   * - New custom-rule integration behavior
     - Add C++ integration and Python adapter integration tests.

Yuclid provider test rule
-------------------------

Provider tests should cover both generated candidates and rejected candidates.
For an optimized provider, test the pruning behavior explicitly. For example,
``CongProvider`` tests should verify not only that valid equal-length mappings
are produced, but also that wrong-length segments, reused points, and invalid
variable aliases are rejected.

This is important because a provider bug can fail in two opposite ways:

- it can generate too many mappings and make matching slow;
- it can generate too few mappings and lose valid theorem candidates.
