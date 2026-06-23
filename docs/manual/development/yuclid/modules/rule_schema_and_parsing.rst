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
