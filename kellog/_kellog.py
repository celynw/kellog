#!/usr/bin/env python3
import sys
assert sys.version_info >= (3, 6) # For f-strings
del sys

import logging
import colorama
from pathlib import Path
import argparse
import ujson
from munch import Munch
from sys import stdout
from typing import Any, Callable, Union, Dict, Optional

loggerName = "kellog"
ready = False

# ==================================================================================================
def setup_logger(
	filePath: Optional[Path] = None,
	name: str = "kellog",
	reset: bool = False,
	prefixes: Union[Dict[str, str], Munch] = {
		"debug": " ",
		"info": " ",
		"warning": " ",
		"error": "✖ ",
		"critical": " "
	}):
	"""
	Set up logger to also log to a file.

	Args:
		filePath (Path, optional): Output file. Defaults to None.
		name (str, optional): Reset the logger name to this. Defaults to "kellog".
		reset (bool, optional): Delete the contents of `filePath` first. Defaults to False.
		prefixes (Union[Dict[str, str], Munch], optional): Set the log message prefixes. Does not automatically add separating whitespace.
	"""
	global loggerName, ready
	loggerName = name

	if reset and filePath is not None:
		open(filePath, "w").close() # Delete contents

	logger = logging.getLogger(loggerName)
	logger.propagate = False
	if logger:
		logger.handlers = []
	logger = logging.getLogger(loggerName)
	logger.setLevel(logging.DEBUG)
	ch = logging.StreamHandler(stream=stdout)
	ch.setLevel(logging.DEBUG)
	formatting = "%(levelname)s%(message)s"
	ch.setFormatter(ColouredFormatter(formatting, prefixes))
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
		*args (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(name="kellog")
	logger = logging.getLogger(loggerName)
	logger.debug(force_to_string(*args))


# ==================================================================================================
def info(*args: Any):
	"""
	Output an info message (grey).

	Args:
		*args (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(name="kellog")
	logger = logging.getLogger(loggerName)
	logger.info(force_to_string(*args))


# ==================================================================================================
def warning(*args: Any):
	"""
	Output a warning message (orange).

	Args:
		*args (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(name="kellog")
	logger = logging.getLogger(loggerName)
	logger.warning(force_to_string(*args))


# ==================================================================================================
def error(*args: Any):
	"""
	Output an error message (red).

	Args:
		*args (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(name="kellog")
	logger = logging.getLogger(loggerName)
	logger.error(force_to_string(*args))


# ==================================================================================================
def critical(*args: Any):
	"""
	Output a critical message (bright red).

	Args:
		*args (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(name="kellog")
	logger = logging.getLogger(loggerName)
	logger.critical(force_to_string(*args))


# ==================================================================================================
def log_args(args: argparse.Namespace, filePath: Path = Path("args.json"), log: Callable = info):
	"""
	Print the argparse arguments in a nice list, and optionally saves to file.

	Args:
		args (argparse.Namespace): Input arguments from `parser.parse_args()`
		filePath (Path, optional): Path to save the arguments to. Defaults to Path("args.json").
		log (Callable, optional): Logging/printing function to use. Defaults to info.
	"""
	argsDict = args.__dict__.copy()
	if log:
		import __main__ as main
		log(f"Main script: {main.__file__}")
		log("Arguments: ")
		for k, v in argsDict.items():
			log(f"  {k}: {v}")
	if filePath is not None:
		for k, v in argsDict.items():
			argsDict[k] = str(v) if not isinstance(v, (str, float, int, bool)) else v
		with open(filePath, "w") as file:
			ujson.dump(argsDict, file, indent=2, ensure_ascii=False, escape_forward_slashes=False,
				sort_keys=False)


# ==================================================================================================
class ColouredFormatter(logging.Formatter):
	# ----------------------------------------------------------------------------------------------
	def __init__(self, msg: str, prefixes: Union[Dict[str, str], Munch]):
		super().__init__(msg)
		self.prefixes = Munch(prefixes)

	# ----------------------------------------------------------------------------------------------
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
			record.levelname = self.prefixes.debug
		elif (record.levelname == "INFO"):
			prefix = colorama.Fore.WHITE
			record.levelname = self.prefixes.info
		elif (record.levelname == "WARNING"):
			prefix = colorama.Fore.YELLOW
			record.levelname = self.prefixes.warning
		elif (record.levelname == "ERROR"):
			prefix = colorama.Fore.RED
			record.levelname = self.prefixes.error
		elif (record.levelname == "CRITICAL"):
			prefix = colorama.Fore.RED + colorama.Style.BRIGHT
			record.levelname = self.prefixes.critical
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


# ==================================================================================================
if __name__ == "__main__":
	setup_logger()
	# setup_logger(prefixes={
	# 	"debug": "[D] ",
	# 	"info": "[I] ",
	# 	"warning": "[W] ",
	# 	"error": "[E] ",
	# 	"critical": "[C] "
	# })
	debug("Debug")
	info("Info")
	warning("Warning")
	error("Error")
	critical("Critical")
