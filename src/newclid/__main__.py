import logging
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
import os
from pathlib import Path

from newclid import AGENTS_REGISTRY
from newclid.api import GeometricSolverBuilder
from newclid.algebraic_reasoning import algebraic_manipulator

LOGGER = logging.getLogger(__name__)


def find_ggb_files(directory: Path):
    for entry in os.listdir(directory):
        if entry.endswith(".ggb"):
            yield entry


def cli_arguments() -> Namespace:
    parser = ArgumentParser("newclid", formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--problem-name",
        required=True,
    )
    parser.add_argument("--env", default="exp", help="The environment folder")
    parser.add_argument("--ggb", default=None, help="Geogebra export file")
    parser.add_argument(
        "--problems-file",
        default=None,
        help="File containing problems including the current one",
    )
    parser.add_argument(
        "--agent",
        default="ddarn",
        help="Name of the agent to use",
        choices=AGENTS_REGISTRY.keys(),
    )
    parser.add_argument(
        "--defs",
        default=None,
        help="Path to definition file if no definition file is found in the environment",
    )
    parser.add_argument(
        "--rules",
        default=None,
        help="Path to rules file if no definition file is found in the environment",
    )
    parser.add_argument(
        "--seed",
        default=998244353,
        type=int,
        help="Seed for random sampling",
    )
    parser.add_argument(
        "--log-level",
        default=logging.WARNING,
        type=int,
        help="Logging level c.f. https://docs.python.org/3/library/LOGGER.html#logging-levels",
    )
    parser.add_argument(
        "--ar-verbose",
        default=None,
        help="Choose one or more from {a, d, r}, to print table of equations of angles (a), distances (d), ratios (r).",
    )
    parser.add_argument("--quiet", action="store_true", help="Do not output any files")
    parser.add_argument(
        "--exhaust",
        action="store_true",
        help="Run until the agent exhausts its actions",
    )
    args, _ = parser.parse_known_args()
    return args


def main() -> None:
    args = cli_arguments()
    logging.basicConfig(level=args.log_level)

    seed: int = args.seed
    algebraic_manipulator.config["verbose"] = (
        args.ar_verbose if args.ar_verbose is not None else ""
    )

    solver_builder = GeometricSolverBuilder(seed)

    # problem_name = load_problem(args.problem, solver_builder)
    envpath = Path(args.env)
    problem_path = envpath / args.problem_name
    problem_path.mkdir(parents=True, exist_ok=True)

    solver_builder.load_defs_from_file(Path(args.defs) if args.defs else None)
    rules = problem_path / "rules.txt"
    rules_env = envpath / "rules.txt"
    solver_builder.load_rules_from_file(
        rules
        if Path.exists(rules)
        else rules_env
        if Path.exists(rules_env)
        else Path(args.rules)
        if args.rules
        else None
    )

    if args.agent not in AGENTS_REGISTRY:
        raise ValueError("Agent not found")
    agent = AGENTS_REGISTRY[args.agent]
    solver_builder.with_deductive_agent(agent())

    ggb_files0 = list(find_ggb_files(problem_path)) + ([args.ggb] if args.ggb else [])
    ggb_files1 = list(find_ggb_files(envpath))
    if len(ggb_files0) >= 2 or len(ggb_files1) >= 2:
        raise Exception("Environment illegal: ambigious ggb setting")
    if (ggb_files0 or ggb_files1) and args.problems_file:
        raise Exception("Ambigious problem source: ggb and jgex")
    if ggb_files0:
        LOGGER.info(f"Use geogebra setting {problem_path / ggb_files0[0]}")
        solver_builder.load_geogebra(problem_path / ggb_files0[0])
    elif ggb_files1:
        LOGGER.info(f"Use geogebra setting {problem_path / ggb_files1[0]}")
        solver_builder.load_geogebra(problem_path / ggb_files1[0])
    elif args.problems_file:
        LOGGER.info(f"Use problem description in {args.problems_file}")
        solver_builder.load_problem_from_file(args.problems_file, args.problem_name)
    else:
        raise Exception("No way to find the problem setting")

    goals_file = problem_path / "goals.txt"
    if Path.exists(goals_file):
        LOGGER.info(f"Load goals in {goals_file}")
        solver_builder.load_goals_file(goals_file)

    if (
        len(solver_builder.goals) == 0 and solver_builder.problemJGEX is None
    ) and not args.exhaust:
        raise Exception("Not with option exhaust and there is no goal!")
    if args.exhaust:
        solver_builder.del_goals()

    if not args.quiet:
        solver_builder.with_problem_path(problem_path)

    solver = solver_builder.build()
    if not args.quiet:
        solver.draw_figure(out_file=problem_path / "construction_figure.svg")
    solver.run()

    LOGGER.info(f"Run infos: {solver.run_infos}")
    if not args.quiet:
        solver.write_all_outputs(problem_path)


if __name__ == "__main__":
    main()
