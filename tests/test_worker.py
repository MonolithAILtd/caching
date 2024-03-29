from unittest import TestCase, main
from mock import patch, PropertyMock, MagicMock
from monolithcaching.worker import Worker, WorkerCacheError


class TestWorker(TestCase):

    @patch("monolithcaching.worker.Register")
    @patch("monolithcaching.worker.os")
    @patch("monolithcaching.worker.Worker._delete_directory")
    @patch("monolithcaching.worker.Worker._connect_directory")
    @patch("monolithcaching.worker.UUID")
    def test___init__(self, mock_uuid, mock_connect_directory, mock_delete_directory, mock_os, mock_register):
        mock_uuid.return_value = "test"

        test = Worker(host="localhost", port=1234)
        mock_os.urandom.assert_called_once_with(16)
        mock_uuid.assert_called_once_with(bytes=mock_os.urandom.return_value, version=4)
        self.assertEqual(mock_uuid.return_value, test.id)
        self.assertEqual(None, test._existing_cache)
        self.assertEqual(str(test.CLASS_BASE_DIR) + "/cache/{}/".format(test.id),
                         test._base_dir)
        self.assertEqual(False, test._locked)
        self.assertEqual(str(test.CLASS_BASE_DIR), test.class_base_dir)
        mock_register.assert_called_once_with(host="localhost", port=1234)
        mock_register.return_value.register_cache.assert_called_once_with(cache_path=test._base_dir)
        mock_register.reset_mock()

        del test

        mock_connect_directory.assert_called_once_with()
        mock_delete_directory.assert_called_once_with()

        test = Worker(host="localhost", port=1234, existing_cache="test")
        self.assertEqual("test", test._existing_cache)
        mock_register.assert_called_once_with(host="localhost", port=1234)
        mock_register.return_value.register_cache.assert_called_once_with(cache_path=test._base_dir)
        mock_register.reset_mock()

        test = Worker(host="localhost", port=1234, local_cache="testing")
        self.assertEqual("testing", test.class_base_dir)
        self.assertEqual("testing/cache/test/", test._base_dir)

        del test

        mock_register.reset_mock()

        test = Worker(port=None, host=None)
        self.assertEqual(0, len(mock_register.call_args_list))

    @patch("monolithcaching.worker.datetime")
    @patch("monolithcaching.worker.open")
    def test_update_timestamp(self, mock_open, mock_datetime):
        test = Worker
        test.id = 20
        test.update_timestamp(cache_path="test/path/")
        mock_open.assert_called_once_with("test/path/" + "timestamp.txt", "a")
        mock_open.return_value.write.assert_called_once_with("\n" + str(mock_datetime.datetime.now.return_value))
        mock_open.return_value.close.assert_called_once_with()

    @patch("monolithcaching.worker.Worker._delete_directory")
    @patch("monolithcaching.worker.Worker._generate_directory")
    @patch("monolithcaching.worker.os")
    @patch("monolithcaching.worker.Worker.__init__")
    def test__connect_directory(self, mock_init, mock_os, mock_generate, mock_delete):
        mock_init.return_value = None
        mock_os.path.isdir.return_value = False

        test = Worker(host="localhost", port=1234)
        test.id = 20
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

        del test

        mock_delete.assert_called_once_with()

    @patch("monolithcaching.worker.Worker.update_timestamp")
    @patch("monolithcaching.worker.os")
    @patch("monolithcaching.worker.Worker.__init__")
    def test__generate_directory(self, mock_init, mock_os, mock_update):
        mock_init.return_value = None
        mock_os.path.isdir.return_value = False

        test = Worker(host="localhost", port=1234)
        test.id = 20
        test._base_dir = "test dir"
        test.timestamp = "test timestamp"
        test._locked = False
        test._generate_directory()
        test._port = None
        test._delete_directory = MagicMock()

        mock_os.path.isdir.assert_called_once_with(test._base_dir)
        mock_os.makedirs.assert_called_once_with(test._base_dir)
        mock_update.assert_called_once_with(cache_path=test._base_dir)

        mock_os.path.isdir.return_value = True

        with self.assertRaises(Exception):
            test._generate_directory()

        mock_os.makedirs.assert_called_once_with(test.base_dir)

        del test

    @patch("monolithcaching.worker.Worker.base_dir", spec=PropertyMock)
    @patch("monolithcaching.worker.shutil")
    @patch("monolithcaching.worker.Register")
    @patch("monolithcaching.worker.Worker.__init__")
    def test__delete_directory(self, mock_init, mock_register, mock_shutil, mock_base_dir):
        mock_init.return_value = None
        mock_base_dir.return_value = "base dir"

        test = Worker(host="localhost", port=1234)
        test.id = "test id"
        test._locked = False
        test._host = "test host"
        test._port = 1234

        mock_register.return_value.deregister_cache.return_value = 1
        test._delete_directory()
        mock_register.assert_called_once_with(host="test host", port=1234)
        mock_register.return_value.deregister_cache.assert_called_once_with(cache_path=test.base_dir,
                                                                            locked=test._locked)
        mock_register.reset_mock()

        mock_register.return_value.deregister_cache.return_value = 0
        test._delete_directory()
        mock_register.assert_called_once_with(host="test host", port=1234)
        mock_register.return_value.deregister_cache.assert_called_once_with(cache_path=test.base_dir,
                                                                            locked=test._locked)
        mock_register.reset_mock()
        mock_shutil.rmtree.assert_called_once_with(test.base_dir)
        mock_shutil.reset_mock()

        test._locked = True
        mock_register.return_value.deregister_cache.return_value = 1
        test._delete_directory()
        mock_register.assert_called_once_with(host="test host", port=1234)
        mock_register.return_value.deregister_cache.assert_called_once_with(cache_path=test.base_dir,
                                                                            locked=test._locked)
        mock_register.reset_mock()
        mock_register.return_value.deregister_cache.return_value = 0
        test._delete_directory()
        mock_register.assert_called_once_with(host="test host", port=1234)
        mock_register.return_value.deregister_cache.assert_called_once_with(cache_path=test.base_dir,
                                                                            locked=test._locked)
        self.assertEqual(0, len(mock_shutil.rmtree.call_args_list))
        test._delete_directory = MagicMock()

    @patch("monolithcaching.worker.Worker._delete_directory")
    @patch("monolithcaching.worker.Worker.__init__")
    def test_base_dir(self, mock_init, mock_delete):
        mock_init.return_value = None
        test = Worker(host="localhost", port=1234)
        test._base_dir = "test dir"

        self.assertEqual(test._base_dir, test.base_dir)

        del test

        mock_delete.assert_called_once_with()

    @patch("monolithcaching.worker.Worker._delete_directory")
    @patch("monolithcaching.worker.Worker.__init__")
    def test_lock(self, mock_init, mock_delete):
        mock_init.return_value = None
        test = Worker(host="localhost", port=1234)
        test.id = 20
        test._base_dir = "test"
        test._locked = False
        test.lock()
        self.assertEqual(True, test._locked)

        del test

        mock_delete.assert_called_once_with()


if __name__ == "__main__":
    main()
