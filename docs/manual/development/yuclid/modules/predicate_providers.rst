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

Yuclid provider mental model
----------------------------

A provider is not just a predicate checker. It is a **candidate supplier** for
one predicate family. During matching, the current mapping may already bind some
rule variables to problem points. The provider uses that partial information to
suggest only the missing assignments that can still satisfy the predicate.

For example, for ``cong A B C D``:

- if no variables are assigned, the provider can generate equal-length segment pairs;
- if ``A`` and ``B`` are assigned, the provider only needs segments with the same length as ``AB``;
- if ``A`` is assigned, the provider only considers segments touching the point mapped to ``A`` as one side of the congruence;
- if all variables are assigned, the provider only checks whether the congruence is satisfied.

This is how providers reduce the search space. They avoid trying mappings that
are definitely wrong for the current predicate, while still preserving mappings
that may lead to a valid theorem candidate.

Yuclid provider methods during search
-------------------------------------

The generic matcher uses provider methods at different moments:

.. list-table::
   :widths: 28 34 38
   :header-rows: 1

   * - Method
     - Called when
     - Purpose
   * - ``estimate_extensions``
     - Planning or choosing the next predicate under a partial mapping.
     - Prefer predicates that are expected to generate fewer branches.
   * - ``generate_extensions``
     - The matcher decides to expand the search using this predicate.
     - Yield candidate assignments for currently unbound variables.
   * - ``is_satisfied``
     - The predicate is fully bound or used as a check-only filter.
     - Reject mappings that do not satisfy the predicate.

The estimate does not need to be exact. It should be good enough to avoid obvious
bad ordering decisions, such as expanding a fallback enumeration before a highly
selective indexed predicate.

Yuclid base provider behavior
-----------------------------

The base provider keeps the matcher general. It can enumerate assignments for
predicates that do not yet have a specialized provider, then check the predicate
through statement construction and numerical validation.

That fallback is useful, but it is expensive. It can become a partial
permutation over many free points. Use it for correctness and unsupported cases,
not as the intended fast path for common selective predicates.

Yuclid congruence provider pruning cases
----------------------------------------

``CongProvider`` specializes ``cong A B C D`` by using the segment-length cache
and the current assignment mask. It tries to cut away impossible mappings before
they become full candidate mappings.

.. list-table::
   :widths: 28 36 36
   :header-rows: 1

   * - Current state
     - What the provider knows
     - How it prunes
   * - All four points assigned
     - Both segments are concrete.
     - It checks the two lengths directly and yields no extensions.
   * - One whole segment assigned
     - The target length is known.
     - It looks up only the matching length bucket instead of trying all point pairs.
   * - Three points assigned
     - The length and one endpoint of the other segment are known.
     - It only tries segments in the matching bucket that touch the known endpoint.
   * - One anchor point assigned
     - One endpoint of one segment is known but the length is unknown.
     - It scans length buckets for segments touching the anchor and pairs them with same-bucket segments.
   * - Two independent anchor points assigned
     - One endpoint from each segment is known.
     - It only combines same-bucket segments touching the respective anchors.
   * - No points assigned
     - No concrete length is known.
     - It enumerates pairs inside equal-length buckets instead of all point quadruples.

The provider also checks duplicate-variable aliases. If two predicate positions
use the same rule variable, the generated mapping must assign those positions to
the same point. If they use different variables, the mapping should not collapse
them into the same point unless the schema explicitly requires that aliasing.

Yuclid provider correctness rule
--------------------------------

A provider may generate too many candidates, but it must not silently drop valid
ones. The safe pruning rule is:

.. code-block:: text

   Reject a candidate early only when the predicate makes it definitely impossible.

Examples of safe pruning include:

- excluding a segment from a ``cong`` candidate when its length bucket cannot match the known segment length;
- excluding a segment that does not touch a required anchor point;
- rejecting a mapping that violates duplicate-variable equality;
- rejecting a fully assigned predicate that fails the predicate's numerical check.

If a check depends on broader theorem validity, leave it to theorem candidate
validation rather than encoding it inside the provider.

Yuclid provider performance rule
--------------------------------

Provider code should avoid rebuilding global geometry structures inside
``generate_extensions``. If a provider needs all point pairs, length buckets,
line groups, or direction buckets, add that structure to ``LazyGeometryCache``
and make the provider request it. This keeps repeated matching branches from
paying the same setup cost again and again.
