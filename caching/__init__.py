import json
from typing import Union, Optional

from caching.errors import CacheManagerError
from caching.worker import Worker
from caching.s3_worker import S3Worker


class CacheManager:
    """
    This is a class for managing workers and meta data to a local cache.

    Attributes:
        worker (caching.worker.Worker): worker object that manages the access to the cache
        s3 (bool): if True, use S3 instead of local file storage
        s3_cache_path (Optional[str]): path to the cache in the s3
    """

    def __init__(self, s3: bool = False, s3_cache_path: Optional[str] = None):
        """
        The constructor for the CacheManager class.

        :param s3: (bool) is True, connect to s3
        :param s3_cache_path: (Optional[str]) path to the cache in the s3
        """
        self.worker: Optional[Worker] = None
        self.s3: bool = s3
        self.s3_cache_path: Optional[str] = s3_cache_path

    def create_cache(self, existing_cache: Optional[str] = None) -> None:
        """
        Deletes the old worker and creates a new one.

        :param existing_cache: (Optional[str]) path to existing cache
        :return: None
        """
        del self.worker
        if self.s3 is True:
            self.worker = S3Worker(cache_path=self.s3_cache_path)
            self._create_meta()
        else:
            self.worker = Worker(existing_cache=existing_cache)
            if existing_cache is None:
                self._create_meta()

    def lock_cache(self) -> None:
        """
        Locks the cache so it doesn't get wiped when finished.

        :return: None
        """
        if self.worker is None:
            raise CacheManagerError(message="cache worker is not defined so cannot be locked")
        self.worker.lock()

    def wipe_cache(self) -> None:
        """
        Deletes the current worker.

        :return: None
        """
        del self.worker
        self.worker = None

    def insert_meta(self, key: str, value: Union[str, int, float, dict, list]) -> None:
        """
        Inserts meta into the meta file in the cache.

        :param key: (str) key the value to be stored
        :param value: (Union[str, int, float, dict, list]) data to be stored
        :return: None
        """
        path = self.worker.base_dir + "meta.json"
        with open(path) as meta_file:
            data = json.load(meta_file)

        data[key] = value

        with open(path, "w") as meta_file:
            json.dump(data, meta_file)

    def _create_meta(self) -> None:
        """
        Writes an empty meta file.

        :return: None
        """
        with open(self.worker.base_dir + "meta.json", "w") as meta_file:
            json.dump({}, meta_file)

    @property
    def cache_path(self):
        """
        Dynamic property.

        :return: if self.worker => self.worker.base_dir else None
        """
        if self.worker:
            return self.worker.base_dir
        else:
            return None

    @property
    def meta(self):
        """
        Dynamic property.

        :return: (dict) of meta data from cache
        """
        with open(self.worker.base_dir + "meta.json") as meta_file:
            data = json.load(meta_file)
        return data

    def __enter__(self):
        self.create_cache()
        return self

    def __exit__(self, type, value, traceback):
        self.wipe_cache()
