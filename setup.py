#!/usr/bin/env python
from setuptools import setup, find_packages
import re

# Read version from pyproject.toml
ini = open('pyproject.toml').read()
vrs = r"^version = ['\"]([^'\"]*)['\"]"
mo  = re.search(vrs, ini, re.M)
version = mo.group(1)

setup(
    name='core-watpy',
    version=version,
    description='Waveform Analysis Tool in Python',
    author='CoRe Team',
    author_email='core@listserv.uni-jena.de',
    url = 'https://git.tpi.uni-jena.de/core/watpy',
    packages = find_packages(),
    requires = ['h5py', 'numpy', 'matplotlib'],
)
