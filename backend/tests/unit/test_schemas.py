def test_create_job_rejects_multiline_custom_theorem_predicates(
    client,
    valid_jgex_problem,
):
    response = client.post(
        "/api/jobs",
        json={
            "input_type": "jgex",
            "problem_input": valid_jgex_problem,
            "custom_theorems": [
                {
                    "name": "custom_theorem",
                    "description": "Invalid predicate line",
                    "premises": ["perp A B C D\npara A B C D"],
                    "conclusions": ["para A B C D"],
                }
            ],
            "timeout_seconds": 120,
        },
    )

    assert response.status_code == 422


def test_create_job_rejects_duplicate_custom_theorem_names(
    client,
    valid_jgex_problem,
):
    response = client.post(
        "/api/jobs",
        json={
            "input_type": "jgex",
            "problem_input": valid_jgex_problem,
            "custom_theorems": [
                {
                    "name": "custom_theorem",
                    "description": "First theorem",
                    "premises": ["perp A B C D"],
                    "conclusions": ["para A B C D"],
                },
                {
                    "name": "custom_theorem",
                    "description": "Second theorem",
                    "premises": ["coll A B C"],
                    "conclusions": ["coll C B A"],
                },
            ],
            "timeout_seconds": 120,
        },
    )

    assert response.status_code == 422
