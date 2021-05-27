from typing import List, Optional

from redis import StrictRedis

from .errors import RegisterError


class Register:
    """
    This class is responsible for logging caches to Redis and counts how many caches are pointing to the cache.
    """

    TABLE = "CACHE_REGISTER"

    def __init__(self, host: str, port: int) -> None:
        """
        The constructor for the Register class.

        :param host: (str) host for the Redis connection
        :param port: (int) port for the Redis connection
        """
        self._connection: StrictRedis = StrictRedis(host=host, port=port, db=0)

    def get_count(self, cache_path: str) -> Optional[int]:
        """
        Gets the reference count for the cache.

        :param cache_path: (str) the path to the cache
        :return: (Optional[int]) number of count, or None if cache does not exist
        """
        count: Optional[str] = self._connection.hget(name=self.TABLE, key=cache_path)
        if count is None:
            return None
        return int(count)

    def register_cache(self, cache_path: str) -> None:
        """
        Registers the cache path if there isn't an entry or increasing the count by one if there is.

        :param cache_path: (str) the path to the cache
        :return: None
        """
        count: Optional[int] = self.get_count(cache_path=cache_path)
        if count is None:
            self._connection.hset(name=self.TABLE, key=cache_path, value="1")
        else:
            count += 1
            self._connection.hset(name=self.TABLE, key=cache_path, value=str(count))

    def deregister_cache(self, cache_path: str, locked: bool) -> int:
        """
        Deletes the cache path from Redis if the count goes to Zero or decreases the count by one if not zero.

        :param cache_path: (str) the path to the cache
        :param locked: (bool) is set to True prevents deleting of cache even if it has a count of zero
        :return: (int) the count of the references after the deregister.
        """
        count: Optional[int] = self.get_count(cache_path=cache_path)
        if count is None:
            raise RegisterError(
                message="cache {} is not in cache register so it cannot be de-registered".format(
                    cache_path
                )
            )
        else:
            if count > 0:
                count -= 1
            if count <= 0 and locked is False:
                self._connection.hdel(self.TABLE, cache_path)
            else:
                self._connection.hset(name=self.TABLE, key=cache_path, value=str(count))
        return count

    def get_all_records(self) -> List[dict]:
        """
        Get's all the key entries for the LOCAL_CLOUD.

        :return: (List[dict]) all cache entries
        """
        return self._connection.hgetall(name=self.TABLE)  # type: ignore
