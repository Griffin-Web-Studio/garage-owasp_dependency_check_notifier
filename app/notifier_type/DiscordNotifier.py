from __future__ import annotations
import datetime
from typing import Any
import disnake
from disnake import SyncWebhook

from settings import Settings
from utils.common import log

TEMP_ICON = "https://files.gwssecureserver.co.uk/files/gws/logo-outline-ico.png"
TEMP_BANNER = "https://files.gwssecureserver.co.uk/files/email/v4/offer.png"
TEMP_URL = "https://griffin-web.studio/"


class DiscordNotifier:
    _settings: Settings
    def __init__(self, settings: Settings):
        """
        Discord Notifier module initialiser for sending out Discord embeds
        
        :param self: ref to class self
        :param settings: settings derived from env vars
        :type settings: Settings
        """
        self._settings = settings

    def notify(self, data: Any):
        webhook = SyncWebhook.from_url(self._settings.discord_webhook_url)

        embed = disnake.Embed(
            title="Embed Title",
            description="Embed Description",
            url="https://griffin-web.studio/",
            color=disnake.Colour.from_rgb(27, 52, 100),
            timestamp=datetime.datetime.now(),
        )

        embed.set_author(
            name="Embed Author",
            url=TEMP_URL,
            icon_url=TEMP_ICON,
        )
        embed.set_footer(
            text="Embed Footer",
            icon_url=TEMP_ICON,
        )

        embed.set_thumbnail(url=TEMP_ICON)
        embed.set_image(url=TEMP_BANNER)

        embed.add_field(
            name="Regular Title",
            value="Regular Value",
            inline=False)
        embed.add_field(
            name="Inline Title",
            value="Inline Value",
            inline=True
        )
        embed.add_field(
            name="Inline Title",
            value="Inline Value",
            inline=True
        )
        embed.add_field(
            name="Inline Title",
            value="Inline Value",
            inline=True
        )

        webhook.send(embed=embed)
        log("Notification sent.")

        return 0
