from fractions import Fraction
from itertools import combinations
from math import sqrt
from typing import TYPE_CHECKING


from newclid.dependencies.dependency import Dependency, Reason
from newclid.dependencies.dependency_building import DependencyBody
from newclid.geometry import Length, Point, Ratio
from newclid.predicates import Predicate
from newclid.reasoning_engines.engines_interface import Derivation, ReasoningEngine
from newclid.statements.statement import Statement


if TYPE_CHECKING:
    from newclid.symbols_graph import SymbolsGraph


class PythagoreanFormula(ReasoningEngine):
    """Allow the use of Pythagorean theorem

    Either to get the missing side length or perp from lengths.

    AB ⟂ AC <=> AB² + AC² = BC²

    """

    def __init__(self, symbols_graph: "SymbolsGraph") -> None:
        self.symbols_graph = symbols_graph
        self._perp_intesections: dict[Point, tuple[Point, Point]] = {}
        self._segments_lengths: dict[tuple[str, str], Length] = {}
        self._intesection_dep: dict[Point, Dependency] = {}
        self._segments_length_dep: dict[tuple[str, str], Dependency] = {}

        self.PREDICATE_TO_INGEST = {
            Predicate.PERPENDICULAR: self._ingest_perp,
            Predicate.CONSTANT_LENGTH: self._ingest_lconst,
        }

    def ingest(self, dependency: Dependency):
        ingest_method = self.PREDICATE_TO_INGEST.get(dependency.statement.predicate)
        if ingest_method is not None:
            return ingest_method(dependency)
        pass

    def _ingest_perp(self, dependency: Dependency):
        statement = dependency.statement
        intersection = None
        others = []
        for p in statement.args:
            if p in others:
                intersection = p
                others.remove(p)
            else:
                others.append(p)

        if intersection is None:
            return

        self._perp_intesections[intersection] = tuple(others)
        self._intesection_dep[intersection] = dependency

    def _ingest_lconst(self, dependency: Dependency):
        statement = dependency.statement
        segment_hash = statement.hash_tuple[1:3]
        lenght = statement.args[-1]
        self._segments_lengths[segment_hash] = lenght
        self._segments_length_dep[segment_hash] = dependency

    def resolve(self, **kwargs) -> list[Derivation]:
        new_deps = self._resolve_implication()
        new_deps.extend(self._resolve_reciprocal())
        return new_deps

    def _resolve_implication(self) -> list[Derivation]:
        new_deps = []
        for intersection, (side1p, side2p) in self._perp_intesections.items():
            potential_values = [
                (side1p, side2p),
                (intersection, side1p),
                (intersection, side2p),
            ]

            values = [None, None, None]
            for pos, candidate in enumerate(potential_values):
                candidate_hash = tuple(sorted(c.name for c in candidate))
                if candidate_hash in self._segments_lengths:
                    lenght = self._segments_lengths[candidate_hash]
                    values[pos] = lenght

            if len([value for value in values if value is not None]) != 2:
                return

            missing_index = values.index(None)
            values.remove(None)
            missing_segment = potential_values[missing_index]
            missing_hypotenuse = missing_index == 0
            if not missing_hypotenuse:
                hypotenuse, side = (
                    _length_to_float(values[0]),
                    _length_to_float(values[1]),
                )
                new_length_val = self.pythagorean_side(hypotenuse, side)
            else:
                side1, side2 = (
                    _length_to_float(values[0]),
                    _length_to_float(values[1]),
                )
                new_length_val = self.pythagorean_hypotenuse(side1, side2)

            new_length = self.symbols_graph.get_or_create_const_length(new_length_val)
            new_statement = Statement(
                Predicate.CONSTANT_LENGTH, (*missing_segment, new_length)
            )

            why_perp = self._intesection_dep[intersection]
            why_lconsts = [
                self._segments_length_dep[(seg[0].name, seg[1].name)]
                for seg in potential_values
                if seg != missing_segment
            ]
            dep_body = DependencyBody(
                Reason("Pythagorean"), why=(why_perp, *why_lconsts)
            )
            new_deps.append(Derivation(new_statement, dep_body))
        return new_deps

    def _resolve_reciprocal(self) -> list[Derivation]:
        new_perps = []

        potential_triangles_bases: dict[str, list[str]] = {}
        for segment, _length in self._segments_lengths.items():
            for i, p_name in enumerate(segment):
                if p_name not in potential_triangles_bases:
                    potential_triangles_bases[p_name] = []
                other_point = segment[1 - i]
                potential_triangles_bases[p_name].append(other_point)

        for base, other_points in potential_triangles_bases.items():
            for two_points in combinations(other_points, 2):
                p1name, p2name = two_points

                hypotenuse = tuple(sorted((p1name, p2name)))
                side1 = tuple(sorted((base, p1name)))
                side2 = tuple(sorted((base, p2name)))

                if any(
                    seg not in self._segments_lengths
                    for seg in (hypotenuse, side1, side2)
                ):
                    continue

                if not self.pythagorean_perp(
                    *[
                        self._segments_lengths[seg].value
                        for seg in (hypotenuse, side1, side2)
                    ]
                ):
                    continue

                hypotenusedep = self._segments_length_dep[hypotenuse]
                side1dep = self._segments_length_dep[side1]
                side2dep = self._segments_length_dep[side2]
                dep_body = DependencyBody(
                    Reason("Pythagorean"), why=(hypotenusedep, side1dep, side2dep)
                )

                new_statement = Statement(
                    Predicate.PERPENDICULAR,
                    (*side1dep.statement.args[:2], *side2dep.statement.args[:2]),
                )
                new_perps.append(Derivation(new_statement, dep_body))

        return new_perps

    @staticmethod
    def pythagorean_hypotenuse(side1: float, side2: float) -> float:
        return sqrt(side1**2 + side2**2)

    @staticmethod
    def pythagorean_side(hypotenuse: float, side: float) -> float:
        return sqrt(hypotenuse**2 - side**2)

    @staticmethod
    def pythagorean_perp(hypotenuse: float, side1: float, side2: float) -> bool:
        return side1**2 + side2**2 == hypotenuse**2


def _length_to_float(length: Length) -> float:
    return float(length.name)


class MenelausFormula(ReasoningEngine):
    """Allow the use of Menelaus theorem to get the completing ratio.

    ncoll e d f, coll a b f, coll c d b, coll e d f, coll c e a
    => AF/FB * BD/DC * CE/DA = 1

    """

    def __init__(self, symbols_graph: "SymbolsGraph") -> None:
        self.ratios: list[Ratio] = []
        self.symbols_graph = symbols_graph

        self._new_colls: list[Dependency] = []

        self._coll_hash_to_dep: dict[tuple[str, ...], Dependency] = {}
        self._rconst_hash_to_dep: dict[tuple[str, ...], Dependency] = {}

        self.coll_candidates: dict[tuple[str, ...], list[tuple[str, ...]]] = {}
        self.triplet_candidates: dict[tuple[str, ...], list[tuple[str, ...]]] = {}

    def ingest(self, dependency: Dependency):
        statement = dependency.statement
        if statement.predicate is Predicate.COLLINEAR:
            self._new_colls.append(dependency)
        elif statement.predicate is Predicate.CONSTANT_RATIO:
            unique_points = set(statement.args[:-1])
            if len(unique_points) != 3:
                return
            hash_key = statement.hash_tuple[1:-1]
            self._rconst_hash_to_dep[hash_key] = dependency

    def resolve(self, **kwargs) -> list[Derivation]:
        while self._new_colls:
            coll = self._new_colls.pop()
            coll_hash = coll.statement.hash_tuple[1:]
            self._coll_hash_to_dep[coll_hash] = coll
            self._make_candidates_from_coll(coll_hash)

        triplet_hits = self.triplet_candidates.copy()
        for representent_triplet, ratios_to_match in self.triplet_candidates.items():
            triplet_hits[representent_triplet] = []
            for r_points, rconst in self._rconst_hash_to_dep.items():
                if r_points not in ratios_to_match:
                    continue
                triplet_hits[representent_triplet].append(r_points)

        new_deps = []
        for representent_triplet, hits in triplet_hits.items():
            if len(hits) != 2:
                continue

            rconst_hit_deps = [self._rconst_hash_to_dep[hit] for hit in hits]
            know_ratios = [dep.statement.args[-1] for dep in rconst_hit_deps]
            new_ratio_frac = self.menelaus_solver(*[r.value for r in know_ratios])
            new_ratio, _ = self.symbols_graph.get_or_create_const_rat(
                new_ratio_frac.numerator, new_ratio_frac.denominator
            )

            possible_hits = self.triplet_candidates[representent_triplet].copy()
            completed_ratio_points = [
                rconst for rconst in possible_hits if rconst not in hits
            ][0]

            ratio_point = self.symbols_graph.names2points(completed_ratio_points)

            new_statement = Statement(
                Predicate.CONSTANT_RATIO, (*ratio_point, new_ratio)
            )

            coll_deps = [
                self._coll_hash_to_dep[_rconst_hash_to_coll_hash(rconst_hash)]
                for rconst_hash in self.triplet_candidates[representent_triplet]
            ]
            initial_coll_triplet = tuple(sorted(representent_triplet))
            coll_deps.append(self._coll_hash_to_dep[initial_coll_triplet])

            dep_body = DependencyBody(
                Reason("Menelaus"), why=coll_deps + rconst_hit_deps
            )
            new_deps.append(Derivation(new_statement, dep_body))
            self.triplet_candidates.pop(representent_triplet)

        return new_deps

    @staticmethod
    def menelaus_solver(r1: Fraction, r2: Fraction) -> Fraction:
        return 1 / (r1 * r2)

    def _make_candidates_from_coll(self, coll_points: tuple[str, ...]):
        self.coll_candidates[coll_points] = []

        for other_coll_points, compatible_colls in self.coll_candidates.items():
            if other_coll_points == coll_points:
                continue

            if set(coll_points).isdisjoint(set(other_coll_points)):
                continue

            self._make_new_triplet_ratio_candidate(
                other_coll_points, coll_points, compatible_colls
            )
            self._make_new_triplet_ratio_candidate(
                coll_points, other_coll_points, self.coll_candidates[coll_points]
            )
            self.coll_candidates[coll_points].append(other_coll_points)
            compatible_colls.append(coll_points)

    def _make_new_triplet_ratio_candidate(
        self,
        main_coll: tuple[str, ...],
        new_coll: tuple[str, ...],
        other_colls: list[tuple[str, ...]],
    ):
        if len(other_colls) < 2:
            return
        for triplet_points in combinations((new_coll, *other_colls), 3):
            self.triplet_candidates[main_coll] = make_rconst_hashs_from_colls(
                main_coll, triplet_points
            )
            self.triplet_candidates[main_coll[::-1]] = make_rconst_hashs_from_colls(
                main_coll, triplet_points, inverse=True
            )


def make_rconst_hashs_from_colls(
    main_coll: tuple[str, ...],
    triplet_points: list[tuple[str, ...]],
    inverse: bool = False,
) -> list[tuple[str, ...]]:
    """Make a triplet of rconst hashs for each coll triplet given a main coll statement.

    For example:
        main = a c e, triplet_points = a b f; d e f; b c d;
        -> rhashs = a b a f; c d b c; e f d e
        main = e c a, triplet_points = a b f; d e f; b c d;
        -> rhashs = a b a f; c d b c; e f d e

    """
    rconst_hashs: list[tuple[str, ...]] = []
    point_is_up: dict[str, bool] = {}

    is_first_point = True
    used_triplets = []
    for point in main_coll:
        corresponding_triplet = [
            triplet for triplet in triplet_points if point in triplet
        ]
        if not corresponding_triplet:
            return []

        corresponding_triplet = corresponding_triplet[0]
        if corresponding_triplet in used_triplets:
            return []

        used_triplets.append(corresponding_triplet)

        non_mid_points = list([p for p in corresponding_triplet if p != point])

        p1, p2 = non_mid_points
        if (
            (is_first_point and not inverse)
            or (p2 in point_is_up and point_is_up[p2])
            or (p1 in point_is_up and not point_is_up[p1])
        ):
            up, down = non_mid_points
        else:
            down, up = non_mid_points

        if up not in point_is_up:
            point_is_up[up] = True
        else:
            point_is_up[up] = None
        if down not in point_is_up:
            point_is_up[down] = False
        else:
            point_is_up[down] = None

        is_first_point = False

        rconst_hashs.append(_rconst_hash(point, up, down))

    return rconst_hashs


def _rconst_hash(both_point: str, up_point: str, down_point: str):
    return (
        *sorted((both_point, up_point)),
        *sorted((both_point, down_point)),
    )


def _rconst_hash_to_coll_hash(rconst_hash: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(rconst_hash)))
