#!/usr/bin/env python
import logging
import colorama
import subprocess
import inspect
from pathlib import Path
import ujson
from sys import stdout

name = "kellog"
ready = False

# ==================================================================================================
def debug(*args):
	if not ready:
		setup_logger("/tmp/log", "kellog", True)
	logger = logging.getLogger(name)
	logger.debug(force_to_string(*args))
def info(*args):
	if not ready:
		setup_logger("/tmp/log", "kellog", True)
	logger = logging.getLogger(name)
	logger.info(force_to_string(*args))
def warning(*args):
	if not ready:
		setup_logger("/tmp/log", "kellog", True)
	logger = logging.getLogger(name)
	logger.warning(force_to_string(*args))
def error(*args):
	if not ready:
		setup_logger("/tmp/log", "kellog", True)
	logger = logging.getLogger(name)
	logger.error(force_to_string(*args))
def critical(*args):
	if not ready:
		setup_logger("/tmp/log", "kellog", True)
	logger = logging.getLogger(name)
	logger.critical(force_to_string(*args))


# ==================================================================================================
def git_rev(log=info):
	cwd = Path(inspect.stack()[1][1]).parent
	try:
		output = str(subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.STDOUT, universal_newlines=True, cwd=cwd)).strip()
	except subprocess.CalledProcessError as exc:
		error(exc.output)
	else:
		log("Git revision:", output)


# ==================================================================================================
def force_to_string(*args):
	msg = ""
	if (len(args) > 0):
		msg = str(args[0])
	if (len(args) > 1):
		for arg in args[1:]:
			msg += f" {str(arg)}"
	return msg


# ==================================================================================================
class ColouredFormatter(logging.Formatter):
	def __init__(self, msg):
		super().__init__(msg)

	def format(self, record):
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
def setup_logger(file, newName="kellog", reset=False):
	global name, ready
	name = newName

	if reset:
		open(file, "w").close() # Delete contents

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

	if file:
		fh = logging.FileHandler(file)
		fh.setLevel(logging.DEBUG)
		fh.setFormatter(logging.Formatter(formatting))
		logger.addHandler(fh)

	ready = True


# ==================================================================================================
def write_args(args, filename="args.json", log=info):
	if log:
		import __main__ as main
		log(f"Main script: {main.__file__}")
		log("Arguments: ")
		for k, v in args.__dict__.items():
			log(f"  {k}: {v}")
	if filename is not None:
		with open(filename, "w") as file:
			ujson.dump(args.__dict__, file, indent=2, ensure_ascii=False, escape_forward_slashes=False, sort_keys=False)
