#!/usr/bin/env python3
import sys
assert sys.version_info >= (3, 6) # For f-strings
del sys

from typing import Any, Callable
import logging
import colorama
from pathlib import Path
import inspect
import subprocess
import argparse
import ujson
from sys import stdout
import inspect
import re

loggerName = "kellog"
ready = False
useEq_ = True
nameIter = 0

# ==================================================================================================
def setup_logger(filePath: Path = None, name: str = "kellog", reset: bool = False, useEq: bool = True):
	"""
	Set up logger to also log to a file.

	Args:
		filePath (Path, optional): Output file. Defaults to None.
		name (str, optional): Reset the logger name to this. Defaults to "kellog".
		reset (bool, optional): Delete the contents of `filePath` first. Defaults to False.
		useEq (bool, optional: Prefix the result with the variable name, if possible. Defaults to True.
	"""
	global loggerName, ready, useEq_
	loggerName = name
	import __main__ as main
	useEq_ = useEq and hasattr(main, "__file__") # Disable for interactive session

	if reset:
		open(filePath, "w").close() # Delete contents

	logger = logging.getLogger(loggerName)
	logger.propagate = False
	if logger:
		logger.handlers = []
	logger = logging.getLogger(loggerName)
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
def retrieve_name(var):
	# Get code which called kellog function
	fName = inspect.currentframe().f_back.f_code.co_name
	call = inspect.getframeinfo(inspect.currentframe().f_back.f_back).code_context[0].strip()

	varNames = re.findall(rf"{fName}[^(]*\(([^)]*)\)", call)
	if varNames:
		global nameIter
		varName = varNames[nameIter]
		if len(varNames) > 1 and nameIter < len(varNames) - 1:
			nameIter += 1
		else:
			nameIter = 0
		if not varName.startswith(('"', "'", 'f"', "f'")):
			return varName

	return None


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

	extra = None
	if useEq_:
		varName = retrieve_name(args)
		extra = {"varName": varName} if varName else extra
	logger.debug(force_to_string(*args), extra=extra)


# ==================================================================================================
def info(*args: str):
	"""
	Output an info message (grey).

	Args:
		*args (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(name="kellog")
	logger = logging.getLogger(loggerName)

	extra = None
	if useEq_:
		varName = retrieve_name(args)
		extra = {"varName": varName} if varName else extra
	logger.info(force_to_string(*args), extra=extra)


# ==================================================================================================
def warning(*args: str):
	"""
	Output a warning message (orange).

	Args:
		*args (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(name="kellog")
	logger = logging.getLogger(loggerName)

	extra = None
	if useEq_:
		varName = retrieve_name(args)
		extra = {"varName": varName} if varName else extra
	logger.warning(force_to_string(*args), extra=extra)


# ==================================================================================================
def error(*args: str):
	"""
	Output an error message (red).

	Args:
		*args (Any): Will be converted to a string using its __str__.
	"""
	if not ready:
		setup_logger(name="kellog")
	logger = logging.getLogger(loggerName)

	extra = None
	if useEq_:
		varName = retrieve_name(args)
		extra = {"varName": varName} if varName else extra
	logger.error(force_to_string(*args), extra=extra)


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

	extra = None
	if useEq_:
		varName = retrieve_name(args)
		extra = {"varName": varName} if varName else extra
	logger.critical(force_to_string(*args), extra=extra)


# ==================================================================================================
def git_rev(log: Callable = info):
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
def write_args(args: argparse.Namespace, filePath: Path = Path("args.json"), log: Callable = info):
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
			ujson.dump(argsDict, file, indent=2, ensure_ascii=False, escape_forward_slashes=False, sort_keys=False)


# ==================================================================================================
class NamingFormatter(logging.Formatter):
	# ----------------------------------------------------------------------------------------------
	def format(self, record: logging.LogRecord, varNamePrefix="", varNameSuffix="") -> str:
		"""
		Handles f-string automatic naming for inherited classes.
		Includes spaces around the operator.

		Args:
			record (logging.LogRecord): Log object

		Returns:
			str: Formatted output
		"""
		if (record.levelname == "DEBUG"):
			record.levelname = "[DEBG]"
		elif (record.levelname == "INFO"):
			record.levelname = "[INFO]"
		elif (record.levelname == "WARNING"):
			record.levelname = "[WARN]"
		elif (record.levelname == "ERROR"):
			record.levelname = "[ERR!]"
		elif (record.levelname == "CRITICAL"):
			record.levelname = "[CRIT]"

		if hasattr(record, "varName"):
			record.msg = f"{varNamePrefix}{record.varName}{colorama.Style.RESET_ALL} = {varNameSuffix}{record.msg}"

		return super().format(record)


# ==================================================================================================
class ColouredFormatter(NamingFormatter):
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
		elif (record.levelname == "INFO"):
			prefix = colorama.Fore.WHITE
		elif (record.levelname == "WARNING"):
			prefix = colorama.Fore.YELLOW
		elif (record.levelname == "ERROR"):
			prefix = colorama.Fore.RED
		elif (record.levelname == "CRITICAL"):
			prefix = colorama.Fore.RED + colorama.Style.BRIGHT
		else:
			prefix = ""
		suffix = colorama.Style.RESET_ALL

		return f"{prefix}{super().format(record, varNamePrefix=colorama.Fore.MAGENTA, varNameSuffix=prefix)}{suffix}"


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
	# setup_logger(useEq=False)

	debug("hello")
	d = {"a": 23, "nope": False}
	debug(d)
	info(d, True)
	warning(True); error(False)
	debug(True); debug(False)
	critical(True)
	a, b = 2, 2
	c = 2
	debug(a)
	debug(c)
	debug(a, b, c)
	debug(None)
	debug(f"ok: {True}")
	# TODO FIX
	debug(f"ok: {True}", c)
	debug(c, f"ok: {True}")
