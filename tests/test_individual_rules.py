import pytest

from newclid.api import GeometricSolverBuilder
from newclid.theorem import Theorem
from newclid.proof_writing import get_proof_steps, proof_step_string
from newclid.statements.adder import ALL_INTRINSIC_RULES


EXPECTED_TO_FAIL = [
    # "eqangle6 B A B C Q R Q P, eqangle6 C A C B R Q R P, ncoll A B C => simtri2 A B C P Q R",
    # "eqratio6 B A B C Q P Q R, eqratio6 C A C B R P R Q, ncoll A B C => simtri* A B C P Q R",
]

EXPECTED_TO_USE_OTHER_RULE = [
    # "cyclic A B C D, para A B C D => eqangle A D C D C D C B",
    "eqangle A B P Q C D U V, perp P Q U V => perp A B C D",
]

EXPECTED_WRONG_PROOF_LENGTH = [
    "perp A B C D, perp E F G H, npara A B E F => eqangle A B E F C D G H",
    "cong O A O B, cong O B O C, cong O C O D => cyclic A B C D",
    "cyclic A B C P Q R, eqangle C A C B R P R Q => cong A B P Q",
    "cyclic A B C D, para A B C D => eqangle A D C D C D C B",
    "circle O A B C, perp O A A X => eqangle A X A B C A C B",
    "circle O A B C, eqangle A X A B C A C B => perp O A A X",
    "circle O A B C, midp M B C => eqangle A B A C O B O M",
    "midp E A B, midp F A C => para E F B C",
    "midp M A B, midp M C D => para A C B D",
    "midp M A B, perp O M A B => cong O A O B",
    "perp A B B C, midp M A C => cong A M B M",
    "circle O A B C, coll O A C => perp A B B C",
    "midp M A B, midp N C D => eqratio M A A B N C C D",
    # "cong A B P Q, cong B C Q R, eqangle6 B A B C Q P Q R, ncoll A B C => contri* A B C P Q R",
    # "eqangle6 B A B C Q P Q R, eqangle6 C A C B R P R Q, ncoll A B C => simtri A B C P Q R",
    # "eqratio6 B A B C Q P Q R, eqangle6 B A B C Q P Q R, ncoll A B C => simtri* A B C P Q R",
    "eqratio6 B A B C Q P Q R, eqratio6 C A C B R P R Q, ncoll A B C, cong A B P Q => contri* A B C P Q R",
    "eqratio A B P Q C D U V, cong P Q U V => cong A B C D",
    "circle O A B C, coll M B C, eqangle A B A C O B O M => midp M B C",
    "midp M A B, para A C B D, para A D B C => midp M C D",
    "para a b c d, coll m a d, coll n b c, para m n a b => eqratio6 m a m d n b n c",
    # "eqratio6 B A B C Q P Q R, eqratio6 C A C B R P R Q, ncoll A B C => simtri* A B C P Q R",
    "midp M A B => rconst M A A B 1/2",
]

DEFINITIONAL_RULES = [  # rules not applied
    "r32"
]


@pytest.mark.parametrize(
    "rule_name,rule_txt,problem_txt",
    [
        (
            "r00",
            "perp A B C D, perp C D E F, ncoll A B E => para A B E F",
            "a = free a; b = free b; c = free c; d = on_tline d c a b; e = free e; f = on_tline f e c d ? para a b e f",
        ),
        (
            "r01",
            "cong O A O B, cong O B O C, cong O C O D => cyclic A B C D",
            "o = free o; a = free a; b = eqdistance b o o a; c = eqdistance c o o b; d = eqdistance d o o c ? cyclic a b c d",
        ),
        (
            "r02",
            "eqangle A B P Q C D P Q => para A B C D",
            "p = free p; q = free q; a = free a; b = free b; c = free c; d = on_aline0 d p q a b p q c ? para a b c d",
        ),
        (
            "r03",
            "cyclic A B P Q => eqangle P A P B Q A Q B",
            "a = free a; b = free b; p = free p; q = on_circum q a b p ? eqangle p a p b q a q b",
        ),
        (
            "r04",
            "eqangle6 P A P B Q A Q B, ncoll P Q A B => cyclic A B P Q",
            "a = free a; b = free b; q = free q; p = eqangle3 p a b q a b ? cyclic a b p q",
        ),
        (
            "r05",
            "cyclic A B C P Q R, eqangle C A C B R P R Q => cong A B P Q",
            "a = free a; b = free b; c = free c; p = on_circum p a b c; r = on_circum r a b c; q = on_circum q a b c, on_aline0 q c a c b r p r ? cong a b p q",
        ),
        (
            "r06",
            "midp E A B, midp F A C => para E F B C",
            "a = free a; b = free b; c = free c; e = midpoint e a b; f = midpoint f a c ? para e f b c",
        ),
        (
            "r07",
            "para A B C D, coll O A C, coll O B D => eqratio3 A B C D O O",
            "a = free a; b = free b; c = free c; d = on_pline d c a b; o = on_line o a c, on_line o b d ? eqratio3 a b c d o o",
        ),
        (
            "r08",
            "perp A B C D, perp E F G H, npara A B E F => eqangle A B E F C D G H",
            "a = free a; b = free b; c = free c; d = on_tline d c a b; e = free e; f = free f; g = free g; h = on_tline h g e f ? eqangle a b e f c d g h",
        ),
        (
            "r09",
            "eqangle a b c d m n p q, eqangle c d e f p q r u => eqangle a b e f m n r u",
            "c = free c; d = free d; p = free p; q = free q; a = free a; b = free b; m = free m; n = on_aline0 n c d a b p q m; e = free e; f = free f; r = free r; u = on_aline0 u c d e f p q r ? eqangle a b e f m n r u",
        ),
        (
            "r10",
            "eqratio a b c d m n p q, eqratio c d e f p q r u => eqratio a b e f m n r u",
            "a = free a; b = free b; c = free c; d = free d; m = free m; n = free n; p = free p; q = eqratio q a b c d m n p; e = free e; f = free f; r = free r; u = eqratio u c d e f p q r ? eqratio a b e f m n r u",
        ),
        (
            "r11",
            "eqratio6 d b d c a b a c, coll d b c, ncoll a b c => eqangle6 a b a d a d a c",
            "a = free a; b = free b; c = free c; d = eqratio6 d b c a b a c, on_line d b c ? eqangle6 a b a d a d a c",
        ),
        (
            "r12",
            "eqangle6 a b a d a d a c, coll d b c, ncoll a b c => eqratio6 d b d c a b a c",
            "a = free a; b = free b; d = free d; c = on_line c b d, on_aline0 c a b a d a d a ? eqratio6 d b d c a b a c",
        ),
        (
            "r13",
            "cong O A O B, ncoll O A B => eqangle O A A B A B O B",
            "o = free o; a = free a; b = eqdistance b o o a ? eqangle o a a b a b o b",
        ),
        (
            "r14",
            "eqangle6 A O A B B A B O, ncoll O A B => cong O A O B",
            "a = free a; b = free b; o = iso_triangle_vertex_angle o a b ? cong o a o b",
        ),
        (
            "r15",
            "circle O A B C, perp O A A X => eqangle A X A B C A C B",
            "a = free a; b = free b; c = free c; o = circle o a b c; x = on_tline x a a o ? eqangle a x a b c a c b",
        ),
        (
            "r16",
            "circle O A B C, eqangle A X A B C A C B => perp O A A X",
            "a = free a; b = free b; c = free c; o = circle o a b c; x = on_aline0 x c b c a a b a ? perp o a a x",
        ),
        (
            "r17",
            "circle O A B C, midp M B C => eqangle A B A C O B O M",
            "a = free a; b = free b; c = free c; o = circle o a b c; m = midpoint m b c ? eqangle a b a c o b o m",
        ),
        (
            "r18",
            "circle O A B C, coll M B C, eqangle A B A C O B O M => midp M B C",
            "a = free a; b = free b; c = free c; o = circle o a b c; m = on_line m b c, on_aline0 m a b a c o b o ? midp m b c",
        ),
        (
            "r19",
            "perp A B B C, midp M A C => cong A M B M",
            "a = free a; b = free b; c = on_tline c b b a; m = midpoint m a c ? cong a m b m",
        ),
        (
            "r20",
            "circle O A B C, coll O A C => perp A B B C",
            "o = free o; a = free a; b = on_circle b o a; c = on_circle c o a, on_line c o a ? perp a b b c",
        ),
        (
            "r21",
            "cyclic A B C D, para A B C D => eqangle A D C D C D C B",
            "a = free a; b = free b; c = free c; d = on_pline d c a b, on_circum d a b c ? eqangle a d c d c d c b",
        ),
        (
            "r22",
            "midp M A B, perp O M A B => cong O A O B",
            "a = free a; b = free b; m = midpoint m a b; o = on_tline o m a b ? cong o a o b",
        ),
        (
            "r23",
            "cong A P B P, cong A Q B Q => perp A B P Q",
            "a = free a; p = free p; q = free q; b = eqdistance b p a p, eqdistance b q a q ? perp a b p q",
        ),
        (
            "r24",
            "cong A P B P, cong A Q B Q, cyclic A B P Q => perp P A A Q",
            "a = free a; b = free b; p = iso_triangle_vertex p a b; q = iso_triangle_vertex q a b, on_circum q a b p ? perp p a a q",
        ),
        (
            "r25",
            "midp M A B, midp M C D => para A C B D",
            "a = free a; b = free b; c = free c; m = midpoint m a b; d = on_line d c m, eqdistance d m c m ? para a c b d",
        ),
        (
            "r26",
            "midp M A B, para A C B D, para A D B C => midp M C D",
            "a = free a; b = free b; c = free c; d = on_pline d b a c, on_pline d a b c; m = midpoint m a b ? midp m c d",
        ),
        (
            "r27",
            "eqratio O A A C O B B D, coll O A C, coll O B D, ncoll A B C, sameside A O C B O D => para A B C D",
            "o = free o; a = free a; b = free b; c = on_line c a o; d = eqratio d o a a c o b b, on_line d o b ? para a b c d",
        ),
        (
            "r28",
            "para A B A C => coll A B C",
            "a = free a; b = free b; c = on_pline0 c a b a ? coll a b c",
        ),
        (
            "r29",
            "midp M A B, midp N C D => eqratio M A A B N C C D",
            "a = free a; b = free b; c = free c; d = free d; m = midpoint m a b; n = midpoint n c d ? eqratio m a a b n c c d",
        ),
        (
            "r30",
            "eqangle A B P Q C D U V, perp P Q U V => perp A B C D",
            "p = free p; q = free q; u = free u; v = on_tline v u p q; a = free a; b = free b; c = free c; d = on_aline0 d p q a b u v c ? perp a b c d",
        ),
        (
            "r31",
            "eqratio A B P Q C D U V, cong P Q U V => cong A B C D",
            "p = free p; q = free q; u = free u; v = eqdistance v u p q; a = free a; b = free b; c = free c; d = eqratio d p q a b u v c ? cong a b c d",
        ),
        (
            "r32",
            "cong A B P Q, cong B C Q R, cong C A R P, ncoll A B C => contri* A B C P Q R",
            "a b c = triangle a b c; p = free p; q = eqdistance q p a b; r = eqdistance r p a c, eqdistance r q c b ? contri* a b c p q r",
        ),
        (
            "r33",
            "cong A B P Q, cong B C Q R, eqangle6 B A B C Q P Q R, ncoll A B C => contri* A B C P Q R",
            "a = free a; b = free b; c = free c; q = free q; p = eqdistance p q b a; r = eqdistance r q b c, on_aline0 r b a b c q p q ? contri* a b c p q r",
        ),
        (
            "r34",
            "eqangle6 B A B C Q P Q R, eqangle6 C A C B R P R Q, ncoll A B C => simtri A B C P Q R",
            "a = free a; b = free b; c = free c; q = free q; r = free r; p = on_aline0 p b c b a q r q, on_aline0 p c b c a r q r ? simtri a b c p q r",
        ),
        (
            "r35",
            "eqangle6 B A B C Q R Q P, eqangle6 C A C B R Q R P, ncoll A B C => simtri2 A B C P Q R",
            "a = free a; b = free b; c = free c; q = free q; r = free r; p = on_aline0 p b a b c q r q, on_aline0 p c a c b r q r ? simtri2 a b c p q r",
        ),
        (
            "r36",
            "eqangle6 B A B C Q P Q R, eqangle6 C A C B R P R Q, ncoll A B C, cong A B P Q => contri A B C P Q R",
            "a = free a; b = free b; p = free p; q = eqdistance q p a b; r = free r; c = on_aline0 c q p q r b a b, eqangle3 c a b r p q ? contri a b c p q r",
        ),
        (
            "r37",
            "eqangle6 B A B C Q R Q P, eqangle6 C A C B R Q R P, ncoll A B C, cong A B P Q => contri2 A B C P Q R",
            "a = free a; b = free b; p = free p; q = eqdistance q p a b; r = free r; c = on_aline0 c q r q p b a b, eqangle3 c a b r q p ? contri2 a b c p q r",
        ),
        (
            "r38",
            "eqratio6 B A B C Q P Q R, eqratio6 C A C B R P R Q, ncoll A B C => simtri* A B C P Q R",
            "a = free a; b = free b; c = free c; q = free q; r = free r; p = eqratio p b c b a q r q, eqratio p c b c a r q r ? simtri* a b c p q r",
        ),
        (
            "r39",
            "eqratio6 B A B C Q P Q R, eqangle6 B A B C Q P Q R, ncoll A B C => simtri* A B C P Q R",
            "a = free a; b = free b; c = free c; p = free p; q = free q; r = eqratio r b a b c q p q, on_aline0 r b a b c q p q ? simtri* a b c p q r",
        ),
        (
            "r40",
            "eqratio6 B A B C Q P Q R, eqratio6 C A C B R P R Q, ncoll A B C, cong A B P Q => contri* A B C P Q R",
            "a = free a; b = free b; c = free c; p = free p; q = eqdistance q p a b; r = eqratio r b a b c q p q, eqratio6 r p q c a c b ? contri* a b c p q r",
        ),
        (
            "r41",
            "para a b c d, coll m a d, coll n b c, eqratio6 m a m d n b n c, sameside m a d n b c => para m n a b",
            "a = free a; b = free b; c = free c; d = on_pline d c a b; n = on_line n b c; m = eqratio6 m a d n b n c, on_line m a d ? para m n a b",
        ),
        (
            "r42",
            "para a b c d, coll m a d, coll n b c, para m n a b => eqratio6 m a m d n b n c",
            "a = free a; b = free b; c = free c; d = on_pline d c a b; m = on_line m a d; n = on_line n b c, on_pline n m a b ? eqratio6 m a m d n b n c",
        ),
        (
            "r50",
            "midp M A B => rconst M A A B 1/2",
            "a b = segment a b; m = midpoint m a b ? rconst m a a b 1/2",
        ),
    ],
)
def test_rule_used_to_solve_in_one_step(
    rule_name: str, rule_txt: str, problem_txt: str
):
    theorem = Theorem.from_txt(rule_txt)
    theorem.rule_name = rule_name

    solver_builder = (
        GeometricSolverBuilder()
        .load_problem_from_txt(problem_txt, translate=False)
        .with_disabled_intrinsic_rules(ALL_INTRINSIC_RULES)
    )
    solver_builder.rules = [theorem]
    solver = solver_builder.build()

    success = solver.run()
    if rule_txt in EXPECTED_TO_FAIL:
        # if success:
        #     raise AssertionError(f"Rule {rule_txt} was expected to fail but succeded.")
        pytest.xfail(f"Rule {rule_txt} is expected to fail.")

    assert success
    if rule_name in DEFINITIONAL_RULES:
        return

    setup, aux, proof_steps, refs = get_proof_steps(
        solver.proof_state, solver.problem.goals
    )
    nl_proof_step = [
        proof_step_string(step, refs, last_step=i == len(proof_steps) - 1)
        for i, step in enumerate(proof_steps)
    ]

    is_one_step = len(proof_steps) == 1
    if rule_txt in EXPECTED_WRONG_PROOF_LENGTH:
        # if is_one_step:
        #     raise AssertionError(
        #         f"Rule {rule_txt} was expected to be too long but was one step."
        #     )
        pytest.xfail(f"Rule {rule_txt} is expected to have too many steps.")

    assert is_one_step
    for i, (step, _nl_step) in enumerate(zip(proof_steps, nl_proof_step)):
        _, [step_dependency] = step

        found_rule_name = step_dependency.reason.name if step_dependency.reason else ""
        if found_rule_name.startswith("b"):
            # Backtracked an hard-coded rule
            found_rule_name = found_rule_name[1:]

        expected_rule = found_rule_name == theorem.rule_name
        if rule_txt in EXPECTED_TO_USE_OTHER_RULE:
            if expected_rule:
                raise AssertionError(
                    f"Rule {rule_txt} was expected to use an other rule but used the same."
                )
            pytest.xfail(f"Rule {rule_txt} is expected to use an other rule.")

        assert expected_rule
