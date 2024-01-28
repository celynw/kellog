#!/usr/bin/env python3
from __future__ import annotations

import logging
from pathlib import Path
from sys import stdout
from typing import TYPE_CHECKING, Any, Callable

import colorama
import ujson
from typing_extensions import Self

if TYPE_CHECKING:
	import argparse


class ColouredFormatter(logging.Formatter):
	def __init__(self: Self, msg: str, prefixes: dict[str, str]) -> None:
		super().__init__(msg)
		self.prefixes = prefixes

	def format(self: Self, record: logging.LogRecord) -> str:
		"""
		Prefixes with the logging level and assigns a colour.

		Parameters
		----------
		record
			Log object

		Returns
		-------
			Formatted output
		"""
		if record.levelname == "DEBUG":
			prefix = colorama.Fore.GREEN
			record.levelname = self.prefixes["debug"]
		elif record.levelname == "INFO":
			prefix = colorama.Fore.WHITE
			record.levelname = self.prefixes["info"]
		elif record.levelname == "WARNING":
			prefix = colorama.Fore.YELLOW
			record.levelname = self.prefixes["warning"]
		elif record.levelname == "ERROR":
			prefix = colorama.Fore.RED
			record.levelname = self.prefixes["error"]
		elif record.levelname == "CRITICAL":
			prefix = colorama.Fore.RED + colorama.Style.BRIGHT
			record.levelname = self.prefixes["critical"]
		else:
			prefix = ""
		suffix = colorama.Style.RESET_ALL

		return prefix + super().format(record) + suffix


class Kellog:
	_instance: Self = None  # type: ignore[attr-defined]

	def __new__(cls: type[Self], *args: tuple[Any], **kwargs: Any) -> Self:
		if cls._instance is None:
			cls._instance = super().__new__(cls, *args, **kwargs)

		return cls._instance

	def __init__(
		self: Self,
		*,
		path: Path | None = None,
		name: str = "kellog",
		prefixes: dict[str, str] | None = None,
		append: bool = True,
	) -> None:
		"""
		Initialise the logger.

		Parameters
		----------
		path, optional
			Output file, by default `None`
		name, optional
			Reset the logger name to this, by default `"kellog"`
		prefixes, optional
			Set the log message prefixes (does not automatically add separating whitespace), by default `None`.
			The dictionary keys to set are "debug", "info", "warning", "error", "critical".
			Setting to None will use the default unicode prefixes, from codicons:      .
		append, optional
			If False, delete the contents of `path` first, by default `True`
		"""
		if prefixes is None:
			prefixes = {
				"debug": " ",
				"info": " ",
				"warning": " ",
				"error": " ",
				"critical": " ",
			}

		self.path = path
		self.name = name
		self.append = append

		if not append and path is not None:
			path.open("w").close()  # Delete contents

		logger = logging.getLogger(self.name)
		logger.propagate = False
		if logger:
			logger.handlers = []
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(logging.DEBUG)
		ch = logging.StreamHandler(stream=stdout)
		ch.setLevel(logging.DEBUG)
		formatting = "%(levelname)s%(message)s"
		ch.setFormatter(ColouredFormatter(formatting, prefixes))
		self.logger.addHandler(ch)

		if path:
			fh = logging.FileHandler(path)
			fh.setLevel(logging.DEBUG)
			fh.setFormatter(logging.Formatter(formatting))
			self.logger.addHandler(fh)

	def _maybe_add_newline(self: Self) -> None:
		if self.path is not None and self.append and self.path.exists() and self.path.stat().st_size > 0:
			with self.path.open("a") as f:
				f.write("\n")

	def debug(self: Self, *args: Any) -> None:
		self._maybe_add_newline()
		self.logger.debug(self._force_to_string(*args))

	def info(self: Self, *args: Any) -> None:
		self._maybe_add_newline()
		self.logger.info(self._force_to_string(*args))

	def warning(self: Self, *args: Any) -> None:
		self._maybe_add_newline()
		self.logger.warning(self._force_to_string(*args))

	def error(self: Self, *args: Any) -> None:
		self._maybe_add_newline()
		self.logger.error(self._force_to_string(*args))

	def critical(self: Self, *args: Any) -> None:
		self._maybe_add_newline()
		self.logger.critical(self._force_to_string(*args))

	@staticmethod
	def _force_to_string(*args: Any) -> str:
		"""
		Force the input to be a string.

		Returns
		-------
			Output as string
		"""
		msg = ""
		if len(args) > 0:
			msg = str(args[0])
		if len(args) > 1:
			for arg in args[1:]:
				msg += f" {arg}"

		return msg

	@staticmethod
	def log_args(args: argparse.Namespace, path: Path = Path("args.json"), log: Callable = info) -> None:
		"""
		Print the argparse arguments in a nice list, and optionally saves to file.

		Parameters
		----------
		args
			Input arguments from `parser.parse_args()`
		path, optional
			Path of JSON file to save the arguments to, by default `Path("args.json")`
		log, optional
			Logging/printing function to use, by default `Kellog.info`
		"""
		args_dict = args.__dict__.copy()
		if log:
			import __main__ as main

			log(f"Main script: {main.__file__}")
			log("Arguments: ")
			for k, v in args_dict.items():
				log(f"  {k}: {v}")
		if path is not None:
			for k, v in args_dict.items():
				args_dict[k] = str(v) if not isinstance(v, (str, float, int, bool)) else v
			with path.open("w") as file:
				ujson.dump(args_dict, file, indent=2, ensure_ascii=False, escape_forward_slashes=False, sort_keys=False)


# Automatically instantiate the singleton class when this module is imported
kellog = Kellog()


def debug(*args: Any) -> None:
	kellog.debug(*args)


def info(*args: Any) -> None:
	kellog.info(*args)


def warning(*args: Any) -> None:
	kellog.warning(*args)


def error(*args: Any) -> None:
	kellog.error(*args)


def critical(*args: Any) -> None:
	kellog.critical(*args)


def log_args(args: argparse.Namespace, path: Path = Path("args.json"), log: Callable = info) -> None:
	kellog.log_args(args, path, log)


if __name__ == "__main__":
	debug("Debug")
	info("Info")
	warning("Warning")
	error("Error")
	critical("Critical")
