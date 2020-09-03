from typing import List, Optional

from redis import StrictRedis

from .errors import RegisterError


class Register:

    TABLE = "CACHE_REGISTER"

    def __init__(self, host: str, port: int) -> None:
        self._connection: StrictRedis = StrictRedis(host=host, port=port, db=0)

    def get_count(self, cache_path: str) -> Optional[int]:
        count: Optional[str] = self._connection.hget(name=self.TABLE, key=cache_path)
        if count is None:
            return None
        return int(count)

    def register_cache(self, cache_path: str) -> None:
        count: Optional[int] = self.get_count(cache_path=cache_path)
        if count is None:
            self._connection.hset(name=self.TABLE, key=cache_path, value="1")
        else:
            count += 1
            self._connection.hset(name=self.TABLE, key=cache_path, value=str(count))

    def deregister_cache(self, cache_path: str, locked: bool) -> int:
        count: Optional[int] = self.get_count(cache_path=cache_path)
        if count is None:
            raise RegisterError(message="cache {} is not in cache register so it cannot be deregistered".format(
                cache_path))
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
        return self._connection.hgetall(name=self.TABLE)
