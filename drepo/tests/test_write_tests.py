r"""
Test file for the `write_tests` module of the "drepo" library.

Notes
-----
#.  Written by David C. Stauffer in March 2025.
"""

# %% Imports
import unittest
from unittest.mock import patch

from slog import LogLevel

import drepo as dr


# %% parse_write_tests
class Test_parse_write_tests(unittest.TestCase):
    r"""
    Tests the parse_write_tests function with the following cases:
        TBD
    """

    pass  # TODO: write this


# %% execute_write_tests
class Test_execute_write_tests(unittest.TestCase):
    r"""
    Tests the execute_write_tests function with the following cases:
        TBD
    """

    pass  # TODO: write this


# %% write_unit_test_templates
class Test_write_unit_test_templates(unittest.TestCase):
    r"""
    Tests the write_unit_test_templates function with the following cases:
        TBD
    """

    def setUp(self) -> None:
        self.folder = dr.get_root_dir()
        self.output = self.folder.joinpath("tests_template")
        self.author = "David C. Stauffer"
        self.exclude = self.folder.joinpath("tests")

    def test_nominal(self) -> None:
        with patch("drepo.write_tests.write_text_file") as mock_writer:
            with patch("drepo.write_tests.setup_dir") as mock_dir:
                with patch("drepo.write_tests.logger") as mock_logger:
                    dr.write_unit_test_templates(self.folder, self.output, author=self.author, exclude=self.exclude)
        self.assertEqual(mock_dir.call_count, 1)
        self.assertGreater(mock_logger.log.call_count, 5)
        self.assertEqual(mock_logger.log.call_args_list[0].args[0], LogLevel.L8)
        self.assertTrue(mock_logger.log.call_args_list[0].args[1].startswith("Writing: "))
        self.assertGreater(mock_writer.call_count, 5)


# %% Unit test execution
if __name__ == "__main__":
    unittest.main(exit=False)
