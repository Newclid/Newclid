# mypy: ignore-errors
from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Any, Literal, Optional

from numpy import pi

from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.predicates.constant_angle import angle_between_4_points
from newclid.symbols.symbols_registry import SymbolsRegistry
from newclid.tools import fraction_to_angle, fraction_to_ratio, str_to_fraction


class AngleEquation(PredicateInterface):
    """aequation a A b B c C ... k -
    Represents the linear equation a * A + b * B + c * C + ... = k. The coefficients (small letters) are signed rational numbers,the capitalized letters are 4-tuples of points representing angles, k is an integer.

    The syntax of k is either a fraction of pi like 2pi/3 for radians or a number followed by a 'o' like 120o for degree.

    This generates an equation that can be added to the deductor for reasoning (AR for example).
    """

    predicate_type: Literal[PredicateType.ANGLE_EQUATION] = PredicateType.ANGLE_EQUATION
    coefficients: list[Fraction]
    angles: list[tuple[str, ...]]
    constant: Fraction

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        if (len(args) - 1) % 5 != 0:
            return None

        y = args[-1]
        pairs: list[tuple[Fraction, tuple[str, ...]]] = []
        for i in range(0, len(args) - 1, 5):
            coefficient = str_to_fraction(args[i])
            p1, p2, p3, p4 = args[i + 1 : i + 5]
            if p1 == p2 or p3 == p4:
                return None
            p1, p2 = sorted((p1, p2))
            p3, p4 = sorted((p3, p4))
            points = (p1, p2, p3, p4)
            pairs.append((coefficient, points))

        pairs_tuple = tuple(pairs)
        pairs_tuple = tuple(
            sorted(pairs_tuple, key=lambda pair: tuple(var for var in pair[1]))
        )

        # Merging coefficients of the same angle
        simplified_equation: list[tuple[Fraction, tuple[str, ...]]] = []
        for angle_points, group in itertools.groupby(
            pairs_tuple, key=lambda pair: pair[1]
        ):
            coefficient_sum = sum(pair[0] for pair in group)
            if coefficient_sum != 0:
                simplified_equation.append((coefficient_sum, angle_points))  # type: ignore

        if not simplified_equation:
            return None

        k = str_to_fraction(y)
        k %= 1
        equation: list[PredicateArgument] = [
            PredicateArgument(term)
            for coefficient, points in simplified_equation
            for term in (fraction_to_ratio(coefficient),) + points
        ]
        return tuple(equation + [PredicateArgument(fraction_to_angle(k))])

    @classmethod
    def parse(
        cls, args: tuple[PredicateArgument, ...], symbols: SymbolsRegistry
    ) -> Optional[tuple[Any, ...]]:
        preparse = cls.preparse(args)
        if not preparse:
            return None

        parsed: list[PredicateArgument] = []

        for i in range(0, len(preparse) - 1, 5):
            coefficient = str_to_fraction(preparse[i])
            points = preparse[i + 1 : i + 5]
            p1, p2, p3, p4 = symbols.points.names2points(points)
            parsed += [coefficient, p1, p2, p3, p4]  # type: ignore

        k = preparse[-1]
        return tuple(parsed + [str_to_fraction(k)])

    def check_numerical(self) -> bool:
        equation = self.args[:-1]
        expected_value = self.args[-1] * pi % pi
        evaluated_expression = 0

        for i in range(0, len(equation) - 1, 5):
            coefficient = float(equation[i])
            a, b, c, d = equation[i + 1 : i + 5]
            angle_value = angle_between_4_points(a, b, c, d)
            evaluated_expression += coefficient * angle_value

        evaluated_expression %= pi

        return close_enough(evaluated_expression, expected_value)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        k = self.args[-1]
        equation = self.args[:-1]
        list_of_tokens: list[str] = []
        for i in range(0, len(equation) - 1, 5):
            coefficient = equation[i]
            p1, p2, p3, p4 = equation[i + 1 : i + 5]
            list_of_tokens.append(fraction_to_ratio(coefficient))
            list_of_tokens.append(p1.name)
            list_of_tokens.append(p2.name)
            list_of_tokens.append(p3.name)
            list_of_tokens.append(p4.name)
        list_of_tokens.append(fraction_to_angle(k))
        return tuple(list_of_tokens)

    def __str__(self) -> str:
        equation = self.args[0:-1]
        k = self.args[-1]
        pretty_string = ""

        for i in range(0, len(equation) - 1, 5):
            coefficient = equation[i]
            a, b, c, d = equation[i + 1 : i + 5]

            pretty_string += f"{fraction_to_ratio(coefficient)} ∠({a}{b},{c}{d}) + "

        pretty_string = pretty_string[:-2]  # Remove the last ' + '

        return pretty_string + f" = {fraction_to_angle(k)}"
