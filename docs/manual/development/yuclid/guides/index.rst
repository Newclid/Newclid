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
   * - :doc:`optimize_a_generic_rule`
     - Improving performance for a rule that currently falls back to enumeration.
   * - :doc:`debug_generic_matching`
     - Debugging rules that parse but produce no candidates or too many candidates.

.. toctree::
   :maxdepth: 1

   Add a provider <add_a_predicate_provider>
   Add a cache <add_a_lazy_cache>
   Optimize a rule <optimize_a_generic_rule>
   Debug matching <debug_generic_matching>
