import numpy as np
import pytest
from newclid.all_rules import R43_ORTHOCENTER_THEOREM
from newclid.api import GeometricSolverBuilder
from newclid.jgex.clause import JGEXClause, JGEXConstruction
from newclid.jgex.jgex_setup_data import (
    JGEXClauseInProof,
    JGEXSetupData,
    JGEXSetupId,
    PredicateConstructionInSetup,
    jgex_clauses_to_setup_data,
)
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.predicate_types import PredicateArgument
from newclid.problem import (
    PredicateConstruction,
    predicate_from_str,
    predicate_to_construction,
)
from newclid.proof_data import (
    PredicateInProof,
    ProofData,
    ProofId,
    ProofStep,
    proof_data_from_state,
)
from newclid.rule import RuleApplication
from newclid.tools import pretty_basemodel_diff


def p(s: str) -> PredicateArgument:
    return PredicateArgument(s)


class TestJGEXProofData:
    def test_setup_data_from_sampled_datagen_problem(self):
        """Test that this sample out of datagen has correct proof data."""
        rng = np.random.default_rng(42)
        jgex_problem_builder = (
            JGEXProblemBuilder(rng=rng)
            .include_auxiliary_clauses()
            .with_problem_from_txt(
                "a b c d = isquare a b c d; e f g h = centroid e f g h d c a; i = on_line i a h; j = eqdistance j c h d; k = parallelogram k g i b; l = intersection_lp l d j k g a; m = intersection_lc m l e d; n o = trisegment n o k j; p q r s = cc_tangent p q r s d m c a; t u v w = centroid t u v w r p e; x = on_bline x c d, on_tline x l e h ? eqangle c q g q p s q s"
            )
        )
        solver = GeometricSolverBuilder(rng=rng).build(jgex_problem_builder.build())
        success = solver.run()
        assert success
        assert jgex_problem_builder.jgex_problem is not None
        setup_data, _predicates_ids = jgex_clauses_to_setup_data(
            setup_clauses=list(jgex_problem_builder.jgex_problem.setup_clauses),
            aux_clauses=list(jgex_problem_builder.jgex_problem.auxiliary_clauses),
            goals=[
                predicate_to_construction(goal) for goal in solver.proof_state.goals
            ],
            clauses_consequences=jgex_problem_builder.clauses_consequences,
        )
        expected_square_clauses_in_proof = JGEXClauseInProof(
            added_points=("a", "b", "c", "d"),
            constructions=(JGEXConstruction.from_str("isquare a b c d"),),
            predicates=(
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C0"),
                    construction=PredicateConstruction.from_str("perp a b b c"),
                ),
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C1"),
                    construction=PredicateConstruction.from_str("cong a b b c"),
                ),
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C2"),
                    construction=PredicateConstruction.from_str("para a b c d"),
                ),
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C3"),
                    construction=PredicateConstruction.from_str("para b c a d"),
                ),
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C4"),
                    construction=PredicateConstruction.from_str("perp a d c d"),
                ),
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C5"),
                    construction=PredicateConstruction.from_str("cong b c c d"),
                ),
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C6"),
                    construction=PredicateConstruction.from_str("cong c d a d"),
                ),
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C7"),
                    construction=PredicateConstruction.from_str("perp a c b d"),
                ),
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C8"),
                    construction=PredicateConstruction.from_str("cong b d a c"),
                ),
            ),
        )
        actual_square_clauses_in_proof = setup_data.setup_clauses[0]
        assert actual_square_clauses_in_proof == expected_square_clauses_in_proof, (
            pretty_basemodel_diff(
                actual_square_clauses_in_proof, expected_square_clauses_in_proof
            )
        )

    def test_setup_data_from_orthocenter(self):
        """At initialisation, the proof data should be filled by construction predicates."""
        rng = np.random.default_rng(42)
        jgex_problem_builder = JGEXProblemBuilder(rng=rng).with_problem_from_txt(
            "a b c = triangle a b c; h = on_tline h b a c, on_tline h c a b ? perp a h b c"
        )
        solver = GeometricSolverBuilder(rng=rng).build(jgex_problem_builder.build())
        assert jgex_problem_builder.jgex_problem is not None
        setup_data, _predicates_ids = jgex_clauses_to_setup_data(
            setup_clauses=list(jgex_problem_builder.jgex_problem.setup_clauses),
            aux_clauses=[],
            clauses_consequences=jgex_problem_builder.clauses_consequences,
            goals=[
                predicate_to_construction(goal) for goal in solver.proof_state.goals
            ],
        )
        assert setup_data == self.orthocenter_setup_data, pretty_basemodel_diff(
            setup_data, self.orthocenter_setup_data
        )

    def test_proof_data_from_orthocenter_solved(self):
        """At initialisation, the proof data should be filled by construction predicates."""
        rng = np.random.default_rng(42)
        jgex_problem_builder = JGEXProblemBuilder(rng=rng).with_problem_from_txt(
            "a b c = triangle a b c; h = on_tline h b a c, on_tline h c a b ? perp a h b c"
        )
        solver = GeometricSolverBuilder(rng=rng).build(jgex_problem_builder.build())
        solver.run()
        assert jgex_problem_builder.jgex_problem is not None

        points = solver.proof_state.symbols.points

        proof_data = proof_data_from_state(
            goals_constructions=[
                predicate_to_construction(goal) for goal in solver.proof_state.goals
            ],
            proof_state=solver.proof_state,
        )

        goal_0 = PredicateInProof(
            id=ProofId("0"),
            predicate=predicate_from_str("perp a h b c", points),
        )

        expected_proof_data = ProofData(
            points=list(solver.proof_state.problem.points),
            proven_goals=[goal_0],
            unproven_goals=[],
            construction_assumptions=[
                PredicateInProof(
                    id=ProofId("C0"),
                    predicate=predicate_from_str("perp a b c h", points),
                ),
                PredicateInProof(
                    id=ProofId("C1"),
                    predicate=predicate_from_str("perp a c b h", points),
                ),
            ],
            numerical_checks=[],
            trivial_predicates=[],
            proof_steps=[
                ProofStep(
                    proven_predicate=goal_0,
                    justification=RuleApplication(
                        rule=R43_ORTHOCENTER_THEOREM,
                        predicate=predicate_from_str("perp a h b c", points),
                        premises=(
                            predicate_from_str("perp a b c h", points),
                            predicate_from_str("perp a c b h", points),
                        ),
                    ),
                    applied_on_predicates=(ProofId("C0"), ProofId("C1")),
                ),
            ],
        )

        assert proof_data == expected_proof_data, pretty_basemodel_diff(
            proof_data, expected_proof_data
        )

    @pytest.fixture(autouse=True)
    def setup(self):
        triangle_clause = JGEXClause(
            points=(p("a"), p("b"), p("c")),
            constructions=(JGEXConstruction.from_str("triangle a b c"),),
        )
        h_on_tlines_clause = JGEXClause(
            points=(p("h"), p("b"), p("a"), p("c")),
            constructions=(
                JGEXConstruction.from_str("on_tline h b a c"),
                JGEXConstruction.from_str("on_tline h c a b"),
            ),
        )

        self.orthocenter_setup_data = JGEXSetupData(
            goals=[
                PredicateConstructionInSetup(
                    id=JGEXSetupId("G0"),
                    construction=PredicateConstruction.from_str("perp a h b c"),
                ),
            ],
            setup_clauses=[
                JGEXClauseInProof(
                    constructions=triangle_clause.constructions,
                    predicates=(),
                    added_points=("a", "b", "c"),
                ),
                JGEXClauseInProof(
                    constructions=h_on_tlines_clause.constructions,
                    predicates=(
                        PredicateConstructionInSetup(
                            id=JGEXSetupId("C0"),
                            construction=PredicateConstruction.from_str("perp a c b h"),
                        ),
                        PredicateConstructionInSetup(
                            id=JGEXSetupId("C1"),
                            construction=PredicateConstruction.from_str("perp a b c h"),
                        ),
                    ),
                    added_points=("h",),
                ),
            ],
            aux_clauses=[],
        )
