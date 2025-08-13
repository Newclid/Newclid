# mypy: ignore-errors

from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Any, Literal, Optional

from newclid.numerical import close_enough
from newclid.predicate_types import PredicateArgument
from newclid.predicates._index import PredicateType
from newclid.predicates._interface import PredicateInterface
from newclid.symbols.points_registry import Segment
from newclid.symbols.symbols_registry import SymbolsRegistry
from newclid.tools import (
    fraction_to_len,
    fraction_to_ratio,
    str_to_fraction,
)


class LengthEquation(PredicateInterface):
    """lequation a A b B c C ... k -
    Represents the equation a * A + b * B + c * C + ... = k. The coefficients (small letters) are signed rational numbers.

    The capitalized letters can represent products of lengths, k should be given as a float.

    This generates an equation that can be added to the deductor for reasoning (AR for example), or used in theorems.
    """

    predicate_type: Literal[PredicateType.LENGTH_EQUATION] = (
        PredicateType.LENGTH_EQUATION
    )
    coefficients: list[Fraction]
    lengths: list[Segment]
    constant: Fraction

    @staticmethod
    def preparse(
        args: tuple[PredicateArgument, ...],
    ) -> tuple[PredicateArgument, ...] | None:
        k = args[-1]
        equation = args[:-1]

        counter = 0
        split_equation = []
        while counter < len(equation):
            term = []
            coefficient = equation[counter]
            coefficient = str_to_fraction(coefficient)

            term.append(coefficient)
            p1, p2 = sorted((equation[counter + 1], equation[counter + 2]))
            if p1 == p2:
                return None
            term.append((p1, p2))
            counter += 3
            while counter < len(equation) and equation[counter] == "*":
                p1, p2 = sorted((equation[counter + 1], equation[counter + 2]))
                if p1 == p2:
                    return None
                term.append((p1, p2))
                counter += 3
            term_to_sort = tuple(term[1:])
            sorted_term = sorted(term_to_sort)
            sorted_term_with_coeff = [term[0], sorted_term]
            split_equation.append(tuple(sorted_term_with_coeff))

        sorted_terms = sorted(
            split_equation, key=lambda term: tuple(var for var in term[1])
        )

        simplified_equation = []
        for term, group in itertools.groupby(sorted_terms, key=lambda pair: pair[1]):
            coefficient_sum = sum(pair[0] for pair in group)
            if coefficient_sum != 0:
                simplified_equation.append((coefficient_sum, term))

        if not simplified_equation:
            return None
        final_equation: list[
            Fraction | tuple[PredicateArgument, PredicateArgument] | str
        ] = []
        for coefficient, lengths in simplified_equation:
            final_equation.append(fraction_to_ratio(coefficient))
            j = 0
            for length in lengths:
                p1, p2 = length
                final_equation.append(p1)
                final_equation.append(p2)
                if j < (len(lengths) - 1):
                    final_equation.append("*")
                    j += 1

        return tuple(final_equation + [fraction_to_len(str_to_fraction(k))])

    @classmethod
    def parse(
        cls, args: tuple[PredicateArgument, ...], symbols: SymbolsRegistry
    ) -> Optional[tuple[Any, ...]]:
        preparse = cls.preparse(args)
        if not preparse:
            return None
        equation = preparse[:-1]
        parsed = []

        for i in range(0, len(equation) - 1, 3):
            if equation[i] != "*":
                coefficient = str_to_fraction(equation[i])
                points = equation[i + 1 : i + 3]
                p1, p2 = symbols.points.names2points(points)
                parsed += [coefficient, p1, p2]
            else:
                points = equation[i + 1 : i + 3]
                p1, p2 = symbols.points.names2points(points)
                parsed += ["*", p1, p2]
        k = preparse[-1]
        return tuple(parsed + [str_to_fraction(k)])

    def check_numerical(self) -> bool:
        expected_value = float(self.args[-1])
        equation = self.args[:-1]

        evaluated_expression = 0.0
        term = 0.0
        i = 0

        while i < len(equation) - 1:
            evaluated_expression += term
            term = 1.0
            coefficient = equation[i]
            coefficient = float(coefficient)
            p1 = equation[i + 1]
            p2 = equation[i + 2]
            length_value = p1.num.distance(p2.num)
            term *= coefficient * length_value
            i += 3

            while i < len(equation) - 1 and equation[i] == "*":
                p1 = equation[i + 1]
                p2 = equation[i + 2]
                length_value = p1.num.distance(p2.num)
                term *= length_value
                i += 3

        evaluated_expression += term

        return close_enough(evaluated_expression, expected_value)

    def to_tokens(self) -> tuple[PredicateArgument, ...]:
        k = self.args[-1]
        equation = self.args[:-1]

        list_of_tokens: list[PredicateArgument] = []
        for i in range(0, len(equation) - 1, 3):
            if equation[i] != "*":
                coefficient = equation[i]
                coefficient = fraction_to_ratio(coefficient)
                p1 = equation[i + 1]
                p2 = equation[i + 2]
                list_of_tokens.append(coefficient)
                list_of_tokens.append(p1.name)
                list_of_tokens.append(p2.name)
            else:
                p1 = equation[i + 1]
                p2 = equation[i + 2]
                list_of_tokens.append("*")
                list_of_tokens.append(p1.name)
                list_of_tokens.append(p2.name)

        list_of_tokens.append(fraction_to_len(k))
        return tuple(list_of_tokens)

    def __str__(self) -> str:
        equation = self.args[:-1]
        k = self.args[-1]
        pretty_string = ""
        for i in range(0, len(equation) - 1, 3):
            if equation[i] != "*":
                coefficient = fraction_to_ratio(equation[i])
                p1 = equation[i + 1]
                p2 = equation[i + 2]
                pretty_string += f"{coefficient} * |{p1}{p2}| "
            else:
                p1 = equation[i + 1]
                p2 = equation[i + 2]
                pretty_string += f"* |{p1}{p2}| "
                if equation[i + 3] != "*":
                    pretty_string += " + "

        pretty_string = pretty_string[:-2]  # Remove the last ' + '

        return pretty_string + f" = {fraction_to_len(k)}"
