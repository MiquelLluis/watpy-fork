# Python Waveform Analysis Tools

The [CoRe](http://www.computational-relativity.org/) python package for the analysis of gravitational waves based on
[scidata](https://bitbucket.org/dradice/scidata/src/default/),
[Matlab's WAT](https://bitbucket.org/bernuzzi/wat/src/master/) and 
[pyGWAnalysis](http://svn.einsteintoolkit.org/pyGWAnalysis/trunk/) 

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

## Content

    + watpy/		Top-level package
    |--- + base/ 			Subpackage with basic routines 
    |    | wave.py 				Contains classes for multipoles and single mode waves
    | 	 | gw_utils.py  		Contains utilities for wave quantity manipulation
    | 	 | num_utils.py 		Contains numerical utilities
    | 	 | phys_utils.py 		Contains physics routines (e.g., for tidal parameters calculation)
    |	 | utils.py    			Contains general inut/output utilities
    |	 | units.py 			Contains unit conversion utilities
    |--- + db_utilities/    Subpackage with database routines
    |    | index.py             Contains the class to handle the database index
    |    | db_utils.py          Contains classes to handle database entries and single runs
    |    | metadata_utils.py    Contains classes for simulation metadata manipulation 
    |    | h5_utils.py          Contains the class for the HDF5 archive operations
    |    | simlist_utils.py     Contains internal routines for database operations used in db_utils
    |--- + examples/	    Not a subpackage
    |    | examples.py          Contains coded examples on how to use the tool for waveform visualization
    |    | db_examples.py       Contains coded examples on how to navigate the database
    |    | DB_tutorial.ipynb    Jupyter notebook with a step-by-step tutorial on how to use the tool and the database
    |    | DB_tutorial.html     HTML version of the tutorial (for non-jupyter users; NB: NOT interactive)
    
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
