from __future__ import annotations
import datetime
import disnake
from disnake import SyncWebhook

from app.DCParser import DCParser
from app.notifier_type.utils import State, state_colours
from settings import Settings
from utils.common import log

GWS_ICON = "https://files.gwssecureserver.co.uk/files/gws/logo-outline-ico.png"
# TEMP_BANNER = "https://files.gwssecureserver.co.uk/files/email/v4/offer.png"
TEMP_URL = "https://griffin-web.studio/"


class DiscordNotifier:
    _settings: Settings
    _title: str
    _desc: str = ""
    _has_vuln: bool = False
    _has_issue: bool = False
    _colour = state_colours(State.OK)
    _has_report: bool = False

    def __init__(self, settings: Settings):
        """
        Discord Notifier module initialiser for sending out Discord embeds

        :param self: ref to class self
        :param settings: settings derived from env vars
        :type settings: Settings
        """
        self._settings = settings
        # If JSON missing, report an issue
        self._check_report_presence()

    def notify(self, parser: DCParser | None):

            # fields: List[Tuple[str, str, bool]] = [
            #     ("Pipeline", self._settings.pipeline_url or "N/A", False),
            #     ("HTML present?", "Yes" if self._settings.report_html else "No", True),
            #     ("JSON present?", "No", True),
            # ]
            # links_field = build_links_field(links)
            # if links_field:
            #     fields.append(links_field)

            # embed = build_embed(description=desc, url=links.get(
            #     "pipeline"), colo

            # r=colour_for_state("issues"), fields=fields)

            # # Decide payload based on NOTIFY_MODE
            # if NOTIFY_MODE == "plain":
            #     send_via_disnake(WEBHOOK_URL, content=title + "\n" + desc,
            #                      embed=None, html_path=html_path if html_exists else None)
            # else:
            #     send_via_disnake(WEBHOOK_URL, content=None, embed=embed,
            #                      html_path=html_path if html_exists else None)

            # log("Sent scan issue notification.")
            # # Do not fail on missing JSON unless you want to; return 1 for visibility.
            # return 1

        if parser and parser.failed:
            self._has_issue = True
            self._has_vuln = False
            self._desc = (
                f"Parser Experienced some issue `"
                f"{self._settings.ci_project_path or self._settings.project_label or 'project'}"
                f"` (`{self._settings.ci_commit_ref_name or 'ref'}`)."
            )

        filtered = None
        counts = None

        if parser:
            data_pack = parser.get_data()
            if data_pack and data_pack.counts:
                counts = data_pack.counts
            filtered = parser.filter_by_min_severity(
                self._settings.min_severity)

        if counts and (counts["critical"] > 0 or counts["high"]) > 0:
            self._has_vuln = True

        self._title = self._make_title(
            project_label=self._settings.project_label,
            branch=self._settings.ci_commit_ref_name)

        webhook = SyncWebhook.from_url(self._settings.discord_webhook_url)

        embed = disnake.Embed(
            title=self._title,
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

        if counts:
            for count in counts:
                embed.add_field(
                    name=count.capitalize(),
                    value=counts[count],
                    inline=True)

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
                    severity = "🅾️ HIGHT"
                elif dep.severity.lower() == 'critical':
                    severity = "📛 CRITICAL!!!"

                if dep.scorev3 and dep.scorev3 != "Unknown":
                    cvssv3 = "{:.1f}".format(float(dep.scorev3))

                embed.add_field(
                    name=f"{severity} - {dep.dependency} "
                    f"(ver: `{dep.version}`) "
                    f"CVSSv2: `{dep.scorev2}` "
                    f"CVSSv3: `{cvssv3}`",
                    value=f"""
                    [{", ".join(dep.ids)}]({dep.url})
                    """,
                    inline=False)

        webhook.send(embed=embed)
        log("Notification sent.")

        return 0

    def _check_report_presence(self) -> None:
        """
        Method to determine if report file is present

        :param self: ref to class self
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

        self._has_report = True

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
