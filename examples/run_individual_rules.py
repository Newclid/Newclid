import cProfile
import logging
from pathlib import Path


from newclid.api import GeometricSolverBuilder
from newclid.problem import Problem
from newclid.statements.adder import IntrinsicRules


def main():
    logging.basicConfig(level=logging.INFO)

    problem_file = "problems_datasets/testing_minimal_rules.txt"
    problems = Problem.to_dict(Problem.from_txt_file(problem_file, translate=False))
    for problem_name in problems.keys():
        solver_builder = (
            GeometricSolverBuilder()
            .load_problem_from_file(problem_file, problem_name, translate=False)
            .with_disabled_intrinsic_rules(
                [
                    IntrinsicRules.PARA_FROM_PERP,
                    IntrinsicRules.CYCLIC_FROM_CONG,
                    IntrinsicRules.CONG_FROM_EQRATIO,
                    IntrinsicRules.PARA_FROM_EQANGLE,
                ]
            )
        )
        solver_builder.rules = []

        solver = solver_builder.build()
        out_folder_path = Path("./ddar_results/") / problem_name

        logging.info(f"Testing rule {problem_name} with ddar only.")

        problem_output_path = out_folder_path
        problem_output_path.mkdir(exist_ok=True, parents=True)

        solver.draw_figure(
            problem_output_path / f"{problem_name}_construction_figure.png",
        )

        max_steps = 10000
        timeout = 600.0
        success = False
        cProfile.runctx(
            "solver.run(max_steps, timeout)",
            globals=globals(),
            locals=locals(),
            filename=str(problem_output_path / f"{problem_name}.prof"),
        )

        if solver.run_infos["success"]:
            logging.info(f"Solved {problem_name}: {solver.run_infos}")
            try:
                solver.write_solution(
                    problem_output_path / f"{problem_name}_proof_steps.txt"
                )
                solver.proof_state.symbols_graph.draw_figure(
                    problem_output_path / f"{problem_name}_proof_figure.png",
                )
            except TypeError:
                logging.info(f"Solved {problem_name}, but saw traceback error.")
        else:
            logging.info(f"Failed at {problem_name}: {solver.run_infos}")


if __name__ == "__main__":
    main()
