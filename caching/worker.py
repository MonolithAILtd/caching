import datetime
import weakref
from uuid import UUID
import os
import shutil
from typing import Optional

from caching.errors import WorkerCacheError


class Worker:
    """
    This is a class for managing a directory and meta data for temp files.

    Attributes:
        id (str): unique id for the worker
    """
    CLASS_BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    instances = []

    def __init__(self, existing_cache: Optional[str] = None) -> None:
        """
        The constructor for the Worker class.

        :param existing_cache: (Optional[str]) path to existing cache
        """
        self._locked: bool = False
        self.id: UUID = UUID(bytes=os.urandom(16), version=4)
        self._existing_cache: Optional[str] = existing_cache
        self._base_dir: str = str(self.CLASS_BASE_DIR) + "/cache/{}/".format(self.id)
        self._connect_directory()
        self.__class__.instances.append(weakref.proxy(self))

    @staticmethod
    def update_timestamp(cache_path: str) -> None:
        """
        Updates the cache timestamp.txt log with a new timestamp

        :param cache_path:
        :return:
        """
        timestamp = datetime.datetime.now()
        f = open(cache_path + "timestamp.txt", "a")
        f.write("\n{}".format(timestamp))
        f.close()

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
                        self._existing_cache)
                )
            else:
                self._base_dir = self._existing_cache
        else:
            self._generate_directory()

    def _generate_directory(self) -> None:
        """
        Generates cache directory with self.id (private).

        :return: None
        """
        if os.path.isdir(self._base_dir):
            raise WorkerCacheError(message="directory {} already exists. Check __del__ and self.id methods".format(
                self._base_dir
            ))
        os.mkdir(self._base_dir)
        self.update_timestamp(cache_path=self._base_dir)

    def _delete_directory(self) -> None:
        """
        Deletes cache directory (private).

        :return: None
        """
        if not os.path.isdir(self._base_dir):
            raise WorkerCacheError(
                "directory {} does not exist. please check __del__ and self._delete_directory methods".format(
                    self._base_dir))
        shutil.rmtree(self._base_dir)

    @property
    def base_dir(self) -> str:
        return self._base_dir

    def __del__(self):
        """
        Fires when self is deleted, deletes the directory.

        :return: None
        """
        other_pointers = False
        for pointer in self.instances:
            if pointer.base_dir == self.base_dir and pointer.id != self.id:
                other_pointers = True

        self.instances.remove(weakref.proxy(self))
        if self._locked is False and other_pointers is False:
            self._delete_directory()


