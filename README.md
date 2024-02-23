# mem_master
Python wrapper for memory interactions using devmem2 command.

## Available commands

Currently available commands are:
- `decode` -- Perform the conversion from hex (32-bit) to a floating...
- `encode` -- Perform the conversion from a floating point to hex...
- `read` -- Read one value (4B) from given index in memory, convert...
- `read-range` -- Read a range of values (4B) from given indexes in...
- `read-raw` -- Read one value (4B) from given index in memory and...
- `read-raw-range` -- Read a range of values (4B) from given indexes in...
- `write` -- Write the given float to the memory on given index.
- `write-raw` -- Write the given value (4B) to the memory on given index.
- `write-img` -- Write the given value (4B) to the memory on given index.

Whenever unsure what to do, use `-h` or `--help` switch to get more information.

## Installation

This package is **not** contained in any standard Python package manager (PyPI, conda-forge etc.), you have to "install" it on your own.
After downloading the repository, there are multiple ways to do so:

### No installation

Running the code directly, using the path of the repo in your filesystem. Cleanest, but commonly impractical solution.
As Python interpreter automatically looks for a `__main__.py` file when a directory path is passed, result of these commands is identical:

```sh
python $REPO_PATH
python $REPO_PATH/__main__.py
```

### Copy to site-packages

Manually copy this repository into where your Python packages are stored. This is commonly `/lib/python3/site-packages`, sometimes `dist-packages`.
Directory path is visible when printing `sys.path` variable in your Python interpreter.
The name of the directory (`mem_master` by default) determines the package name.
Then, run the script using:

```sh
# -m... module
python -m mem_master
```

### Path symlink

First of all, make sure that the `__main__.py` file is executable:

```sh
chmod a+x __main__.py
```

Then, check that the interpreter path in she-bang is valid by running:

```sh
/usr/bin/env python
```

Now, you can create a symlink anywhere in your path (`echo $PATH`), ideally under your user directory (`~/.local/bin`)
that is pointing to `__main__.py`.

```sh
# edit the path directory if needed
ln -s __main__.py ~/.local/bin/mem_master
```