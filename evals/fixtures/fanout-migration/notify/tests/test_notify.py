import unittest
from datetime import datetime

from notify.digest import digest_times_between, next_digest_after
from notify.quiet_hours import is_quiet, next_allowed
from notify.scheduler import Scheduler, SchedulerError


class TestScheduler(unittest.TestCase):
    def test_due_pops_ready_items_in_send_order(self):
        sched = Scheduler()
        sched.schedule("ana@example.com", "hi", "2024-11-20 10:00:00")
        sched.schedule("bo@example.com", "yo", "20/11/2024 09:30")
        sched.schedule("cy@example.com", "later", "2024-11-21T09:00:00")
        ready = sched.due("2024-11-20T12:00:00")
        self.assertEqual(
            [i["recipient"] for i in ready],
            ["bo@example.com", "ana@example.com"],
        )
        self.assertEqual(sched.pending_count(), 1)

    def test_unreadable_send_time_is_an_error(self):
        with self.assertRaises(SchedulerError):
            Scheduler().schedule("ana@example.com", "hi", "soonish")

    def test_unreadable_clock_time_is_an_error(self):
        with self.assertRaises(SchedulerError):
            Scheduler().due("around noon")


class TestQuietHours(unittest.TestCase):
    def test_late_night_is_quiet(self):
        self.assertTrue(is_quiet("2024-11-20 22:30:00"))
        self.assertTrue(is_quiet("2024-11-21T03:00:00"))

    def test_midday_is_not_quiet(self):
        self.assertFalse(is_quiet("20/11/2024 12:00"))

    def test_next_allowed_from_late_evening_is_next_morning(self):
        self.assertEqual(
            next_allowed("2024-11-20 23:15:00"), datetime(2024, 11, 21, 7, 0, 0)
        )

    def test_next_allowed_from_early_morning_is_same_morning(self):
        self.assertEqual(
            next_allowed("2024-11-21 05:30:00"), datetime(2024, 11, 21, 7, 0, 0)
        )

    def test_next_allowed_outside_quiet_hours_is_unchanged(self):
        self.assertEqual(
            next_allowed("2024-11-20T12:00:00"), datetime(2024, 11, 20, 12, 0, 0)
        )


class TestDigest(unittest.TestCase):
    def test_next_digest_before_send_hour_is_same_day(self):
        self.assertEqual(
            next_digest_after("2024-11-20 07:59:00"), datetime(2024, 11, 20, 8, 0, 0)
        )

    def test_next_digest_at_send_hour_rolls_to_next_day(self):
        self.assertEqual(
            next_digest_after("2024-11-20T08:00:00"), datetime(2024, 11, 21, 8, 0, 0)
        )

    def test_digest_times_between_spans_days(self):
        sends = digest_times_between("20/11/2024 09:00", "2024-11-22 09:00:00")
        self.assertEqual(
            sends,
            [datetime(2024, 11, 21, 8, 0, 0), datetime(2024, 11, 22, 8, 0, 0)],
        )

    def test_unreadable_anchor_is_an_error(self):
        with self.assertRaises(ValueError):
            next_digest_after("first thing tomorrow")


if __name__ == "__main__":
    unittest.main()
