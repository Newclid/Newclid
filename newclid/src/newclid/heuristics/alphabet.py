from newclid.jgex.formulation import ALPHABET
from newclid.predicate_types import PredicateArgument


def get_available_from_alphabet(
    current_points: list[PredicateArgument],
) -> PredicateArgument | None:
    """
    Get the first available symbol in the alphabet not used in list.

    Args:
        list (List[str]): A list of symbols to check (typically point names).

    Returns:
        str: The first available symbol from the list.
    """
    for symbol in ALPHABET:
        if symbol not in current_points:
            return PredicateArgument(symbol)
    return None
