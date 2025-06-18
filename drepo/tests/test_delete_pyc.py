r"""
Test file for the `delete_pyc` module of the "drepo" library.

Notes
-----
#.  Written by David C. Stauffer in March 2025.
"""

# %% Imports
import contextlib
import os
from pathlib import Path
import unittest

from dstauffman import write_text_file
from slog import capture_output

import drepo as dr


# %% parse_delete_pyc
class Test_parse_delete_pyc(unittest.TestCase):
    r"""
    Tests the parse_delete_pyc function with the following cases:
        TBD
    """

    pass  # TODO: write this


# %% execute_delete_pyc
class Test_execute_delete_pyc(unittest.TestCase):
    r"""
    Tests the execute_delete_pyc function with the following cases:
        TBD
    """

    pass  # TODO: write this


# %% delete_pyc
class Test_delete_pyc(unittest.TestCase):
    r"""
    Tests the delete_pyc function with the following cases:
        Recursive
        Not recursive
    """

    def setUp(self) -> None:
        self.fold1 = Path(__file__).resolve().parent
        self.file1 = self.fold1 / "temp_file.pyc"
        self.fold2 = self.fold1 / "temp_sub_dir"
        self.file2 = self.fold2 / "temp_file2.pyc"
        write_text_file(self.file1, "Text.")
        self.fold2.mkdir(exist_ok=True)
        write_text_file(self.file2, "More text.")

    def test_recursive(self) -> None:
        self.assertTrue(self.file1.is_file())
        self.assertTrue(self.fold2.is_dir())
        self.assertTrue(self.file2.is_file())
        with capture_output() as ctx:
            dr.delete_pyc(self.fold1)
        output = ctx.get_output()
        ctx.close()
        lines = output.split("\n")
        self.assertFalse(self.file1.is_file())
        self.assertFalse(self.file2.is_file())
        for this_line in lines:
            self.assertTrue(this_line.startswith('Removing "'))
            self.assertTrue(this_line.endswith('temp_file.pyc"') or this_line.endswith('temp_file2.pyc"'))

    def test_not_recursive(self) -> None:
        self.assertTrue(self.file1.is_file())
        self.assertTrue(self.fold2.is_dir())
        self.assertTrue(self.file2.is_file())
        with capture_output() as ctx:
            dr.delete_pyc(self.fold1, recursive=False)
        output = ctx.get_output()
        ctx.close()
        lines = output.split("\n")
        self.assertFalse(self.file1.is_file())
        self.assertTrue(self.file2.is_file())
        for this_line in lines:
            self.assertTrue(this_line.startswith('Removing "'))
            self.assertTrue(this_line.endswith('temp_file.pyc"'))

    def test_no_logging(self) -> None:
        self.assertTrue(self.file1.is_file())
        self.assertTrue(self.fold2.is_dir())
        self.assertTrue(self.file2.is_file())
        with capture_output() as ctx:
            dr.delete_pyc(self.fold1, print_progress=False)
        output = ctx.get_output()
        ctx.close()
        self.assertFalse(self.file1.is_file())
        self.assertFalse(self.file2.is_file())
        self.assertEqual(output, "")

    def tearDown(self) -> None:
        self.file1.unlink(missing_ok=True)
        self.file2.unlink(missing_ok=True)
        with contextlib.suppress(FileNotFoundError):
            os.removedirs(self.fold2)


# %% Unit test execution
if __name__ == "__main__":
    unittest.main(exit=False)
