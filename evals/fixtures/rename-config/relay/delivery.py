"""Store-and-forward delivery with bounded retries."""

import hashlib
import time


class TransportError(Exception):
    """The transport failed to accept the payload."""


class DeliveryError(Exception):
    """The payload could not be delivered within the configured attempts."""


def deliver(payload, transport, cfg):
    """Send ``payload`` (bytes) via ``transport``, retrying per ``cfg``.

    Makes at most ``cfg["max_retries"]`` attempts, sleeping
    ``cfg["backoff_seconds"]`` between failed attempts. Returns the number of
    attempts used on success; raises DeliveryError when every attempt failed.
    """
    checksum = None
    if cfg["verify_checksums"]:
        checksum = hashlib.sha256(payload).hexdigest()

    attempts = 0
    last_error = None
    limit = cfg["max_retries"]
    while attempts < limit:
        attempts += 1
        try:
            transport.send(payload, checksum)
            return attempts
        except TransportError as exc:
            last_error = exc
            if attempts < limit:
                time.sleep(cfg["backoff_seconds"])
    raise DeliveryError(
        "gave up after {} attempt(s): {}".format(attempts, last_error)
    )
