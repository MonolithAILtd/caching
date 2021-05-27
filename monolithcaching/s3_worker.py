"""this file defines the worker for pointing to caches in s3 buckets"""
import ast
import json
import os
from typing import Tuple, Optional, Any, Dict, List
from uuid import UUID

import boto3  # type: ignore
import botocore  # type: ignore


# pylint: disable=too-few-public-methods
class S3Worker:
    """
    This is a class for managing a directory for temp files in S3.

    Attributes:
        id (str): unique id for the worker
        base_dir (str): directory path for the cache
    """

    def __init__(self, cache_path: str, existing_cache: Optional[str] = None) -> None:
        """
        The constructor for the S3Worker class.

        :param cache_path: (str) the root path for all caches
        :param existing_cache: (Optional[str]) points to an existing cache if entered
        """
        # pylint: disable=invalid-name
        if existing_cache is None:
            self.id: str = str(UUID(bytes=os.urandom(16), version=4))  # type: ignore
        else:
            self.id: str = self.extract_id(storage_path=existing_cache)  # type: ignore
        self.base_dir: str = cache_path + "{}/".format(self.id)
        self._client: boto3.client = boto3.client("s3")
        self._resource: boto3.resource = boto3.resource("s3")
        self._locked: bool = False
        if existing_cache is None:
            self.create_meta()

    def delete_directory(self) -> None:
        """
        Deletes cache directory.

        :return: None
        """
        bucket, cache_path, short_file_name = self._split_s3_path(
            storage_path=self.base_dir
        )
        bucket_object = self._resource.Bucket(bucket)
        bucket_object.objects.filter(Prefix=cache_path).delete()

    def create_meta(self) -> None:
        """
        Creates the meta file for the cache.

        :return: None
        """
        bucket, cache_path, _ = self._split_s3_path(storage_path=self.base_dir)
        file_path = cache_path + "meta.json"
        meta_object = self._resource.Object(bucket, file_path)
        meta_object.put(Body=(bytes(json.dumps({}).encode("UTF-8"))))

    def insert_meta(self, key: str, value: Any) -> None:
        """
        Inserts a value into the meta data file of the cache.

        :param key: (str) the key the value is denoted under
        :param value: (Any) the value to be inserted
        :return: None
        """
        bucket, cache_path, _ = self._split_s3_path(storage_path=self.base_dir)
        file_path = cache_path + "meta.json"
        meta_object = self._resource.Object(bucket, file_path)
        meta_data = self.meta
        meta_data[key] = value

        meta_object.put(Body=(bytes(json.dumps(meta_data).encode("UTF-8"))))

    def lock(self) -> None:
        """
        Placeholder for locking as all S3 is locked.

        :return: None
        """
        pass

    def check_file(self, file: str) -> bool:
        """
        Checks to see if a file is present in the cache.

        :param file: (str) name of the file being checked
        :return: True if present, False if not
        """
        bucket, cache_path, _ = self._split_s3_path(storage_path=self.base_dir)
        try:
            file_path = cache_path + file
            self._resource.Object(bucket, file_path).load()
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise
        return True

    @staticmethod
    def _split_s3_path(storage_path: str) -> Tuple[str, str, str]:
        """
        Splits the path to get parameters.

        :param storage_path: (str) path
        :return: bucket_name, file_name, short_file_name
        """
        path: str = storage_path.replace("s3://", "")
        path_buffer: List[str] = path.split("/")
        bucket_name: str = path_buffer[0]
        file_name: str = "/".join(path_buffer[1:])
        short_file_name: str = path_buffer[-1]
        return bucket_name, file_name, short_file_name

    @staticmethod
    def extract_id(storage_path: str) -> str:
        """
        Extracts the id of the cache from a previous cache path.

        :param storage_path: (str) the cache path for the ID to be extracted
        :return: (str) the ID of the cache
        """
        return storage_path.split("/")[-1]

    @property
    def meta(self) -> Dict:
        """
        Extracts the meta data from the meta.json file of the cache.

        :return: (Dict) meta data of the cache
        """
        bucket, cache_path, _ = self._split_s3_path(storage_path=self.base_dir)
        file_path = cache_path + "meta.json"
        meta_object = self._resource.Object(bucket, file_path)
        return ast.literal_eval(meta_object.get()["Body"].read().decode("utf-8"))
