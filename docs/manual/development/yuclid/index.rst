Yuclid custom rule developer guide
==================================

This section documents the Yuclid work added for Newclid custom rules. It is
not a full Yuclid internals manual. It focuses on the path that starts with a
user-defined Newclid rule, passes through the Python Yuclid adapter, reaches the
Yuclid executable as an additional rule file, and is matched by the generic rule
matcher.

Yuclid guide reading order
--------------------------

Start with :doc:`architecture` to understand the complete flow. Then use the
module pages as reference material and the guide pages when extending the
matcher.

.. list-table::
   :widths: 32 68
   :header-rows: 1

   * - Page group
     - Use it for
   * - :doc:`setup`
     - Building Yuclid, running the executable, and passing custom rule files.
   * - :doc:`architecture`
     - Understanding the complete custom-rule matching pipeline.
   * - :doc:`modules/index`
     - Understanding the parser, matcher, providers, cache, and integration modules.
   * - :doc:`guides/index`
     - Extending or debugging the custom-rule matcher.
   * - :doc:`testing`
     - Choosing and running the relevant Yuclid tests.

Yuclid custom rule source map
-----------------------------

The main files added or modified for this work are:

.. code-block:: text

   yuclid/src/parser/rule_parser.*
   yuclid/src/rules/rule_schema.hpp
   yuclid/src/rules/schema_validator.*
   yuclid/src/statement/statement_builder.*
   yuclid/src/rules/theorem_builder.*
   yuclid/src/matchers/generic_rule_matcher.*
   yuclid/src/matchers/rule_plan.*
   yuclid/src/matchers/predicate_provider.*
   yuclid/src/matchers/base_provider.*
   yuclid/src/matchers/cong_provider.*
   yuclid/src/matchers/lazy_geometry_cache.*
   yuclid/python/py_yuclid/yuclid_adapter.py

.. toctree::
   :maxdepth: 2

   setup
   architecture
   modules/index
   guides/index
   testing
