from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes

from newclid.draw.theme import DrawTheme


class TextAnimation:
    def __init__(
        self,
        ax: Axes,
        proof_lines: list[str],
        theme: DrawTheme,
        n_lines_shown: int = 13,
        fontsize: int = 16,
    ):
        if n_lines_shown % 2 == 0:
            raise ValueError(
                "n_lines_shown must be odd for the current line to be highlighted in the center"
            )
        self.ax = ax
        self.proof_lines = proof_lines
        self.theme = theme
        self.n_lines_shown = n_lines_shown
        self.highlighted_line_index = self.n_lines_shown // 2
        self.current_line_index = 0
        self.shown_after_current_line = self.highlighted_line_index
        self.shown_before_current_line = n_lines_shown - self.shown_after_current_line
        self.fontsize = fontsize

    @property
    def current_lines(self) -> list[str]:
        min_index = max(self.current_line_index - self.shown_before_current_line + 1, 0)
        current_and_past = self.proof_lines[min_index : self.current_line_index + 1]
        max_index = min(
            self.current_line_index + self.shown_after_current_line + 1,
            len(self.proof_lines),
        )
        lines_after = self.proof_lines[self.current_line_index + 1 : max_index]
        missing_before_lines = max(
            0, self.highlighted_line_index + 1 - len(current_and_past)
        )
        missing_after_lines = max(0, self.shown_after_current_line - len(lines_after))
        padded_lines = (
            [""] * missing_before_lines
            + current_and_past
            + lines_after
            + [""] * missing_after_lines
        )
        assert len(padded_lines) == self.n_lines_shown, (
            f"Expected {self.n_lines_shown} lines, got {len(padded_lines)}."
            f"lines_before: {len(current_and_past)}, lines_after: {len(lines_after)},"
            f"line_padded: {missing_before_lines}, current_line_index: {self.current_line_index},"
            f"shown_before_current_line: {self.shown_before_current_line},"
            f"shown_after_current_line: {self.shown_after_current_line},"
            f"highlighted_line_index: {self.highlighted_line_index}."
        )
        return padded_lines

    def init(self):
        self.ax.set_facecolor((0.0, 0.0, 0.0))
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)

        self.current_line_index = 0
        text_ys = np.linspace(0, 1, self.n_lines_shown)

        self.lines_artists = [
            self.ax.text(  # pyright: ignore
                1,
                text_ys[i],
                "",
                ha="right",
                va="baseline",
                color=self.theme.text_color,
                family=["DejaVu Sans", "STIXGeneral"],
                fontsize=self.fontsize,
                transform=self.ax.transAxes,
            )
            for i in range(self.n_lines_shown)[::-1]
        ]
        current_line_artist = self.lines_artists[self.highlighted_line_index]
        current_line_artist.set_color(self.theme.point_color)

        for i, artist in enumerate(self.lines_artists):
            size = int(
                _parabola(i, self.highlighted_line_index, max=1, min=0.3)
                * self.fontsize
            )
            artist.set_fontsize(size)
            alpha = _parabola(i, self.highlighted_line_index, max=1, min=0.5)
            artist.set_alpha(alpha)
        return self.lines_artists

    def update(self, frame: int):
        for artist, line in zip(self.lines_artists, self.current_lines):
            artist.set_text(line)
        self.current_line_index += 1
        return self.lines_artists


def _parabola(x: float, h: float, max: float, min: float) -> float:
    return max - ((max - min) / h**2) * (x - h) ** 2
