from typing import NewType

import numpy as np
from sympy.core.backend import Symbol as SympySymbol  # type: ignore

from newclid.deductors.sympy_ar.ar_table import ARTable
from newclid.numerical import close_enough
from newclid.numerical.geometries import LineNum
from newclid.symbols.lines_registry import LineSymbol

LineSympySymbol = NewType("LineSympySymbol", SympySymbol)  # type: ignore


class AnglesTable:
    def __init__(self, ar_table: ARTable) -> None:
        self.inner_table = ar_table

        self.expected_lines: dict[LineSympySymbol, LineNum] = {}
        self.expected_aconsts: dict[tuple[LineSympySymbol, LineSympySymbol], float] = {}
        self.expected_parallels: set[tuple[LineSympySymbol, LineSympySymbol]] = set()
        self.expected_perpendiculars: set[tuple[LineSympySymbol, LineSympySymbol]] = (
            set()
        )
        self.expected_eqangles: set[
            tuple[LineSympySymbol, LineSympySymbol, LineSympySymbol, LineSympySymbol]
        ] = set()

        self.newclid_to_sympy_symbol: dict[LineSymbol, LineSympySymbol] = {}
        self.sympy_to_newclid_symbol: dict[LineSympySymbol, LineSymbol] = {}

    def line_symbol(self, newclid_symbol: LineSymbol) -> SympySymbol:
        if newclid_symbol not in self.newclid_to_sympy_symbol:
            angle_symbol = LineSympySymbol(SympySymbol(str(newclid_symbol)))
            self.newclid_to_sympy_symbol[newclid_symbol] = angle_symbol
            self.sympy_to_newclid_symbol[angle_symbol] = newclid_symbol
            newclid_symbol = self.sympy_to_newclid_symbol[angle_symbol]
            self._add_angle_absolute(angle_symbol, num=newclid_symbol.num)
        return self.newclid_to_sympy_symbol[newclid_symbol]

    def _add_angle_absolute(self, angle: LineSympySymbol, num: LineNum):
        for other_angle, other_line_num in self.expected_lines.items():
            aconst = (angle, other_angle)
            aconst_value = num.angle_to(other_line_num)

            if num.is_parallel(other_line_num):
                self.expected_parallels.add((angle, other_angle))
                continue

            if num.is_perp(other_line_num):
                self.expected_perpendiculars.add((angle, other_angle))

            reversed_aconst = (other_angle, angle)
            reversed_aconst_value = (np.pi - aconst_value) % np.pi

            # Add the eqangle possibilities for both directions.
            for other_aconst, other_aconst_value in self.expected_aconsts.items():
                if close_enough(aconst_value, other_aconst_value):
                    self.expected_eqangles.add((*aconst, *other_aconst))
                if close_enough(reversed_aconst_value, other_aconst_value):
                    self.expected_eqangles.add((*reversed_aconst, *other_aconst))

            self.expected_aconsts[aconst] = aconst_value
            self.expected_aconsts[reversed_aconst] = reversed_aconst_value

        self.expected_lines[angle] = num
