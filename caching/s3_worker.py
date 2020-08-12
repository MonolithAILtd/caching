from typing import Tuple, List, Any
from uuid import UUID
import os

import boto3


class S3Worker:
    """
    This is a class for managing a directory for temp files in S3.

    Attributes:
        id (str): unique id for the worker
        base_dir (str): directory path for the cache
    """

    def __init__(self, cache_path: str) -> None:
        """
        The constructor for the S3Worker.
        """
        self.id: str = str(UUID(bytes=os.urandom(16), version=4))
        self.base_dir: str = cache_path + "{}/".format(self.id)
        self._cached_files: List[Any] = []
        self._connection = boto3.client('s3')
        self._locked: bool = False

    def _delete_directory(self) -> None:
        """
        Deletes cache directory (private).

        :return: None
        """
        bucket_name, file_name, short_file_name = self._split_s3_path(storage_path=self.base_dir)
        # bucket = self._connection.Bucket(bucket_name)
        file_prefix = file_name.replace(short_file_name, "")
        self._connection.delete_bucket(Bucket=file_prefix)

    @staticmethod
    def _split_s3_path(storage_path: str) -> Tuple[str, str, str]:
        """
        Splits the path to get parameters.

        :param storage_path: (str) path
        :return: bucket_name, file_name, short_file_name
        """
        path = storage_path.replace("s3://", "")
        path = path.split("/")
        bucket_name = path[0]
        file_name = "/".join(path[1:])
        short_file_name = path[-1]
        return bucket_name, file_name, short_file_name

    def __del__(self):
        self._delete_directory()
