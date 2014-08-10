# coding=utf-8

from distutils.core import setup
from setuptools import find_packages
from boardgamegeek import __version__

import sys

if sys.version_info >= (3,):
    long_description = open("README.txt", encoding="utf-8").read()
else:
    # python 2 doesn"t have the "encoding" keyword for open()
    long_description = open("README.txt").read()

setup(
    name="boargamegeek",
    version=__version__,
    packages=find_packages(exclude=["*test"]),
    license="BSD License",
    author="Cosmin Luță",
    author_email="q4break@gmail.com",
    description="A Python interface to the boardgamegeek.com API (forked from Geoff Lawler's libBGG).",
    long_description=long_description,
    url="https://github.com/lcosmin/boardgamegeek",
    install_requires=["requests",
                      "requests-cache"],
    scripts=["bin/bgg_query", "bin/top_rated"]
)
