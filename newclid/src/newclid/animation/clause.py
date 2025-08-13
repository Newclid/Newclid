from dataclasses import dataclass

from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.typing import ColorType

from newclid.animation.artists_in_animation import ArtistInAnimation, PointArtists
from newclid.draw.jgex_constructions import draw_jgex_constructions
from newclid.draw.theme import DrawTheme
from newclid.jgex.clause import JGEXClause, is_numerical_argument
from newclid.jgex.formulation import JGEXFormulation
from newclid.predicate_types import PredicateArgument
from newclid.symbols.symbols_registry import SymbolsRegistry


@dataclass
class ClauseArtists:
    clause: JGEXClause
    constructions: list[ArtistInAnimation]
    new_points: list[PointArtists]
    used_points: list[PointArtists]

    def manifest(
        self,
        aux_point_names: set[PredicateArgument],
        highlight_color: ColorType | None = None,
    ) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for used_point in self.used_points:
            updated_artists.update(used_point.highlight())
        for construction in self.constructions:
            if construction.highlight(color=highlight_color):
                updated_artists.add(construction.artist)
        for point in self.new_points:
            color = highlight_color if point.name not in aux_point_names else None
            updated_artists.update(point.highlight(color=color))
        return updated_artists

    def gray_out(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for point in self.used_points:
            updated_artists.update(point.gray_out())
        for construction in self.constructions:
            if construction.gray_out():
                updated_artists.add(construction.artist)
        for point in self.new_points:
            updated_artists.update(point.gray_out())
        return updated_artists

    def hide(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for construction in self.constructions:
            if construction.hide():
                updated_artists.add(construction.artist)
        return updated_artists


def init_clauses_to_draw(
    ax: Axes,
    jgex_problem: JGEXFormulation,
    point_name_to_artist: dict[str, PointArtists],
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> dict[JGEXClause, ClauseArtists]:
    clauses_to_draw: dict[JGEXClause, ClauseArtists] = {}
    for clause in jgex_problem.clauses:
        new_points_artists: list[PointArtists] = [
            point_name_to_artist[pname] for pname in clause.points
        ]
        used_points_in_clause_artists: list[PointArtists] = [
            point_name_to_artist[pname]
            for construction in clause.constructions
            for pname in construction.args
            if not is_numerical_argument(pname)
        ]
        construction_artists: list[ArtistInAnimation] = []
        for construction in clause.constructions:
            for artist in draw_jgex_constructions(
                ax, construction, symbols_registry=symbols, theme=theme
            ):
                construction_artists.append(ArtistInAnimation(artist))
        clauses_to_draw[clause] = ClauseArtists(
            clause=clause,
            new_points=new_points_artists,
            used_points=used_points_in_clause_artists,
            constructions=construction_artists,
        )
    return clauses_to_draw
