# kellog

Extremely easy to use python `print()` replacement with coloured output and status icons.

## Installation

```bash
$ pip install kellog
```

Requires python version 3.7 or above.

## Usage

It is very very simple to start using this right away:

```python
from kellog import debug, info, warning, error, critical

debug("Debug message")
info(f"Five plus six is {5 + 6}")
warning("f-strings are better than", "comma-separated", "arguments")
error("Exception")
critical("DEFCON 1")
```

![image](https://github.com/celynw/kellog/assets/3299161/3ddcfc4d-e8dd-44c3-ad8e-795e03b141cf)

`kellog` wraps the built-in `logging` library, so it can be controlled in the same ways.
For instance, logging to file and configuring the output format.

```none
class Kellog(
	path: Path | None,
	name: str,
	prefixes: dict[str, str] | None,
	append: bool,
)

Parameters
----------
path, optional
  Output file, by default None
name, optional
  Reset the logger name to this, by default "kellog"
prefixes, optional
  Set the log message prefixes (does not automatically add separating whitespace), by default None.
  The dictionary keys to set are "debug", "info", "warning", "error", "critical".
  Setting to None will use the default unicode prefixes, from codicons:      .
append, optional
  If False, delete the contents of `path` first, by default True
```

## Tests

Install this package with:

```bash
pip install -e .[dev]
```

Then run the tests:

```bash
make tests
```
