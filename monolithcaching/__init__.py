"""This module manages the cache directories"""
import json
from typing import Union, Optional, Dict

from .errors import CacheManagerError
from .worker import Worker
from .s3_worker import S3Worker
from .root_directory import RootDirectory


class CacheManager:
    """
    This is a class for managing workers and meta data to a local cache.

    Attributes:
        worker (caching.worker.Worker): worker object that manages the access to the cache
        s3 (bool): if True, use S3 instead of local file storage
        s3_cache_path (Optional[str]): path to the cache in the s3
        local_cache_path (Optional[str]): path to the local cache
    """

    def __init__(
        self,
        port: Optional[int] = None,
        host: Optional[str] = None,
        s3: bool = False,
        s3_cache_path: Optional[str] = None,
        local_cache_path: Optional[str] = None,
    ) -> None:
        """
        The constructor for the CacheManager class.

        :param port: (Optional[int]) port for the Redis connection to enable thread safe caching
        :param host: (Optional[str]) host for the Redis connection to enable thread safe caching
        :param s3: (bool) is True, connect to s3
        :param s3_cache_path: (Optional[str]) path to the cache in the s3
        :param local_cache_path: (Optional[str]) path to the local cache
        """
        self.worker: Union[None, Worker, S3Worker] = None
        # pylint: disable=invalid-name
        self.s3: bool = s3
        self._port: Optional[int] = port
        self._host: Optional[str] = host
        self.s3_cache_path: Optional[str] = s3_cache_path
        self.local_cache_path: Optional[str] = (
            RootDirectory().path if local_cache_path is None else local_cache_path
        )

    def create_cache(self, existing_cache: Optional[str] = None) -> None:
        """
        Deletes the old worker and creates a new one.

        :param existing_cache: (Optional[str]) path to existing cache
        :return: None
        """
        del self.worker
        if self.s3 is True and self.s3_cache_path is not None:
            self.worker = S3Worker(
                cache_path=self.s3_cache_path, existing_cache=existing_cache
            )
        else:
            self.worker = Worker(
                port=self._port,
                host=self._host,
                existing_cache=existing_cache,
                local_cache=self.local_cache_path,
            )
            if existing_cache is None:
                self._create_meta()
            else:
                if self.meta.get("locked", False) is True:
                    self.worker.lock()

    def lock_cache(self) -> None:
        """
        Locks the cache so it doesn't get wiped when finished.

        :return: None
        """
        if self.worker is None:
            raise CacheManagerError(
                message="cache worker is not defined so cannot be locked"
            )
        if self.s3 is False:
            self.worker.lock()
            self.insert_meta(key="locked", value=True)

    def unlock_cache(self) -> None:
        """
        Unlocks the cache so it will get wiped when finished.

        :return: None
        """
        if self.worker is None:
            raise CacheManagerError(
                message="cache worker is not defined so cannot be unlocked"
            )
        if self.s3 is False and isinstance(self.worker, Worker):
            self.worker.unlock()
            self.insert_meta(key="locked", value=False)

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
        if self.worker is None:
            raise CacheManagerError(
                message="you are trying to insert meta data when no cache is made"
            )
        path = self.worker.base_dir + "meta.json"

        if self.s3 is False and isinstance(self.worker, Worker):
            with open(path) as meta_file:
                data = json.load(meta_file)

            data[key] = value

            with open(path, "w") as meta_file:
                json.dump(data, meta_file)
        elif self.s3 is True and isinstance(self.worker, S3Worker):
            self.worker.insert_meta(key=key, value=value)
        else:
            raise CacheManagerError(message="worker type is not consistent with setup")

    def _create_meta(self) -> None:
        """
        Writes an empty meta file.

        :return: None
        """
        if self.s3 is False and isinstance(self.worker, S3Worker):
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
        return None

    @property
    def meta(self) -> Dict:
        """
        Dynamic property.

        :return: (dict) of meta data from cache
        """
        if self.s3 is False and isinstance(self.worker, Worker):
            with open(self.worker.base_dir + "meta.json") as meta_file:
                data = json.load(meta_file)
            return data
        elif isinstance(self.worker, S3Worker):
            return self.worker.meta
        raise CacheManagerError(message="worker is not present for meta data")

    def __del__(self):
        self.wipe_cache()

    def __enter__(self):
        self.create_cache()
        return self

    # pylint: disable=redefined-builtin
    def __exit__(self, type, value, traceback):
        self.wipe_cache()
