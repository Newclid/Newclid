def test_create_job_accepts_custom_theorems(client, monkeypatch, valid_jgex_problem):
    captured = {}

    def fake_enqueue_job(func, *args, job_id=None, timeout_seconds=None, **kwargs):
        captured["func"] = func
        captured["args"] = args
        captured["job_id"] = job_id
        captured["timeout_seconds"] = timeout_seconds

    monkeypatch.setattr(
        "newclid_backend.routers.jobs.enqueue_job",
        fake_enqueue_job,
    )

    response = client.post(
        "/api/jobs",
        json={
            "input_type": "jgex",
            "problem_input": valid_jgex_problem,
            "custom_theorems": [
                {
                    "name": "custom_parallel_theorem",
                    "description": "Perpendiculars to the same line are parallel",
                    "premises": [
                        "perp A B C D",
                        "perp E F C D",
                    ],
                    "conclusions": [
                        "para A B E F",
                    ],
                }
            ],
            "timeout_seconds": 120,
        },
    )

    assert response.status_code == 200
    assert captured["args"][0] == valid_jgex_problem
    assert captured["args"][1] == [
        {
            "name": "custom_parallel_theorem",
            "description": "Perpendiculars to the same line are parallel",
            "premises": [
                "perp A B C D",
                "perp E F C D",
            ],
            "conclusions": [
                "para A B E F",
            ],
        }
    ]
