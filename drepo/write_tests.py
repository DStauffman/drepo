"""Writes template files for unit tests."""

# %% Imports
import argparse
import datetime
from pathlib import Path

from dstauffman import list_python_files, read_text_file, setup_dir, write_text_file
from slog import ReturnCodes

from drepo.make_init import get_python_definitions


# %% Functions - parse_write_tests
def parse_write_tests(input_args: list[str]) -> argparse.Namespace:
    r"""
    Parser for write_tests command.

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
    >>> input_args = ["."]
    >>> args = parse_write_tests(input_args)
    >>> print(args)
    Namespace(folder='.', lineup=True, wrap=100, dry_run=False, outfile='__init__.py')

    """
    parser = argparse.ArgumentParser(
        prog="write_tests", description="Make a python __init__.py" + "file for the given folder."
    )

    parser.add_argument("folder", help="Folder to search for source files")
    parser.add_argument("-a", "--author", nargs="?", default="unknown", help="Author of the test files.")
    parser.add_argument("-e", "--exclude", help="Folders to exclude from processing", action="append")
    parser.add_argument("-r", "--recursive", help="Show what would be copied without doing it", action="store_true")
    parser.add_argument("-s", "--subs", help="Strings to substitute, separated by commas", action="append")
    parser.add_argument("-c", "--classification", help="Add a classification header to each file", action="store_true")
    parser.add_argument(
        "-o", "--output", nargs="?", default="tests", help="Output folder to produce, default is tests"
    )

    args = parser.parse_args(input_args)
    return args


# %% Functions - execute_write_tests
def execute_write_tests(args: argparse.Namespace) -> int:
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
    >>> args = Namespace(folder=".", author="David C. Stauffer", exclude=None, recursive=False, ...
    ...     subs=None, classification=False, output="tests")
    >>> return_code = execute_write_tests(args)  # doctest: +SKIP

    """
    # fmt: off
    folder    = Path(args.folder).resolve()
    output    = Path(args.output).resolve()
    author    = args.author
    exclude   = args.exclude
    recursive = args.recursive
    repo_subs = {s.split(",")[0]: s.split(",")[1] for s in args.subs} if args.subs is not None else None
    add_class = args.classification
    # fmt: on

    output = write_unit_test_templates(
        folder,
        output,
        author=author,
        exclude=exclude,
        recursive=recursive,
        repo_subs=repo_subs,
        add_classification=add_class,
    )
    return ReturnCodes.clean


# %% write_unit_test_templates
def write_unit_test_templates(
    folder: Path,
    output: Path,
    *,
    author: str = "unknown",
    exclude: Path | tuple[Path, ...] | None = None,
    recursive: bool = True,
    repo_subs: dict[str, str] | None = None,
    add_classification: bool = False,
) -> None:
    r"""
    Writes template files for unit tests.  These can then be used with a diff tool to find what is missing.

    Parameters
    ----------
    folder : class pathlib.Path
        Folder location of files to write the unit tests for
    output : class pathlib.Path
        Folder location of the output unit tests
    author : str, optional
        Name of the author
    exclude : pathlib.Path or (pathlib.Path, ...), optional
        Names to exclude
    recursive : bool, optional
        Whether to process recursively
    repo_subs : dict[str, str], optional
        Repository names to replace
    add_classification : bool, optional
        Whether to add a classification to the headers

    Notes
    -----
    #.  Written by David C. Stauffer in July 2020.

    Examples
    --------
    >>> from pathlib import Path
    >>> folder = Path(".").resolve()
    >>> output = folder.joinpath("test_template")
    >>> author = "David C. Stauffer"
    >>> exclude = get_tests_dir()  # can also be tuple of exclusions
    >>> write_unit_test_templates(folder, output, author=author, exclude=exclude)  # doctest: +SKIP

    """
    # hard-coded substitutions for imports
    _subs = {
        "dstauffman": "dcs",
        "dstauffman.aerospace": "space",
        "dstauffman.commands": "commands",
        "dstauffman.estimation": "estm",
        "dstauffman.health": "health",
        "dstauffman.plotting": "plot",
    }
    if repo_subs is not None:
        _subs.update(repo_subs)
    # create the output location
    setup_dir(output)
    # get all the files
    files = list_python_files(folder, recursive=recursive)
    # save the starting point in the name
    num = len(str(folder)) + 1
    # get the name of the repository
    repo_name = files[0].parent.name
    # get date information
    now = datetime.datetime.now()
    month = now.strftime("%B")
    year = now.strftime("%Y")
    for file in files:
        # check for exclusions
        if exclude is not None and exclude in file.parents or output in file.parents:
            continue
        # read the contents of the file
        this_text = read_text_file(file)
        # get a list of definitions from the text file
        funcs = get_python_definitions(this_text, include_private=True)
        # get the name of the test file
        names = str(file)[num:].replace("\\", "/").split("/")
        # get the name of the repo or sub-repo
        sub_repo = ".".join(names[:-1])
        this_repo = repo_name + ("." + sub_repo if sub_repo else "")
        # create the text to write to the file
        text = ['r"""']
        text += [f'Test file for the `{names[-1][:-3]}` module of the "{this_repo}" library.']
        text += ["", "Notes", "-----", f"#.  Written by {author} in {month} {year}."]
        if add_classification:
            text += ["", "Classification", "--------------", "TBD"]
        text += ['"""', "", "# %% Imports", "import unittest", ""]
        import_text = "import " + this_repo
        if this_repo in _subs:
            import_text += " as " + _subs[this_repo]
        text += [import_text, "", ""]
        for func in funcs:
            if func.startswith("_"):
                func = names[-1][:-3] + "." + func
            func_name = sub_repo + "." + func if sub_repo else func
            temp_name = func_name.replace(".", "_")
            text += [f"# %% {func_name}", f"class Test_{temp_name}(unittest.TestCase):", '    r"""']
            text += [f"    Tests the {func_name} function with the following cases:", "        TBD"]
            text += ['    """', "", "    pass  # TODO: write this", "", ""]

        text += ["# %% Unit test execution", 'if __name__ == "__main__":', "    unittest.main(exit=False)", ""]
        new_file = Path.joinpath(output, "test_" + "_".join(names))
        print(f'Writing: "{new_file}".')
        write_text_file(new_file, "\n".join(text))


# %% Script
if __name__ == "__main__":
    import sys
    args = parse_write_tests(sys.argv[1:])
    print(args)
    rc = execute_write_tests(args)
    try:
        rc = execute_write_tests(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(ReturnCodes.bad_command)
    else:
        sys.exit(rc)
