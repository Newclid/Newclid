from __future__ import annotations

from typing import Generic, Self, TypeVar

from pydantic import BaseModel, model_validator

S = TypeVar("S")


class SymbolMergeHistory(BaseModel, Generic[S]):
    """Merge history for a symbol.

    Maintains a merge history to
    other Lines or Circles if they are (found out to be) equivalent

    Example:

        a -> b -
                \
            c -> d -> e -> f -> g


    d.merged_to = e
    representent(d) = g
    d.merged_from = {a, b, c, d}
    d.equivs = {a, b, c, d, e, f, g}

    """

    symbol: S
    fellows: set[S] = set()
    representent: SymbolMergeHistory[S] | None = None

    @model_validator(mode="after")
    def add_self_to_fellows(self) -> Self:
        self.fellows.add(self.symbol)
        return self


def representent_of(merge_history: SymbolMergeHistory[S]) -> SymbolMergeHistory[S]:
    if merge_history.representent is None:
        return merge_history
    return representent_of(merge_history.representent)


def merge_symbols(
    symbol_history_to_merge: SymbolMergeHistory[S],
    symbols_histories: list[SymbolMergeHistory[S]],
    all_symbols: list[S],
) -> None:
    """Merge all nodes."""
    for other_history in symbols_histories:
        _merge_one(symbol_history_to_merge, other_history)

    for symbol_history in symbols_histories + [symbol_history_to_merge]:
        if representent_of(symbol_history) != symbol_history:
            all_symbols.remove(symbol_history.symbol)


def _merge_one(
    symbol: SymbolMergeHistory[S], other_symbol: SymbolMergeHistory[S]
) -> SymbolMergeHistory[S]:
    self_rep = representent_of(symbol)
    other_rep = representent_of(other_symbol)
    if self_rep == other_rep:
        return self_rep

    other_rep.representent = self_rep
    self_rep.fellows.update(other_rep.fellows)
    other_rep.fellows.update(symbol.fellows)
    return self_rep
