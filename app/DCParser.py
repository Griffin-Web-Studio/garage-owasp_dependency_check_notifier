"""
Class holding the primary parsing logic of the OWASP Dependency Checker report
"""

from settings import Settings


class DCParser:
    _data: dict[str, str] | None
    _settings: Settings

    def __init__(self, settings: Settings):
        """
        Initialises the parser with the source data.
        """
        self._settings = settings
        # self._data = self._parse()

    def _load_data(self):
        """
        Loads the source data. Override this method in subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method.")

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
