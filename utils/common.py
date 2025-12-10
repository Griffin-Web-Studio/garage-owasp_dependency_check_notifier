import sys


def log(str: str):
    """
    Print log

    :param str: log string
    :type str: str
    """
    print(str)


def err(str: str):
    """
    Print err

    :param str: error string
    :type str: str
    """
    print(str, file=sys.stderr)
