from abc import ABC, abstractmethod
from typing import NamedTuple

from newclid.jgex.clause import is_numerical_argument
from newclid.justifications.justification import Justification

from ncdgen.build_diagram import Diagram
from newclid.predicates import Predicate


class PointsForConclusion(NamedTuple):
    setup_points: set[str]
    aux_points: set[str]


class AuxDiscriminator(ABC):
    @abstractmethod
    def goals_with_aux_setup_split(
        self, diagram: Diagram
    ) -> dict[Justification, PointsForConclusion]:
        """Get every subproblem in the diagram."""


def predicate_point_names(predicate: Predicate) -> set[str]:
    return set(x for x in predicate.to_tokens() if not is_numerical_argument(x))
