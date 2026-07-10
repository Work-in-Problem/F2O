# relaybox

Tiny store-and-forward delivery relay. Standard library only.

Payloads dropped into the outbox are delivered through a pluggable transport
with bounded retries and optional checksum verification. In production a cron
entry runs a nightly sweep that re-budgets deliveries that got stuck during
the day.

## Configuration

Runtime settings live in `config.json` at the project root. Keys:

| key | type | default | meaning |
|---|---|---|---|
| `source_dir` | str | `./outbox` | Directory scanned for outgoing payloads. |
| `max_retries` | int | `3` | Maximum delivery attempts per payload. |
| `backoff_seconds` | float | `0.5` | Pause between failed attempts. |
| `verify_checksums` | bool | `true` | Attach a SHA-256 checksum to each send. |

`relay/spec.py` is the source of truth for keys, types, and defaults. The
published schema module under `generated/` is machine-written from it — see
that file's header before touching anything there.

## Layout

- `relay/` — core package (config loading, delivery)
- `scripts/` — operational entry points run by cron
- `tools/` — maintainer utilities
- `generated/` — machine-written modules, never edited by hand
- `checks/` — the project's test suite
