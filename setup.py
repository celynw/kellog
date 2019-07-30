#!/usr/bin/env python
from setuptools import setup

setup(
	name = "kellog",
	version = "0.1",
	description = "Easy logging",
	author = "Celyn Walters",
	packages = ["kellog"],
	install_requires=["colorama", "ujson", "gitpython"],
)
