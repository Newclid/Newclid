Yuclid custom rule architecture
===============================

The Yuclid changes add a generic matcher for user-defined rule schemas. The main
idea is that Newclid can pass non-standard rules to Yuclid, and Yuclid can search
for concrete theorem instances without hardcoding every possible custom rule in
C++.

Yuclid custom rule pipeline
---------------------------

.. code-block:: text

   Newclid Rule objects
        │
        ▼
   GeometricSolverBuilder.with_additional_rules(...)
        │
        ▼
   YuclidAdapter writes custom_rules_<problem>.txt
        │
        ▼
   yuclid --input-additional-rules-file custom_rules.txt
        │
        ▼
   parser/rule_parser.cpp parses RuleSchema objects
        │
        ▼
   rules/schema_validator.cpp validates variables and predicates
        │
        ▼
   DDARSolver and TheoremMatcher receive the custom schemas
        │
        ▼
   GenericRuleMatcher plans and matches each schema
        │
        ▼
   PredicateProvider implementations generate candidate mappings
        │
        ▼
   TheoremBuilder builds theorem candidates
        │
        ▼
   Existing theorem validation accepts or rejects candidates
        │
        ▼
   Yuclid returns deductions to the Newclid adapter

Yuclid architecture layers
--------------------------

.. list-table::
   :widths: 28 34 38
   :header-rows: 1

   * - Layer
     - Main files
     - Responsibility
   * - Input and configuration
     - ``config_options.*``, ``main.cpp``
     - Accept an optional custom-rule file and pass parsed schemas into matching and solving.
   * - Rule schema layer
     - ``rule_parser.*``, ``rule_schema.hpp``, ``schema_validator.*``
     - Parse and validate user-defined rule schemas.
   * - Construction layer
     - ``statement_builder.*``, ``theorem_builder.*``, ``rule_mapping.hpp``
     - Turn rule predicates and variable mappings into Yuclid statements and theorem candidates.
   * - Matching layer
     - ``generic_rule_matcher.*``, ``rule_plan.*``, ``mapping_state.*``, ``filter_state.*``
     - Search for mappings from schema variables to problem points.
   * - Provider/cache layer
     - ``predicate_provider.*``, ``base_provider.*``, ``cong_provider.*``, ``lazy_geometry_cache.*``
     - Generate candidate extensions efficiently using predicate-specific indexes and lazy geometry caches.
   * - Newclid boundary
     - ``yuclid_adapter.py``, ``newclid/api.py``
     - Forward custom rules to Yuclid and map returned custom-rule deductions back to Newclid rules.

Yuclid design rules
-------------------

The custom-rule matcher follows these design rules:

.. list-table::
   :widths: 32 68
   :header-rows: 1

   * - Rule
     - Reason
   * - Keep parsing separate from matching.
     - Invalid rule text should fail before the matcher starts searching.
   * - Match schemas through indexed predicates when possible.
     - A selective predicate such as ``cong`` can reduce the search space before fallback enumeration is needed.
   * - Keep providers predicate-specific.
     - Provider code should know how to generate and check one predicate shape well.
   * - Build theorem candidates, then validate them normally.
     - Generic matching proposes candidates; existing theorem validation remains the final guard.
   * - Keep Newclid/Yuclid contracts explicit.
     - Custom rules crossing the Python/C++ boundary should be serialized through a simple text format.

Yuclid matcher extension points
-------------------------------

Most future changes fall into one of these categories:

- add a predicate provider: start with :doc:`guides/add_a_predicate_provider`;
- add a lazy cache: start with :doc:`guides/add_a_lazy_cache`;
- support a new predicate end-to-end: start with :doc:`guides/add_a_supported_predicate`;
- optimize an expensive custom rule: start with :doc:`guides/optimize_a_generic_rule`;
- debug missing or excessive matches: start with :doc:`guides/debug_generic_matching`.
