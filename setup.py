#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='watpy3',
    version='1.0',
    description='Waveform Analysis Tool in Python',
    author='AAVV',
    author_email='core@uni-jena.de',
    url = 'https://bitbucket.org/bernuzzi/watpy',
    packages = find_packages(),
    requires = ['h5py', 'numpy', 'matplotlib'],
)
