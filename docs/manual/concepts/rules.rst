Rules
=====

Rules are the geometric theorems that allow the derivation of new facts. Each rule asks for a collection of 'premises' whose points have to be "matched" in the proof state. Next, the rule adds its 'conclusions' to the proof state.

Rules' 'id' field keeps an order (r00 to r92) to keep consistency through sources (documentation. papers, code). The field 'description' gives a more descriptive name, for readability. The naming shows in the proof step, as the reason a proof step is true.

Through development, different combinations of rules have been tried, and some have been abandoned, typically for efficiency considerations. r00 through r42 are the ones from the original AlphaGeometry paper, r43 through r69 were added in the original Newlclid project, and r70 through r92 were added for version 3.0.

As rules are represented by a constant basemodel, we can manage them using lists, see :doc:`../../source/newclid.all_rules`.

This list of rules contains changes in the statements of r03, r07, r09, r26, r34, r35, r36, r37, and r42 if compared to the original AlphaGeometry work. Also, the original r32, r33, r38, r39, and r40 were replaced by new rules on Newclid for rigour.

Legacy rules
------------

r00 : Perpendiculars give parallel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 30 45 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r00|
     - :math:`\begin{cases}AB \perp CD\\ CD \perp EF \\ABE \text{ non-collinear}\end{cases} \implies AB \parallel EF`
     - Two lines AB, EF, that are orthogonal to a same line CD are parallel to one another. **This rule is not in the final rules.txt file because it is covered by AR.**

.. |r00| image:: ../../../../_static/images/rules/r00.png
    :width: 100%



r01 : Definition of circle
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r01|
     - :math:`|OA|=|OB|=|OC|=|OD|\implies ABCD\text{ on a circle}`
     - Four points A, B, C, D equidistant from a center O all lie on a same circle. (One side of the definition of a circle.)

.. |r01| image:: ../../../../_static/images/rules/r01.png
    :width: 100%

r02 : Parallel from inclination
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r02|
     - :math:`\angle (AB \times PQ)=\angle (CD \times PQ)\implies AB \parallel CD`
     - If two lines AB and CD define the same angle with respect to a fixed transverse line PQ, they are parallel. **This rule is not in the final rules.txt file because it is covered by AR.**

.. |r02| image:: ../../../../_static/images/rules/r02.png
    :width: 100%

r03 : Arc determines internal angles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r03|
     - :math:`ABPQ\text{ on a circle}\implies \angle (PA\times PB)=\angle (QA\times QB)`
     - Two angles with the vertices P, Q on a circle that determine the same arc AB on that same circle are congruent.

.. |r03| image:: ../../../../_static/images/rules/r03.png
    :width: 100%

r04 : Congruent angles are in a circle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r04|
     - :math:`\begin{cases}\angle (PA\times PB)=\angle (QA\times QB)\\ ABPQ\text{ non-collinear} \end{cases}\implies ABPQ\text{ on a circle}`
     - Reverse direction of r03: If P, Q are vertices of congruent angles, and A and B are the intersections of the legs of the angles with vertices P and Q, there is a circle through A, B, P, and Q.

.. |r04| image:: ../../../../_static/images/rules/r04.png
    :width: 100%

r05 : Same arc same chord
^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r05|
     - :math:`\begin{cases}ABCPQR\text{ on a circle}\\ \angle (CA\times CB)=\angle (RP\times RQ)\end{cases}\implies |AB|=|PQ|`
     - From r03, two congruent angles on a circle determine arcs on that circle of the same length. This rule says that arcs of the same length determine chords of the same length on the same circle.

.. |r05| image:: ../../../../_static/images/rules/r05.png
    :width: 100%

r06 : Base of half triangle
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r06|
     - :math:`\begin{cases}E\text{ midpoint of } AB\\ F\text{ midpoint of }AC\end{cases} \implies EF \parallel BC`
     - The line connecting the midpoints of two sides of a triangle is parallel to the third side of the same triangle. (This is a special instance of Thales' Theorem with "midpoint" predicates).

.. |r06| image:: ../../../../_static/images/rules/r06.png
    :width: 100%

r07 : Thales Theorem I
^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r07|
     - :math:`\begin{cases}AB\parallel CD\\ OAC \text{ collinear}\\ OBD\text{ collinear}\\ OAB\text{ non-collinear}\end{cases}\implies \begin{cases}\frac{OA}{OC}=\frac{OB}{OD}\\ \frac{AO}{AC}=\frac{BO}{BD}\\ \frac{OC}{AC}=\frac{OD}{BD}\end{cases}`
     - This is an instance of Thales's theorem, saying that two parallel lines AB and CD cut by two intersecting transverse lines AC and BD, will determine a collection of proportional segments. **The original statement of this rule did not have the non-degeneracy condition ncoll O A B as a hypothesis.**

.. |r07| image:: ../../../../_static/images/rules/r07.png
    :width: 100%

r08 : Right triangles common angle I
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r08|
     - :math:`AB \perp CD \wedge EF \perp GH \implies \angle (AB\times EF) = \angle (CD\times GH)`
     - This rule says that if two right triangles share an acute angle, the third angles of both triangles are congruent, as a consequence of the theorem for the sum of angles of a triangle being :math:`180^\circ`. **This rule is not in the final rules.txt file because it is covered by AR.**

.. |r08| image:: ../../../../_static/images/rules/r08.png
    :width: 100%

r09 : Sum of angles of a triangle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r09|
     - :math:`\begin{cases}\angle (AB\times CD)=\angle (MN\times PQ)\\ \angle (CD\times EF)=\angle (PQ\times RU)\end{cases}\implies \angle(AB\times EF)=\angle(MN\times RU)`
     - This rule says that if two triangles have two pairs of congruent angles, the third pair of angles will be congruent as well. It is a non-numerical version of the statement that the angles of a triangle always add to a given constant. **This rule is not in the final rules.txt file because it is covered by AR.**

.. |r09| image:: ../../../../_static/images/rules/r09.png
    :width: 100%

r10 : Ratio cancellation
^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - (Just a multiplication)
     - :math:`\frac{AB}{CD} = \frac{MN}{PQ} \wedge \frac{CD}{EF} = \frac{PQ}{RU} \implies \frac{AB}{EF} = \frac{MN}{RU}`
     - This is a simple algebraic fact: if you multiply the two equalities from the hypothesis together, there will be a cancellation of numerators and denominators giving you the consequence. **This rule is not in the final rules.txt file because it is covered by AR.**

r11 : Bisector theorem I
^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r11|
     - :math:`\begin{cases}\frac{DB}{DC} = \frac{AB}{AC} \\DBC\text{ collinear}\\ ABC\text{ non-collinear} \end{cases}\implies \angle (AB\times AD)=\angle(AD\times AC)`
     - One direction of the bisector theorem: if a line through a vertex of a triangle cuts the opposite side into two segments that are in proportion as the neighboring sides of the triangle, the line bisects the angle at the vertex it cuts.

.. |r11| image:: ../../../../_static/images/rules/r11.png
    :width: 100%

r12 : Bisector theorem II
^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r12|
     - :math:`\begin{cases}\angle (AB\times AD) = \angle (AD\times AC) \\ DBC\text{ collinear}\\ ABC\text{ non-collinear}\end{cases} \implies \frac{DB}{DC} = \frac{AB}{AC}`
     - Opposite direction of the bisector theorem: the internal bisector of a vertex of a triangle divides the opposite side into two segments that are in proportion to the neighboring sides of the triangle.

.. |r12| image:: ../../../../_static/images/rules/r12.png
    :width: 100%

r13 : Isosceles triangle equal angles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r13|
     - :math:`\begin{cases}|OA|=|OB|\\ OAB\text{ non-collinear} \end{cases}\implies \angle (OA\times AB) = \angle (AB\times OB)`
     - The theorem says that the base angles of an isosceles triangle are congruent.

.. |r13| image:: ../../../../_static/images/rules/r13.png
    :width: 100%

r14 : Equal base angles imply isosceles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r14|
     - :math:`\begin{cases}\angle (AO\times AB) = \angle (BA\times BO)\\ OAB\text{ non-collinear}\end{cases} \implies |OA|=|OB|`
     - This is the reverse direction of r13, saying that if the base angles of a triangle are congruent, the triangle is isosceles.

.. |r14| image:: ../../../../_static/images/rules/r14.png
    :width: 100%

r15 : Arc determines inscribed angles (tangent)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r15|
     - :math:`\begin{cases} O\text{ center of circle }ABC \\ OA \perp AX\end{cases} \implies \angle (AX\times AB) = \angle (CA\times CB)`
     - This rule corresponds to r03 in the case the arc is determined by a tangent line. An inscribed angle determining that same arc will be congruent to the angle determining that arc with one leg being the tangent line at the vertex of the arc.

.. |r15| image:: ../../../../_static/images/rules/r15.png
    :width: 100%

r16 : Same arc giving tangent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r16|
     - :math:`\begin{cases} O\text{ center of circle }ABC \\ \angle (AX\times AB)=\angle(CA\times CB)\end{cases} \implies OA\perp AX`
     - Reverse direction of r15: if two angles with vertices on a circle see the same arc, but one vertex is also an extremal point of the arc, a leg of the angle through this extremal point is the tangent to the circle at that same point.

.. |r16| image:: ../../../../_static/images/rules/r16.png
    :width: 100%

r17 : Central angle vs inscribed angle I
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r17|
     - :math:`\begin{cases} O\text{ center of circle }ABC \\ M\text{ midpoint of }BC\end{cases} \implies \angle(AB\times AC)=\angle(OB\times OM)`
     - This rule implies that the central angle doubles the inscribed angle when both determine the same arc in a circle. It mentions "bisects the chord" as an hypotheis instead of "halves the angle" because midpoint of a segment is a predicate, while bisector of an angle is not.

.. |r17| image:: ../../../../_static/images/rules/r17.png
    :width: 100%

r18 : Central angle vs inscribed angle II
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r18|
     - :math:`\begin{cases} O\text{ center of circle }ABC \\ MBC\text{ collinear}\\ \angle(AB\times AC)=\angle(OB\times OM)\end{cases} \implies M\text{ midpoint of }BC`
     - This is the other direction of rule r17. It also has a statement about the bisection of a chord in the circle. Specifically, it says that if a central angle has the same measure as a given inscribed angle on a circle, it will cut the chord corresponding to that angle in half.

.. |r18| image:: ../../../../_static/images/rules/r18.png
    :width: 100%

r19 : Hypotenuse is diameter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r19|
     - :math:`\begin{cases}AB\perp BC \\ M\text{ midpoint of}AC\end{cases} \implies |AM|=|BM|`
     - This rule says that the hypotenuse of a right triangle is a diameter of its circumcircle, or that the midpoint of the hypotenuse is the circumcenter of the right triangle.

.. |r19| image:: ../../../../_static/images/rules/r19.png
    :width: 100%

r20 : Diameter is hypotenuse
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r20|
     - :math:`\begin{cases}O \text{ center of the circle } ABC \\ OAC\text{ collinear} \end{cases}\implies AB \perp BC`
     - This theorem is the reverse direction of r19. It says that if two points are the edges of the diameter of a circle, and at the same time are vertices of an inscribed triangle, the triangle has a right angle at the third vertex.

.. |r20| image:: ../../../../_static/images/rules/r20.png
    :width: 100%

r21 : Cyclic trapezoid
^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r21|
     - :math:`\begin{cases}ABCD\text{ on a circle} \\ AB \parallel CD\end{cases} \implies \angle (AD\times CD) = \angle (CD\times CB)`
     - This rule says that a cyclic trapezoid is isosceles (refering specifically to the congruence of the angles on a base).

.. |r21| image:: ../../../../_static/images/rules/r21.png
    :width: 100%

r22 : Bisector Construction
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r22|
     - :math:`\begin{cases}M \text{ midpoint of }AB \\ OM\perp AB \end{cases} \implies |OA|=|OB|`
     - This rule says that the perpendicular line through the midpoint of the segment is the perpendicular bisector of the segment (the locus of all equidistant points to the vertices of the segment).

.. |r22| image:: ../../../../_static/images/rules/r22.png
    :width: 100%

r23 : Bisector is perpendicular
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r23|
     - :math:`|AP|=|BP| \wedge |AQ|=|BQ| \implies AB\perp PQ`
     - This rule is the reverse direction of r22. It says that the locus of the points that are equidistant to the two vertices of a segment AB is a straight line perpendicular to AB.

.. |r23| image:: ../../../../_static/images/rules/r23.png
    :width: 100%

r24 : Cyclic kite
^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r24|
     - :math:`\begin{cases}|AP|=|BP| \\ |AQ|=|BQ| \\ ABPQ\text{ on a circle}\end{cases} \implies PA\perp AQ`
     - This theorem says that a cyclic kite is always formed by two symmetric right triangles.

.. |r24| image:: ../../../../_static/images/rules/r24.png
    :width: 100%

r25 : Diagonals of parallelogram I
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r25|
     - :math:`\begin{cases}M\text{ midpoint of }AB \\M \text{ midpoint of }CD\end{cases} \implies AC \parallel BD`
     - If two segments intersect at their common midpoint, the vertices of the segments are the vertices of a parallelogram.

.. |r25| image:: ../../../../_static/images/rules/r25.png
    :width: 100%

r26 : Diagonals of parallelogram II
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r26|
     - :math:`\begin{cases}M \text{ midpoint of }AB \\ AC \parallel BD \\ AD \parallel BC\\ ABD\text{ non-collinear} \end{cases}\implies M \text{ midpoint of }CD`
     - The other direction of the previous rule, it says the diagonals of a parallelogram meet at their common midpoint. **The original statement of this rule did not have the non-degeneracy condition ncoll A B D as a hypothesis.**

.. |r26| image:: ../../../../_static/images/rules/r26.png
    :width: 100%

r27 : Thales theorem II
^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r27|
     - :math:`\begin{cases}\frac{OA}{AC}=\frac{OB}{BD}\\ OAC\text{ collinear}\\OBD\text{ collinear}\\ ABC \text{ non-collinear}\\ A\text{ to the same side of }O\to C\text{ as }B\text{ to }O\to D\end{cases}\implies AB\parallel CD`
     - This is another instance of Thales theorem, one saying that if two points C and D split to legs of a triangle on the same ratio, the line CD will be parallel to the base of the triangle.

.. |r27| image:: ../../../../_static/images/rules/r27.png
    :width: 100%

r28 : Overlapping parallels
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r28|
     - :math:`AB \parallel AC \implies ABC\text{ collinear}`
     - This rule encompasses the fact that two intersecting parallel lines are actually the same.

.. |r28| image:: ../../../../_static/images/rules/r28.png
    :width: 100%

r29 : Midpoint is an eqratio
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r29|
     - :math:`\begin{cases} M \text{ midpoint of }AB \\ N\text{ midpoint of } CD \end{cases}\implies \frac{MA}{AB} = \frac{NC}{CD}`
     - This rule exists to help the solver process the fact that is obvious to humans: midpoints split segments in the same ratio (1:2).

.. |r29| image:: ../../../../_static/images/rules/r29.png
    :width: 100%

r30 : Right triangles common angle II
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r30|
     - :math:`\begin{cases}\angle (AB\times PQ)=\angle (CD\times UV) \\ PQ\perp UV \end{cases}\implies AB\perp CD`
     - This rule is the reverse direction of rule r08 (as can be seen by renaming Q->E, P->F, U->H, and V->G), and it is also a consequence of two triangles sharing a same vertex. **This rule is not in the final rules.txt file because it is covered by AR.**

.. |r30| image:: ../../../../_static/images/rules/r30.png
    :width: 100%

r31 : Denominator cancelling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r31|
     - :math:`\frac{AB}{PQ} = \frac{CD}{UV} \wedge |PQ| = |UV| \implies |AB| = |CD|`
     - This rule simply eliminates equal denominators in an equality of ratios. **This rule is not in the final rules.txt file because it is covered by AR.**

.. |r31| image:: ../../../../_static/images/rules/r06.png
    :width: 100%

r32 : SSS Triangle congruence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r32|
     - :math:`\begin{cases}|AB| = |PQ| \\ |BC| = |QR| \\ |CA| = |RP|\end{cases}\implies \Delta ABC\cong^\ast \Delta PQR`
     - This rule covers the congruence case for two triangles when both have corresponding equal sides. The * in the congruence sign denotes the matching function checks both for triangles that have the same vertex orientation and a different one. **This rule has been replaced by rules r64 and r65 to prevent hiding the orientation checking inside the matching funtion.**

.. |r32| image:: ../../../../_static/images/rules/r32.png
    :width: 100%

r33 : SAS Triangle congruence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r33|
     - :math:`\begin{cases}|AB| = |PQ| \\ |BC| = |QR| \\ \angle (BA\times BC) = \angle (QP\times QR)\end{cases}\implies \Delta ABC\cong^\ast\Delta PQR`
     - This rule covers the congruence case for two triangles when both have two corresponding equal sides and an equal angle between them. The * in the congruence sign denotes the matching function checks both for triangles that have the same vertex orientation and a different one. **This rule has been replaced by rules r66 and r67 to prevent hiding the orientation checking inside the matching funtion.**

.. |r33| image:: ../../../../_static/images/rules/r33.png
    :width: 100%

r34 : AA Similarity of triangles (direct)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r34|
     - :math:`\begin{cases}\angle (BA\times BC) = \angle (QP\times QR) \\ \angle (CA\times CB) = \angle (RP\times RQ)\\ \Delta ABC\text{ has the same orientation as }\Delta PQR\end{cases}\implies \Delta ABC\sim \Delta PQR`
     - This is a similarity condition for a pair of triangles: that of two pairs of congruent angles between the triangles (angle-angle similarity). This rule covers the case of direct similarity, that is, both triangles have the same orientation of vertices. **The original statement of this rule did not have the orientation check sameclock A B C P Q R as an explicit hypothesis, it was done in the background.**

.. |r34| image:: ../../../../_static/images/rules/r34.png
    :width: 100%

r35 : AA Similarity of triangles (reverse)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r35|
     - :math:`\begin{cases}\angle (BA\times BC) = \angle (QR\times QP) \\ \angle (CA\times CB) = \angle (RQ\times RP)\\ \Delta ABC\text{ has the same orientation as }\Delta PRQ\end{cases}\implies \Delta ABC\sim^r \Delta PQR`
     - This is a similarity condition for a pair of triangles: that of two pairs of congruent angles between the triangles (angle-angle similarity). This rule covers the case of reverse similarity, that is, the triangles have reversed orientation for the vertices. **The original statement of this rule did not have the orientation check sameclock A B C P R Q as an explicit hypothesis, it was done in the background.**


.. |r35| image:: ../../../../_static/images/rules/r35.png
    :width: 100%

r36 : ASA Congruence of triangles (direct)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r36|
     - :math:`\begin{cases}\angle (BA\times BC) = \angle (QP\times QR) \\ \angle (CA\times CB) = \angle (RP\times RQ)\\ |AB| = |PQ| \\ ABC\text{ non-collinear} \end{cases}\implies \Delta ABC\cong \Delta PQR`
     - This rule covers the congruence case for two triangles when both have two corresponding equal angles and an equal side. This rule covers the case of direct congruence, that is, both triangles have the same orientation of vertices.

.. |r36| image:: ../../../../_static/images/rules/r36.png
    :width: 100%

r37 : ASA Congruence of triangles (reverse)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r37|
     - :math:`\begin{cases}\angle (BA\times BC) = \angle (QP\times QR) \\ \angle (CA\times CB) = \angle (RP\times RQ)\\ |AB| = |PQ| \\ ABC\text{ non-collinear} \end{cases}\implies \Delta ABC\cong^r \Delta PQR`
     - This rule covers the congruence case for two triangles when both have two corresponding equal angles and an equal side. This rule covers the case of reverse congruence, that is, both triangles have the opposite orientation for the vertices.

.. |r37| image:: ../../../../_static/images/rules/r37.png
    :width: 100%

r38 : SSS Triangle similarity (original)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r38|
     - :math:`\begin{cases}\frac{BA}{BC} = \frac{QP}{QR} \\ \frac{CA}{CB} = \frac{RP}{RQ}\\ ABC\text{ non-collinear} \end{cases}\implies \Delta ABC\sim^\ast \Delta PQR`
     - This rule covers the similarity case for two triangles when both have corresponding proportional sides. The * in the similarity sign denotes the matching function checks both for triangles that have the same vertex orientation and a different one. **This rule has been replaced by rules r60 and r61 to prevent hiding the orientation checking inside the matching funtion.**

.. |r38| image:: ../../../../_static/images/rules/r38.png
    :width: 100%

r39 : SAS Triangle similarity (original)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r39|
     - :math:`\begin{cases}\frac{BA}{BC} = \frac{QP}{QR} \\ \angle (BA\times BC)\rangle = \angle (QP\times QR)\\ ABC\text{ non-collinear}\end{cases} \implies \Delta ABC\sim^\ast \Delta PQR`
     - This rule covers the similarity case for two triangles when both have a corresponding pair of proportional sides, with an equal angle between them. The * in the similarity sign denotes the matching function checks both for triangles that have the same vertex orientation and a different one. **This rule has been replaced by rules r62 and r63 to prevent hiding the orientation checking inside the matching funtion.**

.. |r39| image:: ../../../../_static/images/rules/r39.png
    :width: 100%

r40 : Similarity without scaling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r40|
     - :math:`\begin{cases}\frac{BA}{BC} = \frac{QP}{QR} \\ \frac{CA}{CB} = \frac{RP}{RQ}\\ ABC\text{ non-collinear} \\ |AB| = |PQ|\end{cases}\implies \Delta ABC\cong^\ast \Delta PQR`
     - This rule encompasses the fact that if the ratio of similarity of two similar triangles is one (they have corresponding congruent sides), the triangles are congruent. **This rule has been replaced by rules r68 and r69 to prevent hiding the orientation checking inside the matching funtion.**

.. |r40| image:: ../../../../_static/images/rules/r40.png
    :width: 100%

r41 : Thales theorem III
^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r41|
     - :math:`\begin{cases}AB\parallel CD \\ MAD\text{ collinear} \\ NBC \text{ collinear} \\ \frac{MA}{MD}=\frac{NB}{NC}\\ M\text{ to the same side of } A\to D\text{ as }N\text{ to }B\to C \end{cases}\implies MN\parallel A B`
     - This is still another instance of Thales theorem, one that saying that if two transverse lines cross three lines, two of which are parallel, with proportional pairs of segments in the proper configuration, the third line crossed is also parallel to the other two.

.. |r41| image:: ../../../../_static/images/rules/r41.png
    :width: 100%

r42 : Thales theorem IV
^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r42|
     - :math:`\begin{cases}AB\parallel CD \\ MAD\text{ collinear} \\ NBC\text{ collinear}\\ MN\parallel AB\\ ABC\text{ non-collinear}\end{cases}\implies \frac{MA}{MD}=\frac{NB}{NC}`
     - This is probably the most common version of Thales theorem: if three parallel lines are cut by two other lines, there is a corresponding pair of proportional segments determined by the intersection points. It is the other direction of the theorem in rule r41. **The original version of this rule did not contain the non-degeneracy condition ncoll a b c as a hypothesis.**

.. |r42| image:: ../../../../_static/images/rules/r42.png
    :width: 100%

New rules
---------

r43 : Orthocenter theorem
^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r43|
     - :math:`AB\perp CD \wedge AC\perp BD\implies AD\perp BC`
     - This rule says that the three heights of a triangle meet at a single point (the orthocenter).

.. |r43| image:: ../../../../_static/images/rules/r43.png
    :width: 100%

r44 : Pappus's theorem
^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r44|
     - :math:`\begin{cases}ABC\text{ collinear} \\ PQR\text{ collinear} \\ XAQ\text{ collinear}\\ XPB\text{ collinear} \\ YAR\text{ collinear} \\ YPC\text{ collinear}\\ ZBR\text{ collinear} \\ ZCQ\text{ collinear}\end{cases}\implies XYZ\text{ collinear}`
     - This rule is Pappus's hexagon theorem.

.. |r44| image:: ../../../../_static/images/rules/r44.png
    :width: 100%

r45 : Simson's line theorem
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r45|
     - :math:`\begin{cases} ABCP\text{ on a circle} \\ ALC\text{ collinear} \\ PL\perp AC\\ MBC\text{ collinear} \\ PM\perp BC\\ NAB\text{ collinear} \\ PN\perp AB\end{cases}\implies LMN\text{ collinear}`
     - This rule is Simson's line theorem: The orthogonal projections of a point on the circumcircle of a triangle onto its three sides lie on a same line (Simson's line).

.. |r45| image:: ../../../../_static/images/rules/r45.png
    :width: 100%

r46 : Incenter theorem
^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r46|
     - :math:`\begin{cases}\angle(AB\times AX)=\angle (AX\times AC) \\ \angle(BA\times BX)=\angle (BX\times BC)\\ ABC\text{ non-collinear}\end{cases}\implies \angle (CB\times CX)=\angle (CX\times CA)`
     - The three bisectors of a triangle meet at a single point (the incenter).

.. |r46| image:: ../../../../_static/images/rules/r46.png
    :width: 100%

r47 : Circumcenter theorem
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r47|
     - :math:`\begin{cases}M\text{ midpoint of }AB \\ XM\perp AB \\ N\text{ midpoint of }BC\\ XN\perp BC \\ P\text{ midpoint of }CA\end{cases}\implies XP\perp CA`
     - The three perpendicular bisectors of the sides of a triangle meet at a single point (the circumcenter).

.. |r47| image:: ../../../../_static/images/rules/r47.png
    :width: 100%

r48 : Centroid theorem
^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r48|
     - :math:`\begin{cases}M\text{ midpoint of }AB \\ MXC\text{ collinear}\\ N\text{ midpoint of }BC \\ NXC\text{ collinear}\\ P\text{ midpoint of }CA\end{cases}\implies XPB\text{ collinear}`
     - The three medians of a triangle meet at a single point (the centroid).

.. |r48| image:: ../../../../_static/images/rules/r48.png
    :width: 100%

r49 : Recognize center of cyclic (circle)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r49|
     - :math:`\begin{cases}O\text{ center of the circle }ABC \\ABCD\text{ on a circle}\end{cases}\implies OA= OD`
     - This rule gives an information that is immediate for humans, but previously undetected to the solver: if three points lie on a circle with a known center, and there is a fourth point on that circle, the distance of the center of the circle to this fourth point is the same as to other points in a circle.

.. |r49| image:: ../../../../_static/images/rules/r49.png
    :width: 100%

r50 : Recognize center of cyclic (cong)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r50|
     - :math:`\begin{cases}ABCD\text{ on a circle}\\ OA=OB\\ OC=OD\\ AB\not\parallel CD\end{cases}\implies OA=OC`
     - The intersection of the bisectors of two segments of points that lie on a circle is the center of the circle (if the bisectors do not overlap).

.. |r50| image:: ../../../../_static/images/rules/r50.png
    :width: 100%

r51 : Midpoint splits in two
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - (Feeds algebraic module)
     - :math:`M\text{ midpoint of AB}\implies \frac{MA}{AB}=\frac{1}{2}`
     - This rule converts a symbolic statement (M is the midpoint of AB) into an algebraic one (the ratio between AM and AB is 1:2). This allows AR to process information from midpoints.

r52 : Properties of similar triangles (Direct)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r52|
     - :math:`\Delta ABC\sim \Delta PQR\implies \begin{cases}\angle(BA\times BC)=\angle(QP\times QR)\\ \frac{BA}{BC}=\frac{QP}{QR}\end{cases}`
     - This rule was created to explicitate the definition of what a similar triangle is, by going from the pure statement that two triangles are similar to spilling out the corresponding statements about the proportion of the lengths of the sides and the equivalence of angles on both triangles. This rule covers the case where the vertices of both triangles have the same orientation, and is the reverse direction of rule r62.

.. |r52| image:: ../../../../_static/images/rules/r52.png
    :width: 100%

r53 : Properties of similar triangles (Reverse)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r53|
     - :math:`\Delta ABC\sim^r \Delta PQR\implies \begin{cases}\angle(BA\times BC)=\angle(QR\times QP)\\ \frac{BA}{BC}=\frac{QP}{QR}\end{cases}`
     - This rule was created to explicitate the definition of what a similar triangle is, by going from the pure statement that two triangles are similar to spilling out the corresponding statements about the proportion of the lengths of the sides and the equivalence of angles on both triangles. This rule covers the case where the vertices of both triangles have the opposite orientation, and is the reverse direction of rule r63.

.. |r53| image:: ../../../../_static/images/rules/r53.png
    :width: 100%

r54 : Definition of midpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r54|
     - :math:`\begin{cases}MA=MB\\ MAB\text{ collinear}\end{cases}\implies M\text{ midpoint of AB}`
     - This rule was created to detect midpoints by their defining axiomatic properties. It solidifies midp as a predicate.

.. |r54| image:: ../../../../_static/images/rules/r54.png
    :width: 100%

r55 : Properties of midpoint (cong)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r55|
     - :math:`M\text{ midpoint of }AB\implies MA=MB`
     - This rule extracts from the midp predicate the property that the midpoint is equidistant from the extremes of the segment. **This was done previously inside the definition of a midpoint. Our change makes this implication explicit.**

.. |r55| image:: ../../../../_static/images/rules/r55.png
    :width: 100%

r56 : Properties of midpoint (coll)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r56|
     - :math:`M\text{ midpoint of }AB\implies MAB\text{ collinear}`
     - This rule extracts symbolically from the midp predicate the property that the midpoint is on the line of the segment. **This was done previously inside the definition of a midpoint. Our change makes this implication explicit.**

.. |r56| image:: ../../../../_static/images/rules/r56.png
    :width: 100%

r57 : Pythagoras theorem
^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r57|
     - :math:`\begin{array}{c}\Delta ABC\text{ is a right triangle with hypotenuse }BC\\ \Downarrow\\\text{ Missing information from Pythagoras theorem}\end{array}`
     - This rule behaves differently from the others, as both directions of Pythagoras theorem are checked at the same time. If we have a right triangle ABC, it will verify what conditions are already in the proof state. If the proof state symbolically knows the three lengths of the sides, and they satisfy that the sum of the squares of the lengths of the legs is equal to the square of the hypotenuse, it will add the proper orthogonal relation to the proof state. If the proof state has a perpendicular statement and two lengths of sides of the correspoding right triangle, it will add the lconst predicate corresponding to the missing length. The operation does not solve the algebra, it verifies if enough information exists and if that is the case it numerically gets the missing side when using the famous formula. **This rule has been replaced by rules r85 and r86 to agree with changes made to the predicates.**

.. |r57| image:: ../../../../_static/images/rules/r57.png
    :width: 100%

r58 : Same chord same arc I
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r58|
     - :math:`\begin{cases}ABCPQR\text{ on a circle}\\ AB=PQ\\ \Delta CAB\text{ has the same orientation as }\Delta RPQ\\ C\text{ to the same side of }A\to B\text{ as }R\text{ to }P\to Q\end{cases}\implies \angle(CA\times CB)=\angle(RP\times RQ)`
     - This is one of the rules that gives the opposite direction of r05, giving conditions for inscribed angles on a circle defining chords of the same length to have the same measure. It has to consider two different configurations to account for complications of using full angles. The other configuration is given in r59.

.. |r58| image:: ../../../../_static/images/rules/r58.png
    :width: 100%

r59 : Same chord same arc II
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r59|
     - :math:`\begin{cases}ABCPQR\text{ on a circle}\\ AB=PQ\\ \Delta CBA\text{ has the same orientation as }\Delta RPQ\\ C\text{ not to the same side of }A\to B\text{ as }R\text{ to }P\to Q\end{cases}\implies \angle(CA\times CB)=\angle(RP\times RQ)`
     - This is one of the rules that gives the opposite direction of r05, giving conditions for inscribed angles on a circle defining chords of the same length to have the same measure. It has to consider two different configurations to account for complications of using full angles. The other configuration is given in r58.

.. |r59| image:: ../../../../_static/images/rules/r59.png
    :width: 100%

r60 : SSS Similarity of triangles (Direct)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r60|
     - :math:`\begin{cases}\frac{BA}{BC}=\frac{QP}{QR}\\ \frac{CA}{CB}=\frac{RP}{RQ}\\ \Delta ABC\text{ has the same orientation as }\Delta PQR\end{cases}\implies \Delta ABC\sim \Delta PQR`
     - This rule covers the similarity case for two triangles when both have corresponding proportional sides and have the same orientation. **This rule, together with r61, replaces the original r38.**

.. |r60| image:: ../../../../_static/images/rules/r60.png
    :width: 100%

r61 : SSS Similarity of triangles (Reverse)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r61|
     - :math:`\begin{cases}\frac{BA}{BC}=\frac{QP}{QR}\\ \frac{CA}{CB}=\frac{RP}{RQ}\\ \Delta ABC\text{ has the same orientation as }\Delta PRQ\end{cases}\implies \Delta ABC\sim^r \Delta PQR`
     - This rule covers the similarity case for two triangles when both have corresponding proportional sides and have opposite orientations. **This rule, together with r60, replaces the original r38.**

.. |r61| image:: ../../../../_static/images/rules/r61.png
    :width: 100%

r62 : SAS Similarity of triangles (Direct)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r62|
     - :math:`\begin{cases}\frac{BA}{BC}=\frac{QP}{QR}\\ \angle (BA\times BC)=\angle (QP\times QR)\\ \Delta ABC\text{ has the same orientation as }\Delta PQR\end{cases}\implies \Delta ABC\sim \Delta PQR`
     - This rule covers the similarity case for two triangles when both have a corresponding pair of proportional sides, with an equal angle between them, and have the same orientation. **This rule, together with r63, replaces the original r39.**

.. |r62| image:: ../../../../_static/images/rules/r62.png
    :width: 100%

r63 : SAS Similarity of triangles (Reverse)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r63|
     - :math:`\begin{cases}\frac{BA}{BC}=\frac{QP}{QR}\\ \angle (BA\times BC)=\angle (QR\times QP)\\ \Delta ABC\text{ has the same orientation as }\Delta PRQ\end{cases}\implies \Delta ABC\sim^r \Delta PQR`
     - This rule covers the similarity case for two triangles when both have a corresponding pair of proportional sides, with an equal angle between them, and have opposite orientations. **This rule, together with r62, replaces the original r39.**

.. |r63| image:: ../../../../_static/images/rules/r63.png
    :width: 100%

r64 : SSS Congruence of triangles (Direct)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r64|
     - :math:`\begin{cases}AB=PQ\\ BC=QR\\ AC=RP\\ ABC\text{ non-collinear}\\ \Delta ABC\text{ has the same orientation as }\Delta PQR\end{cases}\implies \Delta ABC\cong \Delta PQR`
     - This rule covers the congruence case for two triangles when both have corresponding equal sides, and have the same orientation. **This rule, together with r65, replaces the original r32.**

.. |r64| image:: ../../../../_static/images/rules/r64.png
    :width: 100%

r65 : SSS Congruence of triangles (Reverse)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r65|
     - :math:`\begin{cases}AB=PQ\\ BC=QR\\ AC=RP\\ ABC\text{ non-collinear}\\ \Delta ABC\text{ has the same orientation as }\Delta PRQ\end{cases}\implies \Delta ABC\cong^r \Delta PQR`
     - This rule covers the congruence case for two triangles when both have corresponding equal sides, and have opposite orientations. **This rule, together with r64, replaces the original r32.**

.. |r65| image:: ../../../../_static/images/rules/r65.png
    :width: 100%

r66 : SAS Congruence of triangles (Direct)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r66|
     - :math:`\begin{cases}AB=PQ\\ BC=QR\\ \angle (BA\times BC)=\angle (QP\times QR)\\ ABC\text{ non-collinear}\\ \Delta ABC\text{ has the same orientation as }\Delta PQR\end{cases}\implies \Delta ABC\cong \Delta PQR`
     - This rule covers the congruence case for two triangles when both have a pair of corresponding equal sides, and a congruent angle between them, and have the same orientation. **This rule, together with r67, replaces the original r33.**

.. |r66| image:: ../../../../_static/images/rules/r66.png
    :width: 100%

r67 : SAS Congruence of triangles (Reverse)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r67|
     - :math:`\begin{cases}AB=PQ\\ BC=QR\\ \angle (BA\times BC)=\angle (QP\times QR)\\ ABC\text{ non-collinear}\\ \Delta ABC\text{ has the same orientation as }\Delta PRQ\end{cases}\implies \Delta ABC\cong^r \Delta PQR`
     - This rule covers the congruence case for two triangles when both have a pair of corresponding equal sides, and a congruent angle between them, and have opposite orientations. **This rule, together with r66, replaces the original r33.**

.. |r67| image:: ../../../../_static/images/rules/r67.png
    :width: 100%

r68 : Similarity without scaling (Direct)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r68|
     - :math:`\begin{cases}\frac{AB}{BC}=\frac{PQ}{QR}\\ \frac{AC}{BC}=\frac{PR}{QR}\\ ABC\text{ non-collinear}\\ AB=PQ\\ \Delta ABC\text{ has the same orientation as }\Delta PQR\end{cases}\implies \Delta ABC\cong \Delta PQR`
     - This rule encompasses the fact that if the ratio of similarity of two similar triangles is one (they have corresponding congruent sides), the triangles are congruent. It considers the case when triangles have the same orientation. **This rule, together with r69, replaces the original r40.**

.. |r68| image:: ../../../../_static/images/rules/r68.png
    :width: 100%

r69 : Similarity without scaling (Reverse)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r69|
     - :math:`\begin{cases}\frac{AB}{BC}=\frac{PQ}{QR}\\ \frac{AC}{BC}=\frac{PR}{QR}\\ ABC\text{ non-collinear}\\ AB=PQ\\ \Delta ABC\text{ has the same orientation as }\Delta PRQ\end{cases}\implies \Delta ABC\cong^r \Delta PQR`
     - This rule encompasses the fact that if the ratio of similarity of two similar triangles is one (they have corresponding congruent sides), the triangles are congruent. It considers the case when triangles have opposite orientation. **This rule, together with r68, replaces the original r40.**

.. |r69| image:: ../../../../_static/images/rules/r69.png
    :width: 100%

r70 : Projective harmonic conjugate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r70|
     - :math:`\begin{cases}ALM\text{ collinear}\\ AKN\text{ collinear}\\ BKM\text{ collinear}\\ BLN\text{ collinear}\\ CMN\text{ collinear}\\ DKL\text{ collinear}\\ ABCD\text{ collinear}\end{cases}\implies \frac{AC}{AD}=\frac{BC}{BD}`
     - This rule implements the cross-ratio criterium for the projective harmonic conjugate configuration of four collinear points A, B, C, D.

.. |r70| image:: ../../../../_static/images/rules/r70.png
    :width: 100%

r71 : Resolution of ratios
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r71|
     - :math:`\begin{cases}\frac{AB}{AC}=\frac{DE}{DF}\\ ABC\text{ collinear}\\ DEF\text{ collinear}\\ A\text{ to the same side of }B\to C\text{ as }D\text{ to }E\to F\end{cases}\implies \frac{AB}{BC}=\frac{DE}{EF}`
     - This rule tells that if A splits segment BC to the same proportion as D splits EF, and either both A and D are inside the respective segements, or both are outside, then we can switch the role of A and B, and of D and E in the proportion. This is a fact about proportions that cannot be derived from AR alone because the sameside condition is necessary.

.. |r71| image:: ../../../../_static/images/rules/r71.png
    :width: 100%

r72 : Disassembling a circle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r72|
     - :math:`O\text{ center of circle }ABC\implies \begin{cases}|OA|=|OB|\\ |OB|=|OC|\end{cases}`
     - This rule was created to realize `circle` as an independent predicate, which is not automatically characterized by the center O being equidistant to the three points A, B, C on the circle. 

.. |r72| image:: ../../../../_static/images/rules/r72.png
    :width: 100%

r73 : Definition of a circle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r73|
     - :math:`\begin{cases}|OA|=|OB|\\ |OB|=|OC|\end{cases}\implies O\text{ center of circle }ABC`
     - This is the other direction of rule r72. They were created to realize `circle` as an independent predicate, which is not automatically characterized by the center O being equidistant to the three points A, B, C on the circle. 

.. |r73| image:: ../../../../_static/images/rules/r73.png
    :width: 100%

r74 : Intersection of angle bisector and perpendicular bisector
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r74|
     - :math:`\begin{cases}\angle(CA\times CD)=\angle(CD\times CB)\\ |DA|=|DB|\\ ABCD\text{ not collinear}\\AB\text{ not perpendicular to }CD\end{cases}\implies ABCD\text{ on a circle}`
     - This rule translates an interesting fact about triangles: in triangle ABC, the perpendicular bisector of side AB and the bisector of angle C intersect at a point (D) on the circumcircle of the triangle. 

.. |r74| image:: ../../../../_static/images/rules/r74.png
    :width: 100%


r75 : Equipartition of segments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r75|
     - :math:`\begin{cases}\frac{AB}{AC}=\frac{DE}{DF}\\ ABC\text{ collinear}\\ DEF\text{ collinear}\\ A\text{ to the same side of }B\to C\text{ as }D\text{ to }E\to F\end{cases}\implies \frac{AB}{BC}=\frac{DE}{EF}`
     - **This rule is a repetition of rule r71. Its name is kept only to preserve the numbering of subsequent rules.**

.. |r75| image:: ../../../../_static/images/rules/r75.png
    :width: 100%

r76 : Locate midpoint of hypotenuse
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r76|
     - :math:`\begin{cases}|AM|=|BM|\\BMC\text{ are collinear}\\AB\perp AC\end{cases}\implies M\text{ midpoint of }AB`
     - This rule gives a condition to locate the circumcenter of a right triangle as the point in the hypotenuse that is equidistant to one vertex of the hypothenuse and to the right angle.

.. |r76| image:: ../../../../_static/images/rules/r76.png
    :width: 100%

r77 : Properties of congruent triangles (Direct)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r77|
     - :math:`\Delta ABC \cong \Delta PQR\implies \begin{cases}\Delta ABC \sim \Delta PQR\\ |AB|=|PQ|\end{cases}`
     - This rule implements the condition of congruence of triangles by decomposing it into a triangle similarity and the congruence of a respective pair of angles, when there is no reflection in the similarity.

.. |r77| image:: ../../../../_static/images/rules/r77.png
    :width: 100%

r78 : Properties of congruent triangles (Reverse)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r78|
     - :math:`\Delta ABC \cong^r \Delta PQR\implies \begin{cases}\Delta ABC \sim^r \Delta PQR\\ |AB|=|PQ|\end{cases}`
     - This rule implements the condition of congruence of triangles by decomposing it into a triangle similarity and the congruence of a respective pair of angles, this time when there is a reflection in the similarity.

.. |r78| image:: ../../../../_static/images/rules/r78.png
    :width: 100%

r79 : Divide congruence equation by segment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - (Equivalent to a multiplication by 1)
     - :math:`\begin{cases}|AB|=|CD|\\X\neq Y\\A\neq B\\C\neq D\end{cases}\implies \frac{AB}{XY}=\frac{CD}{XY}`
     - This rule was created to supply a deficiency of AR at the time, which would not consider segments that were not explicitly added to the tables through some predicate implementation. Because of that, trivial facts, like the ones in the consequence of the theorem, would not be considered when XY was not part of a congruence or equivalence of ratios relation known to the engine beforehand.

r80 : Same chord same arc III
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r80|
     - :math:`\begin{cases}ABPQ\text{ on a circle}\\ |AB|=|PQ|\\ AP\text{ not parallel to }BQ\end{cases}\implies \angle(PA\times PB)=\angle(PB\times QB)`
     - This rule implements a special case of rules r58 and r59, where instead of two separate triangles along the circle, they are joined into a quadrilateral, with the vertex of each angle being an extremity of the other angle's chord. It is one case of the reverse direction of r05, the other being given by r81.

.. |r80| image:: ../../../../_static/images/rules/r80.png
    :width: 100%

r81 : Same chord same arc IV
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r81|
     - :math:`\begin{cases}ABPQ\text{ on a circle}\\ |AB|=|PQ|\\ \Delta APB\text{ has the same orientation as }\Delta APQ\end{cases}\implies \angle(PA\times PB)=\angle(QB\times PB)`
     - This is the other case of the reverse direction of rule r05 for the coincidence of angles determining congruent chords on a circle, the first case being r80.

.. |r81| image:: ../../../../_static/images/rules/r81.png
    :width: 100%

r82 : Parallel from collinear
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r82|
     - :math:`ABC\text{ collinear}\implies \begin{cases}AB\parallel BC\\ AB\parallel AC\end{cases}`
     - This is the reverse direction of rule r28. It is a trivial fact that is derived by engine automatically, but was necessary for the bridge with the C++ Yuclid engine.

.. |r82| image:: ../../../../_static/images/rules/r82.png
    :width: 100%

r83 : Between condition I
^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r83|
     - :math:`\begin{cases}ABC\text{ collinear}\\ \angle(ABC)\text{ is obtuse}\end{cases}\implies |AB|+|BC|-|AC|=0`
     - This rule translates the condition of a point C being between two other points A, B into an equation that can be fed to the AR module.

.. |r83| image:: ../../../../_static/images/rules/r83.png
    :width: 100%

r84 : Between condition II
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r84|
     - :math:`|AB|+|BC|-|AC|=0\implies ABC\text{ collinear}`
     - This rule is the reverse direction of rule r83, which is equivalent to the critical case of the triangle inequality. We don't need to provide the obtuse angle condition because it is generally obtained from a numerical check.

.. |r84| image:: ../../../../_static/images/rules/r84.png
    :width: 100%

r85 : Generalized Pythagorean theorem I
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r85|
     - :math:`AB\perp CD\implies |AC|^2+|BD|^2-|AD|^2-|BC|^2=0`
     - This rule is the first direction of a generalized version of the Pythagorean theorem, characterizing the perpendicularity between two lines without demanding the intersection point between them. It replaces former rule r57.

.. |r85| image:: ../../../../_static/images/rules/r85.png
    :width: 100%

r86 : Generalized Pythagorean theorem II
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r86|
     - :math:`\begin{cases}|AC|^2+|BD|^2-|AD|^2-|BC|^2=0\\ ABC\text{ not collinear}\end{cases}\implies AB\perp CD`
     - This rule is the reversed direction of rule r85, a generalized version of the Pythagorean theorem, characterizing the perpendicularity between two lines without demanding the intersection point between them. It replaces former rule r57.

.. |r86| image:: ../../../../_static/images/rules/r86.png
    :width: 100%

r87 : Characterization of circumcenter I
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r87|
     - :math:`\begin{cases}|OA|=|OC|\\ \angle(AB \times BC)+\angle(AC \times AO)=90^\circ\end{cases}\implies O\text{ center of circle }ABC`
     - This rule gives a characterization of the circumcenter O of a triangle ABC using a linear equation on angles of the quadrilateral ABCO.

.. |r87| image:: ../../../../_static/images/rules/r87.png
    :width: 100%

r88 : Characterization of circumcenter II
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r88|
     - :math:`O\text{ center of circle }ABC\implies \angle(AB \times BC)+\angle(AC \times AO)=90^\circ`
     - This rule is the reverse direction of rule r87, giving a characterization of the circumcenter O of a triangle ABC using a linear equation on angles of the quadrilateral ABCO.

.. |r88| image:: ../../../../_static/images/rules/r88.png
    :width: 100%

r89 : Length of a median of a triangle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r89|
     - :math:`\begin{cases}M\text{ midpoint of }AB\\ ABC\text{ not collinear}\end{cases}\implies 2|AM|^2-2|BC|^2-2|AC|^2+|AB|^2=0`
     - This rule gives a formula for the length of the median AM of triangle ABC with respect to the sides of the triangle.

.. |r89| image:: ../../../../_static/images/rules/r89.png
    :width: 100%

r90 : Parallelogram law
^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r90|
     - :math:`\begin{cases}AB\parallel CD\\ AD\parallel BC\\ ABC\text{ not collinear}\end{cases}\implies 2|AB|^2+2|BC|^2-|AC|^2-|BD|^2=0`
     - This rule gives the parallelogram law for lengths: the sum of the squares of the lengths of the sides of a parallelogram is equal to the sum of the squares of the lengths of the diagonals.

.. |r90| image:: ../../../../_static/images/rules/r90.png
    :width: 100%

r91 : Equal angles in an isosceles trapezoid
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r91|
     - :math:`\begin{cases}|AB|= |CD|\\ AD\parallel BC\\ AB\text{ not parallel to }CD\end{cases}\implies \angle (CA\times CB)=\angle (CB\times BD)`
     - This simple rule that gives the equality of the angles at the bases of an isosceles trapezoid was suggested by the discovery by Harmonic's artificial intelligence agent that very simple problems with isosceles trapezoids always demanded auxiliary points to be solved. This rule prevents that need in a lot of small problems by providing a simple fact that was unreacheable to the engine before.

.. |r91| image:: ../../../../_static/images/rules/r91.png
    :width: 100%

r92 : Any diameter of a circle crosses the center
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. list-table::
   :widths: 50 25 25
   :header-rows: 1

   * - Figure
     - Formal Statement
     - Description
   * - |r92|
     - :math:`\begin{cases}O\text{ midpoint of } AB\\ O\text{ center of circle }ABC\\ ABCD\text{ on a circle}\\ |AB|=|CD|\end{cases}\implies OCD\text{ collinear}`
     - This simple rule tells that if a chord of a circle is congruent to a diameter of the circle, it has to cross the center. This is a very simple geometric fact that was found to be unknown to the engine until the addition of this rule.

.. |r92| image:: ../../../../_static/images/rules/r92.png
    :width: 100%