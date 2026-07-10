import os
import tempfile
import unittest
from datetime import datetime

import logstats


class TestParseLine(unittest.TestCase):
    def test_parses_valid_line(self):
        ts, level, message = logstats.parse_line(
            "2026-07-01T09:15:00 INFO Started worker pool"
        )
        self.assertEqual(ts, datetime(2026, 7, 1, 9, 15, 0))
        self.assertEqual(level, "INFO")
        self.assertEqual(message, "Started worker pool")

    def test_rejects_unknown_level(self):
        self.assertIsNone(
            logstats.parse_line("2026-07-01T09:15:00 TRACE too chatty")
        )

    def test_rejects_bad_timestamp(self):
        self.assertIsNone(logstats.parse_line("yesterday INFO vague"))

    def test_rejects_short_line(self):
        self.assertIsNone(logstats.parse_line("INFO lonely"))


class TestLoadEntries(unittest.TestCase):
    def test_counts_valid_and_skipped(self):
        content = (
            "2026-07-01T09:15:00 INFO ok\n"
            "garbage\n"
            "2026-07-01T09:16:00 ERROR boom\n"
        )
        fd, path = tempfile.mkstemp(suffix=".log")
        try:
            with os.fdopen(fd, "w") as handle:
                handle.write(content)
            entries, skipped = logstats.load_entries(path)
            self.assertEqual(len(entries), 2)
            self.assertEqual(skipped, 1)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
