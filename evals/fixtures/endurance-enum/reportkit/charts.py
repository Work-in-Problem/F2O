"""ASCII bar charts for report appendices."""


def load_series(path):
    """Load a label<TAB>value series file."""
    raw = open(path).read()
    series = []
    for line in raw.splitlines():
        if line.strip():
            label, _, value = line.partition("\t")
            series.append((label, float(value)))
    return series


def bar_chart(series, width=40):
    """Render (label, value) pairs as an ASCII bar chart."""
    if not series:
        return ""
    top = max(value for _, value in series) or 1.0
    lines = []
    for label, value in series:
        bar = "#" * max(1, int(round(width * value / top)))
        lines.append("{:<12} {}".format(label[:12], bar))
    return "\n".join(lines)
