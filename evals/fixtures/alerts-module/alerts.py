"""Tiny alerting helpers: build alert payloads and post them to Slack.

Standard library only.
"""

import json
import os
import urllib.request


def make_alert(title, message, timestamp):
    """Build an alert payload dict from its parts."""
    return {
        "title": title,
        "message": message,
        "timestamp": timestamp,
    }


def to_slack_payload(alert):
    """Convert an alert dict to the JSON body a Slack incoming webhook expects."""
    text = "[{timestamp}] {title}: {message}".format(
        timestamp=alert["timestamp"],
        title=alert["title"],
        message=alert["message"],
    )
    return {"text": text}


def send_slack(payload):
    """POST payload as JSON to the Slack webhook named by $SLACK_WEBHOOK_URL.

    Returns the HTTP status code on success. Raises RuntimeError when
    SLACK_WEBHOOK_URL is not set in the environment.
    """
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url:
        raise RuntimeError(
            "SLACK_WEBHOOK_URL is not set; cannot post to Slack. "
            "Set it to your incoming-webhook URL and retry."
        )
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status
