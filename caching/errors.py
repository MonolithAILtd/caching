

class WorkerCacheError(Exception):

    def __init__(self, message):
        super().__init__(message)


class CacheManagerError(Exception):

    def __init__(self, message):
        super().__init__(message)


class MonitorError(Exception):

    def __init__(self, message):
        super().__init__(message)
