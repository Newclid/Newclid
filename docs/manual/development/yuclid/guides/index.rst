Yuclid extension guides
=======================

Yuclid guides are task-oriented recipes for extending or debugging the custom
rule matcher.

Yuclid guide map
----------------

.. list-table::
   :widths: 34 66
   :header-rows: 1

   * - Guide
     - Use it when
   * - :doc:`add_a_predicate_provider`
     - Adding an optimized provider for a predicate such as ``coll``, ``para``, or ``perp``.
   * - :doc:`add_a_lazy_cache`
     - Adding shared cached geometry needed by providers.
   * - :doc:`add_a_supported_predicate`
     - Supporting a predicate end-to-end in parsing, statement building, matching, and theorem construction.
   * - :doc:`optimize_a_generic_rule`
     - Improving performance for a rule that currently falls back to enumeration.
   * - :doc:`debug_generic_matching`
     - Debugging rules that parse but produce no candidates or too many candidates.
   * - :doc:`debug_custom_rule_integration`
     - Debugging the Newclid adapter to Yuclid executable path.

.. toctree::
   :maxdepth: 2

   add_a_predicate_provider
   add_a_lazy_cache
   add_a_supported_predicate
   optimize_a_generic_rule
   debug_generic_matching
   debug_custom_rule_integration
