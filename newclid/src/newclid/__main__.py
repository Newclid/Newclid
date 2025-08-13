import logging
import os
import sys
from pathlib import Path

import numpy as np

from newclid.agent.agent_builder import make_agent
from newclid.api import GeometricSolverBuilder
from newclid.cli import parse_cli_args
from newclid.jgex.problem_builder import JGEXProblemBuilder


def find_ggb_files(directory: Path):
    for entry in os.listdir(directory):
        if entry.endswith(".ggb"):
            yield entry


LOGGER = logging.getLogger(__name__)


def main() -> None:
    options, problem_builder = parse_cli_args(sys.argv[1:])
    logging.basicConfig(level=options.log_level.value)

    rng = np.random.default_rng(options.seed)
    solver_builder = GeometricSolverBuilder(rng)

    if options.agent is not None:
        agent = make_agent(options.agent)
        solver_builder.with_deductive_agent(agent)

    solver = solver_builder.build(problem_builder.build())

    jgex_problem = None
    if isinstance(problem_builder, JGEXProblemBuilder):
        jgex_problem = problem_builder.jgex_problem

    if options.output_dir:
        solver.draw_figure(
            out_file=options.output_dir / "initial_figure.svg",
            jgex_problem=jgex_problem,
        )

    solver.run()
    if solver.run_infos is not None:
        LOGGER.info(f"Run infos: {solver.run_infos.model_dump_json(indent=2)}")

    if options.output_dir is not None:
        solver.write_all_outputs(options.output_dir, jgex_problem=jgex_problem)


if __name__ == "__main__":
    main()
