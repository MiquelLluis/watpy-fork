# Python Waveform Analysis Tools

A python package for the analysis of gravitational waves based on
[scidata](https://bitbucket.org/dradice/scidata/src/default/),
[Matlab's WAT](https://bitbucket.org/bernuzzi/wat/src/master/) and
Reisswig's
[pyGWAnalysis](http://svn.einsteintoolkit.org/pyGWAnalysis/trunk/) 


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

 * Classes for single pole / Multipoles data
 * Gravitational Wave energy and angular momentum calculation routines
 * Psi4-to-h via FFI or time integral routines
 * Waveform alignment and phasing routines
 * Waveform interpolation routines
 * Waveform spectra calculation
 * Richardson extrapolation
 * Wave objects contain already information on merger quantities (time, frequency)
 * Unit conversion package
 * Compatible file formats: BAM, Cactus (WhiskyTHC / FreeTHC), CoRe database
