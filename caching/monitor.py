"""This file defines the monitoring of the threads"""
import os
import shutil

from caching.singleton import Singleton
from caching.errors import MonitorError


class Monitor(dict, metaclass=Singleton):
    """
    This class is responsible for tracking all caches in all threads.
    """
    def __init__(self) -> None:
        """
        The constructor for the Monitor object.
        """
        super().__init__({})

    def __setitem__(self, key: str, value: str) -> None:
        """
        Overwrites the set item function for the dictionary to check key and value are
        strings before assignment.

        :param key: (str) the key to be assigned the value
        :param value: (str) the value to be assigned to the key
        :return: None
        """
        if not isinstance(key, str):
            raise MonitorError(message="key type is {} instead of string".format(type(key)))
        if not isinstance(value, str):
            raise MonitorError(message="value type is {} instead of string".format(type(value)))
        super().__setitem__(key, value)

    def delete_cache(self, entry_id: str, locked: bool = False) -> None:
        """
        Deletes the entry and the cache if there are not any other pointers to the same cache.

        :param entry_id: (str) the worker ID associated with the cache
        :param locked: (bool) If False, will delete the cache directory
        :return: None
        """
        count = 0
        if self.get(entry_id) is not None and os.path.isdir(self[entry_id]):
            for other_id in self.keys():
                if self[other_id] == self[entry_id]:
                    count += 1

        if count == 1 and locked is False:
            shutil.rmtree(self[entry_id])

        if self.get(entry_id) is not None:
            del self[entry_id]
