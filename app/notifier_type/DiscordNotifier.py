from __future__ import annotations
import datetime
import disnake
from disnake import SyncWebhook

from settings import Settings
from utils.common import log


def discord_notification(settings: Settings) -> int:
    """
    Discord Notifier module for sending out Discord embeds

    :param settings: settings derived from env vars
    :type settings: Settings
    :return: software exit code
    :rtype: int
    """
    webhook = SyncWebhook.from_url(settings.discord_webhook_url)

    embed = disnake.Embed(
        title="Embed Title",
        description="Embed Description",
        url="https://griffin-web.studio/",
        color=disnake.Colour.from_rgb(27, 52, 100),
        timestamp=datetime.datetime.now(),
    )

    embed.set_author(
        name="Embed Author",
        url="https://griffin-web.studio/",
        icon_url="https://files.gwssecureserver.co.uk/files/gws/logo-outline-ico.png",
    )
    embed.set_footer(
        text="Embed Footer",
        icon_url="https://files.gwssecureserver.co.uk/files/gws/logo-outline-ico.png",
    )

    embed.set_thumbnail(
        url="https://files.gwssecureserver.co.uk/files/gws/logo-outline-ico.png")
    embed.set_image(
        url="https://files.gwssecureserver.co.uk/files/email/v4/offer.png")

    embed.add_field(name="Regular Title", value="Regular Value", inline=False)
    embed.add_field(name="Inline Title", value="Inline Value", inline=True)
    embed.add_field(name="Inline Title", value="Inline Value", inline=True)
    embed.add_field(name="Inline Title", value="Inline Value", inline=True)

    webhook.send(embed=embed)
    log("Notification sent.")
    return 0
