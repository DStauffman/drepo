r"""
Test file for the `api` module of the "drepo" library.

Notes
-----
#.  Written by David C. Stauffer in June 2025.

"""

# %% Imports
import unittest

from slog import capture_output

import drepo


# %% print_help
class Test_print_help(unittest.TestCase):
    r"""
    Tests the print_help function with the following cases:
        Nominal
        Specified file
    """

    def test_nominal(self) -> None:
        with capture_output() as ctx:
            drepo.print_help()
        lines = ctx.get_output().split("\n")
        ctx.close()
        self.assertEqual(lines[0], "# drepo")

    def test_specify_file(self) -> None:
        help_file = drepo.get_root_dir().joinpath("tests", "test_api.py")
        with capture_output() as ctx:
            drepo.print_help(help_file)
        lines = ctx.get_output().split("\n")
        ctx.close()
        self.assertEqual(lines[0], 'r"""')
        self.assertEqual(lines[1], 'Test file for the `api` module of the "drepo" library.')


# %% Unit test execution
if __name__ == "__main__":
    unittest.main(exit=False)
