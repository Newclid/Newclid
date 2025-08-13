from sympy.core.backend import Symbol as SympySymbol  # type: ignore

from newclid.deductors.sympy_ar.ar_table import ARTable
from newclid.numerical import close_enough
from newclid.symbols.points_registry import Segment


class RatiosTable:
    def __init__(self, ar_table: ARTable) -> None:
        self.inner_table = ar_table

        self.expected_lconsts: dict[SympySymbol, float] = {}
        self.expected_rconsts: dict[tuple[SympySymbol, SympySymbol], float] = {}
        self.expected_congs: set[tuple[SympySymbol, SympySymbol]] = set()
        self.expected_eqratios: set[
            tuple[SympySymbol, SympySymbol, SympySymbol, SympySymbol]
        ] = set()

        self.segment_to_sympy_symbol: dict[Segment, SympySymbol] = {}
        self.sympy_symbol_to_str_symbol: dict[SympySymbol, Segment] = {}

    def segment_log_length(self, segment: Segment) -> SympySymbol:
        p0, p1 = segment
        if p0.name > p1.name:
            p0, p1 = p1, p0

        if (p0, p1) not in self.segment_to_sympy_symbol:
            name = f"log_seg_length_{p0.name}_{p1.name}"
            length_symbol = SympySymbol(name)
            self.segment_to_sympy_symbol[(p0, p1)] = length_symbol
            self.sympy_symbol_to_str_symbol[length_symbol] = (p0, p1)
            lenght_value = p0.num.distance(p1.num)
            self._add_log_length(length_symbol, lenght_value)

        return self.segment_to_sympy_symbol[(p0, p1)]

    def _add_log_length(self, length_symbol: SympySymbol, numerical_value: float):
        for other_symbol, other_length in self.expected_lconsts.items():
            new_ratio = (length_symbol, other_symbol)
            new_ratio_value = numerical_value / other_length

            if close_enough(numerical_value, other_length):
                self.expected_congs.add((length_symbol, other_symbol))

            for other_ratio, other_ratio_value in self.expected_rconsts.items():
                if close_enough(new_ratio_value, other_ratio_value):
                    self.expected_eqratios.add((*new_ratio, *other_ratio))

            self.expected_rconsts[new_ratio] = new_ratio_value

            self.expected_rconsts[(other_symbol, length_symbol)] = 1 / new_ratio_value

        self.expected_lconsts[length_symbol] = numerical_value
