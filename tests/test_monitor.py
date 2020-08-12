from unittest import TestCase, main
from mock import patch

from caching.monitor import Monitor, Singleton, MonitorError


class TestMonitor(TestCase):

    def tearDown(self) -> None:
        Singleton._instances = {}

    def test___init__(self):
        test = Monitor()
        self.assertEqual({}, test)

        test_two = Monitor()
        self.assertEqual(id(test_two), id(test))

        test["one"] = "1"
        self.assertEqual({"one": "1"}, test)
        self.assertEqual({"one": "1"}, test_two)

    def test___setitem__(self):
        test = Monitor()

        with self.assertRaises(MonitorError) as context:
            test[2] = "something"
        self.assertEqual("key type is <class 'int'> instead of string", str(context.exception))

        with self.assertRaises(MonitorError) as context:
            test["something"] = 2
        self.assertEqual("value type is <class 'int'> instead of string", str(context.exception))

        test["something"] = "something else"

        self.assertEqual({"something": "something else"}, test)

    @patch("caching.monitor.shutil")
    @patch("caching.monitor.os")
    def test_delete_cache(self, mock_os, mock_shutil):
        test: Monitor = Monitor()

        # one where directory is there and we have one ID for one cache
        test.update({
            "1": "cache/path/one/"
        })
        mock_os.path.isdir.return_value = True
        test.delete_cache(entry_id="1")

        mock_os.path.isdir.assert_called_once_with("cache/path/one/")
        mock_shutil.rmtree.assert_called_once_with("cache/path/one/")
        self.assertEqual({}, test)

        mock_os.reset_mock()
        mock_shutil.reset_mock()

        # one where the directory is there and we have multiple IDs for one cache
        test.update({
            "1": "cache/path/one/",
            "2": "cache/path/one/",
            "3": "cache/path/one/"
        })
        test.delete_cache(entry_id="1")
        mock_os.path.isdir.assert_called_once_with("cache/path/one/")
        self.assertEqual(0, len(mock_shutil.rmtree.call_args_list))

        self.assertEqual({"2": "cache/path/one/", "3": "cache/path/one/"}, test)

        mock_os.reset_mock()
        mock_shutil.reset_mock()

        # one where the directory doesn't exist and neither does the key
        mock_os.path.isdir.return_value = False
        del test["2"]
        test.delete_cache(entry_id="2")

        self.assertEqual(0, len(mock_shutil.rmtree.call_args_list))
        self.assertEqual(0, len(mock_os.path.isdir.call_args_list))
        self.assertEqual({"3": "cache/path/one/"}, test)

        mock_os.reset_mock()
        mock_shutil.reset_mock()

        # one where the directory doesn't exist but the key does
        test.delete_cache(entry_id="3")
        self.assertEqual(0, len(mock_shutil.rmtree.call_args_list))
        self.assertEqual({}, test)


if __name__ == "__main__":
    main()
