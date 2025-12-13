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
    _title: str
    _prefix: str
    _context: str
    _suffix: str
    _has_vuln: bool = False
    _has_issue: bool = False
    def __init__(self, settings: Settings):
        """
        Discord Notifier module initialiser for sending out Discord embeds

        :param self: ref to class self
        :param settings: settings derived from env vars
        :type settings: Settings
        """
        self._settings = settings

    def notify(self, data: Any):
        self._title = self._make_title(
            has_vuln=self._has_vuln,
            has_issue=self._has_issue,
            project_label=self._settings.project_label,
            branch=self._settings.ci_commit_ref_name)

        webhook = SyncWebhook.from_url(self._settings.discord_webhook_url)

        embed = disnake.Embed(
            title=self._title,
            description="Embed Description",
            url=TEMP_URL,
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

    def _make_title(
            self,
            has_vuln: bool,
            has_issue: bool,
            project_label: str,
            branch: str) -> str:
        if has_vuln:
            self._prefix = "🚨 Vulnerabilities detected"
        elif has_issue:
            self._prefix = "⚠️ Dependency-Check scan issue"
        else:
            self._prefix = "✅ No vulnerabilities detected"

        self._context = project_label or self._settings.ci_project_path.strip()

        if self._context and branch:
            self._suffix = f" ({self._context} @ {branch})"
        elif self._context:
            self._suffix = f" ({self._context})"
        elif branch:
            self._suffix = f" ({branch})"

        return self._prefix + self._suffix
