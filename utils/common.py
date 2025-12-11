import sys

from settings import Settings


def log(*args: str):
    """
    Print log

    :param args: log string
    :type args: str
    """
    if not Settings.get_instance().quiet:
        print(*args)


def err(*args: str):
    """
    Print err

    :param args: error string
    :type args: str
    """
    if not Settings.get_instance().quiet:
        print(*args, file=sys.stderr)
