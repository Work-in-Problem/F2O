"""Append-only run journal (one entry per line)."""


class JournalReader:
    """Iterate journal entries from disk."""

    def __init__(self, path):
        self._fh = open(path)

    def entries(self):
        """Return all remaining non-blank entries."""
        out = []
        for line in self._fh:
            line = line.strip()
            if line:
                out.append(line)
        return out


class JournalWriter:
    """Append entries to a journal file."""

    def __init__(self, path):
        self._path = path
        self._fh = None

    def open(self):
        self._fh = open(self._path, "a")
        return self

    def record(self, entry):
        """Append one entry, opening the journal on first use."""
        if self._fh is None:
            self.open()
        self._fh.write(entry.rstrip("\n") + "\n")
        self._fh.flush()


def replay(path):
    """Return all non-blank entries of a finished journal."""
    with open(path) as fh:
        return [line.strip() for line in fh if line.strip()]
