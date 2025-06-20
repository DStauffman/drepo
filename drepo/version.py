r"""
Functions related to version history.

Notes
-----
#.  Written by David C. Stauffer in February 2025.
"""

# %% Constants
version_info = (0, 1, 0)

# Below is data about the minor release history for potential use in deprecating older support.
# For inspiration, see: https://numpy.org/neps/nep-0029-deprecation_policy.html

data = """Feb 26, 2025: drepo 0.0
Jun 18, 2025: drepo 0.1
Jun 20, 2025: drepo 0.2
"""

# Historical notes:
# v0.1 Moved most of the capability out of the dstauffman repo.
# v0.2 Removed dependency on dstauffman and only uses core python.
