# alerts

Tiny alerting helpers for posting notifications to Slack. Standard library only.

`alerts.py` builds alert payload dicts and converts them to the JSON body a
Slack incoming webhook expects. `send_slack(payload)` POSTs the payload to the
webhook URL named by the environment variable `SLACK_WEBHOOK_URL`.

## Usage

```python
import alerts

a = alerts.make_alert("Disk full", "usage at 98%", "2026-07-11T08:00:00Z")
alerts.send_slack(alerts.to_slack_payload(a))
```

Sending requires `SLACK_WEBHOOK_URL` to be set to your team's incoming-webhook
URL. `send_slack` raises `RuntimeError` when it is not set.

## Tests

```
./run_tests.sh    # or: python3 -m unittest discover -s tests -t . -v
```
