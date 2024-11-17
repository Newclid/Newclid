def insert_aux_to_premise(pstring: str, auxstring: str) -> str:
    """Insert auxiliary constructs from proof to premise.

    Args:
      pstring: str: describing the problem to solve.
      auxstring: str: describing the auxiliar construction.

    Returns:
      str: new pstring with auxstring inserted before the conclusion.
    """
    setup, goal = pstring.split(" ? ")
    return setup + "; " + auxstring + " ? " + goal
