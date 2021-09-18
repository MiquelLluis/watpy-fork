# Python Waveform Analysis Tools

The [CoRe](http://www.computational-relativity.org/) python package for the analysis of gravitational waves based on
[`scidata`](https://bitbucket.org/dradice/scidata/src/default/),
[Matlab's `WAT`](https://bitbucket.org/bernuzzi/wat/src/master/) and 
[`pyGWAnalysis`](http://svn.einsteintoolkit.org/pyGWAnalysis/trunk/) 

## Installation

The installation relies on standard Python library `setuptools`.
Once the repository is cloned, the installation can be performed in two ways,
depending on the choice of the user:
* Run the command `python setup.py install` or `python setup.py install --user` inside the project directory. 
* Install the module via `pip` running the command `python -m pip install` inside the project directory. It is possible to include the `--user` option and the `-e` option for editing.

## Requirements

The Python Waveform Analysis Tools are compatible with Python3 (Old versions of watpy were Python2 compatible).

Albeit WatPy is a Python package, it requires the following to be able to properly interface with the database:

* [git](https://git-scm.com/) version control system
* [git-lfs](https://git-lfs.github.com/) API (Large File Storage)

The following Python packages are required for installation:

* [Numpy](https://numpy.org/) (Python array-handler)
* [Scipy](https://www.scipy.org/) (Python scientific library)
* [Matplotlib](https://matplotlib.org/) (Nice visualization package)
* [H5py](https://www.h5py.org/) (Pythonic interface to HDF5)

For users interested in interactive usage of this package we suggest ipyhton notebooks. These can be installed with the following packages:

* [iPython](https://ipython.org/) (Strictly better version of the basic python shell)
* [Jupyter](https://jupyter.org/) (Notebooks, slides, HTML conversion of notebooks and more)
    
## Features

 * Classes for multipolar waveform data
 * Classes to work with the CoRe database
 * Gravitational-wave energy and angular momentum calculation routines
 * Psi4-to-h via FFI or time integral routines
 * Waveform alignment and phasing routines
 * Waveform interpolation routines
 * Waveform's spectra calculation
 * Richardson extrapolation
 * Wave objects contain already information on merger quantities (time, frequency)
 * Unit conversion package
 * Compatible file formats: BAM, Cactus (WhiskyTHC / FreeTHC), CoRe database
