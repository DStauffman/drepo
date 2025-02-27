# drepo

This repository is a collection of tools for maintaining consistency across other python repositories.  It was originally part of the dstauffman repo, but was split out to make maintaining that one easier and more streamlined.

## Commands

The following commands are available in this repository:

* delete_pyc
* enforce
* help
* make_init
* version
* write_tests

### delete_pyc

Delete all the Python *.pyc files in the given folder.

```
usage: delete_pyc [-h] [-r] [-p] folder

positional arguments:
  folder           Folder to search for source files

options:
  -h, --help       show this help message and exit
  -r, --recursive  Delete files recursively.
  -p, --print      Display information about any deleted files.
```

### enforce

Enforce consistency in the repo for things like tabs, trailing whitespace, line endings and file execute permissions.

```
usage: enforce [-h] [-e EXTENSIONS] [-l] [-i] [-t] [-s SKIP] [-w | -u] [-x] folder

positional arguments:
  folder                Folder to search for source files

options:
  -h, --help            show this help message and exit
  -e, --extensions EXTENSIONS
                        Extensions to search through.
  -l, --list-all        List all files, even ones without problems.
  -i, --ignore-tabs     Ignore tabs within the source code.
  -t, --trailing        Show files with trailing whitespace
  -s, --skip SKIP       Exclusions to not search.
  -w, --windows         Use Windows (CRLF) line-endings
  -u, --unix            Use Unix (LF) line-endings
  -x, --execute         List files with execute permissions.
```

### help

Displays the contents of this file.

```
usage: help [-h]

options:
  -h, --help  show this help message and exit
```

### make_init

Make a python __init__.pyfile for the given folder.

```
usage: make_init [-h] [-l] [-w [WRAP]] [-n] [-o [OUTFILE]] folder

positional arguments:
  folder                Folder to search for source files

options:
  -h, --help            show this help message and exit
  -l, --lineup          Lines up the imports between files.
  -w, --wrap [WRAP]     Number of lines to wrap at.
  -n, --dry-run         Show what would be copied without doing it
  -o, --outfile [OUTFILE]
                        Output file to produce, default is __init__.py
```

### version

Display version information for the drepo itself.

```
usage: version [-h]

options:
  -h, --help  show this help message and exit
```

### write_tests

Make a python __init__.pyfile for the given folder.

```
usage: write_tests [-h] [-a [AUTHOR]] [-e EXCLUDE] [-r] [-s SUBS] [-c] [-o [OUTPUT]] folder

positional arguments:
  folder                Folder to search for source files

options:
  -h, --help            show this help message and exit
  -a, --author [AUTHOR]
                        Author of the test files.
  -e, --exclude EXCLUDE
                        Folders to exclude from processing
  -r, --recursive       Show what would be copied without doing it
  -s, --subs SUBS       Strings to substitute, separated by commas
  -c, --classification  Add a classification header to each file
  -o, --output [OUTPUT]
                        Output folder to produce, default is tests
```
