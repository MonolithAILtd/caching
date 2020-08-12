import os
from uuid import UUID

from caching.singleton import Singleton


class Monitor(dict, metaclass=Singleton):
    CLASS_BASE_DIR = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        """
        Initialises the monitor dictionary with the unique id and base
        directory

        """
        self.id: UUID = UUID(bytes=os.urandom(16), version=4)
        self._base_dir: str = str(self.CLASS_BASE_DIR) + "/cache/{}/".format(self.id)
        super().__init__(map([self.id, self._base_dir]))

    @property
    def base_dir(self):
        return self._base_dir

    def __del__(self):
        """
        Deletes key/value pairs

        :return: None
        """
        other_pointers = False
        for k, v in self.iteritems():
            if v == self.base_dir and k != self.id:
                other_pointers = True

        if other_pointers is False:
            self.clear()
