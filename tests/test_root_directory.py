import os
from unittest import TestCase, main

from caching.root_directory import RootDirectory


class TestRootDirectory(TestCase):

    def test___init__(self):
        test = RootDirectory()
        test_two = RootDirectory(directory="./some/other/text")

        self.assertEqual(os.environ['PYTHONPATH'].split(":")[0] + "/cache/", test.path)
        self.assertEqual("./some/other/text", test_two.path)


if __name__ == "__main__":
    main()
