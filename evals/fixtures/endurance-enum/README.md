# runlog

A small toolkit for turning raw run-event exports into plain-text reports:
ingest CSV/JSONL event dumps, transform and validate them, archive processed
runs, and render fixed-width text reports. Standard library only.

## Layout

- `pipeline/` — ingest, transform, validate, export, checkpoint, dedupe stages
- `reportkit/` — text report rendering: tables, charts, templates, summaries
- `storage/` — file-backed cache, bundle archive, catalog, run journal
- `utils/` — shared text/CSV/JSON/lockfile helpers
- `scripts/` — command-line entry points
- `data/` — sample inputs for the script examples below

## Scripts

```
python3 scripts/build_report.py data/report_config.json out.txt
python3 scripts/stats.py data/sample_events.csv
python3 scripts/merge_runs.py merged.tsv shard_a.tsv shard_b.tsv
```

## Tests

```
./run_tests.sh
```
