import os


def test_cli_diagram_generation():
    exit_status = os.system(
        "ncdgen min_pts=2 max_pts=5 debug=True random_seed=42 +timeout=0.1"
    )
    assert exit_status == 0
