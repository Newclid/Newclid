from __future__ import annotations

from typing import Annotated

from pydantic import Field

from newclid.symbols.circles_registry import CirclesRegistry, CircleSymbol
from newclid.symbols.lines_registry import LinesRegistry, LineSymbol
from newclid.symbols.points_registry import PointsRegisty

LineOrCircle = Annotated[LineSymbol | CircleSymbol, Field(discriminator="symbol_type")]


class SymbolsRegistry:
    def __init__(self) -> None:
        self.points = PointsRegisty()
        self.lines = LinesRegistry()
        self.circles = CirclesRegistry()
