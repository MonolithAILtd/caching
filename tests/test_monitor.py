import unittest
from mock import patch
from caching.monitor import Monitor


class TestMonitor(unittest.TestCase):

    @patch("caching.monitor.os")
    @patch("caching.monitor.UUID")
    def test___init__(self, mock_uuid, mock_os):
        mock_uuid.return_value = "test"

        test = Monitor()

        mock_os.urandom.assert_called_once_with(16)
        mock_uuid.assert_called_once_with(bytes=mock_os.urandom.return_value, version=4)
        self.assertEqual(mock_uuid.return_value, test.id)
        self.assertEqual(str(test.CLASS_BASE_DIR) + "/cache/{}/".format(test.id),
                         test._base_dir)

        self.assertEqual(list(test.keys())[0], test.id)
        self.assertEqual(list(test.values())[0], test.base_dir)

        del test


if __name__ == '__main__':
    unittest.main()
