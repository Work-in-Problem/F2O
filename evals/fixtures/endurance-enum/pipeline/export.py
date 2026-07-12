"""Write processed events back out to disk."""
import csv
import os


def write_csv(events, path, fields):
    """Write events as CSV with the given column order."""
    fh = open(path, "w", newline="")
    writer = csv.DictWriter(fh, fieldnames=fields)
    writer.writeheader()
    for event in events:
        writer.writerow({key: event.get(key, "") for key in fields})


def write_summary(counts, path):
    """Write a key<TAB>count summary, sorted by key."""
    fh = open(path, "w")
    for key in sorted(counts):
        fh.write("{}\t{}\n".format(key, counts[key]))


def export_partitions(groups, out_dir):
    """Write one .tsv per group; return the paths written."""
    written = []
    for name in sorted(groups):
        target = os.path.join(out_dir, name + ".tsv")
        fh = open(target, "w")
        for event in groups[name]:
            fh.write("\t".join(str(v) for v in event.values()) + "\n")
        written.append(target)
    return written


def write_manifest(paths, path):
    """Record the exported file list, one path per line, sorted."""
    with open(path, "w") as fh:
        for item in sorted(paths):
            fh.write(item + "\n")
