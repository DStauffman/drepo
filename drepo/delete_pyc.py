"""Delete all the *.pyc files (Python Byte Code) in the specified directory."""

# %% Imports
import argparse
from pathlib import Path

from slog import ReturnCodes


# %% Functions - parse_delete_pyc
def parse_delete_pyc(input_args: list[str]) -> argparse.Namespace:
    r"""
    Parser for delete_pyc command.

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
    >>> from drepo import parse_delete_pyc
    >>> input_args = ["-r","-p", "."]
    >>> args = parse_delete_pyc(input_args)
    >>> print(args)
    Namespace(folder='.', recursive=True, print=True)

    """
    parser = argparse.ArgumentParser(prog="delete_pyc", description="Delete all the Python *.pyc files in the given folder.")

    parser.add_argument("folder", help="Folder to search for source files")
    parser.add_argument("-r", "--recursive", help="Delete files recursively.", action="store_true")
    parser.add_argument("-p", "--print", help="Display information about any deleted files.", action="store_true")

    args = parser.parse_args(input_args)
    return args


# %% Functions - execute_delete_pyc
def execute_delete_pyc(args: argparse.Namespace) -> int:
    r"""
    Executes the delete_pyc command.

    Parameters
    ----------
    args : class Namespace
        Arguments as parsed by argparse.parse_args, in this case they can be empty or omitted

    Returns
    -------
    return_code : int
        Return code for whether the command completed successfully

    Examples
    --------
    >>> from drepo import execute_delete_pyc
    >>> from argparse import Namespace
    >>> args = Namespace(folder=".", recursive=False, print=True)
    >>> return_code = execute_delete_pyc(args)  # doctest: +SKIP

    """
    # alias inputs
    folder = Path(args.folder).resolve()
    recursive = args.recursive
    print_progress = args.print

    # execute the deletion
    delete_pyc(folder, recursive, print_progress=print_progress)
    return ReturnCodes.clean


# %% Functions - delete_pyc
def delete_pyc(folder: Path, recursive: bool = True, *, print_progress: bool = True) -> None:
    r"""
    Delete all the *.pyc files (Python Byte Code) in the specified directory.

    Parameters
    ----------
    folder : class pathlib.Path
        Name of folder to delete the files from
    recursive : bool, optional
        Whether to delete files recursively
    print_progress: bool, optional
        Whether to display information about any deleted files

    Examples
    --------
    >>> from drepo import delete_pyc, get_root_dir
    >>> folder = get_root_dir()
    >>> delete_pyc(folder, print_progress=False)  # doctest: +SKIP

    """

    def _remove_pyc(file: Path) -> None:
        r"""Do the actual file removal."""
        # check for allowable extensions
        # fmt: off
        assert file.suffix in {".pyc",}
        assert file.is_file()
        # fmt: on
        # remove this file
        if print_progress:
            print(f'Removing "{file}"')
        file.unlink(missing_ok=True)

    if recursive:
        # walk through folder
        for file in folder.rglob("*.pyc"):
            # remove relevant files
            _remove_pyc(file)
    else:
        # list files in folder
        for file in folder.glob("*.pyc"):
            # remove relevant files
            _remove_pyc(file)


# %% Script
if __name__ == "__main__":
    import sys

    args = parse_delete_pyc(sys.argv[1:])
    try:
        rc = execute_delete_pyc(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(ReturnCodes.bad_command)
    else:
        sys.exit(rc)
