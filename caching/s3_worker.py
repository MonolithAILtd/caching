"""this file defines the worker for pointing to caches in s3 buckets"""
from typing import Tuple, List, Any
from uuid import UUID
import os

import boto3


# pylint: disable=too-few-public-methods
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
        # pylint: disable=invalid-name
        self.id: str = str(UUID(bytes=os.urandom(16), version=4))
        self.base_dir: str = cache_path + "{}/".format(self.id)
        self._cached_files: List[Any] = []
        self._client = boto3.client('s3')
        self._resource = boto3.resource('s3')
        self._locked: bool = False

    def delete_directory(self) -> None:
        """
        Deletes cache directory (private).

        :return: None
        """
        bucket, file_name, short_file_name = self._split_s3_path(storage_path=self.base_dir)
        bucket = self._resource.Bucket(bucket)
        file_prefix = self.base_dir.replace(short_file_name, "").replace("s3://", "")
        print("here is the file prefix: {}".format(file_prefix))
        bucket.objects.filter(Prefix=file_prefix).delete()

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
