import sys
from types import ModuleType
from typing import Any
from unittest.mock import Mock

import pytest
from newclid_backend import tasks


def _install_fake_runner_module(
    monkeypatch: pytest.MonkeyPatch,
    run_newclid_mock: Mock,
) -> None:
    fake_runner_module = ModuleType("newclid_backend.newclid_runner")

    setattr(
        fake_runner_module,
        "run_newclid_from_jgex",
        run_newclid_mock,
    )

    monkeypatch.setitem(
        sys.modules,
        "newclid_backend.newclid_runner",
        fake_runner_module,
    )


@pytest.mark.parametrize(
    "custom_theorems",
    [
        None,
        [
            {
                "name": "custom_parallel_rule",
                "description": ("Perpendicular lines imply parallel lines"),
                "premises": [
                    "perp A B C D",
                    "perp E F C D",
                ],
                "conclusions": [
                    "para A B E F",
                ],
            }
        ],
    ],
)
def test_run_newclid_job_forwards_arguments_and_serializes_result(
    monkeypatch: pytest.MonkeyPatch,
    custom_theorems: list[dict[str, Any]] | None,
) -> None:
    expected_result = {
        "status": "succeeded",
        "message": "Newclid completed successfully.",
        "proof_text": "# Proof",
        "proof_sections": None,
        "run_info": {
            "runtime": 0.1,
        },
        "sketch_points": [],
        "stdout": "",
        "stderr": "",
    }

    runner_result = Mock()
    runner_result.model_dump.return_value = expected_result

    run_newclid_mock = Mock(
        return_value=runner_result,
    )

    _install_fake_runner_module(
        monkeypatch,
        run_newclid_mock,
    )

    result = tasks.run_newclid_job(
        "point A\npoint B",
        custom_theorems=custom_theorems,
    )

    assert result == expected_result

    run_newclid_mock.assert_called_once_with(
        "point A\npoint B",
        custom_theorems=custom_theorems,
    )

    runner_result.model_dump.assert_called_once_with()


def test_run_newclid_job_propagates_runner_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_newclid_mock = Mock(
        side_effect=RuntimeError("Solver failed"),
    )

    _install_fake_runner_module(
        monkeypatch,
        run_newclid_mock,
    )

    with pytest.raises(
        RuntimeError,
        match="Solver failed",
    ):
        tasks.run_newclid_job(
            "point A",
            custom_theorems=None,
        )

    run_newclid_mock.assert_called_once_with(
        "point A",
        custom_theorems=None,
    )
