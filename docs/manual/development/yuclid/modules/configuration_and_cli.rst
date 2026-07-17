Yuclid configuration and CLI
============================

The custom-rule work adds one important command-line boundary to Yuclid: an
optional file containing additional rule schemas. This page explains where that
option is parsed and how it reaches the matcher.

Yuclid additional-rules option
------------------------------

The executable accepts an optional argument:

.. code-block:: bash

   --input-additional-rules-file custom_rules.txt

When the option is omitted, Yuclid behaves like the normal standard-rule matcher.
When the option is present, ``main.cpp`` opens the rule file, parses it into
``RuleSchema`` objects, and passes those schemas into theorem matching and DDAR
solving.

Yuclid CLI flow
---------------

.. code-block:: text

   ConfigOptions parses --input-additional-rules-file
        ↓
   main.cpp reads the file if the path is non-empty
        ↓
   parse_rule_schemas(...) returns validated/custom schemas
        ↓
   run_ddar(...) or match_theorems(...) receives the schemas
        ↓
   DDARSolver / TheoremMatcher passes them to GenericRuleMatcher

The rule file is intentionally separate from the problem file. The problem file
contains the concrete geometry setup. The additional rule file contains runtime
rule schemas that should be matched against that problem.

Yuclid match and DDAR modes
---------------------------

Both ``match`` mode and ``ddar`` mode should receive the same custom schemas.
This is useful because ``match`` mode is the fastest way to debug whether a
custom rule produces theorem candidates before running the full solver.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Mode
     - Custom-rule behavior
   * - ``--mode match``
     - Parses the problem and custom rules, then prints/matches theorem candidates.
   * - ``--mode ddar``
     - Parses the same inputs and uses the matched custom-rule candidates inside solver execution.

Yuclid CLI debugging rule
-------------------------

When Newclid integration fails, save the generated problem file and custom rule
file from the adapter, then run Yuclid manually with the same CLI arguments. This
separates Python adapter issues from C++ parsing/matching issues.
