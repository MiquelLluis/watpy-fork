from ..utils.ioutils import *
import collections
from string import Template


# ------------------------------------------------------------------
# CoRe metadata : fields and short description
# ------------------------------------------------------------------


MDKEYS = {
    'database_key': 'A string like BAM:0001:R01 or THC:0013:R02 that identifies the simulation by the code employed for the evolution and a unique progressive number in the CoRe DB. The first part of the string corresponds to the repository name, like `BAM:0001` or `THC:0013`, and appears in the summary `metadata_main.txt`. The full string includes the different runs (different resolutions, grid setups, hydro scheme, etc.) and appears in the `metadata.txt` inside each run folder',
    #
    'available_runs': 'This is the list of runs (different resolutions, grid setups, hydro scheme, etc.) available for a given simulation, e.g. R01, R02, R03, etc. Note that with "simulation" here we indicate the  set of runs of a given physical setup, i.e. of the same initial data and with the same physical assumptions (e.g. description of matter fields)',
    #
    'simulation_name': 'A string that identifies the simulated binary. The convention used so far is `<EOS>_<mass1>_<mass2>_<spin1z>_<spin2z>_<initial_frequency>_<setup_details>` formatted as e.g. `2B_1.350_1.350_0.00_0.00_0.038_0.186`. Similarly to the database_key, the first part of this string common to all runs of a simulation appears in the summary `metadata_main.txt`, While the full string appears in the `metadata.txt` inside each run folder',
    #
    'binary_type': 'Type of binary: BBH, BNS, or BHNS',
    #
    'reference_bibkeys': 'BibTeX code(s) from HEP-SPIRES referrring to the publication of the simulation.', 
    #
    'id_code': 'Initial data: Code employed for generating initial data',
    #
    'id_type': 'Initial data: Assumptions employed in the initial data contruction, e.g. Irrotational', 
    #
    'id_mass': 'Initial data: Binary''s gravitational mass (solar masses)',
    #
    'id_rest_mass': 'Initial data: Binary''s rest-mass (solar masses)',
    #
    'id_mass_ratio': 'Initial data: Binary''s mass ratio', 
    #
    'id_ADM_mass': 'Initial data: ADM mass (solar masses)',
    #
    'id_ADM_angularmomentum': 'Initial data: ADM angular momentum (c=G=Msun=1 units)',
    #
    'id_gw_frequency_Hz': 'Initial data: initial GW frequency (Hz)', 
    #
    'id_gw_frequency_Momega22': 'Initial data: Mass-rescaled initial GW frequency (c=G=Msun=1 units)', 
    #
    'id_eos': 'Initial data: EOS employed for the matter',
    #
    'id_kappa2T': 'Initial data: tidal coupling constant',
    #
    'id_Lambda': 'Initial data: reduced tidal parameters (this is really $\tilde{\Lambda}$)',
    #
    'id_eccentricity': 'Initial data: measured eccentricity.',
    #
    'id_mass_starA': 'Initial data: Gravitational (TOV) mass of star A (solar masses)',
    #
    'id_rest_mass_starA': 'Initial data: Rest-mass of star A (solar masses)',
    #
    'id_spin_starA': 'Initial data: components of spin vector of star A',
    #
    'id_LoveNum_kell_starA': 'Initial data: Gravitoelectric Love numbers for star A and for ell=2,3,4',
    #
    'id_Lambdaell_starA': 'Initial data: tidal polarizability parameters for star A and for ell=2,3,4',
    #
    'id_mass_starB': 'Initial data: Gravitational (TOV) mass of star B (solar masses)', 
    #
    'id_rest_mass_starB': 'Initial data: Rest-mass of star B (solar masses)',
    #
    'id_spin_starB': 'Initial data: components of spin vector of star B',
    #
    'id_LoveNum_kell_starB': 'Initial data: Gravitoelectric Love numbers for star B and for ell=2,3,4', 
    #
    'id_Lambdaell_starB': 'Initial data: tidal polarizability parameters for star B and for ell=2,3,4',
    #
    'evolution_code': 'Code employed for the evolution of initial data, e.g. BAM, THC, etc',
    #
    'grid_refinement_levels': 'Number of AMR refinement levels',
    #
    'grid_refinement_levels_moving': 'Number of moving AMR refinement levels',
    #
    'grid_refinement_levels_npoints': 'Grid points per direction (approximate) in non-moving refinement levels',
    #
    'grid_refinement_levels_moving_npoints': 'Grid point per direction (approximate) i moving refinement levels',
    #
    'grid_spacing_min': 'AMR minimum grid spacing (approximate)',
    #
    'grid_symmetries': 'Symmetries imposed to the grid',
    #
    'grid_shells': 'Spherical patches for wave zone/wave extraction',
    #
    'grid_shells_radial_npoints': 'Number of radial points in spherical patches',
    #
    'grid_shells_angular_npoints': 'Number of angular points in spherical patches',
    #
    'grid_conservative_amr': 'Tells if a refluxing scheme was employed in the simulations',
    #
    'subgrid_model': 'Subgrid model: None, visL5, visL10, or visK',
    #
    'metric_scheme': 'Formulation employed for the metric field, e.g. Z4c, BSSN, etc',
    #
    'metric_boundary_conditions': 'Boundary conditions for the metric fields',
    #
    'hydro_flux': 'Numerical flux employed in the hydrodynamics scheme',
    #
    'hydro_reconstruction': 'Reconstruction method employed in the hydrodynamics',
    #
    'hydro_atmosphere_level': 'Atmosphere value of the rest-mass density (c=G=Msun=1 units)',
    #
    'hydro_atmosphere_factor': 'Atmosphere is set when rest-mass density drops below the atmosphere level times this factor',
    #
    'number_of_orbits': 'Number of orbits',
    #
    'evolution_mol_scheme': 'Time integrator used in the method of line scheme',
    #
    'eos_evolution_Gamma_thermal': 'EOS employed in the evolution or value of the adiabatic exponent for the thermal pressure component',
    #
    'neutrino_scheme': 'Neutrino scheme: None, Leakage, or M0',
    #
    'id_gw_NR_frequency_Hz': 'Initial frequency of the waveform in Herz',
    #
    'Hybrid_window_freq_Hz': 'Frequency window for the hrybrid part of the waveform in Herz',
    #
    'TEOB_Lambda_starA': 'Tidal deformability of star A for TEOB waveform',
    #
    'TEOB_Lambda_starB': 'Tidal deformability of star B for TEOB waveform',
    #
    'TEOB_version': 'version of TEOBResumS used',
    #
    'NR_simulation_key': 'database_key of the simulation used, identifying it by the code employed for the evolution, e.g. BAM:0013:R02',
    }

MDKEYS = collections.OrderedDict(MDKEYS)


# ------------------------------------------------------------------
# Templates for CoRe medata*.txt
# ------------------------------------------------------------------


TXT_HEAD="""\
database_key            = ${database_key}
"""

TXT_SUBHEAD1="""\
available_runs          = ${available_runs}
"""

TXT_SUBHEAD2="""\
simulation_name         = ${simulation_name}
binary_type             = ${binary_type}
reference_bibkeys       = ${reference_bibkeys}
"""

TXT_ID="""\
# -------------------------------
# Initial data (ID)
# -------------------------------
id_code                     = ${id_code}
id_type                     = ${id_type}
id_mass                     = ${id_mass} 
id_rest_mass                = ${id_rest_mass}
id_mass_ratio               = ${id_mass_ratio}
id_ADM_mass                 = ${id_ADM_mass}
id_ADM_angularmomentum      = ${id_ADM_angularmomentum}
id_gw_frequency_Hz          = ${id_gw_frequency_Hz}
id_gw_frequency_Momega22    = ${id_gw_frequency_Momega22}
id_eos                      = ${id_eos}
id_kappa2T                  = ${id_kappa2T}
id_Lambda                   = ${id_Lambda}
id_eccentricity             = ${id_eccentricity}

id_mass_starA               = ${id_mass_starA}
id_rest_mass_starA          = ${id_rest_mass_starA}
id_spin_starA               = ${id_spin_starA}
id_LoveNum_kell_starA       = ${id_LoveNum_kell_starA}
id_Lambdaell_starA          = ${id_Lambdaell_starA}
id_mass_starB               = ${id_mass_starB}
id_rest_mass_starB          = ${id_rest_mass_starB}
id_spin_starB               = ${id_spin_starB}
id_LoveNum_kell_starB       = ${id_LoveNum_kell_starB}
id_Lambdaell_starB          = ${id_Lambdaell_starB}
"""
 
TXT_EV="""\
# -------------------------------
# Evolution
# -------------------------------
evolution_code                        = ${evolution_code}
grid_refinement_levels                = ${grid_refinement_levels}
grid_refinement_levels_moving         = ${grid_refinement_levels_moving}
grid_refinement_levels_npoints        = ${grid_refinement_levels_npoints}
grid_refinement_levels_moving_npoints = ${grid_refinement_levels_moving_npoints}
grid_spacing_min                      = ${grid_spacing_min}
grid_symmetries                       = ${grid_symmetries}
grid_shells                           = ${grid_shells}
grid_shells_radial_npoints            = ${grid_shells_radial_npoints}
grid_shells_angular_npoints           = ${grid_shells_angular_npoints}
grid_conservative_amr                 = ${grid_conservative_amr}
subgrid_model                         = ${subgrid_model}
metric_scheme                         = ${metric_scheme}
metric_boundary_conditions            = ${metric_boundary_conditions}
hydro_flux                            = ${hydro_flux}
hydro_reconstruction                  = ${hydro_reconstruction}
hydro_atmosphere_level                = ${hydro_atmosphere_level}
hydro_atmosphere_factor               = ${hydro_atmosphere_factor}
number_of_orbits                      = ${number_of_orbits}
evolution_mol_scheme                  = ${evolution_mol_scheme}
eos_evolution_Gamma_thermal           = ${eos_evolution_Gamma_thermal}
neutrino_scheme                       = ${neutrino_scheme}
"""

TXT_H="""\
# -------------------------------
# Hybrid
# -------------------------------
id_gw_NR_frequency_Hz                 = ${id_gw_NR_frequency_Hz}
Hybrid_window_freq_Hz                 = ${Hybrid_window_freq_Hz}
TEOB_Lambda_starA                     = ${TEOB_Lambda_starA}
TEOB_Lambda_starB                     = ${TEOB_Lambda_starB}
TEOB_version                          = ${TEOB_version}
NR_simulation_key                     = ${NR_simulation_key}
"""

TXT_MAIN = TXT_HEAD + TXT_SUBHEAD1 + TXT_SUBHEAD2 + TXT_ID
TXT = TXT_HEAD + TXT_SUBHEAD2 + TXT_ID + TXT_EV
TXT_HYB = TXT_MAIN + TXT_H


# ------------------------------------------------------------------
# Metadata class
# ------------------------------------------------------------------


class CoRe_md():
    """
    Class for managing CoRe DB metdata (md)
    """
    def __init__(self, path ='.', metadata = "metadata.txt"):
        self.path = path
        self.data = self.init_core_md()
        if isinstance(metadata, str):
            if os.path.isfile(os.path.join(path,metadata)):
                self.update_fromfile(os.path.join(path,metadata))
            else:
                print('File {} not found'.format(metadata))
        elif isinstance(metadata, dict):
            self.update_fromdict(metadata)
        else:
            print("{} is neither a file nor a dict. Metadata is empty".format(metadata))
                
    def info(self):
        """
        Print info on CoRe metadata
        """
        print('\n *** CoRe DB METADATA ***\n')
        for key, val in MDKEYS.items():
            print('{} : {}.\n'.format(key,val))

    def init_core_md(self):
        """
        Initialize CoRe md with all the keys
        """
        return dict.fromkeys(MDKEYS.keys())
        
    def read_fromfile(self,fname):
        """
        Read md from a file 
        """
        dat = {}
        if os.path.isfile(fname):        
            with open(fname,'r') as f:
                lines = f.readlines()
                for line in lines:
                    kv = line.split('=')
                    if len(kv)>1:
                        dat[kv[0].strip()] = kv[1].strip()
        else:
            print("File {} not found. Metadata is empty".format(fname))
        return dat

    def update_fromfile(self,fname):
        """
        Update md from a file
        """
        self.data.update(self.read_fromfile(fname))

    def update_fromdict(self,dat):
        """
        Update metadata from a dict
        """
        self.data.update(dat)

    def add(self,key,val = None):
        self.data[key] = val
        
    def del_key(self,key):
        del self.data[key]

    def remove_keys_None_vals(self):
        return {k: v for k, v in self.data.items() if v is not None}

    def substitute_None_vals(self):
        return {k: v if v not in [None,'None'] else '' for k, v in self.data.items()}
    
    def write(self, path = '.',
              fname = 'metadata.txt',
              templ = TXT):
        """
        Write metadata to file
        """
        d = self.substitute_None_vals()
        t = Template(templ)
        s = t.safe_substitute(**d)
        s = remove_template_missed_keys(s) 
        open(os.path.join(path,fname), "w").write(s)
        print('Wrote {}'.format(os.path.join(path,fname)))
