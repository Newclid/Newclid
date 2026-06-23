Yuclid generic rule matcher
===========================

The generic rule matcher searches for concrete instances of user-defined rule
schemas. It is the center of the custom-rule matcher stack.

Yuclid generic matcher input
----------------------------

The matcher receives:

- the current ``Problem``;
- solver/matcher configuration;
- one or more validated ``RuleSchema`` objects;
- lazy geometry data through ``LazyGeometryCache``;
- predicate providers that can generate or check mappings.

Yuclid generic matcher algorithm
--------------------------------

At a high level, matching one rule looks like this:

.. code-block:: text

   RuleSchema
        │
        ▼
   RulePlan orders predicates and variables
        │
        ▼
   MappingState starts empty
        │
        ▼
   providers generate MappingExtension objects
        │
        ▼
   CheckOnly predicates prune invalid mappings
        │
        ▼
   complete mapping reaches TheoremBuilder
        │
        ▼
   theorem candidate is inserted after validation

Yuclid complete mappings
------------------------

A complete mapping assigns every schema variable needed to build the rule's
conclusions. The matcher must preserve variable equality correctly: if a rule
uses the same variable twice, both occurrences must map to the same point. If two
schema variables are different, they should not silently alias unless the rule
semantics explicitly allow it.

Yuclid matcher fallback behavior
--------------------------------

If no predicate-specific provider can generate selective candidates, the matcher
falls back to enumeration through the base provider. This keeps the matcher
complete, but it can be expensive. Expensive rules should be optimized by adding
providers or caches for selective predicates.
