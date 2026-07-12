# stockroom

Small command-line inventory tracker for the parts room. Standard library
only.

Inventory lives in a JSON data file (default `inventory.json`): an object
with an `items` mapping of item name to quantity. See the shipped
`inventory.json` for an example.

## Configuration

`stockroom` reads `stockroom.cfg` (INI format) from the current working
directory when present:

```
[store]
file = inventory.json
```

`file` sets the data-file path; a relative path resolves against the
current working directory. Without a config file (or without the key) the
default `inventory.json` is used.

## Usage

```
python3 -m stockroom add ITEM QTY      # add QTY of ITEM (creates ITEM if new)
python3 -m stockroom remove ITEM QTY   # remove QTY of ITEM
python3 -m stockroom list              # print each item and its quantity
python3 -m stockroom report            # print item count and total quantity
```

## Exit codes

- `0` — success
- `2` — usage error, unreadable or malformed data file, or unknown item

## Tests

```
./run_tests.sh
```
