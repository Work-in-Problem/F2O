import unittest

import alerts


class MakeAlertTests(unittest.TestCase):
    def test_fields_are_preserved(self):
        a = alerts.make_alert("Disk full", "usage at 98%", "2026-07-11T08:00:00Z")
        self.assertEqual(a["title"], "Disk full")
        self.assertEqual(a["message"], "usage at 98%")
        self.assertEqual(a["timestamp"], "2026-07-11T08:00:00Z")


class ToSlackPayloadTests(unittest.TestCase):
    def test_text_line_format(self):
        a = alerts.make_alert("Disk full", "usage at 98%", "2026-07-11T08:00:00Z")
        p = alerts.to_slack_payload(a)
        self.assertEqual(
            p, {"text": "[2026-07-11T08:00:00Z] Disk full: usage at 98%"}
        )

    def test_payload_has_only_text_key(self):
        a = alerts.make_alert("t", "m", "ts")
        self.assertEqual(sorted(alerts.to_slack_payload(a)), ["text"])


if __name__ == "__main__":
    unittest.main()
