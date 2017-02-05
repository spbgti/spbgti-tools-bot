from unittest import TestCase

from bot.log_helpers import log_with_args


class LogHelperTest(TestCase):
    def test_log_with_args(self):
        func = lambda x: x * 2
        wrapped = log_with_args(func)

        result = wrapped(2)

        self.assertEqual(4, result)
