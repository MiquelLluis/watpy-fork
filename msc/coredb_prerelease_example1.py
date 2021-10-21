#!/usr/bin/python

"""
Example script to create a pre-release folder to be later pushed to
the CoRe DB.
SB 10/2021
"""

import numpy as np
from watpy.wave.wave import mwaves
from watpy.utils.coreh5 import CoRe_h5
from watpy.coredb.metadata import CoRe_md, TXT_MAIN
from watpy.utils.units import MSun_sec
import os # mkdirs
import glob

Msun_sec = MSun_sec() #4.925794970773135e-06

def generate_simulation_name(EOS,MA,MB,SzA,SzB,Momega0,extra=None):
    """ String for simulation name as appearing in the metadata*.txt """
    name = '{}_{:.3f}_{:.3f}_{:.2f}_{:.2f}_{:.3f}'.format(EOS,MA,MB,SzA,SzB,Momega0)
    if extra is not None:
        name += extra
    return name


# Simulation data (example)
# --------------------------

# NOTE the waveform files in the sim_folder are NOT in CoRe format. 
# Below, mwaves() is used to generate data in CoRe format
sim_folder = '../tutorials/TestData/MySim_BAM_135135/'

        
# Metadata
# --------

# Generate a short and a long `simulation_name` for the two different metadata files
# IMPORTANT: add to the long name some info on resolution (and other specs) 
# and append a tag 'R??' so it is clear this is a run of a (set of) simulation(s)
simname_short = generate_simulation_name('ABC',1.35,1.35,0,0,0.03789461)
simname_long = generate_simulation_name('ABC',1.35,1.35,0,0,0.03789461,"_R01_0.058_gridX") 

# Metadata info can be provided e.g. from a python dict or a text
# file. Here is a dict example:
bamsim = {}
bamsim['database_key'] = 'will_be_assigned_by_watpy_CoRe_db'
bamsim['simulation_name'] = simname_short # use first the short name !
bamsim['reference_bibkeys'] = 'bibitem:2021avg'
bamsim['available_resolutions'] = '' # empty, this will be added on the way ...

bamsim['id_code']                  = 'LORENE'
bamsim['id_type']                  = 'Irrotational'
bamsim['id_mass']                  = 2.7
bamsim['id_rest_mass']             = 2.94554
bamsim['id_mass_ratio']            = 1.0
bamsim['id_ADM_mass']              = 2.67288
bamsim['id_ADM_angularmomentum']   = 7.01514
bamsim['id_gw_frequency_Hz']       = 663.58
bamsim['id_gw_frequency_Momega22'] = 0.0554514940011
bamsim['id_eos']                   = 'ABC'
bamsim['id_kappa2T']               = 159.0084296249798
bamsim['id_Lambda']                = 848.0449579998918
bamsim['id_eccentricity']          = None # None entries wil remain such in the DB !
bamsim['id_mass_starA']            = 1.35
bamsim['id_rest_mass_starA']       = 1.47277
bamsim['id_spin_starA']            = 0, 0, 0
bamsim['id_LoveNum_kell_starA']    = 0.09996, 0.0269, 0.00984
bamsim['id_Lambdaell_starA']       = 848.0449579998921, 2001.0063178210328, 4584.234164607441
bamsim['id_mass_starB']            = 1.35
bamsim['id_rest_mass_starB']       = 1.47277
# etc., etc. add all entries !
# See: watpy/coredb/metadata.py

# Additional info (not used for the metadata)
bamsim['sim-folder'] = sim_folder
bamsim['pre-release-folder'] = simname_long 

bamsim['mass'] = 2.700297e+00 # binary mass in solar masses
bamsim['q'] = 1.0 # mass ratio, >= 1
bamsim['Momg22'] = 3.789461e-02 # GW frequency (dim/less, mass rescaled)
bamsim['f0'] = bamsim['Momg22'] / (2*np.pi) / bamsim['mass'] # initial GW frequency in geom. units
bamsim['f0_Hz'] = bamsim['Momg22'] / (2*np.pi) / bamsim['mass']  / Msun_sec # initial GW frequency in Hz
bamsim['massA'] = 1.350149e+00
bamsim['massB'] = 1.350149e+00
bamsim['madm'] = 2.678040e+00 # ADM mass (t=0) 
bamsim['jadm'] = 7.858842e+00 # ADM ang.mom. (t=0) 
bamsim['MbA'] = 1.494607e+00
bamsim['MbB'] = 1.494607e+00
bamsim['level'] = 7
bamsim['levelm'] = 4
bamsim['nxyz'] = 320
bamsim['nmxyz'] = 128
bamsim['dxyz']= 7.520000e+00
bamsim['eos']= 'ABC'

# Dump pre-release data
# ---------------------

# Create folder for CoRe pre-release
os.makedirs(bamsim['pre-release-folder'], exist_ok = True)

# Dump the metadata there
# For later convenience, dump both metadata files
# NOTE: entries not matching the CoRe metadata will be ignored
md = CoRe_md(metadata = bamsim) 
md.write(path = bamsim['pre-release-folder'],
         fname = 'metadata.txt')

bamsim['simulation_name'] = simname_short
md.update_fromdict(bamsim)
md.write(path = bamsim['pre-release-folder'],
         fname = 'metadata_main.txt',
         templ = TXT_MAIN)

# Use mwave() to generate data in CoRe format
dfiles = [os.path.split(x)[1] for x in glob.glob('{}/{}'.format(sim_folder,'Rpsi4mode??_r*.l0'))]
wm = mwaves(path = bamsim['sim-folder'], code = 'bam', filenames = dfiles, 
            mass = bamsim['mass'], f0 = bamsim['f0'],
            ignore_negative_m=True)

# Write .txt files in CoRe format 
# Here dump to file only largest radius
# NOTE: mwaves() currently assumes every extraction radius has the same
# modes. Something to be fixed. 
for (l,m) in wm.modes:
    psilm = wm.get(var='Psi4',l=l, m=m)
    psilm.write_to_txt('Psi4', bamsim['pre-release-folder'])
    hlm = wm.get(l=l, m=m)
    hlm.write_to_txt('h', bamsim['pre-release-folder'])

# Compute and write energetics
wm.energetics(bamsim['massA'], bamsim['massB'], bamsim['madm'], bamsim['jadm'], 
              path_out = bamsim['pre-release-folder'])

# Make a list of groups and files for each group
# IMPORTANT: group and file names must follow the CoRe conventions 
dfiles = {}
dfiles['energy'] = [os.path.split(x)[1] for x in glob.glob('{}/EJ_r*.txt'.format(bamsim['pre-release-folder']))]
for (l,m) in wm.modes:
    dfiles['rh_{}{}'.format(l,m)] = [os.path.split(x)[1] for x in
                                     glob.glob('{}/Rh_l{}_m{}_r*.txt'.format(bamsim['pre-release-folder'],l,m))] 
    dfiles['rpsi4_{}{}'.format(l,m)] = [os.path.split(x)[1] for x in
                                        glob.glob('{}/Rpsi4_l{}_m{}_r*.txt'.format(bamsim['pre-release-folder'],l,m))] 

# Generate the CoRe data.h5 and dump it in the pre-release folder
ch5 = CoRe_h5(bamsim['pre-release-folder']) 
ch5.create_dset(dfiles)
ch5.dump() # h5dump -n
