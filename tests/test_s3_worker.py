import json

from unittest import TestCase, main
from mock import patch, MagicMock, PropertyMock

from caching.s3_worker import S3Worker


class TestS3Worker(TestCase):

    @patch("caching.s3_worker.S3Worker.create_meta")
    @patch("caching.s3_worker.boto3")
    @patch("caching.s3_worker.S3Worker.extract_id")
    @patch("caching.s3_worker.os")
    @patch("caching.s3_worker.UUID")
    def test___init__(self, mock_uuid, mock_os, mock_extract_id, mock_boto, mock_create_meta):
        mock_uuid.return_value = "test"

        test = S3Worker(cache_path="/path/to/cache/")

        mock_uuid.assert_called_once_with(bytes=mock_os.urandom.return_value, version=4)
        self.assertEqual(mock_uuid.return_value, test.id)
        self.assertEqual("/path/to/cache" + "/{}/".format(test.id), test.base_dir)
        self.assertEqual(mock_boto.client.return_value, test._client)
        self.assertEqual(mock_boto.resource.return_value, test._resource)
        self.assertEqual(False, test._locked)
        self.assertEqual(0, len(mock_extract_id.call_args_list))
        mock_create_meta.assert_called_once_with()
        mock_boto.client.assert_called_once_with("s3")
        mock_boto.resource.assert_called_once_with("s3")

        mock_boto.reset_mock()

        test = S3Worker(cache_path="/path/to/cache/", existing_cache="/test/cache")
        mock_uuid.assert_called_once_with(bytes=mock_os.urandom.return_value, version=4)
        self.assertEqual(mock_extract_id.return_value, test.id)
        self.assertEqual("/path/to/cache" + "/{}/".format(test.id), test.base_dir)
        self.assertEqual(mock_boto.client.return_value, test._client)
        self.assertEqual(mock_boto.resource.return_value, test._resource)
        self.assertEqual(False, test._locked)
        mock_extract_id.assert_called_once_with(storage_path='/test/cache')
        mock_create_meta.assert_called_once_with()
        mock_boto.client.assert_called_once_with("s3")
        mock_boto.resource.assert_called_once_with("s3")

    @patch("caching.s3_worker.S3Worker._split_s3_path")
    @patch("caching.s3_worker.S3Worker.__init__")
    def test__delete_directory(self, mock_init, mock_split_path):
        mock_split_path.return_value = ("test bucket", "test/file/path.txt", "path.txt")
        mock_init.return_value = None
        test = S3Worker(cache_path="some cache path")
        connection = MagicMock()
        test._resource = connection
        test.base_dir = "s3://bucket/directory/to/cache/"
        test.delete_directory()

        mock_split_path.assert_called_once_with(storage_path="s3://bucket/directory/to/cache/")
        connection.Bucket.assert_called_once_with("test bucket")
        connection.Bucket.return_value.objects.filter.assert_called_once_with(Prefix="test/file/path.txt")
        connection.Bucket.return_value.objects.filter.return_value.delete.assert_called_once_with()

    @patch("caching.s3_worker.S3Worker._split_s3_path")
    @patch("caching.s3_worker.S3Worker.__init__")
    def test_create_meta(self, mock_init, mock_split_path):
        mock_split_path.return_value = ("test bucket", "test/file/", "path.txt")
        mock_init.return_value = None
        test = S3Worker(cache_path="some cache path")
        connection = MagicMock()
        test._resource = connection
        test.base_dir = "s3://bucket/directory/to/cache/"
        data_dump = bytes(json.dumps({}).encode('UTF-8'))

        test.create_meta()
        mock_split_path.assert_called_once_with(storage_path="s3://bucket/directory/to/cache/")
        connection.Object.assert_called_once_with("test bucket", "test/file/meta.json")
        connection.Object.return_value.put.assert_called_once_with(Body=data_dump)

    @patch("caching.s3_worker.S3Worker.meta", new_callable=PropertyMock)
    @patch("caching.s3_worker.S3Worker._split_s3_path")
    @patch("caching.s3_worker.S3Worker.__init__")
    def test_insert_meta(self, mock_init, mock_split_path, mock_meta):
        mock_meta.return_value = {"one": 1, "two": 2}
        mock_split_path.return_value = ("test bucket", "test/file/", "path.txt")
        mock_init.return_value = None
        test = S3Worker(cache_path="some cache path")
        connection = MagicMock()
        test._resource = connection
        test.base_dir = "s3://bucket/directory/to/cache/"
        data_dump = bytes(json.dumps({"one": 1, "two": 2, "three": 3}).encode('UTF-8'))

        test.insert_meta(key="three", value=3)
        mock_split_path.assert_called_once_with(storage_path="s3://bucket/directory/to/cache/")
        connection.Object.assert_called_once_with("test bucket", "test/file/meta.json")
        connection.Object.return_value.put.assert_called_once_with(Body=data_dump)

    def test__split_s3_path(self):
        bucket_name, file_name, short_file_name = S3Worker._split_s3_path(
            storage_path="s3://mybucket/some/other/path.txt")

        self.assertEqual("mybucket", bucket_name)
        self.assertEqual("some/other/path.txt", file_name)
        self.assertEqual("path.txt", short_file_name)

    def test_extract_id(self):
        self.assertEqual("test.txt", S3Worker.extract_id(storage_path="testing/test.txt"))

    @patch("caching.s3_worker.S3Worker._split_s3_path")
    @patch("caching.s3_worker.S3Worker.__init__")
    def test_meta(self, mock_init, mock_split_path):
        mock_split_path.return_value = ("test bucket", "test/file/", "path.txt")
        mock_init.return_value = None
        test = S3Worker(cache_path="some cache path")
        test.base_dir = "s3://bucket/directory/to/cache/"
        connection = MagicMock()
        test._resource = connection

        test._resource.Object.return_value.get.return_value['Body'].read.return_value.decode.return_value = '{"one": 1}'
        self.assertEqual({"one": 1}, test.meta)
        connection.Object.assert_called_once_with("test bucket", "test/file/meta.json")
        mock_split_path.assert_called_once_with(storage_path="s3://bucket/directory/to/cache/")


if __name__ == "__main__":
    main()
