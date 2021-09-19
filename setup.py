#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

NAME = "sprachenkarte"
DESCRIPTION = "Tools for generating linguistic maps from spreadsheets using Cartopy"
URL = "https://github.com/antipodite/sprachenkarte"
EMAIL = "isaac_stead@eva.mpg.de"
AUTHOR = "Isaac Stead"
VERSION = "0.1"
REQUIRES_PYTHON = '>=3.6.0'

REQUIRED = ["matplotlib", "numpy", "scipy", "Cartopy", "pandas",]

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    email=EMAIL,
    url=URL,
    author_email=EMAIL,
    install_requires=REQUIRED,
    python_requires=REQUIRES_PYTHON,
    py_modules=["sprachenkarte"]
)
