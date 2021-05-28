"""
performs unit tests on the CacheManager object. Use: self.test = CacheManager() to ensure memory safety
"""
from unittest import TestCase, main
from mock import patch, MagicMock, PropertyMock

from monolithcaching import CacheManager, CacheManagerError, S3Worker, Worker


class TestCacheManager(TestCase):

    @patch("monolithcaching.RootDirectory")
    def setUp(self, mock_directory):
        self.test = CacheManager(host="localhost", port=6379)
        self.s3_test = CacheManager(host="localhost", port=6379, s3=True, s3_cache_path="/test/cache/path/")
        self.mock_directory = mock_directory

    def tearDown(self) -> None:
        self.test.worker = MagicMock()
        self.s3_test.worker = MagicMock()

    def test___init__(self):
        self.assertEqual(None, self.test.worker)
        self.assertEqual(False, self.test.s3)
        self.assertEqual(None, self.test.s3_cache_path)

        self.assertEqual(None, self.s3_test.worker)
        self.assertEqual(True, self.s3_test.s3)
        self.assertEqual("/test/cache/path/", self.s3_test.s3_cache_path)

    @patch("monolithcaching.CacheManager.meta", new_callable=PropertyMock)
    @patch("monolithcaching.CacheManager._create_meta")
    @patch("monolithcaching.S3Worker")
    @patch("monolithcaching.Worker")
    def test_create_cache(self, mock_worker, mock_s3, mock_create_meta, mock_meta):
        mock_meta.return_value = {}
        path = self.mock_directory.return_value.path

        self.test.create_cache()
        self.assertEqual(mock_worker.return_value, self.test.worker)
        mock_worker.assert_called_once_with(host="localhost", port=6379, existing_cache=None, local_cache=path)
        mock_worker.reset_mock()
        mock_create_meta.assert_called_once_with()

        self.test.create_cache(existing_cache="test cache")
        self.assertEqual(mock_worker.return_value, self.test.worker)
        mock_worker.assert_called_once_with(host="localhost", port=6379, existing_cache="test cache", local_cache=path)
        mock_create_meta.assert_called_once_with()
        mock_worker.reset_mock()

        mock_meta.return_value = {"locked": False}
        self.test.create_cache(existing_cache="test cache")
        self.assertEqual(mock_worker.return_value, self.test.worker)
        mock_worker.assert_called_once_with(host="localhost", port=6379, existing_cache="test cache", local_cache=path)
        mock_create_meta.assert_called_once_with()
        mock_worker.reset_mock()

        mock_meta.return_value = {"locked": True}
        self.test.create_cache(existing_cache="test cache")
        self.assertEqual(mock_worker.return_value, self.test.worker)
        mock_worker.assert_called_once_with(host="localhost", port=6379, existing_cache="test cache", local_cache=path)
        mock_create_meta.assert_called_once_with()
        mock_worker.return_value.lock.assert_called_once_with()
        mock_create_meta.reset_mock()
        mock_worker.reset_mock()

        self.s3_test.create_cache()
        self.assertEqual(mock_s3.return_value, self.s3_test.worker)
        mock_s3.assert_called_once_with(cache_path="/test/cache/path/", existing_cache=None)
        self.assertEqual(0, len(mock_create_meta.call_args_list))

    @patch("monolithcaching.CacheManager.insert_meta")
    def test_lock_cache(self, mock_insert_meta):
        self.test.worker = MagicMock()
        self.test.lock_cache()
        self.test.worker.lock.assert_called_once_with()

        self.test.worker = None

        with self.assertRaises(CacheManagerError) as e:
            self.test.lock_cache()
        self.assertEqual("cache worker is not defined so cannot be locked", str(e.exception))

        mock_insert_meta.assert_called_once_with(key="locked", value=True)

    def test_wipe_cache(self):
        self.test.worker = "testing"
        self.test.s3 = True
        self.test.wipe_cache()
        self.assertEqual(None, self.test.worker)

    @patch("monolithcaching.json")
    @patch("monolithcaching.open")
    def test_insert_meta(self, mock_open, mock_json):
        self.test.worker = MagicMock(spec=Worker)
        self.test.worker.base_dir = "some/base/dir/"
        mock_json.load.return_value = {"one": 1}

        self.test.insert_meta(key="test key", value="test value")
        mock_json.load.assert_called_once_with(mock_open.return_value.__enter__.return_value)
        mock_json.dump.assert_called_once_with({'one': 1, 'test key': 'test value'},
                                               mock_open.return_value.__enter__.return_value)

        self.s3_test.worker = MagicMock(spec=S3Worker)
        self.s3_test.worker.base_dir = "some/base/dir/"
        self.s3_test.insert_meta(key="test key", value="test value")
        self.s3_test.worker.insert_meta.assert_called_once_with(key="test key", value="test value")

    @patch("monolithcaching.json")
    @patch("monolithcaching.open")
    def test___create_meta(self, mock_open, mock_json):
        self.test.worker = MagicMock(spec=Worker)
        self.test.worker.base_dir = "some/dir/"
        self.test._create_meta()
        mock_open.assert_called_once_with(self.test.worker.base_dir + "meta.json", "w")
        mock_json.dump.assert_called_once_with({}, mock_open.return_value.__enter__.return_value)

    def test_cache_path(self):
        self.assertEqual(None, self.test.cache_path)

        self.test.worker = MagicMock()
        self.test.worker.base_dir = "test dir"
        self.assertEqual("test dir", self.test.cache_path)

    @patch("monolithcaching.json")
    @patch("monolithcaching.open")
    def test_meta(self, mock_open, mock_json):
        self.test.worker = MagicMock(spec=Worker)
        self.assertEqual(self.test.meta, mock_json.load.return_value)

        mock_open.assert_called_once_with(self.test.worker.base_dir + "meta.json")
        mock_json.load.assert_called_once_with(mock_open.return_value.__enter__.return_value)

    @patch("monolithcaching.CacheManager.wipe_cache")
    @patch("monolithcaching.CacheManager.create_cache")
    def test___enter__(self, mock_create_cache, mock_wipe_cache):
        self.test = CacheManager(host="localhost", port=6379)

        with self.test as cache:
            self.assertEqual(self.test, cache)

        mock_create_cache.assert_called_once_with()
        self.assertEqual(2, len(mock_wipe_cache.call_args_list))


if __name__ == "__main__":
    main()
