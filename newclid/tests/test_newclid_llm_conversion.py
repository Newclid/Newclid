from difflib import Differ

import pytest
from newclid.jgex.clause import JGEXConstruction
from newclid.jgex.formulation import JGEXFormulation
from newclid.jgex.jgex_setup_data import (
    JGEXClauseInProof,
    JGEXSetupData,
    JGEXSetupId,
    PredicateConstructionInSetup,
)
from newclid.llm_input import (
    AuxTrainingDatapoint,
    TrainingDatapoint,
    new_problem_from_llm_aux_output,
    problem_to_llm_input,
    problem_to_llm_input_without_predicates,
)
from newclid.numerical.geometries import PointNum
from newclid.predicate_types import PredicateArgument
from newclid.problem import PredicateConstruction
from newclid.proof_data import (
    PredicateInProof,
    ProofData,
    ProofId,
    ProofStep,
)
from newclid.rule import Rule, RuleApplication
from newclid.symbols.points_registry import Point, PointsRegisty

from newclid.predicates import predicate_from_construction


def p(name: str) -> PredicateArgument:
    return PredicateArgument(name)


@pytest.mark.parametrize(
    "aux_output",
    [
        "f = on_line f a c, on_line f b d ([C4] coll a c f, [C5] coll b d f); g = on_line g a c, on_line g b d ([C6] coll a c g, [C7] coll b d g)",
        "!aux f = on_line f a c, on_line f b d ([C4] coll a c f, [C5] coll b d f); !aux g = on_line g a c, on_line g b d ([C6] coll a c g, [C7] coll b d g)",
        "f = on_line f a c, on_line f b d; g = on_line g a c, on_line g b d",
        "!aux f = on_line f a c, on_line f b d; !aux g = on_line g a c, on_line g b d",
    ],
    ids=[
        "without_aux_tag",
        "with_aux_tag",
        "no_predicates_without_aux_tag",
        "no_predicates_with_aux_tag",
    ],
)
def test_llm_aux_output_to_jgex_problem(aux_output: str) -> None:
    initial_problem = JGEXFormulation.from_text(
        "a b c = triangle a b c; d = on_tline d b a c, on_tline d c a b ? perp a d b c"
    )
    problem_with_aux = new_problem_from_llm_aux_output(
        initial_problem=initial_problem, aux_output=aux_output, aux_tag="!aux"
    )

    expected_problem_string = "a b c = triangle a b c; d = on_tline d b a c, on_tline d c a b | f = on_line f a c, on_line f b d; g = on_line g a c, on_line g b d ? perp a d b c"
    assert str(problem_with_aux) == expected_problem_string
    assert problem_with_aux != initial_problem, "The problem should be a new object"


def test_problem_to_llm_input():
    problem = JGEXFormulation.from_text(
        "a b c = triangle a b c; d = on_tline d b a c, on_tline d c a b | f = on_line f a c, on_line f b d ? perp a d b c"
    )
    actual = problem_to_llm_input(problem, aux_tag="!aux")
    expected = "a b c = triangle a b c (); d = on_tline d b a c, on_tline d c a b ([C0] perp a c b d, [C1] perp a b c d); f = on_line f a c, on_line f b d ([C2] coll a c f, [C3] coll b d f) ? [G0] perp a d b c"
    assert actual == expected


def test_problem_to_llm_input_no_predicates():
    problem = JGEXFormulation.from_text(
        "a b c = triangle a b c; d = on_tline d b a c, on_tline d c a b | f = on_line f a c, on_line f b d ? perp a d b c"
    )
    actual = problem_to_llm_input_without_predicates(problem)
    expected = "a b c = triangle a b c; d = on_tline d b a c, on_tline d c a b; f = on_line f a c, on_line f b d ? perp a d b c"
    assert actual == expected


class TestTrainingDatapoint:
    @pytest.mark.parametrize(
        "aux_points, expected_aux_io",
        [
            (
                ["e"],
                [
                    AuxTrainingDatapoint(
                        input="a b c = triangle a b c (); d = on_tline d b a c, on_tline d c a b ([C0] perp a b c d, [C1] perp a c b d) ? [G0] perp a d b c",
                        aux_output="!aux e = on_line e a c, on_line e b d ([C2] coll a c e, [C3] coll b d e)",
                    ),
                ],
            ),
            (
                ["e", "f"],
                [
                    # n-1 aux clauses
                    AuxTrainingDatapoint(
                        input="a b c = triangle a b c (); d = on_tline d b a c, on_tline d c a b ([C0] perp a b c d, [C1] perp a c b d); e = on_line e a c, on_line e b d ([C2] coll a c e, [C3] coll b d e) ? [G0] perp a d b c, [G1] perp a d c f",
                        aux_output="!aux f = on_line f a c, on_line f b d ([C4] coll a c f, [C5] coll b d f)",
                    ),
                    # n-2 aux clauses
                    AuxTrainingDatapoint(
                        input="a b c = triangle a b c (); d = on_tline d b a c, on_tline d c a b ([C0] perp a b c d, [C1] perp a c b d) ? [G0] perp a d b c, [G1] perp a d c f",
                        aux_output="!aux e = on_line e a c, on_line e b d ([C2] coll a c e, [C3] coll b d e); !aux f = on_line f a c, on_line f b d ([C4] coll a c f, [C5] coll b d f)",
                    ),
                ],
            ),
        ],
    )
    def test_aux_io_from_setup_data(
        self,
        aux_points: list[str],
        expected_aux_io: list[AuxTrainingDatapoint],
    ):
        if "f" not in aux_points:
            aux_clauses = [self.e_aux_clause]
            goals = [self.goals[0]]
        else:
            aux_clauses = [self.e_aux_clause, self.f_aux_clause]
            goals = self.goals

        setup_data = JGEXSetupData(
            setup_clauses=self.setup_clauses, aux_clauses=aux_clauses, goals=goals
        )
        aux_io = AuxTrainingDatapoint.from_setup_data_aux_combinations(
            setup_data, aux_tag="!aux"
        )

        for actual, expected in zip(aux_io, expected_aux_io):
            assert actual == expected, "\n".join(
                Differ().compare(
                    expected.model_dump_json(indent=2).splitlines(),
                    actual.model_dump_json(indent=2).splitlines(),
                )
            )

    def test_training_datapoint_from_proof_data(self):
        """Test that from_proof_data returns a datapoint for each auxiliary clause."""

        rule = Rule(
            id="r43",
            description="Orthocenter theorem",
            premises_txt=(),
            conclusions_txt=(),
        )

        # Proof: AB ⟂ CD [C0], AC ⟂ BD [C1] (r43 Orthocenter theorem)=> AD ⟂ BC [G0]

        goal_0 = predicate_from_construction(self.goals[0].construction, self.points)
        assert goal_0 is not None
        goal_0_in_proof = PredicateInProof(id=ProofId("G0"), predicate=goal_0)
        goal_1 = predicate_from_construction(self.goals[1].construction, self.points)
        assert goal_1 is not None
        goal_1_in_proof = PredicateInProof(id=ProofId("G1"), predicate=goal_1)
        proof = [
            ProofStep(
                proven_predicate=goal_0_in_proof,
                justification=RuleApplication(predicate=goal_0, rule=rule, premises=()),
                applied_on_predicates=(ProofId("C0"), ProofId("C2")),
            ),
            ProofStep(
                proven_predicate=goal_1_in_proof,
                justification=RuleApplication(predicate=goal_1, rule=rule, premises=()),
                applied_on_predicates=(ProofId("C1"), ProofId("C4")),
            ),
        ]

        proof_data = ProofData(
            points=[
                Point(name=PredicateArgument(p.name), num=p.num)
                for p in self.points.name_to_point.values()
            ],
            proven_goals=[goal_0_in_proof, goal_1_in_proof],
            unproven_goals=[],
            construction_assumptions=[],
            trivial_predicates=[],
            numerical_checks=[],
            proof_steps=proof,
        )

        training_data = TrainingDatapoint.from_proof_data_aux_combinations(
            setup_data=JGEXSetupData(
                setup_clauses=self.setup_clauses,
                aux_clauses=list(self.aux_points_to_clause.values()),
                goals=self.goals,
            ),
            proof_data=proof_data,
            aux_tag="!aux",
        )

        expected_proof_output = (
            "[G0] perp a d b c <(r43)= [C0,C2], [G1] perp a d c f <(r43)= [C1,C4]"
        )
        assert training_data.proof_output == expected_proof_output

    @pytest.fixture(autouse=True)
    def setup(self):
        self.points = PointsRegisty()
        self.points.name_to_point = {
            p("a"): Point(name=p("a"), num=PointNum(x=0, y=0)),
            p("b"): Point(name=p("b"), num=PointNum(x=1, y=0)),
            p("c"): Point(name=p("c"), num=PointNum(x=2, y=0)),
            p("d"): Point(name=p("d"), num=PointNum(x=3, y=0)),
            p("e"): Point(name=p("e"), num=PointNum(x=4, y=0)),
            p("f"): Point(name=p("f"), num=PointNum(x=5, y=0)),
        }

        # Goal: perp a d b c
        self.goals = [
            PredicateConstructionInSetup(
                id=JGEXSetupId("G0"),
                construction=PredicateConstruction.from_str("perp a d b c"),
            ),
            PredicateConstructionInSetup(
                id=JGEXSetupId("G1"),
                construction=PredicateConstruction.from_str("perp a d f c"),
            ),
        ]

        # Setup: a b c = triangle a b c; d = on_tline d b a c, on_tline d c a b
        self.setup_clauses = [
            JGEXClauseInProof(
                constructions=(JGEXConstruction.from_str("triangle a b c"),),
                predicates=(),  # Points are implicitly defined
                added_points=("a", "b", "c"),
            ),
            JGEXClauseInProof(
                constructions=(
                    JGEXConstruction.from_str("on_tline d b a c"),
                    JGEXConstruction.from_str("on_tline d c a b"),
                ),
                predicates=(
                    PredicateConstructionInSetup(
                        id=JGEXSetupId("C0"),
                        construction=PredicateConstruction.from_str("perp a b c d"),
                    ),
                    PredicateConstructionInSetup(
                        id=JGEXSetupId("C1"),
                        construction=PredicateConstruction.from_str("perp a c b d"),
                    ),
                ),
                added_points=("d",),
            ),
        ]

        # Aux: e = on_line e a c, on_line e b d; f = on_line f a c, on_line f b d
        self.e_aux_clause = JGEXClauseInProof(
            constructions=(
                JGEXConstruction.from_str("on_line e a c"),
                JGEXConstruction.from_str("on_line e b d"),
            ),
            predicates=(
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C2"),
                    construction=PredicateConstruction.from_str("coll a c e"),
                ),
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C3"),
                    construction=PredicateConstruction.from_str("coll b d e"),
                ),
            ),
            added_points=("e",),
        )

        self.f_aux_clause = JGEXClauseInProof(
            constructions=(
                JGEXConstruction.from_str("on_line f a c"),
                JGEXConstruction.from_str("on_line f b d"),
            ),
            predicates=(
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C4"),
                    construction=PredicateConstruction.from_str("coll a c f"),
                ),
                PredicateConstructionInSetup(
                    id=JGEXSetupId("C5"),
                    construction=PredicateConstruction.from_str("coll b d f"),
                ),
            ),
            added_points=("f",),
        )
        self.aux_points_to_clause = {
            "e": self.e_aux_clause,
            "f": self.f_aux_clause,
        }
