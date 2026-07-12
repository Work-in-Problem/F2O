"""Shared helpers for the stockroom test suite."""

import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest

from stockroom import cli


class ProjectDirTestCase(unittest.TestCase):
    """Run each test inside a fresh temporary working directory.

    Tests write their own stockroom.cfg / data files, then invoke the CLI,
    which resolves both against the current working directory.
    """

    def setUp(self):
        self._old_cwd = os.getcwd()
        self.workdir = tempfile.mkdtemp(prefix="stockroom-test-")
        os.chdir(self.workdir)

    def tearDown(self):
        os.chdir(self._old_cwd)
        shutil.rmtree(self.workdir, ignore_errors=True)

    def write_data(self, items, filename="inventory.json"):
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump({"items": items}, handle, indent=2, sort_keys=True)
            handle.write("\n")
        return filename


def run_cli(argv):
    """Invoke cli.main(argv); return (exit_code, stdout, stderr)."""
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            code = cli.main(argv)
        except SystemExit as exc:
            code = exc.code
    return code, stdout.getvalue(), stderr.getvalue()
