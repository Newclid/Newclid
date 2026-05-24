from newclid_backend.runner_models import NewclidProofSections, NewclidRunResult


def test_newclid_run_result_serializes_proof_output() -> None:
    proof_sections = NewclidProofSections(
        points=["A(0, 0)", "B(1, 0)"],
        assumptions=["[C0] : AB ⟂ CD"],
        proven_goals=["AD ⟂ BC : Proved [0]"],
        proof_steps=["000. example proof step"],
    )

    result = NewclidRunResult(
        status="succeeded",
        message="Newclid completed successfully.",
        proof_text="# Proof\n\n000. example proof step",
        proof_sections=proof_sections,
        run_info={
            "runtime": 0.01,
            "success": True,
            "steps": 1,
        },
    )

    dumped = result.model_dump()

    assert dumped["status"] == "succeeded"
    assert dumped["message"] == "Newclid completed successfully."
    assert dumped["proof_text"] == "# Proof\n\n000. example proof step"
    assert dumped["proof_sections"]["points"] == ["A(0, 0)", "B(1, 0)"]
    assert dumped["proof_sections"]["assumptions"] == ["[C0] : AB ⟂ CD"]
    assert dumped["proof_sections"]["proven_goals"] == ["AD ⟂ BC : Proved [0]"]
    assert dumped["proof_sections"]["proof_steps"] == ["000. example proof step"]
    assert dumped["proof_sections"]["unproven_goals"] == []
    assert dumped["proof_sections"]["appendix_ar"] == []
    assert dumped["run_info"] == {
        "runtime": 0.01,
        "success": True,
        "steps": 1,
    }
    assert dumped["stdout"] == ""
    assert dumped["stderr"] == ""
