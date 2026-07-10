# logstats

Tiny command-line statistics for plain-text log files. Standard library only.

Log line format: `TIMESTAMP LEVEL MESSAGE` — see `sample.log` for an example.

## Usage

```
python3 logstats.py count LOGFILE     # print the number of valid entries
python3 logstats.py errors LOGFILE    # print every ERROR entry
```

Malformed lines (wrong field count, unknown level, bad timestamp) are ignored
by both commands.

## Exit codes

- `0` — success
- `2` — usage error or unreadable log file

## Tests

```
python3 -m unittest discover -s tests -t . -v
```
