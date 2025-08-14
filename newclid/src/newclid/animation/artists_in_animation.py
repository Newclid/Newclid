from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from matplotlib import patches
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.lines import AxLine
from matplotlib.text import Annotation
from matplotlib.typing import ColorType

from newclid.draw.figure import draw_point
from newclid.draw.theme import DrawTheme
from newclid.predicate_types import PredicateArgument
from newclid.symbols.symbols_registry import SymbolsRegistry


@dataclass
class PointArtists:
    name: str
    path: ArtistInAnimation
    annotation: ArtistInAnimation

    def highlight(self, color: ColorType | None = None) -> set[Artist]:
        updated_artists: set[Artist] = set()
        if self.path.highlight(color=color):
            updated_artists.add(self.path.artist)
        if self.annotation.highlight(color=color):
            updated_artists.add(self.annotation.artist)
        return updated_artists

    def gray_out(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        if self.path.gray_out():
            updated_artists.add(self.path.artist)
        if self.annotation.gray_out():
            updated_artists.add(self.annotation.artist)
        return updated_artists

    def hide(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        if self.path.hide():
            updated_artists.add(self.path.artist)
        if self.annotation.hide():
            updated_artists.add(self.annotation.artist)
        return updated_artists


@dataclass
class ArtistInAnimation:
    artist: Artist
    original_color: ColorType | None = None
    original_zorder: float | None = None
    original_linewidth: float | None = None
    original_arrowstyle: patches.ArrowStyle | None = None

    def __post_init__(self) -> None:
        if isinstance(self.artist, AxLine):
            self.original_color = self.artist.get_color()
            self.original_linewidth = self.artist.get_linewidth()
        elif isinstance(self.artist, patches.FancyArrowPatch):
            self.original_arrowstyle = self.artist.get_arrowstyle()
        elif isinstance(self.artist, Annotation):
            self.original_color = self.artist.get_color()
        elif isinstance(self.artist, patches.Patch):
            self.original_color = self.artist.get_facecolor()
            self.original_linewidth = self.artist.get_linewidth()
        elif isinstance(self.artist, PathCollection):
            self.original_color = cast(ColorType, self.artist.get_facecolor()[0])
            self.original_linewidth = cast(float, self.artist.get_linewidth())
        if isinstance(self.artist, Annotation):
            self.original_size = self.artist.get_fontsize()

        self.original_zorder = self.artist.get_zorder()

    def highlight(self, color: ColorType | None = None) -> bool:
        was_not_visible = self.show()

        current_alpha = self.artist.get_alpha()
        is_angle = isinstance(self.artist, patches.Wedge)
        will_change_alpha = current_alpha != 1 and not is_angle
        if not is_angle:
            self.artist.set_alpha(1)
            self.artist.set_zorder(max(self.original_zorder or 10.0, 10.0))

        updated_kwargs: dict[str, str | float | ColorType] = {}

        if color is not None:
            updated_kwargs["color"] = color
        elif self.original_color is not None:
            updated_kwargs["color"] = self.original_color

        if self.original_linewidth is not None:
            updated_kwargs["linewidth"] = self.original_linewidth
        if self.original_arrowstyle is not None:
            updated_kwargs["arrowstyle"] = "simple,head_length=10,head_width=10"

        self.artist.update(updated_kwargs)
        return was_not_visible or will_change_alpha

    def gray_out(self) -> bool:
        is_visible = self.artist.get_visible()
        was_not_grayed_out = self.artist.get_alpha() != 0.5
        self.artist.set_alpha(0.5)
        self.artist.set_zorder(1.0)

        updated_kwargs: dict[str, str | float | ColorType] = {"color": "gray"}
        if self.original_linewidth is not None:
            updated_kwargs["linewidth"] = self.original_linewidth / 2
        if self.original_arrowstyle is not None:
            updated_kwargs["arrowstyle"] = "simple,head_length=0,head_width=0"

        self.artist.update(updated_kwargs)
        return is_visible and was_not_grayed_out

    def show(self) -> bool:
        was_not_visible = not self.artist.get_visible()
        self.artist.set_visible(True)
        return was_not_visible

    def hide(self) -> bool:
        was_visible = self.artist.get_visible()
        self.artist.set_visible(False)
        return was_visible


def init_point_name_to_artist(
    ax: Axes,
    color_theme: DrawTheme,
    aux_point_names: set[PredicateArgument],
    symbols: SymbolsRegistry,
) -> dict[str, PointArtists]:
    point_name_to_artist: dict[str, PointArtists] = {}
    for point in symbols.points:
        point_color = (
            color_theme.aux_point_color
            if point.name in aux_point_names
            else color_theme.point_color
        )
        point_artist, annotation_artist = draw_point(
            ax, point, point_color=point_color, fontsize=18, zorder=100
        )
        point_name_to_artist[point.name] = PointArtists(
            name=point.name,
            path=ArtistInAnimation(point_artist),
            annotation=ArtistInAnimation(annotation_artist),
        )
    return point_name_to_artist
