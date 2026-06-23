Yuclid predicate providers
==========================

Predicate providers are the main extension point for making generic matching
fast. A provider knows how to estimate, generate, and verify mappings for one
predicate family.

Yuclid provider interface
-------------------------

A provider implements three responsibilities:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Method
     - Responsibility
   * - ``estimate_extensions``
     - Estimate how many candidate extensions this predicate can generate from the current mapping.
   * - ``generate_extensions``
     - Lazily yield candidate variable-to-point assignments.
   * - ``is_satisfied``
     - Check whether a fully bound mapping satisfies the predicate.

Yuclid base provider
--------------------

The base provider is the fallback. It enumerates assignments for unbound
variables and uses statement construction plus numerical checking to verify a
predicate. It is useful for completeness, but it is not selective enough for
large problems.

Yuclid congruence provider
--------------------------

The congruence provider handles predicates of the form:

.. code-block:: text

   cong A B C D

It uses segment-length buckets from the lazy geometry cache. If one segment is
already assigned, the provider can look up the matching length bucket directly.
If only anchor points are known, it searches segments touching those anchors. If
nothing is known, it enumerates pairs inside equal-length buckets instead of all
point quadruples.

Yuclid provider extension rule
------------------------------

Add a provider when a predicate can supply selective candidates from geometry
indexes. Keep the provider focused on one predicate family, and keep shared
precomputed geometry in ``LazyGeometryCache`` rather than rebuilding it inside
the provider.
