# coding=utf-8

from distutils.core import setup
from setuptools import find_packages
from codecs import open

version = {}
with open("boardgamegeek/version.py") as fp:
    exec(fp.read(), version)

long_description = open("README.txt", encoding="utf-8").read()

setup(
    name="boardgamegeek",
    version=version["__version__"],
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
