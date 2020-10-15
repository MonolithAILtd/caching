from typing import Optional, List
import os


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
        python_path_buffer: List[str] = os.environ['PYTHONPATH'].split(":")
        return python_path_buffer[0] + "/cache/"

    @property
    def path(self) -> str:
        """
        Gets the path of the root of the directory.

        :return: (str) path to the root directory
        """
        return self._dir
