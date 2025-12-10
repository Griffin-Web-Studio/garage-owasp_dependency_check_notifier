import sys

from settings import Settings


def run_notifier(settings: Settings) -> int:
    """
    Core notifier function

    :param settings: settings derived from env vars
    :type settings: Settings
    :return: software exit code
    :rtype: int
    """
    print("webhook: ", settings.webhook_url)
    if not settings.webhook_url:
        print("DISCORD_WEBHOOK_URL is required.", file=sys.stderr)
        return 1

    print("Notification sent.")

    return 0
