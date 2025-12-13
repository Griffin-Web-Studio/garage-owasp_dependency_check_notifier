from __future__ import annotations
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, List


def _parse_bool(val: str | None, default: bool = False) -> bool:
    """
    Utility for converting raw string values into boolean.

    This function parses a string value commonly received from environment
    variables to return a standardised boolean representation.
    If the input value is None, the function returns a specified default value,
    which itself defaults to "false" as a value of last resort.

    :param val: Raw value received from environment.
    :type val: str | None
    :param default: Default value to return if val is evaluated as None.
    :type default: bool
    :return: Value represented in boolean form
    :rtype: bool
    """
    if val is None:
        return default

    return val.strip().lower() in ("1", "true", "yes", "y", "on")


def _parse_int(val: str | None, default: int) -> int:
    """
    Utility for converting raw string values into integers.

    This function attempts to parse a string value into an integer. If the input
    value is None or an empty string, the function returns a specified default
    value. If the input cannot be converted to an integer, a ValueError is
    raised.

    :param val: Raw value received, which can be None or a string representation
    of an integer.
    :type val: str | None
    :param default: Default integer value to return
    :type default: int
    :return: Converted integer value from the value string or the default value.
    :rtype: int
    :raises ValueError: If val is not convertible to an integer.
    """
    if val is None or val.strip() == "":
        return default

    try:
        return int(val.strip())
    except ValueError:
        raise ValueError(f"Expected integer, got: {val!r}")


class Severity(str, Enum):
    """
    Severity Enum
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def load_env(cls, value: str | None, default: Severity | None = None
                 ) -> Severity:
        if not value:
            return default or cls.LOW

        v = value.strip().upper()

        try:
            return cls(v)  # Lookup by value, not by name

        except ValueError:
            allowed = ", ".join(m.value for m in cls)

            raise ValueError(
                f"Invalid MIN_SEVERITY {value!r}. Must be one of: {allowed}")


class NotifyMode(str, Enum):
    LINK = "link"
    SUMMARY = "summary"
    BOTH = "both"
    PLAIN = "plain"

    @classmethod
    def load_env(cls, value: str | None, default: NotifyMode | None = None
                 ) -> NotifyMode:
        if not value:
            return default or cls.BOTH

        v = value.strip().lower()

        try:
            return cls(v)  # Lookup by value, not by name

        except ValueError:
            allowed = ", ".join(m.value for m in cls)

            raise ValueError(
                f"Invalid DC_NOTIFY_MODE {value!r}. Must be one of: {allowed}"
            )


@dataclass(frozen=True)
class Settings:

    # instance tracker
    _instance = None

    # Webhook
    discord_webhook_url: str

    # Report discovery
    report_dir: Path | None
    report_json: Path
    report_html: Path

    # Behaviour
    min_severity: Severity
    notify_mode: NotifyMode
    attach_html: bool
    notify_on_zero: bool
    max_items: int
    project_label: str
    fail_on_vuln: bool
    quiet: bool

    # GitLab CI envs
    ci_project_url: str
    ci_project_path: str
    ci_api_v4_url: str
    ci_project_id: str
    ci_pipeline_url: str
    ci_pipeline_id: str
    ci_commit_ref_name: str
    ci_repository_url: str
    artifact_job_name: str

    # Buttons
    buttons: List[str]

    # Links
    html_url: str | None
    zip_url: str | None
    pipeline_url: str | None
    repo_url: str | None

    # Severity helpers
    severity_order: List[str]
    severity_rank: dict[str, int]

    # i am singleton
    def __new__(cls, *args: Any, **kwargs: Any):
        if not hasattr(cls, 'instance'):
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance.__init__(*args, **kwargs)

        return cls._instance

    @staticmethod
    def load_env() -> Settings:
        """
        populate class variables with env var values

        :return: Settings class with values
        :rtype: Settings
        """
        # Read raw envs once
        discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

        # Report paths
        report_dir_raw = os.getenv("REPORT_DIR", "").strip()
        report_dir = Path(report_dir_raw) if report_dir_raw else None

        report_json = os.getenv(
            "REPORT_JSON_NAME", "dependency-check-report.json").strip()
        report_html = os.getenv(
            "REPORT_HTML_NAME", "dependency-check-report.html").strip()

        # Behaviour
        min_severity = Severity.load_env(
            os.getenv("MIN_SEVERITY") or os.getenv("DC_MIN_SEVERITY"),
            Severity.LOW)
        notify_mode = NotifyMode.load_env(
            os.getenv("DC_NOTIFY_MODE"), NotifyMode.BOTH)
        attach_html = _parse_bool(os.getenv("ATTACH_HTML") or os.getenv(
            "DC_ATTACH_HTML"), default=False)
        notify_on_zero = _parse_bool(
            os.getenv("DC_NOTIFY_ON_ZERO"), default=False)
        max_items = _parse_int(os.getenv("DC_MAX_ITEMS"), default=10)
        project_label = os.getenv("DC_PROJECT_LABEL", "").strip()
        fail_on_vuln = _parse_bool(
            os.getenv("DC_FAIL_ON_VULN"), default=False)
        quiet = _parse_bool(os.getenv("DC_QUIET"), default=False)

        # GitLab CI envs
        ci_project_url = os.getenv("CI_PROJECT_URL", "").rstrip("/")
        ci_project_path = os.getenv("CI_PROJECT_PATH", "").strip()
        ci_api_v4_url = os.getenv("CI_API_V4_URL", "").rstrip("/")
        ci_project_id = os.getenv("CI_PROJECT_ID", "").strip()
        ci_pipeline_url = os.getenv("CI_PIPELINE_URL", "").strip()
        ci_pipeline_id = os.getenv("CI_PIPELINE_ID", "").strip()
        ci_commit_ref_name = os.getenv("CI_COMMIT_REF_NAME", "").strip()
        ci_repository_url = os.getenv("CI_REPOSITORY_URL", "").strip()
        artifact_job_name = (os.getenv("ARTIFACT_JOB_NAME") or os.getenv(
            "DC_ARTIFACT_JOB_NAME") or "dependency_check").strip()

        # Buttons
        buttons_raw = os.getenv("DC_BUTTONS", "html,zip,pipeline,repo")
        buttons = [b.strip().lower()
                   for b in buttons_raw.split(",") if b.strip()]

        severity_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        severity_rank = {s: i for i, s in enumerate(severity_order)}

        # Links
        html_url = None
        zip_url = None

        if (
            ci_project_url and
            ci_commit_ref_name and
            artifact_job_name
        ):
            html_url = (
                f"{ci_project_url}/-/jobs/artifacts/"
                f"{ci_commit_ref_name}/file/"
                f"{report_html}?job="
                f"{artifact_job_name}"
            )

        if (
            ci_api_v4_url and
            ci_project_id and
            ci_commit_ref_name and
            artifact_job_name
        ):
            zip_url = (
                f"{ci_api_v4_url}/projects/"
                f"{ci_project_id}/jobs/artifacts/"
                f"{ci_commit_ref_name}/download?job="
                f"{artifact_job_name}"
            )

        pipeline_url = ci_pipeline_url or (
            f"{ci_project_url}/-/pipelines/{ci_pipeline_id}"
            if ci_project_url and ci_pipeline_id
            else None
        )

        repo_url = ci_project_url or (
            ci_repository_url if ci_repository_url else None)

        # Paths resolved relative to report_dir if provided
        report_json = Path(report_json)
        report_html = Path(report_html)

        if report_dir:
            report_json = report_dir / report_json
            report_html = report_dir / report_html

        return Settings(
            discord_webhook_url=discord_webhook_url,
            report_dir=report_dir,
            report_json=report_json,
            report_html=report_html,
            min_severity=min_severity,
            notify_mode=notify_mode,
            attach_html=attach_html,
            notify_on_zero=notify_on_zero,
            max_items=max_items,
            project_label=project_label,
            fail_on_vuln=fail_on_vuln,
            quiet=quiet,
            ci_project_url=ci_project_url,
            ci_project_path=ci_project_path,
            ci_api_v4_url=ci_api_v4_url,
            ci_project_id=ci_project_id,
            ci_pipeline_url=ci_pipeline_url,
            ci_pipeline_id=ci_pipeline_id,
            ci_commit_ref_name=ci_commit_ref_name,
            ci_repository_url=ci_repository_url,
            artifact_job_name=artifact_job_name,
            buttons=buttons,
            severity_order=severity_order,
            severity_rank=severity_rank,
            html_url=html_url,
            zip_url=zip_url,
            pipeline_url=pipeline_url,
            repo_url=repo_url,
        )

    @classmethod
    def get_instance(cls) -> 'Settings':
        if cls._instance is None:
            raise ValueError(
                "Settings not initialized. Call load_env() first.")

        return cls._instance
