from enum import Enum
from disnake import Colour


class State(Enum):
    OK = "ok"
    ISSUE = "issue"
    VULNERABLE = "vulnerable"


def state_colours(state: State | None) -> Colour:
    """
    Discord embed colour

    :param state: OK (green), ISSUE (yellow), VULNERABLE (red).
    :type state: State
    :return: Disnake embed colour
    :rtype: Colour
    """

    if state == State.VULNERABLE:
        return Colour.red()

    elif state == State.ISSUE:
        return Colour.orange()

    elif state == State.OK:
        return Colour.green()

    else:
        return Colour.blue()
