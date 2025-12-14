from app.DCParser import DCParser
from app.notifier_type.DiscordNotifier import DiscordNotifier
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
    parser = None

    if settings.report_json.exists():
        parser = DCParser(settings)
    else:
        err("Can't resolve the json report in the path location: ",
            str(settings.report_json))

    if settings.discord_webhook_url:
        notifier = DiscordNotifier(settings)

        return notifier.notify(parser)

    return 0
