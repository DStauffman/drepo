"""Enforces a number of standards for the given repository."""

# %% Imports
import argparse
import os
from pathlib import Path

from slog import ReturnCodes


# %% Functions - parse_enforce
def parse_enforce(input_args: list[str]) -> argparse.Namespace:
    r"""
    Parser for enforce command.

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
    >>> from drepo import parse_enforce
    >>> input_args = ["."]
    >>> args = parse_enforce(input_args)
    >>> print(args)
    Namespace(folder='.', extensions=None, list_all=False, ignore_tabs=False, trailing=False, skip=None, windows=False, unix=False, execute=False)

    """
    parser = argparse.ArgumentParser(
        prog="enforce",
        description="Enforce consistency in the repo "
        + "for things like tabs, trailing whitespace, line endings and file execute permissions.",
    )

    parser.add_argument("folder", help="Folder to search for source files")
    parser.add_argument("-e", "--extensions", help="Extensions to search through.", action="append")
    parser.add_argument("-l", "--list-all", help="List all files, even ones without problems.", action="store_true")
    parser.add_argument("-i", "--ignore-tabs", help="Ignore tabs within the source code.", action="store_true")
    parser.add_argument("-t", "--trailing", help="Show files with trailing whitespace", action="store_true")
    parser.add_argument("-s", "--skip", help="Exclusions to not search.", action="append")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-w", "--windows", help="Use Windows (CRLF) line-endings", action="store_true")
    group.add_argument("-u", "--unix", help="Use Unix (LF) line-endings", action="store_true")

    parser.add_argument("-x", "--execute", help="List files with execute permissions.", action="store_true")

    args = parser.parse_args(input_args)
    return args


# %% Functions - execute_enforce
def execute_enforce(args: argparse.Namespace) -> int:
    r"""
    Executes the enforce command.

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
    >>> from drepo import execute_enforce
    >>> from argparse import Namespace
    >>> args = Namespace(extensions=None, folder=".", ignore_tabs=False, list_all=False, \
    ...     skip=None, trailing=False, unix=False, windows=False, execute=False)
    >>> return_code = execute_enforce(args)  # doctest: +SKIP

    """
    # defaults
    def_extensions = {".m", ".py"}
    # get settings from input arguments
    folder = Path(args.folder).resolve()
    list_all = args.list_all
    check_tabs = not args.ignore_tabs
    trailing = args.trailing
    exclusions = args.skip
    show_execute = args.execute
    check_eol: str | None
    if args.windows:
        check_eol = "\r\n"
    elif args.unix:
        check_eol = "\n"
    else:
        check_eol = None
    extensions: set[str] | frozenset[str] | None
    if args.extensions is None:
        extensions = frozenset(def_extensions)
    elif len(args.extensions) == 1 and args.extensions[0] == "*":
        extensions = None
    else:
        extensions = args.extensions

    # call the function to do the checks
    is_clean = find_repo_issues(
        folder=folder,
        extensions=extensions,
        list_all=list_all,
        check_tabs=check_tabs,
        trailing=trailing,
        exclusions=exclusions,
        check_eol=check_eol,
        show_execute=show_execute,
    )
    # return a status based on whether anything was found
    return_code = ReturnCodes.clean if is_clean else ReturnCodes.test_failures
    return return_code


# %% find_repo_issues
def find_repo_issues(  # noqa: C901
    folder: Path,
    extensions: frozenset[str] | set[str] | tuple[str, ...] | str | None = frozenset((".m", ".py")),
    *,
    list_all: bool = False,
    check_tabs: bool = True,
    trailing: bool = False,
    exclusions: tuple[Path, ...] | Path | None = None,
    check_eol: str | None = None,
    show_execute: bool = False,
) -> bool:
    r"""
    Find all the tabs in source code that should be spaces instead.

    Parameters
    ----------
    folder : class pathlib.Path
        Folder path to search
    extensions : tuple of str
        File extensions to consider, default is (".m", ".py")
    list_all : bool, optional, default is False
        Whether to list all the files, or only those with problems in them
    check_tabs : bool, optional, default is True
        Whether to include tabs as an issue to check
    trailing : bool, optional, default is False
        Whether to consider trailing whitespace a problem, too
    exclusions : tuple of pathlib.Path
        Folders to ignore, default is empty
    check_eol : str
        If not None, then the line endings to check, such as "\r\n"
    show_execute : bool
        Whether to show files that have execute permissions, default is False

    Returns
    -------
    is_clean : bool
        Whether the folder is clean, meaning nothing was found to report.

    Examples
    --------
    >>> from drepo import find_repo_issues, get_root_dir
    >>> folder = get_root_dir()
    >>> is_clean = find_repo_issues(folder)
    >>> print(is_clean)
    True

    """

    def _is_excluded(path: Path, exclusions: tuple[Path, ...] | None) -> bool:
        if exclusions is None:
            return False
        for this_exclusion in exclusions:
            if this_exclusion == path or this_exclusion in path.parents:
                return True
        return False

    # initialize output
    is_clean = True

    if isinstance(extensions, str):
        extensions = {extensions,}  # fmt: skip
    if isinstance(exclusions, Path):
        exclusions = (exclusions,)

    for this_file in folder.rglob("*"):
        if not this_file.is_file():
            continue
        if extensions is None or this_file.suffix in extensions:
            if _is_excluded(folder, exclusions):
                continue
            already_listed = False
            if list_all:
                print(f'Evaluating: "{this_file}"')
                already_listed = True
            if show_execute and os.access(this_file, os.X_OK):
                print(f'File: "{this_file}" has execute privileges.')
                is_clean = False
            with open(this_file, encoding="utf8", newline="") as file:
                bad_lines = False
                try:
                    lines = file.readlines()
                except UnicodeDecodeError:  # pragma: no cover
                    print(f'File: "{this_file}" was not a valid utf-8 file.')
                    is_clean = False
                for c, line in enumerate(lines):
                    sline = line.rstrip("\n").rstrip("\r").rstrip("\n")  # for all possible orderings
                    if check_tabs and line.count("\t") > 0:
                        if not already_listed:
                            print(f'Evaluating: "{this_file}"')
                            already_listed = True
                            is_clean = False
                        print(f"    Line {c + 1:03}: " + repr(line))
                    elif trailing and len(sline) >= 1 and sline[-1] == " ":
                        if not already_listed:
                            print(f'Evaluating: "{this_file}"')
                            already_listed = True
                            is_clean = False
                        print(f"    Line {c + 1:03}: " + repr(line))
                    if check_eol is not None and c != len(lines) - 1 and not line.endswith(check_eol) and not bad_lines:
                        line_ending = line[-(len(line) - len(sline)) :]
                        print(f'File: "{this_file}" has bad line endings of "{repr(line_ending)[1:-1]}".')
                        bad_lines = True
                        is_clean = False
    # end checks, return overall result
    return is_clean


# %% Script
if __name__ == "__main__":
    import sys

    args = parse_enforce(sys.argv[1:])
    try:
        rc = execute_enforce(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(ReturnCodes.bad_command)
    else:
        sys.exit(rc)
