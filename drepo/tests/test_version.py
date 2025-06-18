r"""
Test file for the `version` module of the "drepo" library.

Notes
-----
#.  Written by David C. Stauffer in March 2025.
"""

# %% Imports
import unittest

import drepo as dr


# %% version_info
class Test_version_info(unittest.TestCase):
    r"""
    Tests the get_root_dir function with the following cases:
        call the function
        get historical data
    """

    def test_version_info(self) -> None:
        version_info = dr.version_info
        self.assertTrue(version_info >= (0, 1, 0))

    def test_data(self) -> None:
        data = dr.version.data
        lines = data.split("\n")[:-1]
        found = False
        for line in lines:
            self.assertIn("drepo", line)
            if "drepo 0.1" in line:
                found = True
        self.assertTrue(found)


# %% Unit test execution
if __name__ == "__main__":
    unittest.main(exit=False)
