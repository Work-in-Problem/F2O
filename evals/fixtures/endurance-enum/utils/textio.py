"""Small text-file helpers."""


def read_text(path):
    """Whole file as one string."""
    return open(path).read()


def write_text(path, text):
    """Replace the file's content with the given text."""
    fh = open(path, "w")
    fh.write(text)


def concat_files(paths, out_path):
    """Concatenate files (in the given order) into out_path."""
    with open(out_path, "w") as out:
        for path in paths:
            fh = open(path)
            out.write(fh.read())


def head(path, limit=10):
    """First `limit` lines, without trailing newlines."""
    lines = []
    with open(path) as fh:
        for line in fh:
            if len(lines) >= limit:
                break
            lines.append(line.rstrip("\n"))
    return lines
