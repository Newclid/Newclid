Yuclid custom rule setup
========================

This page explains the development setup needed for the custom-rule matcher
work. It does not replace the normal Yuclid build instructions; it only calls
out the parts relevant to the Newclid custom-rule integration.

Yuclid local build
------------------

Build Yuclid from the repository root or from the ``yuclid/`` package depending
on the workflow used by the project. A typical CMake workflow is:

.. code-block:: bash

   cmake -S yuclid -B yuclid/build
   cmake --build yuclid/build

The custom-rule matcher adds new C++ source files under ``yuclid/src/matchers/``,
``yuclid/src/parser/``, ``yuclid/src/rules/``, and
``yuclid/src/statement/``. If a new matcher module is added, make sure it is
also added to ``yuclid/src/CMakeLists.txt``.

Yuclid additional rule file
---------------------------

The Yuclid executable accepts an optional additional rules file:

.. code-block:: bash

   yuclid --mode match \
     --input-file problem.txt \
     --input-additional-rules-file custom_rules.txt

The same option is used for DDAR mode. When the option is omitted, Yuclid runs
with only the standard rules.

Yuclid custom rule file format
------------------------------

A custom rule file contains one or more rule schemas:

.. code-block:: text

   rule custom_cong_transitive A B C D E F
   require cong A B C D
   require cong C D E F
   conclude cong A B E F
   end

Each schema has:

- a ``rule`` line with the rule id and variables;
- one or more ``require`` lines;
- one or more ``conclude`` lines;
- an ``end`` line.

Yuclid Python adapter path
--------------------------

When Newclid runs through the Yuclid adapter, custom rules are written to a
temporary file and forwarded to the executable with
``--input-additional-rules-file``. This means most integration bugs can be
reproduced by saving the generated problem and custom rule file, then running
Yuclid directly from the command line.

Yuclid Windows and packaging notes
----------------------------------

The custom-rule work also updates build and packaging behavior. Static linking is
disabled by default, Windows Boost discovery can use ``YUCLID_BOOST_DIR``, and
runtime DLLs are installed next to the Yuclid executable when needed. See
:doc:`modules/build_and_packaging` for the developer-facing details.
