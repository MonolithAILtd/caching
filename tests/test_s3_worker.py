from unittest import TestCase, main
from mock import patch, MagicMock

from caching.s3_worker import S3Worker


class TestS3Worker(TestCase):

    @patch("caching.s3_worker.os")
    @patch("caching.s3_worker.S3Worker._delete_directory")
    @patch("caching.s3_worker.UUID")
    def test___init__(self, mock_uuid, mock_delete_directory, mock_os):
        mock_uuid.return_value = "test"

        test = S3Worker(cache_path="/path/to/cache/")

        mock_uuid.assert_called_once_with(bytes=mock_os.urandom.return_value, version=4)
        self.assertEqual(mock_uuid.return_value, test.id)
        self.assertEqual("/path/to/cache" + "/{}/".format(test.id), test.base_dir)

        del test

        mock_delete_directory.assert_called_once_with()

    @patch("caching.s3_worker.S3Worker._split_s3_path")
    @patch("caching.s3_worker.S3Worker.__init__")
    def test__delete_directory(self, mock_init, mock_split_path):
        mock_split_path.return_value = ("test bucket", "test/file/path.txt", "path.txt")
        mock_init.return_value = None
        test = S3Worker(cache_path="some cache path")
        connection = MagicMock()
        test._connection = connection
        test.base_dir = "s3://bucket/directory/to/cache/"
        del test

        connection.delete_bucket.assert_called_once_with(Bucket='test/file/')

    def test__split_s3_path(self):
        bucket_name, file_name, short_file_name = S3Worker._split_s3_path(
            storage_path="s3://mybucket/some/other/path.txt")

        self.assertEqual("mybucket", bucket_name)
        self.assertEqual("some/other/path.txt", file_name)
        self.assertEqual("path.txt", short_file_name)


if __name__ == "__main__":
    main()
