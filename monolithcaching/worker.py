"""this file defines the worker for managing local cache directories"""
import datetime
import os
import shutil
from typing import Optional
from uuid import UUID

from .errors import WorkerCacheError
from .register import Register


class Worker:
    """
    This is a class for managing a directory and meta data for temp files.

    Attributes:
        id (str): unique id for the worker
    """

    CLASS_BASE_DIR = os.path.dirname(os.path.realpath(__file__))

    def __init__(
        self,
        port: Optional[int],
        host: Optional[str],
        existing_cache: Optional[str] = None,
        local_cache: Optional[str] = None,
    ) -> None:
        """
        The constructor for the Worker class.

        :param port: (Optional[int]) port for the redis connection tracking caches
        :param host: (Optional[str]) host for the redis connection tracking caches
        :param existing_cache: (Optional[str]) path to existing cache
        :param local_cache: (Optional[str]) path to the local cache
        """
        self._locked: bool = False
        self._port: Optional[int] = port
        self._host: Optional[str] = host
        # pylint: disable=invalid-name
        self.id: str = str(UUID(bytes=os.urandom(16), version=4))
        self._existing_cache: Optional[str] = existing_cache
        self.class_base_dir: str = (
            self.CLASS_BASE_DIR if local_cache is None else local_cache
        )
        self._base_dir: str = str(self.class_base_dir) + "/cache/{}/".format(self.id)
        self._connect_directory()
        if self._port is not None and host is not None:
            Register(host=self._host, port=self._port).register_cache(cache_path=self.base_dir)  # type: ignore

    @staticmethod
    def update_timestamp(cache_path: str) -> None:
        """
        Updates the cache timestamp.txt log with a new timestamp

        :param cache_path: (str) path to the cache being
        :return:
        """
        timestamp = datetime.datetime.now()
        file = open(cache_path + "timestamp.txt", "a")
        file.write("\n{}".format(timestamp))
        file.close()

    def lock(self) -> None:
        """
        Sets self._lock to True preventing cleanup.

        :return: None
        """
        self._locked = True

    def unlock(self) -> None:
        """
        Sets the self._lock to False enabling cleanup.

        :return: None
        """
        self._locked = False

    def _connect_directory(self) -> None:
        """
        Checks existing path, creates new cache if existing path not supplied.

        :return: None
        """
        if self._existing_cache is not None:
            if not os.path.isdir(self._existing_cache):
                raise WorkerCacheError(
                    message="directory '{}' was supplied as an existing cache but does not exist".format(
                        self._existing_cache
                    )
                )
            self._base_dir = self._existing_cache
        else:
            self._generate_directory()

    def _generate_directory(self) -> None:
        """
        Generates cache directory with self.id (private).

        :return: None
        """
        if os.path.isdir(self._base_dir):
            raise WorkerCacheError(
                message="directory {} already exists. Check __del__ and self.id methods".format(
                    self._base_dir
                )
            )
        os.makedirs(self._base_dir)
        self.update_timestamp(cache_path=self._base_dir)

    def _delete_directory(self) -> None:
        """
        Deletes cache directory (private).

        :return: None
        """
        if self._port is None and self._locked is False:
            shutil.rmtree(self.base_dir)
        elif self._port is not None:
            count: int = Register(host=self._host, port=self._port).deregister_cache(  # type: ignore
                cache_path=self.base_dir, locked=self._locked  # type: ignore
            )  # type: ignore
            if count == 0 and self._locked is False:
                shutil.rmtree(self.base_dir)

    @property
    def base_dir(self) -> str:
        """
        Dynamic property that defines the base directory for the cache.

        :return: (str) the base directory of the cache
        """
        return self._base_dir

    def __del__(self):
        """
        Fires when self is deleted, deletes the directory.

        :return: None
        """
        self._delete_directory()
