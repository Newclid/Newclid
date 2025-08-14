from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from newclid.agent._index import AgentName
from newclid.api import ProblemBuilder
from newclid.cli import LogLevel, NewclidOptions, parse_cli_args
from newclid.ggb.problem_builder import GeogebraProblemBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.problem import PredicateConstruction
from newclid.tools import pretty_basemodel_diff


class TestCli:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fixture = CliFixture()

    def test_cli_parsing_jgex_problem_from_txt(self):
        self.fixture.given_input_arguments(
            "--seed",
            "123",
            "--log-level",
            "DEBUG",
            "--agent",
            "ddarn",
            "--output-dir",
            "mydir/output",
            "--saturate",
            "jgex",
            "--problem",
            "a b c = triangle a b c; h = on_tline h b a c, on_tline h c a b ? perp a h b c",
        )
        self.fixture.when_parsing_cli_args()
        self.fixture.then_options_should_be(
            seed=123,
            log_level=LogLevel.DEBUG,
            agent=AgentName.DDARN,
            output_dir=Path("mydir/output"),
            saturate=True,
        )
        self.fixture.then_should_have_jgex_problem_builder_with_problem(
            "a b c = triangle a b c; h = on_tline h b a c, on_tline h c a b ? perp a h b c"
        )

    def test_cli_parsing_jgex_problem_from_file(self):
        self.fixture.given_input_arguments(
            "--seed",
            "123",
            "--log-level",
            "DEBUG",
            "--agent",
            "ddarn",
            "--output-dir",
            "mydir/output",
            "jgex",
            "--problem-id",
            "orthocenter",
            "--file",
            "./newclid/problems_datasets/examples.txt",
        )
        self.fixture.when_parsing_cli_args()
        self.fixture.then_should_have_jgex_problem_builder_with_problem(
            "a b c = triangle a b c; h = on_tline h b a c, on_tline h c a b ? perp a h b c"
        )

    def test_cli_parsing_ggb_problem(self):
        self.fixture.given_input_arguments(
            "ggb",
            "--file",
            "mydir/output/problem.ggb",
            "--goals",
            "coll a b c",
            "para a b c d",
        )
        self.fixture.when_parsing_cli_args()
        self.fixture.then_should_have_ggb_problem(
            file="mydir/output/problem.ggb",
            goals=["coll a b c", "para a b c d"],
        )


class CliFixture:
    def __init__(self):
        self.args: list[str] = []
        self.options: NewclidOptions = NewclidOptions(
            seed=None,
            output_dir=None,
            saturate=False,
            agent=AgentName.FOLLOW_DEDUCTIONS,
            log_level=LogLevel.INFO,
        )
        self._problem_builder: ProblemBuilder | None = None

    @property
    def problem_builder(self) -> ProblemBuilder:
        if self._problem_builder is None:
            raise ValueError("Problem builder not parsed")
        return self._problem_builder

    def given_input_arguments(self, *args: str) -> None:
        self.args = list(args)

    def when_parsing_cli_args(self) -> None:
        self.options, self._problem_builder = parse_cli_args(self.args)

    def then_options_should_be(self, **kwargs: Any) -> None:
        expected = self.options.model_copy(update=kwargs)
        assert self.options == expected, pretty_basemodel_diff(self.options, expected)

    def then_should_have_jgex_problem_builder_with_problem(self, problem: str) -> None:
        assert isinstance(self.problem_builder, JGEXProblemBuilder)
        assert str(self.problem_builder.jgex_problem) == problem

    def then_should_have_ggb_problem(self, file: str, goals: list[str]) -> None:
        assert isinstance(self.problem_builder, GeogebraProblemBuilder)
        assert self.problem_builder.ggb_file_path == Path(file)
        assert self.problem_builder.goals == [
            PredicateConstruction.from_str(g) for g in goals
        ]
