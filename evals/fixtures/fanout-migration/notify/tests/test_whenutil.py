import unittest
from datetime import datetime

from notify.whenutil import parse_when


class TestParseWhen(unittest.TestCase):
    def test_space_separated_format(self):
        self.assertEqual(
            parse_when("2024-11-20 21:05:00"), datetime(2024, 11, 20, 21, 5, 0)
        )

    def test_iso_t_separated_format(self):
        self.assertEqual(
            parse_when("2024-11-20T21:05:00"), datetime(2024, 11, 20, 21, 5, 0)
        )

    def test_day_first_slash_format(self):
        self.assertEqual(parse_when("20/11/2024 21:05"), datetime(2024, 11, 20, 21, 5))

    def test_surrounding_whitespace_is_ignored(self):
        self.assertEqual(
            parse_when("  2024-11-20 21:05:00"), datetime(2024, 11, 20, 21, 5, 0)
        )

    def test_garbage_yields_none(self):
        self.assertIsNone(parse_when("after lunch"))

    def test_empty_and_none_yield_none(self):
        self.assertIsNone(parse_when(""))
        self.assertIsNone(parse_when(None))


if __name__ == "__main__":
    unittest.main()
