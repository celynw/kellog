#!/usr/bin/env python
import logging as _logging
import colorama as _colorama
import subprocess as _subprocess

_logger = None

#===================================================================================================
def debug(*args):
	_logger.debug(_force_to_string(*args))
def info(*args):
	_logger.info(_force_to_string(*args))
def warning(*args):
	_logger.warning(_force_to_string(*args))
def error(*args):
	_logger.error(_force_to_string(*args))
def critical(*args):
	_logger.critical(_force_to_string(*args))


#===================================================================================================
def _git_rev(log=info):
	try:
		output = _subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=_subprocess.STDOUT, universal_newlines=True)
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
	if (reset):
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
if (__name__ == "__main__"):
	warning("log.py is supposed to be imported with 'from log import *'")
else:
	if not _logger:
		_setup_logger("/tmp/log", "default_logger", True)
