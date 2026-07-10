import unittest
from datetime import datetime

from catalog.dates import parse_when


class TestParseWhen(unittest.TestCase):
    def test_space_separated_format(self):
        self.assertEqual(
            parse_when("2024-06-01 08:15:00"), datetime(2024, 6, 1, 8, 15, 0)
        )

    def test_iso_t_separated_format(self):
        self.assertEqual(
            parse_when("2024-06-01T08:15:00"), datetime(2024, 6, 1, 8, 15, 0)
        )

    def test_day_first_slash_format(self):
        self.assertEqual(parse_when("01/06/2024 08:15"), datetime(2024, 6, 1, 8, 15))

    def test_surrounding_whitespace_is_ignored(self):
        self.assertEqual(
            parse_when(" 2024-06-01 08:15:00 "), datetime(2024, 6, 1, 8, 15, 0)
        )

    def test_garbage_yields_none(self):
        self.assertIsNone(parse_when("last summer"))

    def test_empty_and_none_yield_none(self):
        self.assertIsNone(parse_when(""))
        self.assertIsNone(parse_when(None))


if __name__ == "__main__":
    unittest.main()
