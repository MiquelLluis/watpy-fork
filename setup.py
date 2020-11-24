#!/usr/bin/env python

from distutils.core import setup

setup(
    name='watpy3',
    version='1.0',
    description='Waveform Analysis Tool in Python',
    author='AAVV',
    author_email='core@uni-jena.de',
    url = 'https://bitbucket.org/bernuzzi/watpy',
    packages = ['watpy/base', 'watpy/db_utilities'],
    requires = ['h5py', 'numpy', 'matplotlib'],
)
