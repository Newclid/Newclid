"""Command line interface for Newclid."""

from __future__ import annotations

import logging
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    Namespace,
    _SubParsersAction,  # pyright: ignore
)
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
from pydantic import BaseModel

from newclid.agent._index import AgentName
from newclid.api import ProblemBuilder
from newclid.ggb.problem_builder import GeogebraProblemBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.problem import PredicateConstruction


class NewclidOptions(BaseModel):
    output_dir: Path | None
    saturate: bool
    agent: AgentName | None
    seed: int | None
    log_level: LogLevel


def parse_cli_args(args: list[str]) -> tuple[NewclidOptions, ProblemBuilder]:
    parser = make_cli_parser()
    parsed_args = parser.parse_args(args)
    problem_builder = parsed_args.make_problem_builder(parsed_args)
    args_dict = vars(parsed_args)
    _adapt_log_level(args_dict)
    return NewclidOptions.model_validate(args_dict), problem_builder


def make_cli_parser() -> ArgumentParser:
    parser = ArgumentParser("newclid", formatter_class=ArgumentDefaultsHelpFormatter)
    _add_top_parser_arguments(parser)
    subparsers = parser.add_subparsers(
        title="Problem builders",
        description="Different methods to build a newclid problem.",
    )
    _add_jgex_parser(subparsers)
    _add_ggb_parser(subparsers)
    return parser


class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR


def _adapt_log_level(args_dict: dict[str, Any]) -> None:
    if "log_level" in args_dict:
        args_dict["log_level"] = LogLevel[args_dict["log_level"]]


def _add_top_parser_arguments(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument("--output-dir", "-o", default=None, help="Output directory")
    parser.add_argument(
        "--saturate",
        action="store_true",
        help="Ignore the goal and saturate the problem",
    )
    parser.add_argument(
        "--draw-initial-figure",
        action="store_true",
        help="Draw the initial figure",
    )
    parser.add_argument(
        "--draw-final-figure",
        action="store_true",
        help="Draw the final figure",
    )
    parser.add_argument(
        "--agent",
        default=None,
        help="Name of the agent to use",
        choices=[name.value for name in AgentName],
    )
    parser.add_argument(
        "--seed", default=None, type=int, help="Seed for random sampling"
    )
    parser.add_argument(
        "--log-level",
        default=LogLevel.INFO.name,
        type=str,
        choices=[level.name for level in LogLevel],
        help="Logging level c.f. https://docs.python.org/3/library/logging.html#logging-levels",
    )
    return parser


def _jgex_problem_builder(args: Namespace) -> ProblemBuilder:
    if args.problem_id is None and args.problem is None:  # pragma: no cover
        raise ValueError("Either --problem-id or --problem must be provided")
    if args.problem_id is not None and args.problem is not None:  # pragma: no cover
        raise ValueError("Only one of --problem-id or --problem must be provided")
    jgex_problem_builder = JGEXProblemBuilder(rng=np.random.default_rng(args.seed))
    if args.problem_id is not None:
        jgex_problem_builder.with_problem_from_file(
            problem_name=args.problem_id, problems_path=Path(args.file)
        )
    else:
        jgex_problem_builder.with_problem_from_txt(args.problem)
    return jgex_problem_builder


def _add_jgex_parser(subparsers: _SubParsersAction[ArgumentParser]) -> ArgumentParser:
    parser = subparsers.add_parser("jgex")
    parser.add_argument("--problem-id", "-p", help="The id of a JGEX problem to solve")
    parser.add_argument(
        "--file",
        "-f",
        help="The name of the problems file to read the problem from",
    )
    parser.add_argument("--problem", "-s", help="A JGEX string of a problem.")
    parser.set_defaults(make_problem_builder=_jgex_problem_builder)
    return parser


def _ggb_problem_builder(args: Namespace) -> ProblemBuilder:
    return GeogebraProblemBuilder(ggb_file_path=Path(args.file)).with_goals(
        [PredicateConstruction.from_str(g) for g in args.goals]
    )


def _add_ggb_parser(subparsers: _SubParsersAction[ArgumentParser]) -> ArgumentParser:
    parser = subparsers.add_parser("ggb")
    parser.add_argument(
        "--file",
        "-f",
        help="The ggb export file to read the problem from",
        required=True,
    )
    parser.add_argument(
        "--goals",
        "-g",
        nargs="+",
        help="The goals to add to the problem",
        type=str,
        required=True,
    )
    parser.set_defaults(make_problem_builder=_ggb_problem_builder)
    return parser
