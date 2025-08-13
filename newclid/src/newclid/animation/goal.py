from dataclasses import dataclass

from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.typing import ColorType

from newclid.animation.artists_in_animation import ArtistInAnimation, PointArtists
from newclid.draw.predicates import draw_predicate
from newclid.draw.theme import DrawTheme
from newclid.predicate_types import PredicateArgument
from newclid.predicates import NUMERICAL_PREDICATES, Predicate
from newclid.problem import predicate_points
from newclid.proof_data import PredicateInProof
from newclid.symbols.symbols_registry import SymbolsRegistry


@dataclass
class GoalArtists:
    goal: Predicate
    artists: list[ArtistInAnimation]
    used_points: list[PointArtists]

    def highlight(
        self,
        aux_point_names: set[PredicateArgument],
        highlight_color: ColorType | None = None,
    ) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for artist in self.artists:
            if artist.highlight(highlight_color):
                updated_artists.add(artist.artist)
        for point in self.used_points:
            color = highlight_color if point.name not in aux_point_names else None
            updated_artists.update(point.highlight(color=color))
        return updated_artists

    def hide(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for artist in self.artists:
            if artist.hide():
                updated_artists.add(artist.artist)
        return updated_artists


def init_goals_to_draw(
    ax: Axes,
    proven_goals: list[PredicateInProof],
    point_name_to_artist: dict[str, PointArtists],
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> dict[str, GoalArtists]:
    goals_artists: dict[str, GoalArtists] = {}
    for goal in proven_goals:
        if goal.predicate.predicate_type in NUMERICAL_PREDICATES:
            continue

        used_points: list[PointArtists] = []
        for point in predicate_points(goal.predicate):
            used_points.append(point_name_to_artist[point])

        artists = draw_predicate(ax, goal.predicate, symbols, theme=theme)
        goals_artists[goal.id] = GoalArtists(
            goal=goal.predicate,
            artists=[ArtistInAnimation(artist) for artist in artists],
            used_points=used_points,
        )
    return goals_artists
