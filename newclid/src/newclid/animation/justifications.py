from dataclasses import dataclass

from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.typing import ColorType
from pydantic import BaseModel

from newclid.animation.artists_in_animation import ArtistInAnimation, PointArtists
from newclid.draw.ar_application import draw_ar_application
from newclid.draw.predicates import draw_predicate
from newclid.draw.rule import draw_rule_application
from newclid.draw.theme import DrawTheme
from newclid.justifications._index import JustificationType
from newclid.justifications.justification import Justification
from newclid.predicate_types import PredicateArgument
from newclid.problem import predicate_points
from newclid.proof_data import ProofData
from newclid.proof_writing import write_proof_sections
from newclid.symbols.symbols_registry import SymbolsRegistry


@dataclass
class JustificationArtists:
    justification: Justification
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

    def gray_out(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for artist in self.artists:
            if artist.gray_out():
                updated_artists.add(artist.artist)
        return updated_artists

    def hide(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for artist in self.artists:
            if artist.hide():
                updated_artists.add(artist.artist)
        return updated_artists


class JustificationToDraw(BaseModel):
    justification: Justification
    text: str


def init_justifications_to_draw(
    ax: Axes,
    point_name_to_artist: dict[str, PointArtists],
    symbols: SymbolsRegistry,
    proof_data: ProofData,
    theme: DrawTheme,
) -> tuple[
    list[JustificationToDraw],
    dict[Justification, JustificationArtists],
]:
    justifications_to_draw: list[JustificationToDraw] = []
    justification_artists: dict[Justification, JustificationArtists] = {}

    proof_lines_by_sections = write_proof_sections(proof_data)
    for proof_step, step_text in zip(
        proof_data.proof_steps, proof_lines_by_sections.proof_steps
    ):
        justification = proof_step.justification

        used_points_names: set[PredicateArgument]
        used_points: list[PointArtists]
        artists: set[Artist]
        match justification.dependency_type:
            case JustificationType.RULE_APPLICATION:
                used_points_names = set(predicate_points(justification.predicate))
                for premise in justification.premises:
                    used_points_names.update(predicate_points(premise))
                used_points = [
                    point_name_to_artist[pname] for pname in used_points_names
                ]
                artists = set(
                    draw_rule_application(ax, justification, symbols, theme=theme)
                )
            case JustificationType.AR_DEDUCTION:
                if justification.ar_premises is None:
                    raise ValueError(f"No why for dependency: {justification}")

                used_points_names = set(predicate_points(justification.predicate))
                for ar_premise in justification.ar_premises:
                    used_points_names.update(predicate_points(ar_premise.predicate))
                used_points = [
                    point_name_to_artist[pname] for pname in used_points_names
                ]
                artists = draw_ar_application(ax, justification, symbols, theme=theme)
            case _:
                used_points_names = set(predicate_points(justification.predicate))
                used_points = [
                    point_name_to_artist[pname] for pname in used_points_names
                ]
                artists = draw_generic_justification(ax, justification, symbols, theme)

        justification_artists[justification] = JustificationArtists(
            justification=justification,
            artists=[ArtistInAnimation(artist) for artist in artists],
            used_points=used_points,
        )
        justifications_to_draw.append(
            JustificationToDraw(
                justification=justification,
                text=_adapt_text_line(step_text),
            )
        )
    return justifications_to_draw, justification_artists


def _adapt_text_line(text_line: str) -> str:
    text_line = text_line.split("| ")[1]
    if len(text_line) > 110:
        text_line = text_line[:30] + " ... " + text_line[-80:]
    return text_line


def draw_generic_justification(
    ax: Axes,
    justification: Justification,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> set[Artist]:
    artists: set[Artist] = set()
    artists.update(draw_predicate(ax, justification.predicate, symbols, theme=theme))
    return artists
