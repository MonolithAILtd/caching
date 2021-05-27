from unittest import TestCase, main
from unittest.mock import patch, MagicMock

from monolithcaching.register import Register, RegisterError


class TestRegister(TestCase):

    @patch("monolithcaching.register.StrictRedis")
    def test___init__(self, mock_redis):
        test = Register(host="localhost", port=12345)
        self.assertEqual(mock_redis.return_value, test._connection)
        mock_redis.assert_called_once_with(host="localhost", port=12345, db=0)

    @patch("monolithcaching.register.Register.__init__")
    def test_get_count(self, mock_init):
        mock_init.return_value = None
        test = Register(host="localhost", port=12345)
        test._connection = MagicMock()
        test._connection.hget.return_value = "3"

        outcome = test.get_count(cache_path="test path")
        self.assertEqual(3, outcome)
        test._connection.hget.assert_called_once_with(name="CACHE_REGISTER", key="test path")

        test._connection.hget.reset_mock()
        test._connection.hget.return_value = None
        outcome = test.get_count(cache_path="test path")
        self.assertEqual(None, outcome)
        test._connection.hget.assert_called_once_with(name="CACHE_REGISTER", key="test path")

    @patch("monolithcaching.register.Register.get_count")
    @patch("monolithcaching.register.Register.__init__")
    def test_register_cache(self, mock_init, mock_get_count):
        mock_init.return_value = None
        test = Register(host="localhost", port=12345)
        test._connection = MagicMock()

        mock_get_count.return_value = 3
        test.register_cache(cache_path="test path")
        test._connection.hset.assert_called_once_with(name="CACHE_REGISTER", key="test path", value="4")

        test._connection.hset.reset_mock()
        mock_get_count.return_value = None
        test.register_cache(cache_path="test path")
        test._connection.hset.assert_called_once_with(name="CACHE_REGISTER", key="test path", value="1")

    @patch("monolithcaching.register.Register.get_count")
    @patch("monolithcaching.register.Register.__init__")
    def test_deregister_cache(self, mock_init, mock_get_count):
        mock_init.return_value = None
        test = Register(host="localhost", port=12345)
        test._connection = MagicMock()

        mock_get_count.return_value = 3
        test.deregister_cache(cache_path="test path", locked=False)
        test._connection.hset.assert_called_once_with(name="CACHE_REGISTER", key="test path", value="2")
        test._connection.hset.reset_mock()

        mock_get_count.return_value = 1
        test.deregister_cache(cache_path="test path", locked=False)
        test._connection.hdel.assert_called_once_with("CACHE_REGISTER", "test path")
        test._connection.hdel.reset_mock()

        mock_get_count.return_value = 3
        test.deregister_cache(cache_path="test path", locked=True)
        test._connection.hset.assert_called_once_with(name="CACHE_REGISTER", key="test path", value="2")
        test._connection.hset.reset_mock()

        mock_get_count.return_value = 1
        test.deregister_cache(cache_path="test path", locked=True)
        self.assertEqual(0, len(test._connection.hdel.call_args_list))

        mock_get_count.return_value = None
        with self.assertRaises(RegisterError) as context:
            test.deregister_cache(cache_path="test path", locked=True)

        self.assertEqual("cache test path is not in cache register so it cannot be de-registered",
                         str(context.exception))

    @patch("monolithcaching.register.Register.__init__")
    def test_get_all_records(self, mock_init):
        mock_init.return_value = None
        test = Register(host="localhost", port=12345)
        test._connection = MagicMock()

        outcome = test.get_all_records()
        self.assertEqual(test._connection.hgetall.return_value, outcome)
        test._connection.hgetall.assert_called_once_with(name="CACHE_REGISTER")


if __name__ == "__main__":
    main()
