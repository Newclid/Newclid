from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_core import Url

from newclid.jgex.formulation import JGEXFormulation


class CompetitionIds(Enum):
    IMO = "imo"


class Competition(BaseModel):
    id: CompetitionIds
    name: str
    url: Url


Formulation = Annotated[JGEXFormulation, Field(discriminator="formulation_type")]


class ProblemFormulation(BaseModel):
    name: str
    formulation: Formulation


class Problem(BaseModel):
    """A problem and its multiple formulations."""

    source: Competition
    name: str
    natural_language_formulation: str
    formulations: list[ProblemFormulation]
