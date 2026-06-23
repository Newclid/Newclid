Yuclid matcher modules
======================

The Yuclid module pages explain the custom-rule matcher by responsibility. They
are reference pages, not step-by-step guides.

Yuclid matcher module map
-------------------------

.. list-table::
   :widths: 34 66
   :header-rows: 1

   * - Module page
     - What it explains
   * - :doc:`custom_rule_pipeline`
     - The end-to-end flow from Newclid custom rules to Yuclid theorem candidates.
   * - :doc:`rule_schema_and_parsing`
     - Rule schema format, parsing, validation, and variable handling.
   * - :doc:`statement_and_theorem_building`
     - Conversion from matched rule variables into Yuclid statements and theorem candidates.
   * - :doc:`matcher_integration`
     - Where custom rules enter the existing theorem matcher and DDAR solver.
   * - :doc:`generic_rule_matcher`
     - The generic matcher algorithm and its responsibilities.
   * - :doc:`rule_planning`
     - Rule planning, predicate metadata, mapping state, and filter state.
   * - :doc:`predicate_providers`
     - Provider interface, fallback provider, and the optimized congruence provider.
   * - :doc:`lazy_geometry_cache`
     - Lazy point/segment buckets used by providers.
   * - :doc:`matching_and_optimization`
     - Join order, pruning, fallback enumeration, and performance behavior.
   * - :doc:`theorem_candidate_validation`
     - Why generated matches are still validated before becoming accepted theorems.
   * - :doc:`integration_with_newclid`
     - Python adapter and Newclid API integration.
   * - :doc:`configuration_and_cli`
     - CLI/configuration support for additional rule files.
   * - :doc:`build_and_packaging`
     - CMake, wheel, Boost, and runtime packaging changes.

.. toctree::
   :maxdepth: 2

   custom_rule_pipeline
   rule_schema_and_parsing
   statement_and_theorem_building
   matcher_integration
   generic_rule_matcher
   rule_planning
   predicate_providers
   lazy_geometry_cache
   matching_and_optimization
   theorem_candidate_validation
   integration_with_newclid
   configuration_and_cli
   build_and_packaging
