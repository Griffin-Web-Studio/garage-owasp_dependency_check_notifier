from app.notifier_type.discord import discord_notification
from settings import Settings
from utils.common import err


def run_notifier(settings: Settings) -> int:
    """
    Core notifier function

    :param settings: settings derived from env vars
    :type settings: Settings
    :return: software exit code
    :rtype: int
    """

    if not settings.report_json.exists():
        err("Can't resolve the json report in the path location: ",
            str(settings.report_json))

        return 1

    if settings.discord_webhook_url:
        return discord_notification(settings)

    return 0
