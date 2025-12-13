"""
Class holding the primary parsing logic of the OWASP Dependency Checker report
"""

import json
from typing import Any, Dict, List, Optional
from pydantic import ValidationError
from app.models.report_models import DCModel

from settings import Settings
from utils.common import err


class DCParser:
    _report: Optional[DCModel] = None
    _settings: Settings

    def __init__(self, settings: Settings):
        """
        Initialises the parser with the source data.
        """
        self._settings = settings
        self._load_data()
        # self._data = self._parse()

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

    def _parse(self):
        """
        Parses the loaded data. Override this method in subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def get_data(self):
        """
        Returns the parsed data.

        :return: The parsed data.
        """
        return None
        # return self.data
