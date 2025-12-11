from disnake import Colour


def state_colours(state: str) -> Colour:
    """
    Discord embed colour

    :param state: 'ok' (green), 'issues' (yellow), 'vulns' (red).
    :type state: str
    :return: Disnake embed colour
    :rtype: Colour
    """
    if state == "vulns":
        return Colour(0xE74C3C)  # red

    if state == "issues":
        return Colour(0xE1A32A)  # yellow

    return Colour(0x2ECC71)      # green
