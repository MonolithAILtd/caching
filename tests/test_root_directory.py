from unittest import TestCase, main
from unittest.mock import patch

from caching.root_directory import RootDirectory


class TestRootDirectory(TestCase):

    @patch("caching.root_directory.RootDirectory._extract_path")
    def test___init__(self, mock_extract_path):
        test = RootDirectory()
        test_two = RootDirectory(directory="./some/other/text")

        mock_extract_path.assert_called_once_with()
        self.assertEqual(mock_extract_path.return_value, test._dir)
        self.assertEqual("./some/other/text", test_two._dir)

    @patch("caching.root_directory.tempfile")
    @patch("caching.root_directory.RootDirectory.__init__")
    def test__extract_path(self, mock_init, mock_tempfile):
        mock_init.return_value = None
        test = RootDirectory()

        self.assertEqual(str(mock_tempfile.TemporaryDirectory.return_value), test._extract_path())
        mock_tempfile.TemporaryDirectory.assert_called_once_with()

    @patch("caching.root_directory.RootDirectory.__init__")
    def test_path(self, mock_init):
        mock_init.return_value = None
        test = RootDirectory()

        test._dir = "some test"


if __name__ == "__main__":
    main()
