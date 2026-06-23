Yuclid theorem candidate validation
===================================

Generic matching produces theorem candidates. It does not directly prove that a
candidate should be accepted by the solver.

Yuclid validation boundary
--------------------------

The matcher is responsible for finding mappings that satisfy the schema
premises. The theorem builder constructs candidate premises and conclusions from
that mapping. The existing theorem insertion and validation path is still
responsible for deciding whether the candidate is accepted.

Yuclid candidate rejection reasons
----------------------------------

A candidate can be rejected because:

- a provider generated a mapping that passes local checks but fails a full statement check;
- a conclusion is degenerate;
- the theorem duplicates an existing theorem;
- the theorem does not satisfy the normal Yuclid theorem invariants;
- a rule schema is syntactically valid but semantically unhelpful for the problem.

Yuclid validation design rule
-----------------------------

Do not weaken final validation to make generic matching accept more candidates.
If a valid custom rule produces no accepted theorem, debug parsing, mapping,
provider generation, and theorem construction first.
