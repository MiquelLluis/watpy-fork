#!/usr/local/bin/python

"""
HowTo, some examples on CoRe database manipulation
"""

"""
Import the main module, where the wave classes are stored.
Utilities are available to the user as they are imported in watpy.wave as follows:

from utils import * 
from units import * 

import gw_utils   as gwu
import num_utils  as num
import phys_utils as phu
"""

from base.wave import *
from db_utilities.dbutils import *

"""
Define the path where the CoRe database is stored and create
the database object, containing the metadata for all the runs 
in the database.
"""
db_path = 'PATH/TO/CORE/DATABASE'

cdb = CoRe_database(db_path)

"""
Now, to setup a new entry for the database we need to create
the appropriate directory tree. If the simulation is already
present, the script will aknowledge that and add the run as 
a new run of the same simulation.
"""

new_run_dir = cdb.setup_new_run('SIMULATION_NAME', 'SIMULATION_CODE')

"""
Now we need the CoRe simulation class to build the data in the 
correct format for the database submission.
"""

new_run = Core_simulation(new_run_dir)

"""
We can use the new object to create the initial metadata file
"""

new_run.create_metadata(sim_name='SIMULATION_NAME', 
			bibkey_ref='BIBKEY_REFERENCE')

"""
Now we need the actual gw data in the correct format in order 
to create the HDF5 archive (data.h5). In order to do this we 
will need the multipoles class from watpy.base and several
parameters (that will be needed to complete the metadata
file anyways later) like the masses of the NSs, the ADM mass
and angular momentum, the total mass and the initial frequency
of the gravitational waves.

Here follows an example using a THC simulation directory as
source for the gw data.
"""

"""
First we need to find all available files containing gw data
"""

# Define the simulation source directory and the run properties
simpath = 'PATH/TO/THC/SIMULATION'
m1      = 1.020
m2      = 1.856
m_adm   = 2.850
j_adm   = 7.406

# Setup the correct regular expression for the wanted files
rf = r'mp_Psi4_l\d_m\d_r(\d+).00.asc'

# Loop over all files in the first output directory to find 
# which radii and poles are available.
files = []

for f in os.listdir(simpath+'output-0000/data/'):
    if re.match(rf, f):
        files.append(f)
    #
#

# Now load the multipoles
mpls = mwaves(path=simpath, code='cactus', filenames=files, 
              mass=2.876, f0=576.*HZ_CU, ignore_negative_m=True)

# Save Rh_22, RPsi4_22 and the energetics at all available radii

for rad in mpls.radii:
    mpls.energetics(m1, m2, m_adm, j_adm, radius=rad, txt_out='yes')
    gw22 = mpls.get(l=2,m=2,r=rad)
    gw22.write_to_txt('Psi4')
    gw22.write_to_txt('h')
#

"""
We can now proceed with the creation of the HDF5 archive using 
the CoRe simulation object we previously created.
"""

new_run.h5.create(path='PATH/TO/CORE-FORMATTED/GW_DATA')

"""
We now need to update metadata.txt with the missing information.
This can be either done by editing the txt file, or by loading 
the .txt into a dictionary using new_run.get_metadata() and 
then modifying the python dictionary new_run.mdata. In the second 
case one then needs to rewrite the metadata file dumping the 
dictionary to a txt file with 
"""

new_run.update_metadata()