#!/usr/bin/python

"""
Example script to create a pre-release folder to be later pushed to
the CoRe DB
SB 10/2021
"""

from watpy.utils.coreh5 import CoRe_h5
from watpy.coredb.metadata import CoRe_md, TXT_MAIN
from watpy.utils.units import MSun_sec
import os # mkdirs

Msun_sec = MSun_sec() #4.925794970773135e-06

def generate_simulation_name(EOS,MA,MB,SzA,SzB,Momega0,extra=None):
    """ String for simulation name as appearing in the metadata*.txt """
    name = '{}_{:.3f}_{:.3f}_{:.2f}_{:.2f}_{:.3f}'.format(EOS,MA,MB,SzA,SzB,Momega0)
    if extra is not None:
        name += extra
    return name


# Simulation data (example)
# --------------------------

# NOTE the .txt files in the sim_folder are already in CoRe format. 
# To generate them from standard BAM or THC output use e.g. watpy's
# wave() and mwave(). See:
#  tutorials/watpy_wave.ipynb
sim_folder = '../tutorials/TestData/MySim_THC_135135/CoReDB/'

# Make a list of groups and files for each group
# IMPORTANT: group and file names must follow the CoRe conventions 
thcdfiles = {}
thcdfiles['energy'] = ['EJ_r00400.txt']
thcdfiles['rh_22'] = ['Rh_l2_m2_r00400.txt']
thcdfiles['rh_30'] = ['Rh_l3_m0_r00400.txt']
thcdfiles['rpsi4_20'] = ['Rpsi4_l2_m0_r00400.txt']
thcdfiles['rpsi4_22'] = ['Rpsi4_l2_m2_r00400.txt']
# etc.


# Metadata
# --------

# Generate a short and a long `simulation_name` for the two different metadata files
# IMPORTANT: add to the long name some info on resolution (and other specs) 
# and, if this is a new simulation, append a tag 'R01' so it is clear this is a run of a simulation
simname_short = generate_simulation_name('ABC',1.35,1.35,0,0,0.03789461)
simname_long = generate_simulation_name('ABC',1.35,1.35,0,0,0.03789461,"_R01_0.058_gridX") 

# Metadata info can be provided e.g. from a python dict or a text
# file. Here is a dict example:
thcsim = {}
thcsim['database_key'] = 'will_be_assigned_by_watpy_CoRe_db'
thcsim['simulation_name'] = simname_short # use first the short name !
thcsim['reference_bibkeys'] = 'bibitem:2021avg'
thcsim['available_resolutions'] = '' # empty, this will be added on the way ...

thcsim['id_code']                  = 'LORENE'
thcsim['id_type']                  = 'Irrotational'
thcsim['id_mass']                  = 2.7
thcsim['id_rest_mass']             = 2.94554
thcsim['id_mass_ratio']            = 1.0
thcsim['id_ADM_mass']              = 2.67288
thcsim['id_ADM_angularmomentum']   = 7.01514
thcsim['id_gw_frequency_Hz']       = 663.58
thcsim['id_gw_frequency_Momega22'] = 0.0554514940011
thcsim['id_eos']                   = 'ABC'
thcsim['id_kappa2T']               = 159.0084296249798
thcsim['id_Lambda']                = 848.0449579998918
thcsim['id_eccentricity']          = None # None entries wil remain such in the DB !
thcsim['id_mass_starA']            = 1.35
thcsim['id_rest_mass_starA']       = 1.47277
thcsim['id_spin_starA']            = 0, 0, 0
thcsim['id_LoveNum_kell_starA']    = 0.09996, 0.0269, 0.00984
thcsim['id_Lambdaell_starA']       = 848.0449579998921, 2001.0063178210328, 4584.234164607441
thcsim['id_mass_starB']            = 1.35
thcsim['id_rest_mass_starB']       = 1.47277
# etc., etc. add all entries !
# See: watpy/coredb/metadata.py

thcsim['sim-folder'] = sim_folder
thcsim['pre-release-folder'] = simname_long 


# Dump pre-release data
# ---------------------

# Create folder for CoRe pre-release
os.makedirs(thcsim['pre-release-folder'], exist_ok = True)

# Dump the metadata there
# For later convenience, dump both metadata files
# NOTE: entries not matching the CoRe metadata will be ignored
md = CoRe_md(metadata = thcsim) 
md.write(path = thcsim['pre-release-folder'],
         fname = 'metadata.txt')

thcsim['simulation_name'] = simname_short
md.update_fromdict(thcsim)
md.write(path = thcsim['pre-release-folder'],
         fname = 'metadata_main.txt',
         templ = TXT_MAIN)

# Generate The CoRe data.h5 and dump it in the pre-release folder
ch5 = CoRe_h5(thcsim['pre-release-folder']) 
ch5.create_dset(thcdfiles,
                path = thcsim['sim-folder'])
