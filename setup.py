from distutils.core import setup
from setuptools import find_packages
from libBGG import __version__

import sys

if sys.version_info >= (3,):
    long_description = open('README.txt', 'r', encoding='utf-8').read()
else:
    # python 2 doesn't have the 'encoding' keyword for open()
    long_description = open('README.txt', 'r').read() 

setup(
    name='libBGG',
    version=__version__,
    packages=find_packages(exclude=['*test']),
    license='FreeBSD License',
    author='Geoff Lawler',
    author_email='geoff.lawler@gmail.com',
    description='A python interface to the boardgamegeek.com API and boardgame utils.',
    long_description=long_description,
    url='https://github.com/philsstein/libBGG',
    install_requires=[],
    scripts=['bin/bgg_query', 'bin/top_rated']
)
