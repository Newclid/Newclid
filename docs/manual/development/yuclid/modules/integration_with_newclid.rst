Yuclid integration with Newclid
===============================

The Newclid/Yuclid integration lets Newclid register additional rules and lets
Yuclid return deductions that reference those custom rules.

Yuclid adapter custom rules
---------------------------

The Python ``YuclidAdapter`` stores optional custom rules for the current run. If
custom rules are present, the adapter writes them to a temporary file and passes
that file to the Yuclid executable with ``--input-additional-rules-file``.

Yuclid adapter rule serialization
---------------------------------

Each Newclid ``Rule`` is serialized into the Yuclid custom rule format:

.. code-block:: text

   rule <id> <variables...>
   require <predicate> <args...>
   conclude <predicate> <args...>
   end

The adapter writes only the transport format. Yuclid still parses and validates
the rule file on the C++ side.

Yuclid deduction mapping back to Newclid
----------------------------------------

When Yuclid returns a rule deduction, the adapter uses an extended rule lookup:
standard Yuclid-backed rules plus the custom rules for this run. That allows
custom-rule deductions to become normal Newclid cached rule deductions.

Yuclid related Newclid API changes
----------------------------------

The Newclid solver builder can register additional rules. It forwards rules that
are not part of the standard rule library to the Yuclid adapter. Proof section
signatures are also exposed so downstream consumers can identify construction,
step, and goal predicates more easily.
