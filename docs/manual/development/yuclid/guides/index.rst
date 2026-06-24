Yuclid extension guides
=======================

Yuclid guides are task-oriented recipes for extending or debugging the custom
rule matcher. Use the module pages for explanation, and use these pages when you
need concrete implementation steps.

.. toctree::
   :maxdepth: 1
   :hidden:

   Add a provider <add_a_predicate_provider>
   Add a cache <add_a_lazy_cache>
   Add a supported predicate <add_a_supported_predicate>
   Optimize a rule <optimize_a_generic_rule>
   Debug matching <debug_generic_matching>
   Debug Newclid integration <debug_custom_rule_integration>

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
     - Supporting a new predicate through parsing, statement building, provider checks, and theorem construction.
   * - :doc:`optimize_a_generic_rule`
     - Improving performance for a rule that currently falls back to enumeration.
   * - :doc:`debug_generic_matching`
     - Debugging rules that parse but produce no candidates or too many candidates.
   * - :doc:`debug_custom_rule_integration`
     - Debugging the full Newclid → Yuclid → Newclid custom-rule path.

Yuclid guide navigation rule
----------------------------

The top-level Yuclid page links only to ``guides/index``. This page owns the
individual guide pages, so the sidebar can expand cleanly under ``Yuclid
extension guides`` instead of moving those pages to a different parent.
