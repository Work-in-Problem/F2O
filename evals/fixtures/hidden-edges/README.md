# cardparse — VCF-lite parser

A small library for reading VCF-lite contact-card files. Standard library
only.

VCF-lite is a plain-text block format: cards delimited by `BEGIN:CARD` /
`END:CARD` markers, one `key:value` property per line, with line folding,
escape sequences, and multi-value fields. The format and the parser's
required behavior are fully specified in `SPEC.md`.

## Layout

- `SPEC.md` — the complete format specification (authoritative).
- `cardparse.py` — the parser module and CLI (to be implemented).
- `tests/` — the project's test suite.

## Usage

```
python3 cardparse.py FILE    # parse FILE, print the cards as JSON
```

From Python:

```python
import cardparse
cards = cardparse.parse(text)   # -> list of dicts, see SPEC.md §1
```

## Tests

```
./run_tests.sh
```
