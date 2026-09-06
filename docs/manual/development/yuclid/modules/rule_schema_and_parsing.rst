Yuclid rule schema and parsing
==============================

The rule schema layer turns custom rule text into structured data that the
matcher can use. It is implemented mainly by ``parser/rule_parser.*``,
``rules/rule_schema.hpp``, and ``rules/schema_validator.*``.

Yuclid rule schema format
-------------------------

A rule schema describes variables, required predicates, and concluded
predicates:

.. code-block:: text

   rule custom_midpoint_rule A B M
   require cong A M M B
   conclude midp M A B
   end

The parser should produce a schema with:

- a rule id;
- an ordered set of variables;
- premise predicate patterns;
- conclusion predicate patterns.

Yuclid schema validation
------------------------

Validation should happen before matching. The validator protects the matcher
from malformed schemas, for example:

- duplicate or invalid variables;
- predicates that reference variables not declared by the rule;
- missing ``require`` or ``conclude`` sections;
- unsupported or malformed predicate patterns.

Yuclid parser ownership
-----------------------

The parser should understand rule syntax, but it should not perform geometric
matching. The matcher is responsible for finding concrete point assignments. The
statement builder is responsible for turning a matched predicate into Yuclid
statement objects.

Yuclid rule schema extension rule
---------------------------------

When adding a new predicate shape, update parsing and validation only for the
syntax-level contract. Predicate semantics belong in the statement builder,
predicate providers, and final theorem validation.

Yuclid custom rule grammar
--------------------------

The custom-rule file is intentionally small and line-oriented. A file can contain
one or more rules. Each rule has this shape:

.. code-block:: text

   rule <rule_id> <var_1> <var_2> ... <var_n>
   require <predicate_name> <arg_1> <arg_2> ...
   require <predicate_name> <arg_1> <arg_2> ...
   conclude <predicate_name> <arg_1> <arg_2> ...
   end

The first line declares the rule id and the variables that may appear in the
rule. ``require`` lines are the hypotheses the matcher must satisfy. ``conclude``
lines are the statements the theorem candidate will produce. ``end`` closes the
schema and lets the parser start reading the next rule.

Example:

.. code-block:: text

   rule custom_isosceles_base_angles A B C
   require cong A B A C
   conclude eqangle B C C B C B B C
   end

The exact predicate arity is still predicate-specific. Parsing should preserve
the raw predicate name and arguments; semantic meaning is handled later by the
statement builder and providers.

Yuclid parsed schema responsibilities
-------------------------------------

A parsed schema should contain only matcher-ready structure:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Field
     - Meaning
   * - Rule id
     - The id reported back when a theorem candidate is accepted.
   * - Declared variables
     - The symbolic variables that may be mapped to problem points.
   * - Required predicate patterns
     - Predicate patterns that must hold before the rule can be applied.
   * - Conclusion predicate patterns
     - Predicate patterns used to build the generated theorem candidate.

The schema should not store problem-specific point assignments. Those live in
``MappingState`` during matching.

Yuclid validation checks
------------------------

Validation should reject schemas before the matcher starts if they are malformed.
Typical checks include:

.. list-table::
   :widths: 36 64
   :header-rows: 1

   * - Problem
     - Why it is rejected early
   * - Empty or duplicate rule variables
     - The matcher needs a stable variable-index table.
   * - Predicate argument uses undeclared variable
     - The matcher cannot map a variable that was never declared.
   * - Missing ``require`` section
     - A rule with no hypotheses can generate too many unconditional candidates.
   * - Missing ``conclude`` section
     - The matcher would have nothing to build.
   * - Malformed rule block
     - The parser cannot safely know where one schema ends and the next begins.
   * - Unsupported predicate syntax
     - The statement builder or provider stack would not know how to interpret it.

Keep validation focused on rule shape. Geometric truth belongs to provider checks
and final theorem validation.

Yuclid variable-index model
---------------------------

After parsing, variables are treated by index rather than by repeatedly comparing
strings. Planning and mapping code works with those indices because they are
faster, easier to store in arrays, and make duplicate-variable handling explicit.

This is important for rules like:

.. code-block:: text

   require cong A B C B

The symbol ``B`` appears twice in one predicate. The matcher must understand that
both occurrences refer to the same rule variable. Providers should preserve that
aliasing when generating mappings: equal variables must map to equal points, and
different variables should normally map to different points unless the schema
explicitly aliases them.

Yuclid parser extension rule
----------------------------

When adding a new predicate, do not put geometric reasoning into the parser. The
parser should accept the predicate line if the syntax is valid and the variables
are declared. The implementation work then belongs in:

- ``statement_builder`` if the predicate must become a Yuclid statement;
- ``predicate_provider`` if the predicate should generate optimized mappings;
- theorem validation if the predicate has degeneracy or numerical constraints.
