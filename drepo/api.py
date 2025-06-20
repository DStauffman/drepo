"""High level API functions."""

# %% Imports
import argparse
from functools import lru_cache
from pathlib import Path
import sys

from slog import ReturnCodes

from drepo.delete_pyc import execute_delete_pyc as execute_delete_pyc, parse_delete_pyc as parse_delete_pyc
from drepo.enforce import execute_enforce as execute_enforce, parse_enforce as parse_enforce
from drepo.make_init import execute_make_init as execute_make_init, parse_make_init as parse_make_init
from drepo.version import version_info
from drepo.write_tests import execute_write_tests as execute_write_tests, parse_write_tests as parse_write_tests

# assert that these functions exist to be potentially used later
assert parse_delete_pyc  # type: ignore[truthy-function]
assert execute_delete_pyc  # type: ignore[truthy-function]
assert parse_enforce  # type: ignore[truthy-function]
assert execute_enforce  # type: ignore[truthy-function]
assert parse_make_init  # type: ignore[truthy-function]
assert execute_make_init  # type: ignore[truthy-function]
assert parse_write_tests  # type: ignore[truthy-function]
assert execute_write_tests  # type: ignore[truthy-function]


# %% Constants
_VALID_COMMANDS = frozenset({"delete_pyc", "enforce", "help", "make_init", "version", "write_tests"})


# %% Functions - _print_bad_command
def _print_bad_command(command: str) -> None:
    r"""Prints to the command line when a command name is not understood."""
    print(f'Command "{command}" is not understood.')


# %% Functions - get_root_dir
@lru_cache
def get_root_dir() -> Path:
    r"""
    Return the folder that contains this source file and thus the root folder for the whole code.

    Returns
    -------
    class pathlib.Path
        Location of the folder that contains all the source files for the code.

    Notes
    -----
    #.  Written by David C. Stauffer in March 2015.

    Examples
    --------
    >>> from drepo import get_root_dir
    >>> print("p = ", repr(get_root_dir()))  # doctest: +ELLIPSIS
    p = .../drepo')

    """
    # this folder is the root directory based on the location of this file (paths.py)
    return Path(__file__).resolve().parent


# %% Functions - print_help
def print_help(help_file: Path | None = None) -> int:
    r"""
    Prints the contents of the README.rst file.

    Returns
    -------
    return_code : int
        Return code for whether the help file was successfully loaded

    Examples
    --------
    >>> from drepo import print_help
    >>> print_help()  # doctest: +SKIP

    """
    if help_file is None:
        help_file = get_root_dir().parent / "README.md"
    if not help_file.is_file():
        print(f'Warning: help file at "{help_file}" was not found.')
        return ReturnCodes.bad_help_file
    with open(help_file, encoding="utf-8") as file:
        text = file.read()
    print(text)
    return ReturnCodes.clean


# %% Functions - print_version
def print_version() -> int:
    r"""Prints the version of the library.

    Returns
    -------
    return_code : int
        Return code for whether the version was successfully read

    Examples
    --------
    >>> from drepo import print_version
    >>> print_version()  # doctest: +SKIP

    """
    try:
        version = ".".join(str(x) for x in version_info)
        return_code = ReturnCodes.clean
    except Exception:
        version = "unknown"
        return_code = ReturnCodes.bad_version
    print(version)
    return return_code


# %% Functions - parse_help
def parse_help(input_args: list[str]) -> argparse.Namespace:
    r"""
    Parser for help command.

    Parameters
    ----------
    input_args : list of str
        Input arguments as passed to sys.argv for this command

    Returns
    -------
    args : class Namespace
        Arguments as parsed by argparse.parse_args

    Examples
    --------
    >>> from drepo import parse_help
    >>> input_args = []
    >>> args = parse_help(input_args)
    >>> print(args)
    Namespace()

    """
    parser = argparse.ArgumentParser(prog="help")

    args = parser.parse_args(input_args)
    return args


# %% Functions - parse_version
def parse_version(input_args: list[str]) -> argparse.Namespace:
    r"""
    Parser for version command.

    Parameters
    ----------
    input_args : list of str
        Input arguments as passed to sys.argv for this command

    Returns
    -------
    args : class Namespace
        Arguments as parsed by argparse.parse_args

    Examples
    --------
    >>> from drepo import parse_version
    >>> input_args = []
    >>> args = parse_version(input_args)
    >>> print(args)
    Namespace()

    """
    parser = argparse.ArgumentParser(prog="version")

    args = parser.parse_args(input_args)
    return args


# %% Functions - execute_help
def execute_help(args: argparse.Namespace) -> int:  # pylint: disable=unused-argument
    r"""
    Executes the help command.

    Parameters
    ----------
    args : class Namespace
        Arguments as parsed by argparse.parse_args, in this case they can be empty or ommitted

    Returns
    -------
    return_code : int
        Return code for whether the command completed successfully

    Examples
    --------
    >>> from drepo import execute_help
    >>> args = []
    >>> execute_help(args) # doctest: +SKIP

    """
    return_code = print_help()
    return return_code


# %% Functions - execute_version
def execute_version(args: argparse.Namespace) -> int:  # pylint: disable=unused-argument
    r"""
    Executes the version command.

    Parameters
    ----------
    args : class Namespace
        Arguments as parsed by argparse.parse_args, in this case they can be empty or ommitted

    Returns
    -------
    return_code : int
        Return code for whether the command completed successfully

    Examples
    --------
    >>> from drepo import execute_version
    >>> args = []
    >>> execute_version(args) # doctest: +SKIP

    """
    return_code = print_version()
    return return_code


# %% Functions - parse_wrapper
def parse_wrapper(args: list[str]) -> tuple[str, argparse.Namespace]:
    r"""Wrapper function to parse out the command name from the rest of the arguments."""
    # check for no command option
    if len(args) >= 1:
        command = args[0]
    else:
        command = "help"
    # check for alternative forms of help with the base drepo command
    if command in {"--help", "-h"}:
        command = "help"
    elif command in {"--version", "-v"}:
        command = "version"
    # pass the command and remaining arguments to the command parser
    parsed_args = parse_commands(command, args[1:])
    return (command, parsed_args)


# %% Functions - parse_commands
def parse_commands(command: str, args: list[str]) -> argparse.Namespace:
    r"""
    Splits the parsing based on the name of the command.

    Parameters
    ----------
    command : str
        Name of command to parse
    args : list
        Command line arguments

    Returns
    -------
    parsed_args : class argparse.Namespace
        Parsed arguments ready to be passed to command to execute

    Examples
    --------
    >>> from drepo import parse_commands
    >>> command = "help"
    >>> args = []
    >>> parsed_args = parse_commands(command, args)
    >>> print(parsed_args)
    Namespace()

    """
    # check for valid commands
    if command in _VALID_COMMANDS:
        # If valid, then parse the arguments with the appropiate method, so help calls parse_help etc.
        func = globals()["parse_" + command]
        parsed_args: argparse.Namespace = func(args)
    else:
        raise ValueError(f'Unexpected command "{command}".')
    return parsed_args


# %% Functions - execute_command
def execute_command(command: str, args: argparse.Namespace) -> int:
    r"""Executes the given command."""
    # check for valid commands
    if command in _VALID_COMMANDS:
        # If valid, then call the appropriate method, so help calls execute_help etc.
        func = globals()["execute_" + command]
        rc: int | None = func(args)
    else:
        _print_bad_command(command)
        rc = ReturnCodes.bad_command
    if rc is None:
        rc = ReturnCodes.clean
    return rc


# %% Functions - main
def main() -> int:
    r"""Main function called when executed using the command line api."""
    try:
        (command, args) = parse_wrapper(sys.argv[1:])
    except ValueError:
        _print_bad_command(" ".join(sys.argv[1:]))
        return ReturnCodes.bad_command
    rc = execute_command(command, args)
    return sys.exit(rc)


# %% Script
if __name__ == "__main__":
    args = parse_help(sys.argv[1:])
    print(args)
    try:
        rc = execute_help(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(ReturnCodes.bad_command)
    else:
        sys.exit(rc)
