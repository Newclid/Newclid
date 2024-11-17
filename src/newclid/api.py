"""Module containing the facade for the external API that must be maintained."""
# !!! Do not change the external API except if you know what you are doing !!!

from __future__ import annotations
import logging
from pathlib import Path
import traceback
from typing import Optional
from typing_extensions import Self

from newclid.auxiliary_constructions import insert_aux_to_premise
from newclid.configs import default_defs_path, default_rules_path
from newclid.graph import Graph
from newclid.numericals import draw
from newclid.ddar import solve
from newclid.problem import Problem, Theorem, Definition, Clause
from newclid.geometry import Point, Circle, Line, Segment
from newclid.write_proof import write_solution


class GeometricSolver:
    def __init__(
        self,
        proof_state: "Graph",
        problem: "Problem",
        defs: dict[str, "Definition"],
        rules: list["Theorem"],
    ) -> None:
        self.proof_state = proof_state
        self.problem = problem
        self.defs = defs
        self.rules = rules
        self.problem_string = problem.txt()

    @property
    def goal(self):
        return self.problem.goal

    def load_state(self, proof_state: "Graph"):
        self.proof_state = proof_state

    def load_problem_string(self, problem_string: str):
        self.problem_string = problem_string

    def get_problem_string(self) -> str:
        return self.problem.txt()

    def get_proof_state(self) -> str:
        return self.proof_state

    def get_defs(self):
        return self.defs

    def get_setup_string(self) -> str:
        return self.problem.setup_str_from_problem(self.defs)

    def run(self, max_steps: int = 1000) -> bool:
        solve(self.proof_state, self.rules, self.problem, max_level=max_steps)
        goal = self.problem.goal
        goal_args_names = self.proof_state.names2nodes(goal.args)
        if not self.proof_state.check(goal.name, goal_args_names):
            logging.info("Solver failed to solve the problem.")
            return False
        logging.info("Solved.")
        return True

    def write_solution(self, out_file: Path):
        write_solution(self.proof_state, self.problem, out_file)

    def draw_figure(self, out_file: Path):
        draw(
            self.proof_state.type2nodes[Point],
            self.proof_state.type2nodes[Line],
            self.proof_state.type2nodes[Circle],
            self.proof_state.type2nodes[Segment],
            block=False,
            save_to=out_file,
        )

    def get_existing_points(self) -> list[str]:
        return [p.name for p in self.proof_state.all_points()]

    def validate_clause_txt(self, clause_txt: str):
        if clause_txt.startswith("ERROR"):
            return clause_txt
        clause = Clause.from_txt(clause_txt)
        try:
            self.proof_state.copy().add_clause(clause, 0, self.defs)
        except Exception:
            return "ERROR: " + traceback.format_exc()
        return clause_txt

    def add_auxiliary_construction(self, aux_string: str):
        # Update the constructive statement of the problem with the aux point:
        candidate_pstring = insert_aux_to_premise(self.problem_string, aux_string)
        logging.info('Solving: "%s"', candidate_pstring)
        p_new = Problem.from_txt(candidate_pstring)
        p_new.url = self.problem.url
        # This is the new proof state graph representation:
        g_new, _ = Graph.build_problem(p_new, self.defs)

        self.problem = p_new
        self.proof_state = g_new


class GeometricSolverBuilder:
    def __init__(self) -> None:
        self.problem = None
        self.defs = None
        self.rules = None
        self.proof_state = None

    def build(self) -> "GeometricSolver":
        if self.problem is None:
            raise ValueError("Did not load problem before building solver.")

        if self.defs is None:
            self.defs = Definition.to_dict(
                Definition.from_txt_file(default_defs_path())
            )

        if self.rules is None:
            self.rules = Theorem.from_txt_file(default_rules_path(), to_dict=True)

        if self.proof_state is None:
            self.proof_state, _ = Graph.build_problem(self.problem, self.defs)

        return GeometricSolver(self.proof_state, self.problem, self.defs, self.rules)

    def load_problem_from_file(
        self, problems_path: Path, problem_name: str, translate: bool = True
    ) -> Self:
        problems = Problem.to_dict(
            Problem.from_txt_file(problems_path, translate=translate)
        )
        if problem_name not in problems:
            raise ValueError(f"Problem name `{problem_name}` not found in `{problems}`")
        self.problem = problems[problem_name]
        return self

    def load_problem_from_txt(
        self, problem_string: str, translate: bool = True
    ) -> Self:
        self.problem = Problem.from_txt(problem_string, translate)
        return self

    def load_rules_from_file(self, rules_path: Optional[Path] = None) -> Self:
        if rules_path is None:
            rules_path = default_rules_path()
        self.rules = Theorem.from_txt_file(rules_path, to_dict=True)
        return self

    def load_defs_from_file(self, defs_path: Optional[Path] = None) -> Self:
        if defs_path is None:
            defs_path = default_defs_path()
        self.defs = Definition.from_txt_file(defs_path, to_dict=True)
        return self
