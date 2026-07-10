import unittest
from datetime import datetime

from shipping.eta import estimate_eta
from shipping.manifest import ManifestError, load_shipment
from shipping.tracking import TrackingLog


class TestLoadShipment(unittest.TestCase):
    def test_load_delivered_shipment(self):
        shp = load_shipment(
            {
                "tracking_id": "TRK-7001",
                "shipped_at": "2024-09-10 08:00:00",
                "delivered_at": "12/09/2024 16:30",
            }
        )
        self.assertEqual(shp.shipped_at, datetime(2024, 9, 10, 8, 0, 0))
        self.assertEqual(shp.delivered_at, datetime(2024, 9, 12, 16, 30))
        self.assertFalse(shp.in_transit())
        self.assertEqual(shp.transit_seconds(), 203400)

    def test_missing_delivered_at_means_in_transit(self):
        shp = load_shipment(
            {"tracking_id": "TRK-7002", "shipped_at": "2024-09-10T08:00:00"}
        )
        self.assertTrue(shp.in_transit())

    def test_malformed_delivered_at_means_in_transit(self):
        # Legacy leniency: an unreadable delivered_at silently means "on the road".
        shp = load_shipment(
            {
                "tracking_id": "TRK-7003",
                "shipped_at": "2024-09-10 08:00:00",
                "delivered_at": "fell off the truck",
            }
        )
        self.assertTrue(shp.in_transit())

    def test_unreadable_shipped_at_is_an_error(self):
        with self.assertRaises(ManifestError):
            load_shipment({"tracking_id": "TRK-7004", "shipped_at": "last week"})

    def test_delivered_before_shipped_is_an_error(self):
        with self.assertRaises(ManifestError):
            load_shipment(
                {
                    "tracking_id": "TRK-7005",
                    "shipped_at": "2024-09-10 08:00:00",
                    "delivered_at": "2024-09-09 08:00:00",
                }
            )


class TestTrackingLog(unittest.TestCase):
    def test_scans_kept_sorted_and_latest_wins(self):
        log = TrackingLog("TRK-7001")
        log.add_scan("depot", "2024-09-10 09:00:00")
        log.add_scan("hub", "10/09/2024 08:15")
        self.assertEqual(log.latest()["location"], "depot")

    def test_scans_between_is_inclusive(self):
        log = TrackingLog("TRK-7001")
        log.add_scan("hub", "2024-09-10 08:15:00")
        log.add_scan("depot", "2024-09-10T09:00:00")
        log.add_scan("van", "2024-09-11 07:40:00")
        window = log.scans_between("2024-09-10T08:15:00", "2024-09-10T09:00:00")
        self.assertEqual([s["location"] for s in window], ["hub", "depot"])

    def test_unreadable_scan_timestamp_is_an_error(self):
        with self.assertRaises(ValueError):
            TrackingLog("TRK-7001").add_scan("hub", "tea time")


class TestEstimateEta(unittest.TestCase):
    def test_short_haul_next_day(self):
        eta = estimate_eta("2024-09-10 08:00:00", 30)
        self.assertEqual(eta, datetime(2024, 9, 11, 8, 0, 0))

    def test_long_haul_falls_back_to_a_week(self):
        eta = estimate_eta("10/09/2024 08:00", 3200)
        self.assertEqual(eta, datetime(2024, 9, 17, 8, 0))

    def test_unreadable_ship_time_is_an_error(self):
        with self.assertRaises(ValueError):
            estimate_eta("at dawn", 30)


if __name__ == "__main__":
    unittest.main()
