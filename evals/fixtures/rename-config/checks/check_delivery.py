import unittest

from relay.delivery import DeliveryError, TransportError, deliver

BASE_CFG = {
    "source_dir": "./outbox",
    "max_retries": 3,
    "backoff_seconds": 0.0,
    "verify_checksums": True,
}


def cfg(**overrides):
    merged = dict(BASE_CFG)
    merged.update(overrides)
    return merged


class FlakyTransport:
    """Fails the first ``failures`` sends, then accepts."""

    def __init__(self, failures):
        self.failures = failures
        self.calls = []

    def send(self, payload, checksum):
        self.calls.append((payload, checksum))
        if len(self.calls) <= self.failures:
            raise TransportError("simulated outage #{}".format(len(self.calls)))


class TestDeliver(unittest.TestCase):
    def test_succeeds_within_retry_budget(self):
        transport = FlakyTransport(failures=2)
        attempts = deliver(b"parcel", transport, cfg(max_retries=3))
        self.assertEqual(attempts, 3)
        self.assertEqual(len(transport.calls), 3)

    def test_gives_up_after_budget_exhausted(self):
        transport = FlakyTransport(failures=99)
        with self.assertRaises(DeliveryError):
            deliver(b"parcel", transport, cfg(max_retries=2))
        self.assertEqual(len(transport.calls), 2)

    def test_budget_of_one_means_single_attempt(self):
        transport = FlakyTransport(failures=99)
        with self.assertRaises(DeliveryError):
            deliver(b"parcel", transport, cfg(max_retries=1))
        self.assertEqual(len(transport.calls), 1)

    def test_checksum_attached_when_verification_on(self):
        transport = FlakyTransport(failures=0)
        deliver(b"parcel", transport, cfg())
        payload, checksum = transport.calls[0]
        self.assertEqual(payload, b"parcel")
        self.assertEqual(len(checksum), 64)

    def test_checksum_omitted_when_verification_off(self):
        transport = FlakyTransport(failures=0)
        deliver(b"parcel", transport, cfg(verify_checksums=False))
        self.assertIsNone(transport.calls[0][1])
