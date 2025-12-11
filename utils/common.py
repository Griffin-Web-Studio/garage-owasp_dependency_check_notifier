import sys


def log(*args: str):
    """
    Print log

    :param args: log string
    :type args: str
    """
    print(*args)


def err(*args: str):
    """
    Print err

    :param args: error string
    :type args: str
    """
    print(*args, file=sys.stderr)
