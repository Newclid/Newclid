Yuclid theorem candidate validation
===================================

Generic matching produces theorem candidates. It does not directly prove that a
candidate should be accepted by the solver.

Yuclid validation boundary
--------------------------

The matcher is responsible for finding mappings that satisfy the schema
premises. The theorem builder constructs candidate premises and conclusions from
that mapping. The existing theorem insertion and validation path is still
responsible for deciding whether the candidate is accepted.

Yuclid candidate rejection reasons
----------------------------------

A candidate can be rejected because:

- a provider generated a mapping that passes local checks but fails a full statement check;
- a conclusion is degenerate;
- the theorem duplicates an existing theorem;
- the theorem does not satisfy the normal Yuclid theorem invariants;
- a rule schema is syntactically valid but semantically unhelpful for the problem.

Yuclid validation design rule
-----------------------------

Do not weaken final validation to make generic matching accept more candidates.
If a valid custom rule produces no accepted theorem, debug parsing, mapping,
provider generation, and theorem construction first.

Yuclid statement builder role
-----------------------------

The statement builder converts a predicate pattern plus a concrete rule mapping
into Yuclid statement objects. It is the bridge between symbolic custom rules and
existing Yuclid geometry checks.

.. code-block:: text

   predicate pattern:  cong A B C D
   rule mapping:       A -> p0, B -> p1, C -> p2, D -> p3
        │
        ▼
   statement builder creates the corresponding Yuclid statement object

This keeps provider code from constructing every statement type manually. A
provider can focus on candidate generation and local checks, while the statement
builder owns predicate-to-statement construction.

Yuclid theorem builder role
---------------------------

The theorem builder receives:

- the matched ``RuleSchema``;
- a complete ``RuleMapping`` from rule variables to problem points;
- the premise and conclusion predicate patterns.

It builds a theorem candidate that can be inserted into the normal Yuclid theorem
pipeline. The result is still only a candidate. It must pass the same downstream
checks as theorem candidates coming from built-in logic.

Yuclid candidate lifecycle
--------------------------

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Step
     - What happens
   * - Candidate mapping found
     - ``GenericRuleMatcher`` finds a complete mapping for all rule variables.
   * - Premises checked
     - Providers and check-only predicates verify that the mapped hypotheses hold.
   * - Statements built
     - ``statement_builder`` converts mapped predicate patterns into statement objects.
   * - Theorem candidate built
     - ``theorem_builder`` creates a candidate theorem from premises and conclusions.
   * - Final validation runs
     - Existing theorem validation rejects degenerate, duplicate, or invalid candidates.
   * - Accepted theorem returned
     - The theorem can participate in DDAR/proof search like other matched theorems.

Yuclid why providers are not enough
-----------------------------------

Providers deliberately cut corners to make search fast. For example, a provider
may use buckets or anchors to avoid mappings that are definitely impossible, but
it may still yield candidates that only fail after a full statement check.

That is expected. The safe design is:

.. code-block:: text

   provider generation removes obvious impossibilities
       ↓
   provider satisfaction check removes local false positives
       ↓
   statement/theorem construction normalizes the candidate
       ↓
   final theorem validation remains the correctness guard

Do not move final correctness assumptions into a provider. A provider should be
selective, but the theorem candidate must still be valid if provider heuristics
or estimates are imperfect.

Yuclid duplicate and degenerate candidate handling
--------------------------------------------------

Custom rules can create candidates that are syntactically valid but not useful.
Examples include:

- a conclusion that is already known;
- a conclusion with degenerate geometry;
- a mapping that aliases points in a way the final statement rejects;
- a theorem that duplicates an existing theorem from another rule;
- a rule that is true but produces no new information for the current goal.

These cases should be rejected by normal insertion/validation logic rather than
special-cased in the generic matcher. Keeping rejection centralized avoids
having every provider duplicate theorem invariants.
