import tempfile
from typing import Optional


class RootDirectory:
    """
    This class is responsible for defining the monitoring the root directory for the cache.
    """

    def __init__(self, directory: Optional[str] = None) -> None:
        """
        The constructor for the RootDirectory.

        :param directory: (Optional[str]) the directory for the root of the cache
        """
        self._dir: str = self._extract_path() if directory is None else directory

    @staticmethod
    def _extract_path() -> str:
        """
        Extracts the first python path in the os environment variables.

        :return: (str)
        """
        return str(tempfile.TemporaryDirectory())

    @property
    def path(self) -> str:
        """
        Gets the path of the root of the directory.

        :return: (str) path to the root directory
        """
        return self._dir
