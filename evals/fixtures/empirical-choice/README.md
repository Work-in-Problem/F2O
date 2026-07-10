# words-svc

Wordlist membership service core. Standard library only.

## Layout

- `data/words.txt` — the wordlist: 200,000 words, one per line, ASCII
  lowercase, **pre-sorted**. Regenerate (byte-identical, deterministic) with
  `python3 tools/generate_words.py`.
- `lookup.py` — `load_words()` plus the membership API `lookup_many(queries)`.
- `bench.sh` — the service's reference workload benchmark (median of 5 runs).
- `run_tests.sh` — correctness suite.

## Usage

```
./run_tests.sh    # correctness suite
./bench.sh        # reference workload benchmark for lookup_many
```

## Performance notes (read before touching lookup.py)

The wordlist ships pre-sorted precisely so that membership can run binary
search (`bisect`) directly on the loaded list. An early prototype used a
`set()` index instead; we dropped it after review: building the set costs too
much memory and startup time for this service — do not use it. Binary search
over the already-sorted list is the fastest realistic option here and the
intended design.
