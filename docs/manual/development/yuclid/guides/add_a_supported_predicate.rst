Yuclid guide to adding a supported predicate
============================================

Use this guide when a new predicate should work in custom rules end-to-end. This
is broader than adding a provider: the predicate must be parseable, buildable,
matchable, and validatable.

Yuclid supported predicate steps
--------------------------------

1. Define the public predicate shape.

   Decide the predicate name, arity, argument order, and duplicate-variable
   behavior. The custom-rule syntax should match the predicate spelling used by
   Newclid/Yuclid at the boundary.

2. Accept and validate the predicate pattern.

   Update schema validation if the predicate has fixed arity or special syntax
   constraints. The parser should preserve predicate names and arguments; avoid
   putting geometric reasoning into the parser.

3. Add statement-builder support.

   If the predicate can appear as a premise or conclusion, ``statement_builder``
   must be able to convert the predicate pattern plus a concrete ``RuleMapping``
   into the correct Yuclid statement object.

4. Decide the matching role.

   If the predicate is selective, add a provider. If it is only useful after its
   variables are assigned, treat it as a check-only predicate. If it is not yet
   supported, make the failure explicit.

5. Add cache support if needed.

   Shared geometry structures such as collinearity groups, line directions, or
   perpendicular lookups should live in ``LazyGeometryCache`` instead of being
   rebuilt inside the provider.

6. Add theorem-builder and matcher tests.

   Test the predicate as a premise, as a conclusion, and inside at least one
   complete generic-rule matcher case.

Yuclid supported predicate checklist
------------------------------------

Before considering the predicate supported, check:

- invalid arity is rejected clearly;
- undeclared variables are rejected by schema validation;
- statement construction works for a concrete mapping;
- provider/check-only behavior preserves completeness;
- final theorem validation still runs;
- integration tests cover one successful custom rule using the predicate.
