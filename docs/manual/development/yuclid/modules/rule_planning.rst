Yuclid rule planning and state
==============================

Rule planning prepares a custom rule for efficient matching. It groups predicate
patterns, maps rule variables to compact indices, and decides which predicates
should generate mappings first.

Yuclid planned predicates
-------------------------

A planned predicate stores the original predicate pattern together with matcher
metadata:

- predicate name and arguments;
- variable indices used by that predicate;
- provider metadata and estimated cost;
- whether the predicate can generate candidates or only check completed ones.

Yuclid mapping state
--------------------

``MappingState`` tracks the current partial assignment from rule variables to
problem points. It is responsible for:

- checking whether a variable is assigned;
- checking whether a problem point is already used;
- applying a ``MappingExtension``;
- taking snapshots and rolling back during search.

Yuclid filter state
-------------------

``FilterState`` tracks which check-only predicates have already been evaluated
for the current branch. This prevents repeated work while still allowing the
matcher to roll back when the search backtracks.

Yuclid planning design rule
---------------------------

Planning should decide search order and metadata. It should not perform the
actual geometric check. Geometric generation and checking belong in predicate
providers, and final theorem validation remains the last guard.
