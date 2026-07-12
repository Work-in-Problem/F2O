"""Concatenate text files into a single .bundle archive."""
import os

SEPARATOR = "--- {} ---"


def pack(paths, out_path):
    """Bundle the given files (sorted by path) into out_path."""
    with open(out_path, "w") as out:
        for path in sorted(paths):
            fh = open(path)
            out.write(SEPARATOR.format(os.path.basename(path)) + "\n")
            out.write(fh.read().rstrip("\n") + "\n")


def _split_entries(fh):
    """Parse a bundle stream into {name: content} in file order."""
    entries = {}
    name = None
    buf = []
    for line in fh.read().splitlines():
        if line.startswith("--- ") and line.endswith(" ---"):
            if name is not None:
                entries[name] = "\n".join(buf) + "\n"
            name = line[4:-4]
            buf = []
        else:
            buf.append(line)
    if name is not None:
        entries[name] = "\n".join(buf) + "\n"
    return entries


def unpack(bundle_path):
    """Read a bundle back into {name: content}."""
    fh = open(bundle_path)
    return _split_entries(fh)
