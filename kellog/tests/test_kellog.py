from __future__ import annotations

import argparse
import logging
import tempfile
from io import StringIO
from pathlib import Path
from typing import Generator

import colorama
import pytest

from kellog import Kellog, critical, debug, error, info, log_args, warning


def test_instantiated_on_import() -> None:
	"""Ensure the singleton is instantiated when the module is imported."""
	assert Kellog._instance is not None, "The singleton should be instantiated"


def test_force_to_string() -> None:
	"""Ensure things are casted to string as we expect."""
	assert Kellog._force_to_string("Hello", "World") == "Hello World", "Strings should be concatenated"
	assert Kellog._force_to_string(123, 456) == "123 456", "Integers should be concatenated"
	assert Kellog._force_to_string() == "", "Empty string should be returned"
	assert Kellog._force_to_string(None) == "None", "None should be casted to string"


def test_instantiation() -> None:
	"""Ensure the singleton pattern works."""
	name = Kellog._instance.name
	Kellog(name="newname")

	assert Kellog._instance.name != name, "The name should have changed"


def test_loggers() -> None:
	"""Ensure the loggers are created correctly."""
	redirect_stream()
	assert Kellog._instance.logger is logging.getLogger("kellog"), "The logger should be named 'kellog'"
	logger = Kellog._instance.logger

	assert logger is not None, "The logger should exist"
	assert logger.level == logging.DEBUG, "The logger should be set to DEBUG"
	assert len(logger.handlers) == 1, "The logger should have one handler"


def test_append_to_file(existing_file: Path) -> None:
	"""Ensure we can write to an existing file without deleting the contents."""
	Kellog(path=existing_file)
	redirect_stream()
	logger = Kellog._instance.logger

	hs = [type(h) for h in logger.handlers]
	assert len(hs) == 2, "There should be two handlers"
	assert logging.StreamHandler in hs, "One handler should be a StreamHandler"
	assert logging.FileHandler in hs, "One handler should be a FileHandler"

	info("Info string")
	lines = existing_file.read_text().splitlines()
	assert len(lines) == 2, "There should be two lines"
	assert lines[1] == " Info string", "The second line should be the info string"


def test_overwrite_file(existing_file: Path) -> None:
	"""Ensure we can replace the content in an existing file."""
	Kellog(path=existing_file, append=False)
	redirect_stream()
	logger = Kellog._instance.logger

	hs = [type(h) for h in logger.handlers]
	assert len(hs) == 2, "There should be two handlers"
	assert logging.StreamHandler in hs, "One handler should be a StreamHandler"
	assert logging.FileHandler in hs, "One handler should be a FileHandler"
	assert existing_file.read_text() == "", "The file should be empty"

	info("Info string")
	lines = existing_file.read_text().splitlines()
	assert len(lines) == 1, "There should be one line"
	assert lines[0] == " Info string", "The first line should be the info string"

	debug("Debug string")
	lines = existing_file.read_text().splitlines()
	assert len(lines) == 2, "There should now be two lines"
	assert lines[1] == " Debug string", "The second line should be the debug string"


def test_colours() -> None:
	"""Ensure the colours are correct."""
	buffer = redirect_stream()

	debug("Debug string")
	info("Info string")
	warning("Warning string")
	error("Error string")
	critical("Critical string")

	output = buffer.getvalue().splitlines()
	assert colorama.Fore.GREEN in output[0], "The debug string should be green"
	assert colorama.Fore.WHITE in output[1], "The info string should be white"
	assert colorama.Fore.YELLOW in output[2], "The warning string should be yellow"
	assert colorama.Fore.RED in output[3], "The error string should be red"
	assert colorama.Fore.RED in output[4], "The critical string should be red"
	assert colorama.Style.BRIGHT in output[4], "The critical string should be bright (bold)"


def test_log_args() -> None:
	"""Ensure log_args works as expected."""
	buffer = redirect_stream()

	args = argparse.Namespace(arg1="value1", arg2="value2")
	log_args(args)
	output = buffer.getvalue().splitlines()

	assert "arg1: value1" in output[-2], "The first argument was not found"
	assert "arg2: value2" in output[-1], "The second argument was not found"


def test_prefixes() -> None:
	"""Ensure the prefixes can be set correctly."""
	Kellog(prefixes={"debug": "[D]", "info": "[I]", "warning": "[W]", "error": "[E]", "critical": "[C]"})
	buffer = redirect_stream()

	debug("Debug string")
	info("Info string")
	warning("Warning string")
	error("Error string")
	critical("Critical string")

	output = buffer.getvalue().splitlines()
	assert "[D]" in output[0], "The debug string should have the debug prefix"
	assert "[I]" in output[1], "The info string should have the info prefix"
	assert "[W]" in output[2], "The warning string should have the warning prefix"
	assert "[E]" in output[3], "The error string should have the error prefix"
	assert "[C]" in output[4], "The critical string should have the critical prefix"


def redirect_stream() -> StringIO:
	"""Redirect the stream handler to a buffer, and return the buffer."""
	buffer = StringIO()
	stream_handler = next(
		(handler for handler in Kellog._instance.logger.handlers if isinstance(handler, logging.StreamHandler)),
		None,
	)
	assert isinstance(stream_handler, logging.StreamHandler), "No stream handler found"
	stream_handler.stream = buffer

	return buffer


@pytest.fixture(autouse=True)
def _reinstantiate_kellog() -> None:
	Kellog()


@pytest.fixture()
def existing_file() -> Generator[Path, None, None]:
	"""Create a temporary file with some content, and yield the path to it."""
	temp = tempfile.NamedTemporaryFile(delete=False)
	temp.write(b"Hello World")
	temp.close()
	yield Path(temp.name)
	if Path(temp.name).exists():
		Path(temp.name).unlink()
