# coding=utf-8

from distutils.core import setup
from setuptools import find_packages

import sys

if sys.version_info >= (3,):
    long_description = open("README.txt", encoding="utf-8").read()
else:
    # python 2 doesn't have the "encoding" keyword for open()
    long_description = open("README.txt").read()

setup(
    name="boardgamegeek",
    version="0.0.5",
    packages=find_packages(),
    license="BSD",
    author="Cosmin Luță",
    author_email="q4break@gmail.com",
    description="A Python interface to boardgamegeek.com's API",
    long_description=long_description,
    url="https://github.com/lcosmin/boardgamegeek",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    install_requires=["requests",
                      "requests-cache"],
    entry_points={
        "console_scripts": [
            "boardgamegeek = boardgamegeek.main:main"
        ]
    }
)
