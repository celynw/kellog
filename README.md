# kellog

Easy to use `print()` replacement with coloured output.
It's a wrapper around `logging`, so it can also log to file.

## Installation

```python
$ pip install kellog
```

## Usage

Standard usage example:

```python
from kellog import debug, info, warning, error, critical

debug("Debug message")
>>> [DEBG] Debug message
info(f"Five plus six is {5 + 6}")
>>> [INFO] Five plus six is 11
warning("f-strings are better than", "comma-separated", "arguments")
>>> [WARN] f-strings are better than comma-separated arguments
error("Exception")
>>> [ERR!] Exception
```

## Other options

### setup_logger

`setup_logger(filePath: Path = None, name: str = "kellog", reset: bool = False)`

- `filePath`: If specified, also write the log messages to this file.
- `name`: Set name of `logging` logger.
- `reset`: Delete the contents of `filePath` first.

### log_args

`log_args(args: argparse.Namespace, filePath: Path=Path("args.json"), log: Callable=info)`

- `args`: Output of `argparse.parse_args()`.
- `filePath`: If specified, also write the output in JSON format.
- `log`: Which log function to use, e.g. `info`.
