"""Build an __init__.py file for the given folder."""

# %% Imports
import argparse
from pathlib import Path

from dstauffman import line_wrap, read_text_file, write_text_file
from slog import ReturnCodes


# %% Functions - parse_make_init
def parse_make_init(input_args: list[str]) -> argparse.Namespace:
    r"""
    Parser for make_init command.

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
    >>> input_args = ["-l", "."]
    >>> args = parse_make_init(input_args)
    >>> print(args)  # doctest: +ELLIPSIS
    Namespace(folder='...', lineup=True, wrap=100, dry_run=False, outfile='__init__.py')

    """
    parser = argparse.ArgumentParser(
        prog="make_init", description="Make a python __init__.py" + "file for the given folder."
    )

    parser.add_argument("folder", help="Folder to search for source files")
    parser.add_argument("-l", "--lineup", help="Lines up the imports between files.", action="store_true")
    parser.add_argument("-w", "--wrap", nargs="?", default=100, type=int, help="Number of lines to wrap at.")
    parser.add_argument("-n", "--dry-run", help="Show what would be copied without doing it", action="store_true")
    parser.add_argument(
        "-o", "--outfile", nargs="?", default="__init__.py", help="Output file to produce, default is __init__.py"
    )

    args = parser.parse_args(input_args)
    return args


# %% Functions - execute_make_init
def execute_make_init(args: argparse.Namespace) -> int:
    r"""
    Executes the make_init command.

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
    >>> from argparse import Namespace
    >>> args = Namespace(dry_run=False, folder=".", outfile='__init__.py', lineup=True, wrap=100)
    >>> return_code = execute_make_init(args)  # doctest: +SKIP

    """
    # fmt: off
    folder   = Path(args.folder).resolve()
    lineup   = args.lineup
    wrap     = args.wrap
    filename = Path(args.outfile).resolve()
    dry_run  = args.dry_run
    # fmt: on

    if dry_run:
        cmd = f'make_python_init(r"{folder}", lineup={lineup}, wrap={wrap}, filename=r"{filename}")'
        print(f'Would execute "{cmd}"')
        return ReturnCodes.clean

    output = make_python_init(folder, lineup=lineup, wrap=wrap, filename=filename)
    return_code = ReturnCodes.clean if output else ReturnCodes.bad_command
    return return_code


# %% Functions - get_python_definitions
def get_python_definitions(text: str, *, include_private: bool = False) -> list[str]:  # noqa: C901
    r"""
    Get all public class and def names from the text of the file.

    Parameters
    ----------
    text : str
        The text of the python file

    Returns
    -------
    funcs : array_like, str
        List of functions within the text of the python file

    Examples
    --------
    >>> text = "def a():\n    pass\n"
    >>> funcs = get_python_definitions(text)
    >>> print(funcs)
    ['a']

    """
    cap_letters = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    extended_letters = frozenset(cap_letters & {"_"})
    assert len(cap_letters) == 26
    funcs: list[str] = []
    skip_next = False
    skip_strs = False
    for line in text.split("\n"):
        # check for @overload function definitions and skip them
        if skip_next:
            skip_next = False
            continue
        if skip_strs:
            if line.endswith('"""'):
                skip_strs = False
            continue
        if line == "@overload":
            skip_next = True
            continue
        if line.startswith('r"""') or line.startswith('"""'):
            skip_strs = True
        if line.startswith("class ") and (include_private or not line.startswith("class _")):
            temp = line[len("class ") :].split("(")
            temp = temp[0].split(":")  # for classes without arguments
            funcs.append(temp[0])
        if line.startswith("def ") and (include_private or not line.startswith("def _")):
            temp = line[len("def ") :].split("(")
            temp = temp[0].split(":")  # for functions without arguments
            funcs.append(temp[0])
        if len(line) > 0 and line[0] in cap_letters and "=" in line and " " in line:
            temp2 = line.split(" ")[0].split(":")[0]
            if len(extended_letters - set(temp2)) == 0:
                funcs.append(temp2)
    return funcs


# %% Functions - make_python_init
def make_python_init(folder: Path, *, lineup: bool = True, wrap: int = 100, filename: Path | None = None) -> str:
    r"""
    Make the Python __init__.py file based on the files/definitions found within the specified folder.

    Parameters
    ----------
    folder : str
        Name of folder to process

    Returns
    -------
    output : str
        Resulting text for __init__.py file

    Notes
    -----
    #.  This tool is written without using the dis library, such that the code does not have to be
        valid or importable into Python.  It can thus be used very early on in the development
        cycle. The files are read as text.

    Examples
    --------
    >>> from pathlib import Path
    >>> folder = Path(".").resolve()
    >>> text = make_python_init(folder)
    >>> print(text[0:22])
    from .binary    import

    """
    # exclusions
    exclusions = ["__init__.py"]
    # initialize intermediate results
    results = {}
    # Loop through the contained files/folders
    for this_elem in folder.glob("*"):
        # check if a folder or file
        if not this_elem.is_dir():
            # only process source *.py files
            if this_elem.suffix == ".py":
                # exclude any existing "__init__.py" file
                if any((exc in this_elem.parents for exc in exclusions)):
                    continue
                # read the contents of the file
                this_text = read_text_file(this_elem)
                # get a list of definitions from the text file
                funcs = get_python_definitions(this_text)
                # append these results (if not empty)
                if len(funcs) > 0:
                    results[this_elem.stem] = funcs
    # check for duplicates
    all_funcs = [func for v in results.values() for func in v]
    if len(all_funcs) != len(set(all_funcs)):
        print(f"Uniqueness Problem: {len(all_funcs)} functions, but only {len(set(all_funcs))} unique functions")
    dups = set((x for x in all_funcs if all_funcs.count(x) > 1))
    if dups:
        print("Duplicated functions:")
        print(dups)
    # get information about padding
    max_len = max(len(x) for x in results)
    indent = len("from . import ") + max_len + 4
    # start building text output
    text: list[str] = []
    # loop through results and build text output
    for key in sorted(results):
        pad = " " * (max_len - len(key)) if lineup else ""
        temp = ", ".join(results[key])
        header = "from ." + key + pad + " import "
        min_wrap = len(header)
        this_line = [header + temp]
        wrapped_lines = line_wrap(this_line, wrap=wrap, min_wrap=min_wrap, indent=indent)
        text += wrapped_lines
    # combined the text into a single string with newline characters
    output = "\n".join(text)
    # optionally write the results to a file
    if filename is not None:
        write_text_file(filename, output)
    return output


# %% Script
if __name__ == "__main__":
    import sys
    args = parse_make_init(sys.argv[1:])
    try:
        rc = execute_make_init(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(ReturnCodes.bad_command)
    else:
        sys.exit(rc)
