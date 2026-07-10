# contacts

Tiny command-line helpers for contact CSV files. Standard library only.

CSV format: a header row `name,email,phone` followed by one row per contact —
see `sample.csv` for an example.

## Usage

```
python3 contacts.py check CSVFILE    # validate the header and count data rows
python3 contacts.py names CSVFILE    # print the name column, one per line
```

Blank lines are ignored by both commands.

## Exit codes

- `0` — success
- `2` — usage error, unreadable file, or bad header

## Tests

```
python3 -m unittest discover -s tests -t . -v
```
