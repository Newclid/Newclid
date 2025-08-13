Newclid Predicates
==================

The predicates are the most fundamental blocks of Newclid's language. They correspond to logical statements that can be verified to be true during the proof. In the code, each predicate corresponds to a type in the `predicates/_index.py` file (see :doc:`../../source/newclid.predicate_types`), which links to its corresponding class. Each predicate class will have a `predicate_type` (see :doc:`../../source/newclid.predicate_types`), characterizing its meaning, and a collection of arguments (points, angles, segments, etc.) that are specific to its nature.

In practice, the user has to use the predicates to specify goals and manipulate assumptions of problems. They are also the hypothesis and consequences of rules and proof steps in general, as well as the consequences of constructions and the representations of numerical checks. In a sense, Newclid does not know what is a definition or a rule, only a predicate.


.. list-table::
    :widths: 13 15 34 6 31
    :header-rows: 1

    * - Predicate type
      - Syntax
      - Arguments
      - Only numerical?
      - Meaning
    * - DIFFERENT
      - `diff a b c...`
      - tuple of points - `(a, b, c, ...)`
      - Yes
      - Returns true if all the points `a`, `b`, `c`, ... in the tuple are distinct.
    * - MIDPOINT
      - `midp m a b`
      - segment - `(a, b)`; point - `m`
      - No
      - Corresponds to `m` being the midpoint of the segment from `a` to `b`.
    * - COLLINEAR
      - `coll a b c...`
      - tuple of points - `(a, b, c, ...)`
      - No
      - Corresponds to all the points `a`, `b`, `c`, ... in the tuple being collinear.
    * - N_COLLINEAR
      - `ncoll a b c...`
      - tuple of points - `(a, b, c, ...)`
      - Yes
      - Returns true if at least one of the points `a`, `b`, `c`, ... in not in the same line as the others.
    * - PERPENDICULAR
      - `perp a b c d`
      - lines - `(a, b)` (`line1`);  `(c, d)` (`line2`)
      - No
      - Corresponds to `line1` being perpendicular to `line2`.
    * - N_PERPENDICULAR
      - `nperp a b c d`
      - lines - `(a, b)` (`line1`);  `(c, d)` (`line2`)
      - Yes
      - Returns true if `line1` is not perpendicular to `line2`.
    * - PARALLEL
      - `para a b c d`
      - lines - `(a, b)` (`line1`);  `(c, d)` (`line2`)
      - No
      - Corresponds to `line1` being parallel to `line2`.
    * - N_PARALLEL
      - `npara a b c d`
      - lines - `(a, b)` (`line1`);  `(c, d)` (`line2`)
      - Yes
      - Returns true if `line1` is not parallel to `line2`.
    * - CIRCUMCENTER
      - `circle o a b c`
      - point - `o`; tuple of points - `(a, b, c)`
      - No
      - Corresponds to `o` being the center of a circle through points `a`, `b`, and `c`.
    * - CYCLIC
      - `cyclic a b c d`
      - tuple of points - `(a, b, c, d, ...)`
      - No
      - Corresponds to the all the points `a`, `b`, `c`, `d`, ... lying on the same circle.
    * - CONSTANT_ANGLE
      - `aconst a b c d r`
      - lines - `(a, b)` (`line1`); `(c, d)` (`line2`); fraction - `r`
      - No
      - Corresponds to the counterclockwise angle going from `line1` to `line2` being equal to `r`. `r` can be provided either a fraction of pi like 2pi/3 for radians or a number followed by a 'o' like 120o for degrees.
    * - A_COMPUTE
      - `acompute a b c d`
      - segments - `(a, b)` (`segment1`); `(c, d)` (`segment2`)
      - No
      - Can only be used as a goal, and will return the value `r` of `aconst a b c d r` if it exists in the proof state.
    * - OBTUSE_ANGLE
      - `obtuse_angle a b c`
      - points - `a`, `b`, `c`
      - Yes
      - Returns true is the aangle `abc` is obtuse. It is typically used in the context of collinear points, in which case it returns true if `b` is between `a` and `c`.
    * - EQUAL_ANGLES
      - `eqangle a b c d e f g h`
      - angles - `((a, b), (c, d))` (`angle1`); `((e, f), (g, h))` (`angle2`)
      - No
      - Corresponds to the angles `angle1` and `angle2` being equal in the sense that there is a rigid composition of a translation and a rotation that simultaneously takes line `(a, b)` to line `(e, f)` and line `(c, d)` to line `(g, h)`. It is equivalent to saying that the angles are equal mod pi. This notion of equivalent angles is the most consequential difference between JGEX based logics (like Newclid) and usual Euclidean geometry.
    * - CONSTANT_LENGTH
      - `lconst a b l`
      - segment - `(a, b)`; fraction - `l`
      - No
      - Corresponds to the length of segment `(a, b)` being equal to `l`. `l` should be provided as a float.
    * - L_COMPUTE
      - `lcompute a b`
      - segment - `(a, b)`
      - No
      - Can only be used as a goal, and will return the value `l` of `lconst a b l` if it exists in the proof state.
    * - SQUARED_CONSTANT_LENGTH
      - `l2const a b l`
      - segment - `(a, b)`; fraction - `l`
      - No
      - Corresponds to the squared length of segment `(a, b)` being equal to `l`. `l` should be provided as a float.
    * - CONGRUENT
      - `cong a b c d`
      - segments - `(a, b)` (`segment1`); `(c, d)` (`segment2`)
      - No
      - Corresponds to the segments `segment1` and `segment2` being congruent, meaning they have the same length.
    * - CONSTANT_RATIO
      - `rconst a b c d r`
      - ratio - `((a, b), (c, d))`; fraction - `r`
      - No
      - Corresponds to the ratio of lengths of segments `|ab|/|cd|` being equal to `r`. `r` should be provided as a fraction such as 2/3.
    * - R_COMPUTE
      - `rcompute a b c d`
      - ratio - `((a, b), (c, d))`
      - No
      - Can only be used as a goal, and will return the value `r` of `rconst a b c d r` if it exists in the proof state.
    * - SQUARED_CONSTANT_RATIO
      - `r2const a b c d r`
      - segments - `(a, b)` (`segment1`), `(c, d)` (`segment2`); fraction - `r`
      - No
      - Corresponds to the squared ratio of lengths of segments `|ab|^2/|cd|^2` being equal to `r`. `r` should be provided as a fraction such as 2/3.
    * - EQUAL_RATIOS
      - `eqratio a b c d e f g h`
      - ratios - `((a, b), (c, d))` (`ratio1`); `((e, f), (g, h))` (`ratio2`)
      - No
      - Corresponds to the ratios `ratio1` and `ratio2` being equal.
    * - SIMTRI_CLOCK
      - `simtri a b c p q r`
      - triangles - `(a, b, c)` (`triangle1`); `(p, q, r)` (`triangle2`)
      - No
      - Corresponds to `triangle1` being similar to `triangle2` by an orientation-preserving transformation (no reflections).
    * - SIMTRI_REFLECT
      - `simtrir a b c p q r`
      - triangles - `(a, b, c)` (`triangle1`); `(p, q, r)` (`triangle2`)
      - No
      - Corresponds to `triangle1` being similar to `triangle2` by an orientation-reversing transformation (that is, one reflection is part of the transformation).
    * - CONTRI_CLOCK
      - `contri a b c p q r`
      - triangles - `(a, b, c)` (`triangle1`); `(p, q, r)` (`triangle2`)
      - No
      - Corresponds to `triangle1` being congruent to `triangle2` by an orientation-preserving rigid transformation (no reflections).
    * - CONTRI_REFLECT
      - `contrir a b c p q r`
      - triangles - `(a, b, c)` (`triangle1`); `(p, q, r)` (`triangle2`)
      - No
      - Corresponds to `triangle1` being congruent to `triangle2` by an orientation-reversing rigid transformation (that is, one reflection is part of the transformation).
    * - SAME_CLOCK
      - `sameclock a b c x y z`
      - triangles - `(a, b, c)` (`triangle1`); `(x, y, z)` (`triangle2`)
      - Yes
      - Returns true if the path `a`-> `b`-> `c` has the same orientation as the path `x`-> `y`-> `z`, in the sense that both are a clockwise turn or both are a counterclockwise turn.
    * - SAME_SIDE
      - `sameside a b c x y z`
      - triangles - `(a, b, c)` (`triangle1`); `(x, y, z)` (`triangle2`)
      - Yes
      - Returns true if `a` is in the same kind of arc (the smaller or the larger) of the circumcircle of `triangle1` delimited by `b` and `c` as `x` is in the circumcircle of `triangle2` delimited by `y` and `z`. It admits the degenerate case when either of the circumcircles is a line.
    * - N_SAME_SIDE
      - `nsameside a b c x y z`
      - triangles - `(a, b, c)` (`triangle1`); `(x, y, z)` (`triangle2`)
      - Yes
      - Returns true if `sameside a b c x y z` is false.
    * - PYTHAGOREAN_PREMISES
      - `pythagorean_premises a b c`
      - points - `a`, `b`, `c`
      - No
      - Corresponds to the points `a`, `b`, and `c` being the vertices of a right triangle, with `a` being the right angle. This predicate was created specifically to process r57 and it is added to the proof state either if `ab` is perpendicular to `ac` of if `|ab|^2 + |ac|^2 = |bc|^2` holds. It will be the hypothesis of r57.
    * - PYTHAGOREAN_CONCLUSIONS
      - `pythagorean_conclusions a b c`
      - points - `a`, `b`, `c`
      - No
      - Corresponds to the points `a`, `b`, and `c` being the vertices of a right triangle, with `c` being the right angle. This predicate was created specifically to process r57 and it is added to the proof state either if `ab` is perpendicular to `ac` of if `|ab|^2 + |ac|^2 = |bc|^2` holds. It will be the conclusion of r57.
    * - LENGTH_EQUATION
      - `lequation k1 a1 b1 * a2 b2 * ... * an1 bn1 k2 c1 d1 * c2 d2 * ... * cn2 dn2 ... k`
      - list of fractions - `[k1, k2, ...]`; list of segments - `[(a1, b1),(a2, b2), ...]` (`lengths`); fraction - `k` 
      - No
      - Corresponds to the validity of the equation `k1 * |a1 b1| * |a1 b2| * ... * |an1 bn1| + k2 * |c1 d1| * |c2 d2| * ... * |cn2 dn2| + ... = k`. 
    * - ANGLE_EQUATION
      - `aequation k1 a1 b1 c1 d1 k2 a2 b2 c2 d2 ... k`
      - list of fractions - `[k1, k2, ...]`; list of angles - `[((a1, b1),(c1, d1)), ((a2, b2), (c2, d2)),...]` (`angles`); fraction - `k` 
      - No
      - Corresponds to the validity of the linear equation `k1 * angles[0] + k2 * angles[1] + ... = k`. 
