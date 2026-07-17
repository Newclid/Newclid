from types import SimpleNamespace

from newclid_backend import runner_helpers


def _proof_step(predicate_id: str, applied_on: list[str]) -> SimpleNamespace:
    return SimpleNamespace(
        proven_predicate=SimpleNamespace(id=predicate_id),
        applied_on_predicates=applied_on,
    )


def _proof_data(*steps: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(proof_steps=list(steps))


def test_maps_known_premise_ids_to_step_indices() -> None:
    proof_data = _proof_data(
        _proof_step("step-a", []),
        _proof_step("step-b", ["step-a"]),
    )
    assert runner_helpers._build_step_premise_indices(proof_data) == [[], [0]]


def test_ignores_unknown_premise_ids() -> None:
    proof_data = _proof_data(
        _proof_step("step-a", []),
        _proof_step("step-b", ["construction-assumption", "unknown"]),
    )
    assert runner_helpers._build_step_premise_indices(proof_data) == [[], []]


def test_deduplicates_repeated_premise_ids() -> None:
    proof_data = _proof_data(
        _proof_step("step-a", []),
        _proof_step("step-b", ["step-a", "step-a", "step-a"]),
    )
    assert runner_helpers._build_step_premise_indices(proof_data) == [[], [0]]


def test_sorts_premise_indices_ascending() -> None:
    proof_data = _proof_data(
        _proof_step("step-a", []),
        _proof_step("step-b", []),
        _proof_step("step-c", []),
        _proof_step("step-d", ["step-c", "step-a", "step-b"]),
    )
    assert runner_helpers._build_step_premise_indices(proof_data) == [
        [],
        [],
        [],
        [0, 1, 2],
    ]


def test_handles_mixed_known_and_unknown_references() -> None:
    proof_data = _proof_data(
        _proof_step("step-a", []),
        _proof_step("step-b", []),
        _proof_step("step-c", ["unknown", "step-b", "step-a", "step-b"]),
    )
    assert runner_helpers._build_step_premise_indices(proof_data) == [[], [], [0, 1]]
