r"""
The "drepo" module is a set of tools useful for manipulating python repositories.

Originally created by David C. Stauffer in March 2015 as part of the dstauffman library.
Eventually, this repo code was split off to be more reusable, and not be a runtime dependency.

"""

# %% Imports
# fmt: off
from .api         import print_help, print_version, parse_help, parse_version, execute_help, \
                             execute_version, parse_wrapper, parse_commands, execute_command, main
from .delete_pyc  import parse_delete_pyc, execute_delete_pyc, delete_pyc
from .enforce     import parse_enforce, execute_enforce, find_repo_issues
from .make_init   import parse_make_init, execute_make_init, get_python_definitions, make_python_init
from .version     import version_info
from .write_tests import parse_write_tests, execute_write_tests, write_unit_test_templates
# fmt: on

# %% Constants
__version__ = ".".join(str(x) for x in version_info)
