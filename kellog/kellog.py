from typing import Any, Callable
import logging
import colorama
from pathlib import Path
import inspect
import subprocess
import argparse
import ujson
from sys import stdout

name = "kellog"
ready = False

# ==================================================================================================
def setup_logger(filePath: Path, newName: str="kellog", reset: bool=False):
	"""
	Set up logger to also log to a file.

	Args:
		filePath (Path): Output file
		newName (str, optional): Reset the logger name to this. Defaults to "kellog".
		reset (bool, optional): Delete the contents of `filePath` first. Defaults to False.
	"""
	global name, ready
	name = newName

	if reset:
		open(filePath, "w").close() # Delete contents

	logger = logging.getLogger(name)
	if logger:
		logger.handlers = []
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	ch = logging.StreamHandler(stream=stdout)
	ch.setLevel(logging.DEBUG)
	formatting = "%(levelname)s %(message)s"
	ch.setFormatter(ColouredFormatter(formatting))
	logger.addHandler(ch)

	if filePath:
		fh = logging.FileHandler(filePath)
		fh.setLevel(logging.DEBUG)
		fh.setFormatter(logging.Formatter(formatting))
		logger.addHandler(fh)

	ready = True


# ==================================================================================================
def debug(*args: Any):
	"""
	Output a debug message (green).

	Args:
		anyting (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(Path("/tmp/log"), "kellog", True)
	logger = logging.getLogger(name)
	logger.debug(force_to_string(*args))


# ==================================================================================================
def info(*args: str):
	"""
	Output an info message (grey).

	Args:
		anyting (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(Path("/tmp/log"), "kellog", True)
	logger = logging.getLogger(name)
	logger.info(force_to_string(*args))


# ==================================================================================================
def warning(*args: str):
	"""
	Output a warning message (orange).

	Args:
		anyting (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(Path("/tmp/log"), "kellog", True)
	logger = logging.getLogger(name)
	logger.warning(force_to_string(*args))


# ==================================================================================================
def error(*args: str):
	"""
	Output an error message (red).

	Args:
		anyting (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(Path("/tmp/log"), "kellog", True)
	logger = logging.getLogger(name)
	logger.error(force_to_string(*args))


# ==================================================================================================
def critical(*args: Any):
	"""
	Output a critical message (bright red).

	Args:
		anyting (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(Path("/tmp/log"), "kellog", True)
	logger = logging.getLogger(name)
	logger.critical(force_to_string(*args))


# ==================================================================================================
def git_rev(log: Callable=info):
	"""
	Print out the git revision (short hash).

	Args:
		log (Callable, optional): Logging/printing function to use. Defaults to info.
	"""
	cwd = Path(inspect.stack()[1][1]).parent
	try:
		output = str(subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.STDOUT, universal_newlines=True, cwd=cwd)).strip()
	except subprocess.CalledProcessError as exc:
		error(exc.output)
	else:
		log("Git revision:", output)


# ==================================================================================================
def write_args(args: argparse.Namespace, filePath: Path=Path("args.json"), log: Callable=info):
	"""
	Print the argparse arguments in a nice list, and optionally saves to file.

	Args:
		args (argparse.Namespace): Input arguments from `parser.parse_args()`
		filePath (Path, optional): Path to save the arguments to. Defaults to Path("args.json").
		log (Callable, optional): Logging/printing function to use. Defaults to info.
	"""
	if log:
		import __main__ as main
		log(f"Main script: {main.__file__}")
		log("Arguments: ")
		for k, v in args.__dict__.items():
			log(f"  {k}: {v}")
	if filePath is not None:
		for k, v in args.__dict__.items():
			args.__dict__[k] = str(v) if type(v) not in [str, float, int, bool] else v
		with open(str(filePath), "w") as file:
			ujson.dump(args.__dict__, file, indent=2, ensure_ascii=False, escape_forward_slashes=False, sort_keys=False)


# ==================================================================================================
class ColouredFormatter(logging.Formatter):
	def __init__(self, msg: str):
		super().__init__(msg)

	def format(self, record: logging.LogRecord) -> str:
		"""
		Prefixes with the logging level and assigns a colour.

		Args:
			record (logging.LogRecord): Log object

		Returns:
			str: Formatted output
		"""
		if (record.levelname == "DEBUG"):
			prefix = colorama.Fore.GREEN
			record.levelname = "[DEBG]"
		elif (record.levelname == "INFO"):
			prefix = colorama.Fore.WHITE
			record.levelname = "[INFO]"
		elif (record.levelname == "WARNING"):
			prefix = colorama.Fore.YELLOW
			record.levelname = "[WARN]"
		elif (record.levelname == "ERROR"):
			prefix = colorama.Fore.RED
			record.levelname = "[ERR!]"
		elif (record.levelname == "CRITICAL"):
			prefix = colorama.Fore.RED + colorama.Style.BRIGHT
			record.levelname = "[CRIT]"
		else:
			prefix = ""
		suffix = colorama.Style.RESET_ALL

		return prefix + super().format(record) + suffix


# ==================================================================================================
def force_to_string(*args: Any) -> str:
	"""
	Force the input to be a string.

	Returns:
		str: Output
	"""
	msg = ""
	if (len(args) > 0):
		msg = str(args[0])
	if (len(args) > 1):
		for arg in args[1:]:
			msg += f" {str(arg)}"

	return msg