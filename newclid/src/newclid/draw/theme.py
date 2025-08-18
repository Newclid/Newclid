from typing import TypeVar

from pydantic import BaseModel

PALETTE = [
    "#e6194b",
    "#3cb44b",
    "#ffe119",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#31a8a8",
    "#f032e6",
    "#bcf60c",
    "#fabebe",
    "#008080",
    "#e6beff",
    "#9a6324",
    "#fffac8",
    "#800000",
    "#aaffc3",
    "#808000",
    "#ffd8b1",
    "#0000cd",
    "#808080",
    "#00ff73",
    "#ffffff",
]

HARMONIC_BLUE = "#00479e"


class DrawTheme(BaseModel):
    circle_color: str = "#c63661"
    line_color: str = "#ffd1a9"
    triangle_color: str = "#B35555"
    goal_color: str = "#A38905"
    aux_point_color: str = HARMONIC_BLUE
    new_point_color: str = "#a5e838"
    construction_color: str = "#487f56"
    point_color: str = "#3ee838"
    text_color: str = "#ffd1a9"
    perpendicular_color: str = "#FFE100"
    title_color: str = "#FFFFFF"
    thick_line_width: int = 3
    thin_line_width: int = 2


K1 = TypeVar("K1")
V1 = TypeVar("V1")


def fill_missing(d0: dict[K1, V1], d1: dict[K1, V1]) -> dict[K1, V1]:
    combined: dict[K1, V1] = d0.copy()  # type: ignore
    for k in d1.keys():
        if k not in d0:
            combined[k] = d1[k]
    return combined
