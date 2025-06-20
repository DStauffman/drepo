r"""
Test file for the `enforce` module of the "drepo" library.

Notes
-----
#.  Written by David C. Stauffer in March 2025.
"""

# %% Imports
import argparse
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from slog import capture_output, write_text_file

import drepo as dr


# %% parse_enforce
class Test_parse_enforce(unittest.TestCase):
    r"""
    Tests the parse_enforce function with the following cases:
        Nominal
    """

    def setUp(self) -> None:
        # fmt: off
        self.folder               = str(dr.get_root_dir())
        self.expected             = argparse.Namespace()
        self.expected.execute     = False
        self.expected.extensions  = None
        self.expected.folder      = self.folder
        self.expected.ignore_tabs = False
        self.expected.list_all    = False
        self.expected.skip        = None
        self.expected.trailing    = False
        self.expected.unix        = False
        self.expected.windows     = False
        # fmt: on

    def test_nominal(self) -> None:
        args = dr.parse_enforce([self.folder])
        self.assertEqual(args, self.expected)

    def test_extensions(self) -> None:
        self.expected.extensions = ["f", "f90"]
        args = dr.parse_enforce([self.folder, "-e", "f", "-e", "f90"])
        self.assertEqual(args, self.expected)

    def test_list_all(self) -> None:
        self.expected.list_all = True
        args = dr.parse_enforce([self.folder, "-l"])
        self.assertEqual(args, self.expected)

    def test_ignore_tabs(self) -> None:
        self.expected.ignore_tabs = True
        args = dr.parse_enforce([self.folder, "-i"])
        self.assertEqual(args, self.expected)

    def test_trailing(self) -> None:
        self.expected.trailing = True
        args = dr.parse_enforce([self.folder, "-t"])
        self.assertEqual(args, self.expected)

    def test_skip(self) -> None:
        self.expected.skip = ["m"]
        args = dr.parse_enforce([self.folder, "-s", "m"])
        self.assertEqual(args, self.expected)

    def test_windows(self) -> None:
        self.expected.windows = True
        self.expected.unix = False
        args = dr.parse_enforce([self.folder, "-w"])
        self.assertEqual(args, self.expected)

    def test_unix(self) -> None:
        self.expected.windows = False
        self.expected.unix = True
        args = dr.parse_enforce([self.folder, "-u"])
        self.assertEqual(args, self.expected)

    def test_bad_os_combination(self) -> None:
        with capture_output("err") as ctx:
            with self.assertRaises(SystemExit):
                dr.parse_enforce([self.folder, "-w", "-u"])
        stderr = ctx.get_error()
        ctx.close()
        self.assertTrue(stderr.startswith("usage: enforce"))

    def test_execute(self) -> None:
        self.expected.execute = True
        args = dr.parse_enforce([self.folder, "-x"])
        self.assertEqual(args, self.expected)


# %% execute_enforce
@patch("drepo.enforce.find_repo_issues")
class Test_execute_enforce(unittest.TestCase):
    r"""
    Tests the execute_enforce function with the following cases:
        Nominal
        TBD
    """

    def setUp(self) -> None:
        self.folder = dr.get_root_dir().joinpath("tests")
        self.args = argparse.Namespace(
            execute=False,
            extensions=None,
            folder=self.folder,
            ignore_tabs=False,
            list_all=False,
            skip=None,
            trailing=False,
            unix=False,
            windows=False,
        )
        self.patch_args = {
            "folder": self.folder,
            "extensions": frozenset({".m", ".py"}),
            "list_all": False,
            "check_tabs": True,
            "trailing": False,
            "exclusions": None,
            "check_eol": None,
            "show_execute": False,
        }

    def test_nominal(self, mocker: Mock) -> None:
        dr.execute_enforce(self.args)
        mocker.assert_called_once_with(**self.patch_args)

    def test_windows(self, mocker: Mock) -> None:
        self.args.windows = True
        self.patch_args["check_eol"] = "\r\n"
        dr.execute_enforce(self.args)
        mocker.assert_called_once_with(**self.patch_args)

    def test_unix(self, mocker: Mock) -> None:
        self.args.unix = True
        self.patch_args["check_eol"] = "\n"
        dr.execute_enforce(self.args)
        mocker.assert_called_once_with(**self.patch_args)

    def test_all_extensions(self, mocker: Mock) -> None:
        self.args.extensions = "*"
        self.patch_args["extensions"] = None
        dr.execute_enforce(self.args)
        mocker.assert_called_once_with(**self.patch_args)

    def test_extensions(self, mocker: Mock) -> None:
        self.args.extensions = ["f90"]
        self.patch_args["extensions"] = ["f90"]
        dr.execute_enforce(self.args)
        mocker.assert_called_once_with(**self.patch_args)


# %% find_repo_issues
class Test_find_repo_issues(unittest.TestCase):
    r"""
    Tests the find_repo_issues function with the following cases:
        Nominal
        Different Extensions
        List All
        Trailing Spaces
        Exclusions x2
        Bad New Lines
        Ignore tabs
    """

    folder: Path
    linesep: str
    files: list[Path]
    bad1: str
    bad2: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.folder = dr.get_root_dir().joinpath("tests")
        cls.linesep = os.linesep.replace("\n", "\\n").replace("\r", "\\r")
        file1 = cls.folder / "temp_code_01.py"
        file2 = cls.folder / "temp_code_02.py"
        file3 = cls.folder / "temp_code_03.m"
        cont1 = "Line 1\n\nAnother line\n    Line with leading spaces\n"
        cont2 = "\n\n    Start line\nNo Bad tab lines\n    Start and end line    \nAnother line\n\n"
        cont3 = "\n\n    Start line\n\tBad tab line\n    Start and end line    \nAnother line\n\n"
        cls.files = [file1, file2, file3]
        write_text_file(file1, cont1)
        write_text_file(file2, cont2)
        write_text_file(file3, cont3)
        cls.bad1 = "    Line 004: '\\tBad tab line" + cls.linesep + "'"
        cls.bad2 = "    Line 005: '    Start and end line    " + cls.linesep + "'"

    def test_nominal(self) -> None:
        with capture_output() as ctx:
            dr.find_repo_issues(self.folder, extensions=".m", list_all=False, trailing=False)
        lines = ctx.get_output().split("\n")
        ctx.close()
        self.assertTrue(lines[0].startswith('Evaluating: "'))
        self.assertEqual(lines[1], self.bad1)
        self.assertEqual(len(lines), 2)

    def test_different_extensions(self) -> None:
        with capture_output() as ctx:
            dr.find_repo_issues(self.folder, extensions=(".txt",))
        lines = ctx.get_output().split("\n")
        ctx.close()
        self.assertEqual(lines[0], "")
        self.assertEqual(len(lines), 1)

    def test_list_all(self) -> None:
        with capture_output() as ctx:
            dr.find_repo_issues(self.folder, list_all=True)
        lines = ctx.get_output().split("\n")
        ctx.close()
        self.assertIn(self.bad1, lines)
        self.assertNotIn(self.bad2, lines)

    def test_trailing_spaces(self) -> None:
        with capture_output() as ctx:
            dr.find_repo_issues(self.folder, trailing=True)
        lines = ctx.get_output().split("\n")
        ctx.close()
        self.assertEqual(sum(x.startswith('Evaluating: "') for x in lines), 2)
        self.assertIn(self.bad1, lines)
        self.assertIn(self.bad2, lines)
        self.assertEqual(len(lines), 5)

    def test_trailing_and_list_all(self) -> None:
        with capture_output() as ctx:
            dr.find_repo_issues(self.folder, list_all=True, trailing=True)
        lines = ctx.get_output().split("\n")
        ctx.close()
        self.assertTrue(lines[0].startswith('Evaluating: "'))
        self.assertIn(self.bad1, lines)
        self.assertIn(self.bad2, lines)
        self.assertTrue(len(lines) > 7)

    def test_exclusions_skip(self) -> None:
        exclusions = self.folder
        with capture_output() as ctx:
            dr.find_repo_issues(self.folder, exclusions=exclusions)
        lines = ctx.get_output().split("\n")
        ctx.close()
        self.assertEqual(lines, [""])

    def test_exclusions_invalid(self) -> None:
        exclusions = (Path(r"C:\non_existant_path"),)
        with capture_output() as ctx:
            dr.find_repo_issues(self.folder, exclusions=exclusions)
        lines = ctx.get_output().split("\n")
        ctx.close()
        self.assertTrue(lines[0].startswith('Evaluating: "'))
        self.assertEqual(lines[1], self.bad1)
        self.assertEqual(len(lines), 2)

    def test_bad_newlines(self) -> None:
        with capture_output() as ctx:
            dr.find_repo_issues(self.folder, extensions=".m", check_eol="0")
        lines = ctx.get_output().split("\n")
        ctx.close()
        self.assertTrue(lines[0].startswith('File: "'))
        self.assertIn('" has bad line endings of "', lines[0])
        self.assertTrue(any(x.startswith('Evaluating: "') for x in lines))
        self.assertIn(self.bad1, lines)
        self.assertEqual(len(lines), 3)

    def test_ignore_tabs(self) -> None:
        with capture_output() as ctx:
            dr.find_repo_issues(self.folder, extensions=".m", check_tabs=False)
        output = ctx.get_output()
        ctx.close()
        self.assertEqual(output, "")

    @classmethod
    def tearDownClass(cls) -> None:
        for this_file in cls.files:
            this_file.unlink(missing_ok=True)


# %% Unit test execution
if __name__ == "__main__":
    unittest.main(exit=False)
