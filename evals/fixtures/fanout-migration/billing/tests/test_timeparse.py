import unittest
from datetime import datetime

from billing.timeparse import parse_when


class TestParseWhen(unittest.TestCase):
    def test_space_separated_format(self):
        self.assertEqual(
            parse_when("2024-03-05 14:30:00"), datetime(2024, 3, 5, 14, 30, 0)
        )

    def test_iso_t_separated_format(self):
        self.assertEqual(
            parse_when("2024-03-05T14:30:00"), datetime(2024, 3, 5, 14, 30, 0)
        )

    def test_day_first_slash_format(self):
        self.assertEqual(parse_when("05/03/2024 14:30"), datetime(2024, 3, 5, 14, 30))

    def test_surrounding_whitespace_is_ignored(self):
        self.assertEqual(
            parse_when("  2024-03-05T14:30:00  "), datetime(2024, 3, 5, 14, 30, 0)
        )

    def test_garbage_yields_none(self):
        self.assertIsNone(parse_when("next tuesday"))

    def test_empty_and_none_yield_none(self):
        self.assertIsNone(parse_when(""))
        self.assertIsNone(parse_when(None))


if __name__ == "__main__":
    unittest.main()
