from pathlib import Path

from ncdgen.generation_loop import Datapoint


def read_datapoints_from_file(path: Path) -> list[Datapoint]:
    with path.open() as f:
        datapoints = [Datapoint.model_validate_json(line) for line in f.readlines()]
    return datapoints
