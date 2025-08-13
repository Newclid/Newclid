from pathlib import Path

from pydantic import BaseModel, TypeAdapter


class ConstructionDefinition(BaseModel):
    in_args: int
    out_args: int

    @property
    def n_required_points(self) -> int:
        return self.in_args - self.out_args


def load_constructions(
    constructions_path: Path = Path(__file__).parent,
) -> tuple[
    dict[str, ConstructionDefinition],
    dict[str, ConstructionDefinition],
    dict[str, ConstructionDefinition],
]:
    dict_construction_adapter = TypeAdapter(dict[str, ConstructionDefinition])
    FREE = dict_construction_adapter.validate_json(
        constructions_path.joinpath("constructions_free.json").read_bytes()
    )

    # INTERSECT is a construction that is not supposed to return a point, it has a degree of freedom.
    # For example on_circum creates a point in a given circle, but it could be any point there.
    # If it is not intersected with something else, the point will be chosen at random.
    INTERSECT = dict_construction_adapter.validate_json(
        constructions_path.joinpath("constructions_intersect.json").read_bytes()
    )

    # OTHER is a construction that does not have that freedom.
    # For example midpoint, there is only one midpoint of a segment, so you can't expect to combine it with another construction.
    OTHER = dict_construction_adapter.validate_json(
        constructions_path.joinpath("constructions_other.json").read_bytes()
    )
    return FREE, INTERSECT, OTHER
