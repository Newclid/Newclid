Yuclid matcher modules
======================

The Yuclid module pages explain the custom-rule matcher by responsibility. They
are reference pages, not step-by-step guides. Read them in order if you want the
full input-to-output flow, or jump directly to the subsystem you need.

.. toctree::
   :maxdepth: 1
   :hidden:

   Rule parsing <rule_schema_and_parsing>
   Rule planning <rule_planning>
   Generic matcher <generic_rule_matcher>
   Providers <predicate_providers>
   Geometry cache <lazy_geometry_cache>
   Optimization <matching_and_optimization>
   Theorem validation <theorem_candidate_validation>
   Newclid integration <integration_with_newclid>
   CLI/config <configuration_and_cli>
   Build/packaging <build_and_packaging>

Yuclid matcher module map
-------------------------

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Module page
     - What it explains
   * - :doc:`rule_schema_and_parsing`
     - Custom rule text, ``rule`` / ``require`` / ``conclude`` / ``end`` parsing, validation, and variable handling.
   * - :doc:`rule_planning`
     - Planned predicates, variable indices, mapping state, filter state, and predicate ordering metadata.
   * - :doc:`generic_rule_matcher`
     - The search loop that combines provider-generated mappings, check-only filters, and theorem construction.
   * - :doc:`predicate_providers`
     - How providers suggest only plausible mappings instead of enumerating every point assignment.
   * - :doc:`lazy_geometry_cache`
     - Lazy point pairs, segment-length buckets, and shared geometry data used by providers.
   * - :doc:`matching_and_optimization`
     - Join order, early pruning, fallback enumeration, and expensive-rule behavior.
   * - :doc:`theorem_candidate_validation`
     - Statement building, theorem candidate construction, and final numerical validation.
   * - :doc:`integration_with_newclid`
     - Newclid API, Python adapter, temporary custom-rule files, and deduction mapping back to Newclid.
   * - :doc:`configuration_and_cli`
     - Command-line configuration for loading additional custom rule files.
   * - :doc:`build_and_packaging`
     - CMake, packaging, Boost, and runtime installation changes needed by the integration.

Yuclid matcher navigation rule
------------------------------

The sidebar hierarchy is defined here. The top-level Yuclid page links only to
``modules/index``; this page owns the detailed matcher-module children. That
keeps every document in exactly one toctree parent and prevents Sphinx from
replacing the sidebar with a different flat tree when opening deeper pages.
