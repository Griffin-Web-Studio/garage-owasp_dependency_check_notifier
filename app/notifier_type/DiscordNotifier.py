from __future__ import annotations
import datetime
from typing import Optional
import disnake
from disnake import SyncWebhook, Embed

from app.DCParser import DCParser
from app.notifier_type.utils import State, state_colours
from settings import Settings
from utils.common import err, log

GWS_ICON = "https://files.gwssecureserver.co.uk/files/gws/logo-outline-ico.png"
# TEMP_BANNER = "https://files.gwssecureserver.co.uk/files/email/v4/offer.png"
TEMP_URL = "https://griffin-web.studio/"


class DiscordNotifier:
    _settings: Settings
    _parser: Optional[DCParser]
    _title: str = ""
    _desc: str = ""
    _has_vuln: bool = False
    _has_issue: bool = False
    _colour = state_colours(State.ISSUE)
    _embed: Optional[Embed] = None
    _has_report: bool = False
    _webhook: SyncWebhook

    def __init__(self, settings: Settings, parser: Optional[DCParser]):
        """
        Discord Notifier module initialiser for sending out Discord embeds

        :param self: ref to class self
        :param settings: settings derived from env vars
        :type settings: Settings
        :param parser: Dependency Vulnerability Report Parser
        :type parser: Optional[DCParser]
        """
        self._settings = settings
        self._parser = parser
        self._webhook = SyncWebhook.from_url(
            self._settings.discord_webhook_url)

    def notify(self):
        try:
            self._check_report_presence()
        except FileNotFoundError as e:
            err(e)
            return 0

        if self._parser and self._parser.failed:
            self._has_issue = True
            self._has_vuln = False
            self._desc = (
                f"Parser Experienced some issue `"
                f"{self._settings.ci_project_path or self._settings.project_label or 'project'}"
                f"` (`{self._settings.ci_commit_ref_name or 'ref'}`)."
            )

        filtered = None
        counts = None

        if self._parser:
            data_pack = self._parser.get_data()
            if data_pack and data_pack.counts:
                counts = data_pack.counts
            filtered = self._parser.filter_by_min_severity(
                self._settings.min_severity)

        if counts and (counts["critical"] > 0 or counts["high"]) > 0:
            self._has_vuln = True

        self._embed = self._create_embed()

        self._embed_vuln_counter(counts=counts)

        if filtered:
            max_embed = 20

            for dep in filtered:
                if max_embed == 0:
                    break

                max_embed -= 1

                severity = "N/A"
                cvssv3 = "n/a"

                if dep.severity.lower() == 'low':
                    severity = "🟩 Low"
                elif dep.severity.lower() == 'medium':
                    severity = "🟨 Medium"
                elif dep.severity.lower() == 'moderate':
                    severity = "🟧 Moderate"
                elif dep.severity.lower() == 'high':
                    severity = "🅾️ HIGH"
                elif dep.severity.lower() == 'critical':
                    severity = "📛 CRITICAL!!!"

                if dep.scorev3 and dep.scorev3 != "Unknown":
                    cvssv3 = "{:.1f}".format(float(dep.scorev3))

                self._embed.add_field(
                    name=f"{severity} - {dep.dependency} "
                    f"(ver: `{dep.version}`) "
                    f"CVSSv2: `{dep.scorev2}` "
                    f"CVSSv3: `{cvssv3}`",
                    value=f"""
                    [{", ".join(dep.ids)}]({dep.url})
                    """,
                    inline=False)
        self._send_notification()

        return 0

    def _check_report_presence(self) -> None:
        """
        Method to determine if report file is present

        :param self: ref to class self
        :raises FileNotFoundError: Missing file
        """
        if not self._settings.report_json.exists():
            self._has_issue = True
            self._has_vuln = False
            self._desc = (
                f"Reports missing for `"
                f"{self._settings.ci_project_path
                   or self._settings.project_label
                   or 'project'}"
                f"` (`{self._settings.ci_commit_ref_name or 'ref'}`)."
            )

            self._create_embed()
            self._send_notification()
            raise FileNotFoundError(
                f"The file '{self._settings.report_json}' does not exist.")

    def _create_embed(self):
        """
        Method to Create the embed

        :param self: reference to self
        """
        embed = disnake.Embed(
            title=self._make_title(
                project_label=self._settings.project_label,
                branch=self._settings.ci_commit_ref_name),
            description=self._desc,
            url=self._settings.ci_project_url,
            color=self._colour,
            timestamp=datetime.datetime.now(),
        )

        embed.set_author(
            name="OWASP | DC Notifier - By GWS Garage",
            url=TEMP_URL,
            icon_url=GWS_ICON,
        )

        # embed.set_footer(
        #     text="Embed Footer",
        #     icon_url=TEMP_ICON,
        # )

        embed.set_thumbnail(url=self._settings.dc_icon)
        # embed.set_image(url=TEMP_BANNER)
        return embed

    def _make_title(
            self,
            project_label: str,
            branch: str) -> str:
        """
        Method for generating title based on parser findings

        :param self: ref to class self
        :param project_label: Project Label (defaults to project path)
        :type project_label: str
        :param branch: project branch
        :type branch: str
        :return: new title
        :rtype: str
        """
        prefix: str = ""
        context: str = ""
        suffix: str = ""

        if self._has_vuln:
            prefix = "🚨 Vulnerabilities detected"
            self._colour = state_colours(State.VULNERABLE)
        elif self._has_issue:
            prefix = "⚠️ Dependency-Check scan issue"
            self._colour = state_colours(State.ISSUE)
        else:
            prefix = "✅ No vulnerabilities detected"

        context = project_label or self._settings.ci_project_path.strip()

        if context and branch:
            suffix = f" ({context} @ {branch})"
        elif context:
            suffix = f" ({context})"
        elif branch:
            suffix = f" ({branch})"

        return prefix + suffix

    def _embed_vuln_counter(
            self,
            counts: dict[str, int] | None) -> None:
        """
        Method for embedding vulnerability counter

        :param self: ref to class self
        :param counts: Key value pair of vuln level to integer count
        :type counts: dict[str, int] | None
        """

        if counts and self._has_vuln and self._embed and not self._has_issue:
            value = ""

            for count in counts:
                value += f"**{count.capitalize()}**: `{counts[count]}`\n"

            self._embed.add_field(
                name="Vulnerabilities Count",
                value=value,
                inline=False)

    def _send_notification(self):
        if self._embed:
            self._webhook.send(embed=self._embed)
            log("Notification sent.")
            return

        log("Notification not sent due to missing embeds.")
