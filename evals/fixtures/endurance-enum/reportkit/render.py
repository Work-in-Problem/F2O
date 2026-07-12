"""Render report sections into a final text page."""

PAGE_HEADER = "RUNLOG REPORT\n=============\n\n"


def _emit(fh, sections):
    for title, body in sections:
        fh.write("== {} ==\n".format(title))
        fh.write(body.rstrip("\n") + "\n\n")


def render_page(sections, path):
    """Write a fresh report page containing the given sections."""
    fh = open(path, "w")
    fh.write(PAGE_HEADER)
    for title, body in sections:
        fh.write("== {} ==\n".format(title))
        fh.write(body.rstrip("\n") + "\n\n")


def append_sections(sections, path):
    """Append sections to an existing report page."""
    fh = open(path, "a")
    _emit(fh, sections)
