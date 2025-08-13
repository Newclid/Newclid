from newclid.jgex.constructions._index import JGEXConstructionName
from newclid.jgex.constructions.complete_figure import COMPLETE_FORM_CONSTRUCTIONS
from newclid.jgex.constructions.free import FREE_CONSTRUCTIONS
from newclid.jgex.constructions.intersections import INTERSECTION_CONSTRUCTIONS
from newclid.jgex.constructions.point_on_object import POINT_ON_OBJECT_CONSTRUCTIONS
from newclid.jgex.constructions.predicate_prescriptions import PREDICATE_PRESCRIPTIONS
from newclid.jgex.constructions.problem_specific import PROBLEM_SPECIFIC_CONSTRUCTIONS
from newclid.jgex.constructions.relative_to import RELATIVE_TO_CONSTRUCTIONS
from newclid.jgex.definition import JGEXDefinition

ALL_JGEX_CONSTRUCTIONS = (
    FREE_CONSTRUCTIONS
    + POINT_ON_OBJECT_CONSTRUCTIONS
    + INTERSECTION_CONSTRUCTIONS
    + COMPLETE_FORM_CONSTRUCTIONS
    + PREDICATE_PRESCRIPTIONS
    + PROBLEM_SPECIFIC_CONSTRUCTIONS
    + RELATIVE_TO_CONSTRUCTIONS
)

ALL_JGEX_CONSTRUCTIONS_BY_NAME: dict[JGEXConstructionName, JGEXDefinition] = {
    c.name: c for c in ALL_JGEX_CONSTRUCTIONS
}
