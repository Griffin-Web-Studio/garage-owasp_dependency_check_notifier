"""
Class holding the primary parsing logic of the OWASP Dependency Checker report
"""

import json
from typing import Any, List, Optional
from pydantic import BaseModel, ValidationError
from app.models.report_models import DCModel

from settings import Settings
from utils.common import err


class Vulnerability(BaseModel):
    dependency: str
    version: str
    id: List[str]
    severity: str
    scorev2: Any | str
    scorev3: Any | str
    url: str


class DataPack(BaseModel):
    vulnerabilities: List[Vulnerability]
    counts: dict[str, int]


class DCParser:
    _data: Optional[DataPack] = None
    _report: Optional[DCModel] = None
    _settings: Settings

    def __init__(self, settings: Settings):
        """
        Initialises the parser with the source data.
        """
        self._settings = settings
        self._load_data()
        self._data = self._parse()

    def _load_data(self):
        """
        Loads the source data. Override this method in subclasses.
        """
        try:
            raw = json.loads(self._settings.report_json.read_text())
            self._report = DCModel.model_validate(raw)
        except ValidationError:
            err(
                "Could not correctly validate the report schema against the",
                "known model."
            )

    def _parse(self) -> Optional[DataPack]:
        """
        Parse OWASP Dependency-Check JSON into a simple structure

        :param self: ref to class self
        :return: simplified info
        :rtype: Optional[Dict[str, Any]]
        """
        if not self._report:
            return None

        dependencies = self._report.dependencies
        vulns: List[Vulnerability] = []

        for dep in dependencies:
            dep_name_parts = dep.fileName.split(":")
            dep_name: str = dep_name_parts[0]
            dep_version: str = (
                dep_name_parts[1] if len(dep_name_parts) > 1 else "Unknown")

            for d_vulns in dep.vulnerabilities or []:
                severity = d_vulns.severity.lower()
                scorev2 = getattr(d_vulns.cvssv2, 'score', 'Unknown')
                scorev3 = getattr(d_vulns.cvssv3, 'baseScore', 'Unknown')
                refs = d_vulns.references or []
                vuln_ids: List[str] = []
                url = ""

                # Get IDs
                if d_vulns.name:
                    vuln_ids.append(d_vulns.name)
                else:
                    for vuln_soft in d_vulns.vulnerableSoftware:
                        vuln_ids.append(vuln_soft.software.id)

                # Get ref URLs
                if len(refs) > 1:
                    keywords = ["advisories", "vuln", "detail"]
                    first_advisory_ref = next(
                        (ref for ref in refs if any(
                            keyword in ref.url for keyword in keywords)),
                        None
                    )
                    url = getattr(first_advisory_ref, 'url', "")

                vulns.append(Vulnerability(
                    dependency=dep_name,
                    version=dep_version,
                    id=vuln_ids,
                    severity=severity,
                    scorev2=scorev2,
                    scorev3=scorev3,
                    url=url,
                ))

        counts = dict.fromkeys(self._settings.severity_order, 0)

        for vuln in vulns:
            counts[vuln.severity] = counts.get(vuln.severity, 0) + 1

        return DataPack(vulnerabilities=vulns, counts=counts)

    def get_data(self) -> Optional[DataPack]:
        """
        Returns the parsed data.

        :return: The parsed data.
        """
        return self._data
