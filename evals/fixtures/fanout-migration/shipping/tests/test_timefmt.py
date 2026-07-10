import unittest
from datetime import datetime

from shipping.timefmt import parse_when


class TestParseWhen(unittest.TestCase):
    def test_space_separated_format(self):
        self.assertEqual(
            parse_when("2024-09-12 06:45:00"), datetime(2024, 9, 12, 6, 45, 0)
        )

    def test_iso_t_separated_format(self):
        self.assertEqual(
            parse_when("2024-09-12T06:45:00"), datetime(2024, 9, 12, 6, 45, 0)
        )

    def test_day_first_slash_format(self):
        self.assertEqual(parse_when("12/09/2024 06:45"), datetime(2024, 9, 12, 6, 45))

    def test_surrounding_whitespace_is_ignored(self):
        self.assertEqual(
            parse_when("\t2024-09-12T06:45:00\n"), datetime(2024, 9, 12, 6, 45, 0)
        )

    def test_garbage_yields_none(self):
        self.assertIsNone(parse_when("somewhere in transit"))

    def test_empty_and_none_yield_none(self):
        self.assertIsNone(parse_when(""))
        self.assertIsNone(parse_when(None))


if __name__ == "__main__":
    unittest.main()
