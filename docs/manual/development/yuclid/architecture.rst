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

Yuclid full custom-rule round trip
----------------------------------

The custom-rule feature is a cross-component flow. Yuclid does not receive a
Python ``Rule`` object directly. Newclid first decides which rules are not part
of the standard library, the Python adapter serializes them into Yuclid's rule
file syntax, and the C++ executable parses that file before theorem matching
starts.

.. code-block:: text

   1. Frontend/backend submits custom theorem text
          │
          ▼
   2. Newclid backend builds Newclid Rule objects
          │
          ▼
   3. GeometricSolverBuilder.with_additional_rules(...) appends non-duplicate rules
          │
          ▼
   4. GeometricSolverBuilder.build(...) detects non-standard rules
          │
          ▼
   5. YuclidAdapter.custom_rules stores only rules not present in ALL_RULES
          │
          ▼
   6. YuclidAdapter writes two temporary files
          │       problem_<name>.txt
          │       custom_rules_<name>.txt
          ▼
   7. Yuclid executable is called with both files
          │       --input-file problem_<name>.txt
          │       --input-additional-rules-file custom_rules_<name>.txt
          ▼
   8. C++ main.cpp parses the problem and the custom rule schemas
          │
          ▼
   9. TheoremMatcher receives standard matching plus custom schemas
          │
          ▼
   10. GenericRuleMatcher searches concrete mappings for each schema
          │
          ▼
   11. TheoremBuilder turns accepted mappings into theorem candidates
          │
          ▼
   12. Existing theorem validation/insertion accepts only valid candidates
          │
          ▼
   13. Yuclid returns deductions tagged with the custom rule id
          │
          ▼
   14. YuclidAdapter maps the deduction id back to the Newclid Rule object

The important design point is that the Python side owns transport and rule
registration, while the C++ side owns parsing, matching, and theorem candidate
construction. A future developer debugging a missing deduction should follow the
same order: Newclid rule creation, adapter serialization, Yuclid rule parsing,
generic matching, theorem validation, and returned deduction mapping.

Yuclid matcher role in the existing solver
------------------------------------------

The generic matcher does not replace Yuclid's existing hardcoded theorem
matching. It is added as an extra source of theorem candidates for rules that are
not known at compile time. Standard rules still use the normal Yuclid machinery.
Custom rules use the generic path because their predicate patterns are only known
at runtime.

.. list-table::
   :widths: 32 68
   :header-rows: 1

   * - Rule source
     - Matching path
   * - Built-in Yuclid/Newclid rule
     - Existing theorem matcher logic.
   * - User-defined custom rule
     - ``RuleSchema`` → ``RulePlan`` → ``GenericRuleMatcher`` → provider-based mapping search → theorem candidate validation.
   * - Final accepted theorem
     - Inserted back into the same theorem/proof pipeline as other theorem candidates.

This is why the docs focus on the custom-rule pipeline instead of documenting all
of DDAR. The changed code connects custom rules to the existing solver; it does
not redesign the whole solver.

Yuclid provider idea in the pipeline
------------------------------------

A generic rule matcher could try every possible assignment of rule variables to
problem points. That is complete, but it becomes unusable as soon as a rule has
several variables and the problem has many points.

Predicate providers are the optimization layer. A provider looks at one planned
predicate and suggests only mappings that have a realistic chance of satisfying
that predicate. For example, the ``cong`` provider uses equal-length segment
buckets. If the rule requires ``cong A B C D`` and ``A`` and ``B`` are already
mapped, it does not try every possible ``C`` and ``D``. It only tries point pairs
whose segment length matches ``AB``.

The goal is to cut the search space without losing valid matches:

- exclude mappings that are definitely impossible for the predicate;
- keep mappings that may satisfy the predicate;
- let ``is_satisfied`` and final theorem validation reject remaining false positives.

Providers therefore optimize candidate generation, but they are not the final
source of truth for theorem correctness.
