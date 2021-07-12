#!/usr/bin/env python3
from setuptools import setup

setup(
	name="kellog",
	version="0.2.0",
	description="Easy logging",
	author="Celyn Walters",
	url="https://github.com/celynw/kellog",
	packages=["kellog"],
	install_requires=["colorama", "ujson", "munch"],
	python_requires=">=3.6",
)
