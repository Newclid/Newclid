Adding new rules
----------------

Rules (represented by :ref:`Rule`) allow to create new statements
given that a list of other statements are true.

In geosolver, statements are expressed as a predicate and a list of points.
The list of predicates used by Newclid are enumerated in :ref:`Predicates`.

Rules can be initialized from a text representation as such:

::

   perp A B C D, perp C D E F, ncoll A B E => para A B E F


Where `perp`, `ncoll` and `para` are predicates found at :ref:`Predicates`.
`A`, `B`, `C`, `D`, `E`, `F` are arguments of the rule representing points.

The default rules used can be found in ``default_configs/rules.txt`` as an example.

