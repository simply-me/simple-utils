# Simple Utils

A simple centralised launcher for my personal set of python utils
to isolate the installations into its separate virtual environment and
not pollute the global python environment.

## List of Utilities Supported

The list of supported python packages can be seen and amended through
the _py_lib\requirements.txt_ file.

When changes are made to this file, run _setup_env.cmd_ to refresh the
Python virtual environment.

Additional commands supported through custom Python scripts:

1. **pdf-compress _--input {input file}_**

    Takes a pdf file and generates {filename}-compressed.pdf,
    downsampling images to 150 DPI.

### Prerequisites

Make sure you have Python installed. Testing is done on Python 3.14.

### Installation

1. Download the distribution package.
1. Unzip it into your desired folder.
1. Add the folder to your path.

## Usage

Syntax:

`simply {mode} {command} [arguments...]`

supported modes:

- run: use to run an executable
- py: use to run a python module including the custom Python scripts

>Note: Each custom python script uses its own predefined command.

### Examples

``` cmd
  simply run git status
  simply run pyftsubset --input font.ttf --output font-subset.ttf --unicodes=U+0020-007E
  simply py pymupdf --input document.pdf --output compressed.pdf
  simply py pdf-compress --input document.pdf
```

## License

This project is licensed under the MIT License - see the [License](LICENSE) file.
