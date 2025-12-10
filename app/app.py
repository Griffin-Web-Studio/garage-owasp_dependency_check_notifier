from app.notifier_type.discord import discord_notification
from settings import Settings


def run_notifier(settings: Settings) -> int:
    """
    Core notifier function

    :param settings: settings derived from env vars
    :type settings: Settings
    :return: software exit code
    :rtype: int
    """

    if settings.discord_webhook_url:
        return discord_notification(settings)

    return 0
