#!/usr/local/bin/python

"""
HowTo, some examples on gw data manipulation
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


#-----------------------------------------------------------------------------------------------------------#
#                                       Analyze gw from the CoRe dataset                                    #
#-----------------------------------------------------------------------------------------------------------#


"""
First of all, set the path to where the CoRe database is located
"""
db_path = 'PATH/TO/DATABASE'

cdb     = CoRe_database(db_path)
"""
Now the metadata from all simulations stored at db_path is loaded
into an element of the list cdb.sims. The class contains utilities 
to manipulate the list.

If we instead want to work on a single simulation we need to call
the single simulation class as follows
"""

i   = 0 #index specifiying which simulation we want from the list

run = CoRe_simulation(os.path.join(db_path,cdb.sims[0]['database_key']))

"""
If we have never worked with this run already, we need to extract the .txt
files from the .h5 archive first.
"""

run.h5.extract_all()

"""
Now it's possible to use the other watpy tools to analyze the waveform data
and produce various plots.
"""

"""
Recover the metadata dictionary for reading data of a specific run. 
"""

run  = cdb.sims[0].runs[0]

"""
Now using the wave class we can recover both the strain and then gravitational
wave energetics (E, J and their time derivatives)
"""

ej =  wave(path=run['path'], code='core', filename='EJ_r00700.txt',
          mass=run['id_mass'], f0=run['id_gw_frequency_Hz']*HZ_CU)

gw  = wave(path=run['path'], code='core', filename='Rh_l2_m2_r00700.txt',
          mass=run['id_mass'], f0=run['id_gw_frequency_Hz']*HZ_CU)

#-----------------------------------------------------------------------------------------------------------#
#                                       Analyze gw from a THC simulation directory                          #
#-----------------------------------------------------------------------------------------------------------#

"""
Read Psi4 l=2, m=2 wave data from a THC simulation directory and save it locally as a CoRe-formatted .txt
"""
sim_path = run['path']
fname    = 'mp_Psi4_l2_m2_r600.00.asc' 
#Which variable, which mode, at which extraction radius are all extracted from the filename.
#The tool expects to find the name already in the correct format for the specified code (cactus, CoRe, BAM)
mass	 = run['mass']
f0     = run['f0']

gw =  wave(path=sim_path, code='cactus', filename=fname,
          mass=mass, f0=f0)

gw.writetxt('Psi4_l2_m2_r600.00.txt')

"""
For the same dataset, load Psi4 from a THC simulation, but plot the strain instead. 
There are two possibilities:
(a) Substitute Psi4 -> h in fname
(b) Reload Psi4 and integrate it to get the strain
"""

#Case (a)
fname = 'mp_h_l2_m2_r600.00.asc'

gw =  wave(path=sim_path, code='cactus', filename=fname,
          mass=mass, f0=f0)

#Case (b)
fname = 'mp_Psi4_l2_m2_r600.00.asc'

gw =  wave(path=sim_path, code='cactus', filename=fname,
          mass=mass, f0=f0)


"""
For the same dataset, load Psi4 for several modes at a given extraction
radius. Then plot a summary for the l=m=2 mode.
"""
files = []
lmax  = 4
for l in range(lmax+1):
    for m in range(-l,l+1):
        files.append('mp_Psi4_l%d_m%d_r600.00.asc' % (l , m)) 
    #
#

mpls = mwaves(path=path, code='cactus', filenames=files, 
              mass=mass, f0=f0, ignore_negative_m=True)

h22 = mpls.get(l=2,m=2)

h22.show()

"""
Once created the multipoles class, one can extract any available mode. 
To see which modes are available and then load one:
"""

print mpls.modes

given_l      = 3
given_m      = 2
given_radius = 400.00
given_var    = None

# If the varible is not specified, the first variable in the list of files given
# when creating the class is chosen. In this case, Psi4.

h32 = mpls.get(var=given_var, l=given_l, m=given_m, r=given_radius)

h32.show()


