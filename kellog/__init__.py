#!/usr/bin/env python
import logging as _logging
import colorama as _colorama
import subprocess as _subprocess
import inspect as _inspect
from pathlib import Path
import ujson

_logger = None

#===================================================================================================
def debug(*args):
	if _logger is None:
		_setup_logger("/tmp/log", "default_logger", True)
	_logger.debug(_force_to_string(*args))
def info(*args):
	if _logger is None:
		_setup_logger("/tmp/log", "default_logger", True)
	_logger.info(_force_to_string(*args))
def warning(*args):
	if _logger is None:
		_setup_logger("/tmp/log", "default_logger", True)
	_logger.warning(_force_to_string(*args))
def error(*args):
	if _logger is None:
		_setup_logger("/tmp/log", "default_logger", True)
	_logger.error(_force_to_string(*args))
def critical(*args):
	if _logger is None:
		_setup_logger("/tmp/log", "default_logger", True)
	_logger.critical(_force_to_string(*args))


#===================================================================================================
def _git_rev(log=info):
	cwd = Path(_inspect.stack()[1][1]).parent
	try:
		output = str(_subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=_subprocess.STDOUT, universal_newlines=True, cwd=cwd)).strip()
	except _subprocess.CalledProcessError as exc:
		error(exc.output)
	else:
		log("Git revision:", output)


#===================================================================================================
def _force_to_string(*args):
	msg = ""
	if (len(args) > 0):
		msg = str(args[0])
	if (len(args) > 1):
		for arg in args[1:]:
			msg += f" {str(arg)}"
	return msg


#===================================================================================================
class _ColouredFormatter(_logging.Formatter):
	def __init__(self, msg):
		super().__init__(msg)

	def format(self, record):
		if (record.levelname == "DEBUG"):
			prefix = _colorama.Fore.GREEN
			record.levelname = "[DEBG]"
		elif (record.levelname == "INFO"):
			prefix = _colorama.Fore.WHITE
			record.levelname = "[INFO]"
		elif (record.levelname == "WARNING"):
			prefix = _colorama.Fore.YELLOW
			record.levelname = "[WARN]"
		elif (record.levelname == "ERROR"):
			prefix = _colorama.Fore.RED
			record.levelname = "[ERR!]"
		elif (record.levelname == "CRITICAL"):
			prefix = _colorama.Fore.RED + _colorama.Style.BRIGHT
			record.levelname = "[CRIT]"
		else:
			prefix = ""
		suffix = _colorama.Style.RESET_ALL
		return prefix + _logging.Formatter.format(self, record) + suffix


#===================================================================================================
def _setup_logger(file, name="logger", reset=False):
	if reset:
		open(file, "w").close() # Delete contents
	global _logger
	if _logger:
		_logger.handlers = []
	_logger = _logging.getLogger(name)
	_logger.setLevel(_logging.DEBUG)
	ch = _logging.StreamHandler()
	ch.setLevel(_logging.DEBUG)
	formatting = "%(levelname)s %(message)s"
	ch.setFormatter(_ColouredFormatter(formatting))
	_logger.addHandler(ch)
	if file:
		fh = _logging.FileHandler(file)
		fh.setLevel(_logging.DEBUG)
		fh.setFormatter(_logging.Formatter(formatting))
		_logger.addHandler(fh)


#===================================================================================================
def _write_args(args, filename="args.json", log=info):
	if log:
		import __main__ as main
		log(f"Main script: {main.__file__}")
		log("Arguments: ")
		for k, v in args.__dict__.items():
			log(f"  {k}: {v}")
	if filename is not None:
		with open(filename, "w") as file:
			ujson.dump(args.__dict__, file, indent=2, ensure_ascii=False, escape_forward_slashes=False, sort_keys=False)
