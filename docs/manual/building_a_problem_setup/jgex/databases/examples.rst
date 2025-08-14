examples
========

This miscelaneous file of problems contains straightforward problems used to test the engine, test new features, check if the reasoner knows basic geometry facts and theorems, as well as larger problems that were used to see the engine's overall capabilities. It started with the first four problems (orthocenter, orthocenter_aux, incenter_excenter, euler), released as examples with the original AlphaGeometry codebase, and was expanded during the process of getting to know and enhancing the capabilities of the engine. Most of them are simple, straightforward problems, meant to check one very specific theorem, rule or behavior, and should run quickly. That is not always the case though.

A more detailed crackdown of the problems is shown in the table below.

.. list-table::
    :widths: 20 30 30 10 10
    :header-rows: 1

    * - Problem Name
      - Description
      - Justification
      - Solved w/ original DDAR?
      - Solved w/ Newclid?
    * - orthocenter
      - Given a triangle ABC, and H the intersection of the heights relative to vertices B and C, H is also in the height relative to vertex A.
      - One of the original problems. It needs an auxiliary point to be solved, and could be solved by the original DDAR+LLM combination.
      - No
      - No
    * - orthocenter_aux
      - Given a triangle ABC, and D the intersection of the heights relative to vertices B and C, and E the foot of the height with respect to B, D is also in the height relative to vertex A.
      - One of the original problems. It is the orthocenter problem with the auxiliary point needed for a pure DDAR solution prescribed.
      - Yes
      - Yes
    * - incenter_excenter
      - Given a triangle ABC, with incenter D and excenter E, center of a circle externally tangent to the side BC, the lines CD and CE are perpendicular.
      - One of the original problems.
      - 
      - Yes
    * - euler
      - In a triangle ABC with orthocenter H, centroid G, and circumcenter O, the points H, G, and O are collinear.
      - One of the original problems.
      - 
      - Yes
    * - pappus
      - 
      - A straight application of Pappus hexagon's theorem. It was created to first check if the engine could originally prove this theorem (it could not), and then to see if we could add Pappus theorem as a rule.
      - No
      - No
    * - orthocenter_consequence
      - 
      - A trivial consequence of the result of the orthocenter problem, created to test the dependency graph and see how it changes when a new rule (the orthocenter theorem) was added, the first one to be successfully added. It still lacks the auxiliary point needed for a simple DDAR/Newclid solution, but it can be solved with the assistance of the LLM.
      - No
      - No
    * - orthocenter_consequence_aux
      - 
      - The previous orthocenter_consequence problem, but now with the auxiliary point necessary for a pure DDAR solution prescribed.
      - Yes
      - Yes
    * - imo_2004_p1
      - 
      - The statement of problem 1 from the IMO 2004 exam, added the auxiliary points prescribed by the LLM as mentioned in the original paper. This problem was brought to the examples so we had a "bigger" problem to test the engine against, with more complexity. This problem is also discussed in the original paper as one that could be generalized by AlphaGeometry.
      - Yes
      - Yes
    * - imo_2004_p1_generalized
      - 
      - This is the statement of imo_2004_p1 with the generalization of point O as proposed in the original AlphaGeometry paper. This generalization should allow for the solution to be found only in a fraction of the sample space allowed for O, and to investigate this phenomenon better we created the simpler not_always_good problem below.
      - 
      - Yes
    * - not_always_good
      - 
      - A smaller version of the problem imo_2004_p1_generalized, for faster testing, that is not true for all choices of the free point O. It revealed that the building routine for problems will check the goal, erase the construction in case it is not met, and try new random attributions until finding a good one. This could result in an infinite loop, so we introduced a limit to the number of trials.
      - 
      - Yes
    * - rule_r29_not_found_disguise
      - 
      - This was the first problem created to find single applications of rules. It tried to be something that would be solved by a single application of rule r29, but the original engine did not even use the rule, resorting to AR and implicit rules instead. This problem proved that trying to predict the engine's proofs was to be a very hard task, if possible at all. A second trial was made with rule_29_not_found_explicit below, using a notation closer to the one in the statement of r29 itself.
      - Yes
      - Yes
    * - rule_r29_not_found_explicit
      - 
      - This was a second trial to build a single application of rule r29. Differently from rule_29_not_found_disguise, this problem tries to replicate the setting and notation of the rule statement exactly, with two independent segments AB and CD and their midpoints only. The solution found by the original engine did use rule r29, but also other steps involving non-stated rules.
      - Yes
      - Yes
    * - find_r22
      - 
      - This problem was created to be a one-shot test for rule r22, in the sense that the solution should be a single application of the rule. When ran, it ended up revealing a hidden process: originally the definition of midpoint would not give a midp predicate, so the first step of the proof was actually re-deducing that M was the midpoint of AB.
      - Yes
      - Yes
    * - two_paths_problem_aux
      - 
      - This problem and the one below were created as problems that could get their solution from two different reasoning paths, hoping this could be reflected in the version of the dependency graph we had running at the time. The auxiliary point when compared to two_paths_problem below reinforces the possibility of the problem having two possible solutions. Indeed, the superfluous point changes the proof written.
      - 
      - Yes
    * - two_paths_problem
      - 
      - This problem was created as a problem that could get their solution from two different reasoning paths, hoping this could be reflected in the version of the dependency graph we had running at the time.
      - 
      - Yes
    * - b23_may_need_BUILT_IN_FNS
      - 
      - The original engine had special matching functions for a subset of the rules, listed in a list called BUILT_In_FNS. We wanted to know if those functions were strictly necessary for the working of the engine, so we tried running problems with the access to that list enabled and disabled. This problem suggested that r10 needed the special function to be used.
      - 
      - Yes
    * - ratio_chase_incorrect_on_step_one
      - 
      - This problem was found trying to come up with the problem forcing_ratio below. The proof produced had a mistake, due to a wrongly defined function in the AR module. We later found out that this bug had been recognized as a bug in the public alphageometry repository on GitHub.
      - 
      - Yes
    * - forcing_ratio
      - 
      - This problem was created to check if the original rconst predicate was functional. Its only ocurrence was in the definition triangle12, it was unstable and it could not be used as a goal.
      - 
      - Yes
    * - check_r00
      - 
      - This problem was created as a initial step of a systematic attempt to check one-shot functioning of all the original 43 rules from alphageometry. Later, this would become the testing_minimal_rules.txt problem file. This problem specifically showed that the original engine defaulted to replacing r00 by intrinsic rules.
      - 
      - Yes
    * - angles_in_triangle
      - 
      - This is part of a series of problems created to check the capabilites of the original AlphaGeometry engine when it came to angle chasing. It is supposed to check if it can find the third angle of a triangle given the other two, but the goal had to ask for a 90o angle because that could be stated as a perp statement, the software originally could not treat aconst or s_angle as full predicates.
      - Yes
      - Yes
    * - testing_aline0
      - (Verification problem) Given points A, B, C, D, E, F, G, if H is built in a way that the angle between EF and GH is equal to the angle between AB and CD, than we have the equality of the angles between AB and CD and between EF and GH.
      - This problem was created to check the definition on_aline0 we introduced was working properly.
      - No
      - Yes
    * - testing_iso_triangle_vertex_angle
      - 
      - This problem was created to check the definition iso_triangle_vertex_angle we introduced was working properly.
      - No
      - Yes
    * - angles_eq_triangle
      - An internal angle of an equilateral triangle is 60o.
      - This is part of a sequence of problems created to check the capabilities of the original AlphaGeometry engine when it came to angle chasing. The fact that it could solve this problem, for example, showed its ability to recognize (even indirectly) that the sum of the angles of a triangle was 180o and to actually use the system to find the numerical value of an angle it didn't know before. The question could not be posed on the original AlphaGeometry, though, as aconst did not have full capabilities as a predicate.
      - No
      - Yes
    * - angles_double_eq_triangle
      - 
      - This problem was meant to check if the algebra module could somehow sum the values of two adjacent angles even if it had to find their values by itself, knowing it could find each value due to the solution of the angles_eq_triangle problem. The question could not be posed to the original AlphaGeometry, as aconst did not have full capabilities as a predicate.
      - No
      - Yes
    * - suplementary_angles
      - If an angle between two lines is 30o, the other angle between the same lines is 150o.
      - This problem was meant to check in a very straightforward way if the algebra engine could find the value of the angle supplementary to a given one (it actually generated both angles in the symbols graph at instantiation). The question could not be posed to the original AlphaGeometry, as aconst did not have full capabilities as a predicate.
      - No
      - Yes
    * - square_side
      - 
      - This is part of a series of problems trying to investigate the capacity of the engine to develop an extended reasoning made of small steps, namely to prove that the first and last sides provided in a construction of a polygon are congruent. The solution for a square is too simple to need a complex line of reasoning.
      - 
      - Yes
    * - square_angle
      - 
      - This is part of a series of problems trying to investigate the capacity of the engine to develop an extended reasoning made of small steps, namely to prove that the first and last angles provided in a construction of a polygon are congruent. The solution for a square is too simple to need a complex line of reasoning.
      - 
      - Yes
    * - regular_pentagon_side
      - 
      - This is part of a series of problems trying to investigate the capacity of the engine to develop an extended reasoning made of small steps, namely to prove that the first and last sides provided in a construction of a polygon are congruent. The solution for a pentagon can be done, but it starts to take a long time. Also, following the proof pictures throughout the reasoning one can see that information is actually being gathered from the starting angle ABC and moves towards the last one EAB.
      - 
      - Yes
    * - regular_pentagon_angle
      - 
      - This is part of a series of problems trying to investigate the capacity of the engine to develop an extended reasoning made of small steps, namely to prove that the first and last angles provided in a construction of a polygon are congruent. The solution for a pentagon can be done, but it takes very long. Also, following the proof pictures throughout the reasoning one can see that information is actually being gathered from the starting angle ABC and moves towards the last one EAB.
      - 
      - Yes
    * - regular_hexagon_side
      - 
      - This is part of a series of problems trying to investigate the capacity of the engine to develop an extended reasoning made of small steps, namely to prove that the first and last sides provided in a construction of a polygon are congruent. The original engine could not find all the equilateral triangles in an hexagon at first, and this problem showed the lack of knowledge of the engine when it came to circles, which led to the insertion of rule r49.
      - 
      - Yes
    * - regular_hexagon_angle
      - 
      - This is part of a series of problems trying to investigate the capacity of the engine to develop an extended reasoning made of small steps, namely to prove that the first and last angle provided in a construction of a polygon are congruent. This problem was long enough to timeout the initial engine, although we could guide a solution with the human agent in less than 80 steps, proving the inefficiency of the breadth-first search algorithm. The time was made manageable with the introduction of the caching mechanism and our new engine can solve it automatically as well.
      - No
      - Yes
    * - regular_triangle_side
      - 
      - This is part of a series of problems trying to investigate the capacity of the engine to develop an extended reasoning made of small steps, namely to prove that the first and last sides provided in a construction of a polygon are congruent. The case of the regular triangle is very easy for the engine, and was added for completion.
      - 
      - Yes
    * - worlds_hardest_easy_geometry_problem1
      - 
      - In checking the ability of the engine to perform angle chasing, we implemented the "world's hardest easy geometry problems", proposed by Keith Enevoldsen. The questions could not be posed to the original engine due to the malfunction of the aconst predicate, but even the new engine is incapable of solving the problems without auxiliary points.
      - No
      - No
    * - worlds_hardest_easy_geometry_problem1_with_construction
      - 
      - In checking the ability of the engine to perform angle chasing, we implemented the "world's hardest easy geometry problems", proposed by Keith Enevoldsen. The questions could not be posed to the original engine due to the malfunction of the aconst predicate. The new engine can solve the first problem with an auxiliary point provided by a human.
      - No
      - Yes
    * - worlds_hardest_easy_geometry_problem2
      - 
      - In checking the ability of the engine to perform angle chasing, we implemented the "world's hardest easy geometry problems", proposed by Keith Enevoldsen. The questions could not be posed to the original engine due to the malfunction of the aconst predicate, but even the new engine is incapable of solving the problems without auxiliary points.
      - 
      - No
    * - geometric_ratios
      - 
      - This problem was created to check the effectiveness of ratio chase with the recently fixed rconst predicate, when it should be obtained from purely geometric constructions (midpoint).
      - 
      - Yes
    * - concatenating_ratios
      - 
      - This problem was created to check the effecticeness of ratio chase with the recently fixed rconst predicate, with a statement that involves prescribing ratios with rconst itself.
      - 
      - Yes
    * - ar_example_paper_angle_chasing
      - 
      - This problem was given in the original AlphaGeometry paper in Extended Data Table 2 as an example of the functioning of angle chasing as done by AR. The actual proof provided by DDAR diverged a little from the one presented in the paper, but it could still solve the problem.
      - 
      - Yes
    * - ar_example_paper_distance_chasing
      - 
      - This problem was given in the original AlphaGeometry paper in Extended Data Table 2 as an example of the functioning of distance chasing as done by AR. When examining the code we found no evidence that the procedure described in the paper could be done, and running the problem with DDAR revealed the engine could not actually solve the problem given.
      - No
      - Yes
    * - ar_example_paper_ratio_chasing
      - 
      - This problem was given in the original AlphaGeometry paper in Extended Data Table 2 as an example of the functioning of angle chasing as done by AR. The actual proof provided by DDAR does not look like the one presented in the paper, but it could still solve the problem.
      - 
      - Yes
    * - test_get_two_intersections
      - Given a segment AB, if C and D are the two intersections of the circle of center A and radius AB and of the circle of center B and radius AB, AB is perpendicular to CD.
      - This problem was created to check the behavior of the builder when two points were prescribed with the same description (the two intersections of a pair of circles). It shows the choice of intersections will be made at random, but without points overlapping, and this procedure only checks the numerical structure, it doesn't matter if two points are symbolically the same.
      - 
      - Yes
    * - ar_two_triangles_angle_chasing
      - 
      - This problem was created to check the effectiveness of angle chasing across two adjacent triangles, using arbitraty prescription of angles (s_angle). Compare to angles_double_eq_triangle for a more rigid version of the problem.
      - 
      - Yes
    * - ar_three_triangles_angle_chasing
      - 
      - This problem was created to check the effectiveness of angle chasing across three neighboring triangles, using arbitrary prescription of angles (s_angle).
      - 
      - Yes
    * - cong2_problem
      - 
      - This problem was created as an attempt to investigate the functioning of the then existing cong2 predicate, that seemed related to the functioning of the AR module.
      - 
      - Yes
    * - point_on_circle_eqdistant_from_center
      - Given a triangle ABC (three points), D a point added that is concyclic to ABC, and O the circumcenter of ABC, the distance from D to O is the same as the distance from A to O.
      - This problem was created as a straightforward test for the need of r49. Namely it verified that the original engine could not prove that by adding a point to a circle, its distance to the center would be the same as the distance from any of the other points to the center.
      - No
      - Yes
    * - minimal_example_2l1c
      - 
      - This problem was created to figure out, and get a picture, of what was constructed in the obscure definition 2l1c.
      - 
      - Yes
    * - midpoint_splits_in_two
      - If M is the midpoint of AB, it splits AB in a ratio of 1:2.
      - This problem was created to check if the definition of midpoint was communicating with the AR module to get the fact that the midpoint splits the segment in half. The original engine could not get this fact (even after the fixing of rconst as a predicate), and it prompted the addition of rule r51.
      - No
      - Yes
    * - central_angle_vs_internal_angle
      - 
      - This example is the first of a series of three examples designed to check if the engine could operate with some basic theorems involving angles on a circle. This specific problem checked if it could prove that, if both determine the same arc, the central angle is twice the angle with vertex lying on the circle. The theorem is also true in the reverse direction, investigated below at double_angle_implies_central_angle and at double_angle_implies_central_angle_2.
      - 
      - Yes
    * - double_angle_implies_central_angle
      - 
      - This example is the second of a series of three examples designed to check if the engine could operate with some basic theorems involving angles on a circle. This specific problem checked if it could prove that, if two angles have the same vertex and one doubles the other one, they are the central and internal angle of a circle. Here, one corner of the angles and the vertex of the smaller angle are in the same circle, and the question is if the second corner of the arc will also be in the circle (compare to double_angle_implies_central_angle_2 below). The theorem is also true in the reverse direction, investigated above at central_angle_vs_internal_angle.
      - No
      - No
    * - double_angle_implies_central_angle_2
      - 
      - This example is the third of a series of three examples designed to check if the engine could operate with some basic theorems involving angles on a circle. This specific problem checked if it could prove that, if two angles have the same vertex and one doubles the other one, they are the central and internal angle of a circle. Here, the points on the arc are established in a circle and the question is if the vertex of the smaller angle is in the same circle (compare to double_angle_implies_central_angle above). The theorem is also true in the reverse direction, investigated above at central_angle_vs_internal_angle.
      - No
      - No
    * - checking_rconst2
      - 
      - This problem was created as a straightforward check for the working of the recently created definition rconst2.
      - No
      - Yes
    * - menelaus_test
      - 
      - This problem was created to check the functioning of an external module that could apply Menelaus' Theorem. It was meant to check if it could solve the equation for the third ratio, given the other two, under Menelaus's conditions. The module was discontinued and the problem can no longer be solved.
      - No
      - No
    * - menelaus_frac1_test
      - 
      - This problem was created to check the functioning of an external module that could apply Menelaus' Theorem. It was meant to check if it could get the eqratio claim from Menelaus's conditions being met with one of the ratios in the equation being equal to one. The module was discontinued and the problem can no longer be solved.
      - No
      - No
    * - menelaus_crossed_cong_test
      - 
      - This problem was created to check the functioning of an external module that could apply Menelaus' Theorem. It was meant to check if it could get the eqratio claim from Menelaus's conditions being met with two segments involved in different ratios of the equation being congruent. The module was discontinued and the problem can no longer be solved.
      - No
      - No
    * - frac1_cong
      - 
      - This very straightforward problem was made to test the capacity of the AR module to get the congruence statement between segments forming a ratio of one. It proved successful.
      - 
      - Yes
    * - eqratio_lconst_check
      - 
      - This is part of a series of problems created at the implementation of the lconst predicate, to check if it was sufficiently well-connected to the AR module to get basic results. Here, that given an eqratio equation with three of the segments having prescribed lengths, that it could get the length of the fourth segment.
      - No
      - Yes
    * - cong_lconst_check
      - 
      - This is part of a series of problems created at the implementation of the lconst predicate, to check if it was sufficiently well-connected to the AR module to get basic results. Here, that given a prescribed length and a congruence statement, it could get the length of the congruent segment.
      - No
      - Yes
    * - lconst_cong_check
      - 
      - This is part of a series of problems created at the implementation of the lconst predicate, to check if it was sufficiently well-connected to the AR module to get basic results. Here, that given two segments with the same prescribed length, it could detect that they were congruent.
      - No
      - Yes
    * - lconst_eqratio_check
      - 
      - This is part of a series of problems created at the implementation of the lconst predicate, to check if it was sufficiently well-connected to the AR module to get basic results. Here, that given four segments with prescribed lengths in a way that forms an equality of ratios, the engine could detect the eqratio statement.
      - No
      - Yes
    * - rconst_lconst_check
      - 
      - This is part of a series of problems created at the implementation of the lconst predicate, to check if it was sufficiently well-connected to the AR module to get basic results. Here, that given a segment and the value of the ratio between it and a second segment, it could solve the equation for the length of the second segment.
      - No
      - Yes
    * - lconst_rconst_check
      - 
      - This is part of a series of problems created at the implementation of the lconst predicate, to check if it was sufficiently well-connected to the AR module to get basic results. Here, that given two segments with prescribed lengths, it could get the ratio between them.
      - No
      - Yes
    * - r50_vs_square_cyclic
      - 
      - Our first implementation of r50 overlooked the problem that if the opposite sides of a cyclic quadrilateral are parallel, their respective perpendicular bisectors overlap, so they can't be used to find the center of the circumcircle. We ruled the degenerate case out in the statement of r50, and created a series of problems to verify that we still could find the center of the circumcircle in the degenerate case through other rules. This problem checks that the engine knows that a square built through right angles is indeed a cyclic quadrilateral. It is a middle step towards r50_vs_square_center below.
      - 
      - Yes
    * - r50_vs_square_center
      - 
      - The second problem in the series checking if we can circumvent r50 in the degenerate case (see r50_vs_square_cyclic). It checks that the engine can recognize the center of a square built through right angles, checking a vertex of the initial segment used for the construction of the square.
      - 
      - Yes
    * - r50_vs_square
      - 
      - The third problem in the series checking if we can circumvent r50 in the degenerate case (see r50_vs_square_cyclic). It checks that the engine can recognize the center of a square built through right angles, checking the last vertex built in the square.
      - 
      - Yes
    * - r50_vs_trapezoid
      - 
      - The third problem in the series checking if we can circumvent r50 in the degenerate case (see r50_vs_square_cyclic). It checks that the engine can recognize the center of a generic cyclic trapezoid. The auxiliary point E is used to define the center O of the circle in a way that avoids giving extra information to the engine.
      - 
      - Yes
    * - pyt_test_formula_to_perp
      - 
      - This problem was created to test the functioning of Pythagoras theorem at implementation. It checks that if Pythagoras's formula is satisfied for a triangle, then the triangle has a right angle (perp statement).
      - No
      - Yes
    * - pyt_test_perp_to_formula
      - 
      - This problem was created to test the functioning of Pythagoras theorem at implementation. It checks that if we have a right angle (perp statement), and two lengths of sides of a triangle, then we can find the length of the third side.
      - No
      - Yes
    * - two_goals_cong_aconst
      - 
      - This problem was created to check the new functionality we implemented to have multiple goals for a single problem.
      - 
      - Yes
    * - two_goals_perp_cong
      - 
      - This problem was created to check the new functionality we implemented to have multiple goals for a single problem.
      - 
      - Yes
    * - checking_ordering_r27_oac_obd
      - 
      - This problem is part of a series created to examine the functioning of the original sameside predicate through rule r27 (before the consolidation of the sameside and nsameside predicates). Here, the points are created in a way that O-A-C are alligned in that order, just as as O-B-D are aligned on that order (in a different line). The construction interfered with the proof, making it longer than a single application of rule r27.
      - 
      - Yes
    * - checking_ordering_r27_aoc_bod
      - 
      - This problem is part of a series created to examine the functioning of the original sameside predicate through rule r27 (before the consolidation of the sameside and nsameside predicates). Here, the points are created in a way that A-O-C are alligned in that order, just as as B-O-D are aligned on that order (in a different line). The construction interfered with the proof, making it longer than a single application of rule r27.
      - 
      - Yes
    * - checking_ordering_r27_aoc_bod_eqratio
      - 
      - This problem is part of a series created to examine the functioning of the original sameside predicate through rule r27 (before the consolidation of the sameside and nsameside predicates). Here, the points are created in a way that A-O-C are alligned in that order, just as as B-O-D are aligned on that order (in a different line). In this proof, we also check the behavior of the eqratio3 predicate, which assumes the same configurations as rule r27.
      - 
      - Yes
    * - checking_ordering_r27_aoc_bod_sameside
      - 
      - This problem is part of a series created to examine the functioning of the original sameside predicate through rule r27 (before the consolidation of the sameside and nsameside predicates). Here, the points are created in a way that A-O-C are alligned in that order, just as as B-O-D are aligned on that order (in a different line). In this proof, we finally check the behavior of the sameside predicate directly, in a situation where B1-O-D is true but A-O-C is not (we have O-A-C), so we correctly have an unsolved problem.
      - No
      - No
    * - checking_ordering_r27_aoc_dob_sameside
      - 
      - This problem is part of a series created to examine the functioning of the original sameside predicate through rule r27 (before the consolidation of the sameside and nsameside predicates). Here, the points are created in a way that A-O-C are alligned in that order, just as as B-O-D are aligned on that order (in a different line). In this proof, we finally check the behavior of the sameside predicate directly, in a situation where B1-O-D and A1-O-C are satisfied.
      - 
      - Yes
    * - obm_phase1_2016_p10
      - 
      - This is a complete olympiad problem that could not be stated in the original AlphaGeometry. It served as a full test that the new predicates did communicate well with the overall engine, and new problems could be solved.
      - No
      - Yes
    * - inmo_1995_p1
      - 
      - This is a complete olympiad problem that could not be stated in the original AlphaGeometry, and one that uses the fact that multiple goals are now a possibility. Still, even though the problem can be stated, it could not be solved by the new engine, at least not without the prescription of additional points.
      - No
      - No
    * - acompute_test
      - 
      - This problem was created to test the recently implemented acompute predicate, that not only proves that the angle asked has a given value, but also finds the value of said angle, if available in the proof state, first.
      - No
      - Yes
    * - 2009_sl_g3_excenters
      - 
      - This was an attempt to find auxiliary points to problem G3 of the IMO 2009 shortlist. The attempt did not prove fruitful.
      - No
      - No
    * - tangents_to_circle
      - 
      - This problem was created to check if the engine could detect the simple fact that the two segments from the two tangents from an external point to the tangency points on a circle are congruent. This time, the fact could be proved without any problem.
      - 
      - Yes
    * - ninepoints
      - 
      - This problem was part of the general investigations of the capabilities of the engine to deal with triangles, and showed it can prove the concyclicity of the midpoints of the sides of a triangle and its heights.
      - 
      - Yes
    * - finding_mutual_circles
      - 
      - This problem was created to check if the engine could understand that building the circumcenter of a triangle and then creating points on the circle centered at the circumcenter with the circumradius would add point to the circumcircle of the triangle still. It used rule r49 to be able to tie both circles up.
      - 
      - Yes
    * - finding_center_giving_cyclic
      - 
      - This problem was meant to check if the engine could understand that the intersection of the perpendicular bisectors of two chords on a circle is the center of the circle. The failure of the original engine in doing that prompted the addition of rule r51.
      - No
      - Yes
    * - miquel_theorem
      - 
      - This is part of a series of problems created to examine the capability of the engine to apply Miquel's theorem, which was part of the study of IMO problem 6 from 2011. This specific problem asks if the engine knows the theorem in it most basic form: that the three circles through points on the sides of the triangles and the corresponding vertices intersect at a single point. The engine could apply all variations of Miquel's theorem we tried.
      - 
      - Yes
    * - miquel_theorem_angles
      - 
      - This is part of a series of problems created to examine the capability of the engine to apply Miquel's theorem, which was part of the study of IMO problem 6 from 2011. This specific problem asks if the engine can use the angle property of the theorem. The engine could apply all variations of Miquel's theorem we tried.
      - 
      - Yes
    * - miquel_quadrangle_theorem1
      - 
      - This is part of a series of problems created to examine the capability of the engine to apply Miquel's theorem, which was part of the study of IMO problem 6 from 2011. This specific problem checks a first part of the multiple circles intersecting in the version of the theorem for quadrangles, see miquel_quadrangle_theorem2 below for the second part of the same theorem. The engine could apply all variations of Miquel's theorem we tried.
      - 
      - Yes
    * - miquel_quadrangle_theorem2
      - 
      - This is part of a series of problems created to examine the capability of the engine to apply Miquel's theorem, which was part of the study of IMO problem 6 from 2011. This specific problem checks a first part of the multiple circles intersecting in the version of the theorem for quadrangles, see miquel_quadrangle_theorem1 above for the second part of the same theorem. The engine could apply all variations of Miquel's theorem we tried.
      - 
      - Yes
    * - two_perps_at_point_are_collinear
      - 
      - This problem was created to verify that the engine could prove the very straightforward fact that if two lines are perpendicular to another line at the same point, they are the same. The engine can do that, although it does prefer to call the algebraic method to start the proof, instead of using a purely axiomatic approach.
      - 
      - Yes
    * - miquel_theorem_circumcenter_implies_line
      - 
      - This is part of a series of problems created to examine the capability of the engine to apply Miquel's theorem, which was part of the study of IMO problem 6 from 2011. This specific problem checks that the engine can show that if the intersection of the circles lies on the circumcenter of the triangle, the points on the sides of the triangle are collinear. See miquel_theorem_line_implies_circumcenter below for the other direction of this theorem. The engine could apply all variations of Miquel's theorem we tried.
      - 
      - Yes
    * - miquel_theorem_line_implies_circumcenter
      - 
      - This is part of a series of problems created to examine the capability of the engine to apply Miquel's theorem, which was part of the study of IMO problem 6 from 2011. This specific problem checks that the engine can show that if the points on the sides of the triangle are collinear, Miquel's point lies on the circumcenter of the triangle. See miquel_theorem_circumcenter_implies_line above for the other direction of this theorem. The engine could apply all variations of Miquel's theorem we tried.
      - 
      - Yes
    * - pre_reflection_of_points_is_on_circumcenter_of_mirrors
      - 
      - This problem was part of the study of IMO problem 6 from 2011. In it, we were investigating the possibility of reversing the construction of the problem, that is, start from the points that could be involved in Miquel's theorem on a line, and from the reflected triangle, and try to recover the initial triangle and Miquel's instersection point on the circumcenter of the recovered triangle. This specific result was available for the engine, but this path of investigation did not bring any fruits to the larger search for a solution of the problem.
      - 
      - Yes
    * - centers_of_miquels_circles_are_concyclic
      - 
      - This is part of a series of problems created to examine the capability of the engine to apply Miquel's theorem, which was part of the study of IMO problem 6 from 2011. This specific problem checks the less intuitive fact that the centers of Miquel's circles, the circumcenter of the triangle and Miquel's point, when it lies on the circumcircle (see miquel_theorem_line_implies_circumcenter above) are concyclic. The engine could apply all variations of Miquel's theorem we tried.
      - 
      - Yes
    * - imo_2009_p2_angle_chase_verification
      - 
      - This problem was created specifically to verify the validity of step 15 of the proof of P2 in the 2009 IMO problem provided in the supplementary material of the original AlphaGometry paper. The step depends on the choice of point D by the engine, but the fact that the building of the problem checks the goal guarantees that the proper choice will be made.
      - 
      - Yes
    * - 2019_p2_with_extra_points_paper
      - 
      - This is a translation of problem 2 of the 2019 IMO paper with the extra points suggested by a human as described in the original AlphaGeometry paper in the Extended Data Figure 4.
      - 
      - Yes
    * - euler_simplified
      - 
      - This is a simplified version of problem euler above, including only the distinguished points of the triangle, not the auxiliary points from the original problem, which are not used in the proof but that take a big amount of useless calculations.
      - 
      - Yes
    * - testing_problem
      - 
      - The specific content of this problem is not relevant. It was created as a placeholder to make quick tests on the engine, without the need to change the problem name on the scripts and, later, the commands. This cannot be done as easily since the implementation of the caching mechanism.
      - x
      - x