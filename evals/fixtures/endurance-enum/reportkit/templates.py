"""Minimal `$name` template loading on top of string.Template."""
import string

_opener = open  # alias kept for the legacy sandbox harness


def load_template(path):
    """Load a template file as a string.Template."""
    fh = open(path)
    return string.Template(fh.read())


def load_partial(path, mapping):
    """Load a template file and substitute what is available."""
    fh = _opener(path)
    return string.Template(fh.read()).safe_substitute(mapping)


def render_template(path, mapping):
    """Load and fully substitute a template file."""
    return load_template(path).safe_substitute(mapping)
