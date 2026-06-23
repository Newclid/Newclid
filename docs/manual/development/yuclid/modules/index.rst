Yuclid matcher modules
======================

The Yuclid module pages explain the custom-rule matcher by responsibility. They
are reference pages, not step-by-step guides.

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

Yuclid matcher navigation
-------------------------

The sidebar uses short labels, but the page titles stay globally unique for
Sphinx labels. Start with ``Rule parsing`` and follow the order below if you
want to understand the matcher from input to accepted theorem.

.. toctree::
   :maxdepth: 1

   Rule parsing <rule_schema_and_parsing>
   Rule planning <rule_planning>
   Generic matcher <generic_rule_matcher>
   Providers <predicate_providers>
   Geometry cache <lazy_geometry_cache>
   Optimization <matching_and_optimization>
   Theorem validation <theorem_candidate_validation>
   Newclid integration <integration_with_newclid>
