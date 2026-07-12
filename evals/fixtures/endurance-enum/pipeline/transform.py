"""Apply rewrite rules to event streams."""
import json


def load_rules(path):
    """Rules file: one JSON object per line, blank lines ignored."""
    return [json.loads(line) for line in open(path) if line.strip()]


def apply_rules(events, rules):
    """Return a new event list with every matching field rewritten."""
    out = []
    for event in events:
        item = dict(event)
        for rule in rules:
            if item.get(rule["field"]) == rule["match"]:
                item[rule["field"]] = rule["replace"]
        out.append(item)
    return out


def apply_rules_file(events_path, rules_path):
    """Load a JSONL event file and rewrite it with the given rules file."""
    fh = open(events_path)
    events = [json.loads(line) for line in fh if line.strip()]
    return apply_rules(events, load_rules(rules_path))
