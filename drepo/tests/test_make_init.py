r"""
Test file for the `make_init` module of the "drepo" library.

Notes
-----
#.  Written by David C. Stauffer in March 2025.
"""

# %% Imports
import argparse
import unittest
from unittest.mock import Mock, patch

from slog import capture_output

import drepo as dr


# %% parse_make_init
class Test_parse_make_init(unittest.TestCase):
    r"""
    Tests the parse_make_init function with the following cases:
        TBD
    """

    def setUp(self) -> None:
        # fmt: off
        self.folder           = str(dr.get_root_dir())
        self.expected         = argparse.Namespace()
        self.expected.dry_run = False
        self.expected.folder  = self.folder
        self.expected.lineup  = False
        self.expected.outfile = "__init__.py"
        self.expected.wrap    = 100
        # fmt: on

    def test_nominal(self) -> None:
        args = dr.parse_make_init([self.folder])
        self.assertEqual(args, self.expected)

    def test_dry_num(self) -> None:
        self.expected.dry_run = True
        args = dr.parse_make_init([self.folder, "-n"])
        self.assertEqual(args, self.expected)

    def test_lineup(self) -> None:
        self.expected.lineup = True
        args = dr.parse_make_init([self.folder, "-l"])
        self.assertEqual(args, self.expected)

    def test_outfile(self) -> None:
        self.expected.outfile = "init_file.py"
        args = dr.parse_make_init([self.folder, "-o", "init_file.py"])
        self.assertEqual(args, self.expected)

    def test_wrap(self) -> None:
        self.expected.wrap = 50
        args = dr.parse_make_init([self.folder, "-w", "50"])
        self.assertEqual(args, self.expected)


# %% execute_make_init
@patch("drepo.make_init.make_python_init")
class Test_execute_make_init(unittest.TestCase):
    r"""
    Tests the execute_make_init function with the following cases:
        Nominal
        TBD
    """

    def setUp(self) -> None:
        self.folder = dr.get_root_dir()
        self.init_file = self.folder / "temp_init.py"
        self.args = argparse.Namespace(
            dry_run=False, folder=str(self.folder), lineup=False, outfile=str(self.init_file), wrap=100
        )
        self.patch_args = {"lineup": False, "wrap": 100, "filename": self.init_file}

    def test_nominal(self, mocker: Mock) -> None:
        dr.execute_make_init(self.args)
        mocker.assert_called_once_with(self.folder, **self.patch_args)

    def test_dry_num(self, mocker: Mock) -> None:
        self.args.dry_run = True
        with capture_output() as ctx:
            dr.execute_make_init(self.args)
        output = ctx.get_output()
        ctx.close()
        mocker.assert_not_called()
        self.assertTrue(output.startswith('Would execute "make_python_init('))

    def test_lineup(self, mocker: Mock) -> None:
        self.args.lineup = True
        self.patch_args["lineup"] = True
        dr.execute_make_init(self.args)
        mocker.assert_called_once_with(self.folder, **self.patch_args)

    def test_outfile(self, mocker: Mock) -> None:
        self.args.outfile = self.init_file
        self.patch_args["filename"] = self.args.outfile
        dr.execute_make_init(self.args)
        mocker.assert_called_once_with(self.folder, **self.patch_args)

    def test_wrap(self, mocker: Mock) -> None:
        self.args.wrap = 500
        self.patch_args["wrap"] = 500
        dr.execute_make_init(self.args)
        mocker.assert_called_once_with(self.folder, **self.patch_args)


# %% get_python_definitions
class Test_get_python_definitions(unittest.TestCase):
    r"""
    Tests the get_python_definitions function with the following cases:
        Functions
        Classes
        No arguments
        Lots of arguments
    """

    def test_functions(self) -> None:
        funcs = dr.get_python_definitions("def a():\n    pass\ndef _b():\n    pass\n")
        self.assertEqual(funcs, ["a"])

    def test_classes(self) -> None:
        funcs = dr.get_python_definitions("def a():\n    pass\nclass b():\n    pass\nclass _c():\n    pass\n")
        self.assertEqual(funcs, ["a", "b"])

    def test_no_inputs(self) -> None:
        funcs = dr.get_python_definitions("def _a:\n    pass\ndef b:\n    pass\n")
        self.assertEqual(funcs, ["b"])

    def test_with_inputs(self) -> None:
        funcs = dr.get_python_definitions("def a(a, b=2):\n    pass\nclass bbb(c, d):\n    pass\nclass _c(e):\n    pass\n")
        self.assertEqual(funcs, ["a", "bbb"])

    def test_nothing(self) -> None:
        funcs = dr.get_python_definitions("")
        self.assertEqual(len(funcs), 0)

    def test_constant_values(self) -> None:
        funcs = dr.get_python_definitions("def a():\n    pass\nCONSTANT = 5\n")
        self.assertEqual(funcs, ["a", "CONSTANT"])

    def test_include_private(self) -> None:
        funcs = dr.get_python_definitions(
            "def a():\n    pass\ndef _b():\n    pass\nclass _c():\n    pass\n", include_private=True
        )
        self.assertEqual(funcs, ["a", "_b", "_c"])

    def test_overload(self) -> None:
        funcs = dr.get_python_definitions(
            "@overload\ndef fun(x: int, x: Literal[False]) -> int: ...\n\n@overload\ndef fun(x: int, x: Literal[True]) -> float: ...\n"
            + "\ndef fun(x: int, x: bool = False) -> int | float:\n    pass\n\n"
        )
        self.assertEqual(funcs, ["fun"])

    def test_typed_constants(self) -> None:
        funcs = dr.get_python_definitions("def fun(x: int, y: int):\n    pass\nCONSTANT: int = 5\n")
        self.assertEqual(funcs, ["fun", "CONSTANT"])


# %% make_python_init
class Test_make_python_init(unittest.TestCase):
    r"""
    Tests the make_python_init function with the following cases:
        TBD
    """

    def setUp(self) -> None:
        # fmt: off
        self.folder   = dr.get_root_dir()
        self.text     = "from .enforce import parse_enforce"
        self.text2    = "from .enforce     import parse_enforce"
        self.line_num = 4
        self.folder2  = dr.get_root_dir().joinpath("tests")
        self.filepath = self.folder2 / "temp_file.py"
        self.filename = self.folder2 / "__init__2.py"
        # fmt: on

    def test_nominal_use(self) -> None:
        text = dr.make_python_init(self.folder)
        lines = text.split("\n")
        self.assertEqual(lines[self.line_num][0 : len(self.text2)], self.text2)

    def test_duplicated_funcs(self) -> None:
        with open(self.filepath, "wt") as file:
            file.write("def Test_print_help():\n    pass\n")
        with capture_output() as ctx:
            text = dr.make_python_init(self.folder2)
        output = ctx.get_output()
        ctx.close()
        self.assertRegex(text[0:100], r"from \.temp\_file(\s{2,})import Test_print_help")
        self.assertTrue(output.startswith("Uniqueness Problem"))

    def test_no_lineup(self) -> None:
        text = dr.make_python_init(self.folder, lineup=False)
        lines = text.split("\n")
        self.assertEqual(lines[self.line_num - 1][0 : len(self.text)], self.text)

    def test_big_wrap(self) -> None:
        text = dr.make_python_init(self.folder, wrap=1000)
        lines = text.split("\n")
        self.assertEqual(lines[self.line_num - 2][0 : len(self.text2)], self.text2)

    def test_small_wrap(self) -> None:
        with self.assertRaises(ValueError) as context:
            dr.make_python_init(self.folder, wrap=30)
        self.assertEqual(str(context.exception), 'The specified min_wrap:wrap of "25:30" was too small.')

    def test_really_small_wrap(self) -> None:
        with self.assertRaises(ValueError) as context:
            dr.make_python_init(self.folder, wrap=10)
        self.assertEqual(str(context.exception), 'The specified min_wrap:wrap of "25:10" was too small.')

    def test_saving(self) -> None:
        text = dr.make_python_init(self.folder, filename=self.filename)
        lines = text.split("\n")
        self.assertEqual(lines[self.line_num][0 : len(self.text2)], self.text2)
        self.assertTrue(self.filename.is_file())

    def tearDown(self) -> None:
        self.filepath.unlink(missing_ok=True)
        self.filename.unlink(missing_ok=True)


# %% Unit test execution
if __name__ == "__main__":
    unittest.main(exit=False)
