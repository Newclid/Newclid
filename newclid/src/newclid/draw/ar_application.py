from matplotlib.artist import Artist
from matplotlib.axes import Axes

from newclid.deductors import ARReason
from newclid.draw.predicates import draw_predicate
from newclid.draw.theme import DrawTheme
from newclid.justifications.justification import ARDeduction
from newclid.symbols.symbols_registry import SymbolsRegistry


def draw_ar_application(
    ax: Axes,
    ar_deduction: ARDeduction,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> set[Artist]:
    match ar_deduction.ar_reason:
        case ARReason.ANGLE_CHASING:
            return draw_deps_predicates(ax, ar_deduction, symbols, theme=theme)
        case ARReason.RATIO_CHASING:
            return draw_deps_predicates(ax, ar_deduction, symbols, theme=theme)
        case _:  # pyright: ignore
            raise NotImplementedError(
                f"Cannot draw AR application: {ar_deduction.ar_reason}"
            )


def draw_deps_predicates(
    ax: Axes,
    ar_deduction: ARDeduction,
    symbols: SymbolsRegistry,
    theme: DrawTheme,
) -> set[Artist]:
    if ar_deduction.ar_premises is None:
        raise ValueError(
            f"No premises to apply rule {ar_deduction.ar_reason} in dependency: {ar_deduction}"
        )

    artists: set[Artist] = set()
    artists.update(draw_predicate(ax, ar_deduction.predicate, symbols, theme=theme))
    for premise in ar_deduction.ar_premises:
        artists.update(draw_predicate(ax, premise.predicate, symbols, theme=theme))
    return artists
