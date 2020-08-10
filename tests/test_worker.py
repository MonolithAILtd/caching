from unittest import TestCase, main
from mock import patch
from caching.worker import Worker, WorkerCacheError


class TestWorker(TestCase):

    @patch("caching.worker.os")
    @patch("caching.worker.Worker._delete_directory")
    @patch("caching.worker.Worker._connect_directory")
    @patch("caching.worker.UUID")
    def test___init__(self, mock_uuid, mock_connect_directory, mock_delete_directory, mock_os):
        mock_uuid.return_value = "test"

        test = Worker()

        mock_os.urandom.assert_called_once_with(16)
        mock_uuid.assert_called_once_with(bytes=mock_os.urandom.return_value, version=4)
        self.assertEqual(mock_uuid.return_value, test.id)
        self.assertEqual(None, test._existing_cache)
        self.assertEqual(str(test.CLASS_BASE_DIR) + "/cache/{}/".format(test.id),
                         test._base_dir)
        self.assertEqual(False, test._locked)

        del test

        mock_connect_directory.assert_called_once_with()
        mock_delete_directory.assert_called_once_with()

        test = Worker(existing_cache="test")
        self.assertEqual("test", test._existing_cache)

    @patch("caching.worker.datetime")
    @patch("caching.worker.open")
    def test_update_timestamp(self, mock_open, mock_datetime):
        test = Worker
        test.update_timestamp(cache_path="test/path/")
        mock_open.assert_called_once_with("test/path/" + "timestamp.txt", "a")
        mock_open.return_value.write.assert_called_once_with("\n" + str(mock_datetime.datetime.now.return_value))
        mock_open.return_value.close.assert_called_once_with()

    @patch("caching.worker.Worker._generate_directory")
    @patch("caching.worker.os")
    @patch("caching.worker.Worker.__init__")
    def test__connect_directory(self, mock_init, mock_os, mock_generate):
        mock_init.return_value = None
        mock_os.path.isdir.return_value = False

        test = Worker()
        test._locked = True
        test._existing_cache = None
        test._connect_directory()

        mock_generate.assert_called_once_with()

        test._existing_cache = "test"

        with self.assertRaises(WorkerCacheError) as context:
            test._connect_directory()

        self.assertEqual("directory 'test' was supplied as an existing cache but does not exist",
                         str(context.exception))
        mock_generate.assert_called_once_with()

        mock_os.path.isdir.return_value = True

        test._connect_directory()

        self.assertEqual(test._base_dir, test._existing_cache)
        mock_generate.assert_called_once_with()

    @patch("caching.worker.Worker.update_timestamp")
    @patch("caching.worker.os")
    @patch("caching.worker.Worker._delete_directory")
    @patch("caching.worker.Worker.__init__")
    def test__generate_directory(self, mock_init, mock_delete_directory, mock_os, mock_update):
        mock_init.return_value = None
        mock_os.path.isdir.return_value = False

        test = Worker()
        test._base_dir = "test dir"
        test.timestamp = "test timestamp"
        test._locked = False
        test._generate_directory()

        mock_os.path.isdir.assert_called_once_with(test._base_dir)
        mock_os.mkdir.assert_called_once_with(test._base_dir)
        mock_update.assert_called_once_with(cache_path=test._base_dir)

        mock_os.path.isdir.return_value = True

        with self.assertRaises(Exception):
            test._generate_directory()

        mock_os.mkdir.assert_called_once_with(test.base_dir)

        del test

        mock_delete_directory.assert_called_once_with()

    @patch("caching.worker.shutil")
    @patch("caching.worker.os")
    @patch("caching.worker.Worker.__init__")
    def test__delete_directory(self, mock_init, mock_os, mock_shutil):
        mock_init.return_value = None
        mock_os.path.isdir.return_value = True

        test = Worker()
        test._base_dir = "test dir"
        test._locked = False
        test._delete_directory()

        mock_os.path.isdir.assert_called_once_with(test._base_dir)
        mock_shutil.rmtree.assert_called_once_with(test._base_dir)

    @patch("caching.worker.Worker._delete_directory")
    @patch("caching.worker.Worker.__init__")
    def test_base_dir(self, mock_init, mock_delete):
        mock_init.return_value = None
        test = Worker()
        test._base_dir = "test dir"
        test._locked = False

        self.assertEqual(test._base_dir, test.base_dir)

        del test

        mock_delete.assert_called_once_with()

    @patch("caching.worker.Worker._delete_directory")
    @patch("caching.worker.Worker.__init__")
    def test_lock(self, mock_init, mock_delete):
        mock_init.return_value = None
        test = Worker()
        test._locked = False
        test.lock()
        self.assertEqual(True, test._locked)

        del test
        self.assertEqual(0, len(mock_delete.call_args_list))


if __name__ == "__main__":
    main()
