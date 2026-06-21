# Simple Utils

A simple centralised launcher for my personal set of python utils
to isolate the installations into its separate virtual environment and
not pollute the global python environment.

## Usage

Syntax:

`simply {mode} {command} [arguments...]`

supported modes:

- run: use to run a command line utility
- py: use to run an installed python module or custom simple-utils command

When a file name argument contains spaces:

- Use a `\"` to surround the file name e.g. `simply py pdf-compress \"pdf input file.pdf\"`

simple-utils comes configured with:

| Type           | Name                                             |
| :------------- | ------------------------------------------------ |
| PyPI package   | [fontTools](https://pypi.org/project/fonttools/) |
| PyPI package   | [PyMuPDF](https://pypi.org/project/PyMuPDF/)     |
| Custom command | pdf-compress (see below)                         |

### Custom simple-utils commands

- **pdf-compress _{pdf filename}_**
  - Reads specified pdf file and generates _{pdf filename}-compressed.pdf_, downsampling images to 150 DPI.

## Installation

Note: Testing has been done on Python 3.14 but might/should work with other Python versions.

### Installation steps

1. Make sure you have Python installed and in your path.
1. Download the distribution package (_simple-utils.zip_).
1. Unzip it into your desired folder.
1. Add the folder to your path.
1. Open a cmd window and type

    ```cmd
    simply {mode} {command} [arguments...]
    ```

    The first time it runs, it will create the environment and install the packages before
    executing the command.

## Adding more utilities

To add more PyPI packages to run under simple-utils:

1. Add the required packages into the _py_lib\requirements.txt_ file.
1. Run the command to update the installed packages:

    ```cmd
    simply-env --update
    ```

## License

This project is licensed under the MIT License - see the [License](LICENSE) file.
