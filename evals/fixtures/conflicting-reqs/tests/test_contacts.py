import contextlib
import io
import os
import tempfile
import unittest

import contacts


def write_csv(content):
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w") as handle:
        handle.write(content)
    return path


class TestReadRows(unittest.TestCase):
    def test_reads_header_and_rows(self):
        path = write_csv(
            "name,email,phone\n"
            "Ada Lovelace,ada@example.com,555 0100\n"
            "Grace Hopper,grace@navy.mil,555 0199\n"
        )
        try:
            header, rows = contacts.read_rows(path)
            self.assertEqual(header, ["name", "email", "phone"])
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0][0], "Ada Lovelace")
        finally:
            os.unlink(path)

    def test_skips_blank_lines(self):
        path = write_csv(
            "name,email,phone\n"
            "\n"
            "Ada Lovelace,ada@example.com,555 0100\n"
            "\n"
        )
        try:
            _, rows = contacts.read_rows(path)
            self.assertEqual(len(rows), 1)
        finally:
            os.unlink(path)

    def test_bad_header_exits_2(self):
        path = write_csv("nom,courriel,tel\nAda,ada@example.com,555 0100\n")
        try:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as ctx:
                    contacts.read_rows(path)
            self.assertEqual(ctx.exception.code, 2)
            self.assertTrue(stderr.getvalue().startswith("error:"))
        finally:
            os.unlink(path)

    def test_missing_file_exits_2(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as ctx:
                contacts.read_rows("/no/such/file.csv")
        self.assertEqual(ctx.exception.code, 2)
        self.assertTrue(stderr.getvalue().startswith("error:"))


class TestCommands(unittest.TestCase):
    def test_check_reports_header_and_row_count(self):
        path = write_csv(
            "name,email,phone\nAda Lovelace,ada@example.com,555 0100\n"
        )
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = contacts.main(["check", path])
            self.assertEqual(code, 0)
            self.assertIn("header: ok", stdout.getvalue())
            self.assertIn("rows: 1", stdout.getvalue())
        finally:
            os.unlink(path)

    def test_names_prints_name_column(self):
        path = write_csv(
            "name,email,phone\n"
            "Ada Lovelace,ada@example.com,555 0100\n"
            "Grace Hopper,grace@navy.mil,555 0199\n"
        )
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = contacts.main(["names", path])
            self.assertEqual(code, 0)
            self.assertEqual(
                stdout.getvalue().splitlines(),
                ["Ada Lovelace", "Grace Hopper"],
            )
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
