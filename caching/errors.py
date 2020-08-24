"""this file defines the errors"""


class WorkerCacheError(Exception):
    """The error for the Worker class"""
    def __init__(self, message: str) -> None:
        """
        The constructor for the WorkerCacheError class.

        :param message: (str) the message for the error
        """
        super().__init__(message)


class CacheManagerError(Exception):
    """The error for the CacheManager class"""
    def __init__(self, message: str) -> None:
        """
        The constructor for the CacheManagerError class.

        :param message: (str) the message for the error
        """
        super().__init__(message)


class MonitorError(Exception):
    """The error for the Monitor class"""
    def __init__(self, message: str) -> None:
        """
        The constructor for the MonitorError class.

        :param message: (str) the message for the error
        """
        super().__init__(message)
