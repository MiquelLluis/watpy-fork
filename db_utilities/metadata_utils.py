import csv
import json
import os
import argparse

main_keys = ['database_key', 'simulation_name', 'reference_bibkeys', 
            'id_code', 'id_type', 'id_mass', 'id_rest_mass', 'id_mass_ratio', 
            'id_ADM_mass', 'id_ADM_angularmomentum', 'id_gw_frequency_Hz', 
            'id_gw_frequency_Momega22', 'id_eos', 'id_kappa2T', 'id_Lambda',
            'id_mass_starA', 'id_rest_mass_starA', 'id_spin_starA', 
            'id_LoveNum_kell_starA', 'id_Lambdaell_starA', 'id_mass_starB', 
            'id_rest_mass_starB', 'id_spin_starB', 'id_LoveNum_kell_starB', 
            'id_Lambdaell_starB', 'id_eccentricity']
keys = ['database_key', 'simulation_name', 'available_resolutions', 'reference_bibkeys', 
            'id_code', 'id_type', 'id_mass', 'id_rest_mass', 'id_mass_ratio', 
            'id_ADM_mass', 'id_ADM_angularmomentum', 'id_gw_frequency_Hz', 
            'id_gw_frequency_Momega22', 'id_eos', 'id_kappa2T', 'id_Lambda',
            'id_mass_starA', 'id_rest_mass_starA', 'id_spin_starA', 
            'id_LoveNum_kell_starA', 'id_Lambdaell_starA', 'id_mass_starB', 
            'id_rest_mass_starB', 'id_spin_starB', 'id_LoveNum_kell_starB', 
            'id_Lambdaell_starB', 'id_eccentricity', 'evolution_code','grid_refinement_levels', 'grid_refinement_levels_moving', 'grid_refinement_levels_npoints',
        'grid_refinement_levels_moving_npoints', 'grid_spacing_min', 'grid_symmetries', 'grid_shells',
        'grid_shells_radial_npoints', 'grid_shells_angular_npoints', 'grid_conservative_amr', 'metric_scheme',
        'metric_boundary_conditions', 'hydro_flux', 'hydro_reconstruction', 'hydro_atmosphere_level',
        'hydro_atmosphere_factor', 'number_of_orbits', 'evolution_mol_scheme', 'eos_evolution_Gamma_thermal']


def get_metadata(path, mdata_file='metadata_main.txt'):
    """
    Reads the metadata.txt file at the specified path 
    into a python dictionary 
    """
    mdata = {}
    mdpath = os.path.join(path,mdata_file)
    if os.path.isfile(mdpath):        
        with open(mdpath,'r') as f:
            lines = f.readlines()
            for line in lines:
                lst = line.split('=')
                if len(lst)>1:
                    mdata[lst[0].strip()] = lst[1].strip()
                #
            #
        #
    else:
        print("No metadata available for this simulation!")
    #
    return mdata
#

#---------------------------------------------------------------------------#
#                                    CSV                                    #
#---------------------------------------------------------------------------#

def read_csv_into_dict(filename):
    """ 
    Read a CSV file into a python dictionary
    """
    data = [] 
    with open(filename) as f:
        reader = csv.DictReader(f, delimiter=',')
        for line in reader:
            data.append(line)
        #
    #
    return data
#

def write_dict_into_csv(filename, fieldnames, data):
    """ 
    Writes a python dictionary into a CSV file 
    """
    with open(filename, "wb") as f:
        writer = csv.DictWriter(f, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        #
    #
#

#---------------------------------------------------------------------------#
#                                    JSON                                   #
#---------------------------------------------------------------------------#

def write_dict_into_json(filename, d):
    """ 
    Write python dictionary to JSON file 
    """
    with open(filename, 'w') as f:
        json.dump(d, f)
    return 
#

def read_json_into_dict(filename):
    """ 
    Read JSON file into a python dictionary 
    """
    print("fixme - not working") # do not know why
    return json.load(open(filename))
#


#---------------------------------------------------------------------------#
#                                    TXT                                    #
#---------------------------------------------------------------------------#

def read_txt_header(filename, comm_char='#'):
    """ Read TXT file header lines into list """
    h = []
    with open(filename) as data:
        for line in data:
            if line[0]==comm_char:
                h.append(line[1::].strip())
            #
        #
    #
    return h
#


def read_txt_into_dict(filename, sep_char='=', comm_char='#'):
    """ 
    Read a TXT file with lines 'parameter = value', return a dict 
    """
    d = dict()
    with open(filename) as data:
        for line in data:
            if line[0]==comm_char:
                continue
            #
            if sep_char in line:
                key,value = line.split(sep_char, 1)
                d[key.strip()] = value.strip()
            #
            else:
                pass # skip empty/bad lines
            #
        #
    #
    return d
#

def write_dict_into_txt(d, filename, sep_char='='):
    """ 
    Write dict into a TXT file with lines 'parameter = value' 
    """
    with open(filename, 'w') as f:
        for key, value in d.items():
            f.write('%s = %s\n' % (key, value))
        #
    #
    return None
#

#---------------------------------------------------------------------------#
#                         GENERAL METADATA ROUTINES                         #
#---------------------------------------------------------------------------#

def ind_match (match, lis):
    """
    Return the index of match in list lis
    """
    return [index for index, value in enumerate(lis) if value == match][0]
#
    
def write_ks_lines (spec_keys, s, file, format = '%-40s\t=\t %s\n'):
    """
    Write some lines in metadatafile_write having identical pattern
    """
    keys= s.keys()
    for j in spec_keys:
        if keys.__contains__(j):
            file.write(format % (j, s[j]))
        else:
            pass
        #
    #
    return None
#

def metadatafile_write(path='./', db_key=None, sim_name=None, code=None,
                        ref_bibk=None, ecc=False, main=False, filename="metadata.txt"):
    """ 
    Create metadata.txt for a given simulation
    """
    #keys = s.keys()
    keys       = []
    av_res = []
    res = ''
    if main:
        first_keys = ['database_key', 'available_resolutions', 'simulation_name', 'reference_bibkeys']
        for ddr in os.listdir(path):
            if ddr[0]=='R' and len(ddr)==3:
                av_res.append(ddr)
            #
        #
    #
        for r in av_res:
            if len(res)==0:
                res = r
            else:
                res = res + ', '+r
            #
        #
    else :
        first_keys = ['database_key', 'simulation_name', 'reference_bibkeys']
    #
    keys.extend(first_keys)

    id_key_binary = ['id_code', 'id_type', 'id_mass', 'id_rest_mass', 'id_mass_ratio', 'id_ADM_mass', 'id_ADM_angularmomentum',
        'id_gw_frequency_Hz', 'id_gw_frequency_Momega22', 'id_eos', 'id_kappa2T', 'id_Lambda']

    id_key_single_stars = ['id_mass_starA', 'id_rest_mass_starA',
        'id_spin_starA', 'id_LoveNum_kell_starA', 'id_Lambdaell_starA', 'id_mass_starB', 'id_rest_mass_starB', 'id_spin_starB', 
        'id_LoveNum_kell_starB', 'id_Lambdaell_starB'] 

    if ecc:
        id_key_binary.append('id_eccentricity_3PN')
    else:
        id_key_binary.append('id_eccentricity')
    #
    keys.extend(id_key_binary)
    keys.extend(id_key_single_stars)
    
    ev_key = ['evolution_code','grid_refinement_levels', 'grid_refinement_levels_moving', 'grid_refinement_levels_npoints',
        'grid_refinement_levels_moving_npoints', 'grid_spacing_min', 'grid_symmetries', 'grid_shells',
        'grid_shells_radial_npoints', 'grid_shells_angular_npoints', 'grid_conservative_amr', 'metric_scheme',
        'metric_boundary_conditions', 'hydro_flux', 'hydro_reconstruction', 'hydro_atmosphere_level',
        'hydro_atmosphere_factor', 'number_of_orbits', 'evolution_mol_scheme', 'eos_evolution_Gamma_thermal']
    #
    keys.extend(ev_key)
    s = initialize_metadict(keys, [db_key, sim_name, ref_bibk, code, res], main)
    if not os.path.isfile(os.path.join(path,filename)):
        open(os.path.join(path,filename), 'w+')
    #

    with open(os.path.join(path,filename), 'w+') as f:

        write_ks_lines(first_keys, s, f, '%-20s\t=\t %s\n')   
        
        f.write('# -------------------------------\n')
        f.write('# Initial data (ID)\n')
        f.write('# -------------------------------\n')
        write_ks_lines(id_key_binary, s, f, '%-24s\t=\t %s\n')
        
        f.write('\n')
        
        write_ks_lines(id_key_single_stars, s, f, '%-24s\t=\t %s\n')
        if not main:
            f.write('# -------------------------------\n')
            f.write('# Evolution \n')
            f.write('# -------------------------------\n')
            write_ks_lines(ev_key, s, f, '%-46s\t=\t %s\n')
    #
    return None
#

def metadata_write(path='./', py_dict=None, filename="metadata.txt"):
    if not py_dict:
        print("Creating empty metadata file in %s..." % path)
        py_dict = {}
        for key in keys:
            py_dict[key] = None
        #
    #
    
    if filename=="metadata.txt":
        print("Woking on database run...")
        py_dict['database_key'] = path.split('/')[-2]
        s = """database_key            = {db_key}
simulation_name         = {sim_name}
reference_bibkeys       = {ref_bibkey}
# -------------------------------
# Initial data (ID)
# -------------------------------
id_code                     = {id_code}
id_type                     = {id_type}
id_mass                     = {id_mass} 
id_rest_mass                = {id_rest_mass}
id_mass_ratio               = {id_mass_ratio}
id_ADM_mass                 = {id_ADM_mass}
id_ADM_angularmomentum      = {id_ADM_angularmomentum}
id_gw_frequency_Hz          = {id_gw_frequency_Hz}
id_gw_frequency_Momega22    = {id_gw_frequency_Momega22}
id_eos                      = {id_eos}
id_kappa2T                  = {id_kappa2T}
id_Lambda                   = {id_Lambda}
id_mass_starA               = {id_mass_starA}
id_rest_mass_starA          = {id_rest_mass_starA}
id_spin_starA               = {id_spin_starA}
id_LoveNum_kell_starA       = {id_LoveNum_kell_starA}
id_Lambdaell_starA          = {id_Lambdaell_starA}
id_mass_starB               = {id_mass_starB}
id_rest_mass_starB          = {id_rest_mass_starB}
id_spin_starB               = {id_spin_starB}
id_LoveNum_kell_starB       = {id_LoveNum_kell_starB}
id_Lambdaell_starB          = {id_Lambdaell_starB}
id_eccentricity             = {id_eccentricity}
# -------------------------------
# Evolution
# -------------------------------
evolution_code                        = {evolution_code}
grid_refinement_levels                = {grid_refinement_levels}
grid_refinement_levels_moving         = {grid_refinement_levels_moving}
grid_refinement_levels_npoints        = {grid_refinement_levels_npoints}
grid_refinement_levels_moving_npoints = {grid_refinement_levels_moving_npoints}
grid_spacing_min                      = {grid_spacing_min}
grid_symmetries                       = {grid_symmetries}
grid_shells                           = {grid_shells}
grid_shells_radial_npoints            = {grid_shells_radial_npoints}
grid_shells_angular_npoints           = {grid_shells_angular_npoints}
grid_conservative_amr                 = {grid_conservative_amr}
metric_scheme                         = {metric_scheme}
metric_boundary_conditions            = {metric_boundary_conditions}
hydro_flux                            = {hydro_flux}
hydro_reconstruction                  = {hydro_reconstruction}
hydro_atmosphere_level                = {hydro_atmosphere_level}
hydro_atmosphere_factor               = {hydro_atmosphere_factor}
number_of_orbits                      = {number_of_orbits}
evolution_mol_scheme                  = {evolution_mol_scheme}
eos_evolution_Gamma_thermal           = {eos_evolution_Gamma_thermal}
""".format(
          db_key = py_dict['database_key'],
          sim_name = py_dict['simulation_name'],
          ref_bibkey = py_dict['reference_bibkeys'],
          id_code = py_dict['id_code'],
          id_type = py_dict['id_type'],
          id_mass = py_dict['id_mass'],
          id_rest_mass = py_dict['id_rest_mass'], 
          id_mass_ratio = py_dict['id_mass_ratio'], 
          id_ADM_mass = py_dict['id_ADM_mass'], 
          id_ADM_angularmomentum = py_dict['id_ADM_angularmomentum'],
          id_gw_frequency_Hz = py_dict['id_gw_frequency_Hz'], 
          id_gw_frequency_Momega22 = py_dict['id_gw_frequency_Momega22'],
          id_eos = py_dict['id_eos'],
          id_kappa2T = py_dict['id_kappa2T'], 
          id_Lambda = py_dict['id_Lambda'],
          id_mass_starA = py_dict['id_mass_starA'], 
          id_rest_mass_starA = py_dict['id_rest_mass_starA'],
          id_spin_starA = py_dict['id_spin_starA'], 
          id_LoveNum_kell_starA = py_dict['id_LoveNum_kell_starA'],
          id_Lambdaell_starA = py_dict['id_Lambdaell_starA'],
          id_mass_starB = py_dict['id_mass_starB'],
          id_rest_mass_starB = py_dict['id_rest_mass_starB'], 
          id_spin_starB = py_dict['id_spin_starB'], 
          id_LoveNum_kell_starB = py_dict['id_LoveNum_kell_starB'], 
          id_Lambdaell_starB = py_dict['id_Lambdaell_starB'],
          evolution_code = py_dict['evolution_code'],
          grid_refinement_levels = py_dict['grid_refinement_levels'],
          grid_refinement_levels_moving = py_dict['grid_refinement_levels_moving'],
          grid_refinement_levels_npoints = py_dict['grid_refinement_levels_npoints'],
          grid_refinement_levels_moving_npoints = py_dict['grid_refinement_levels_moving_npoints'],
          grid_spacing_min = py_dict['grid_spacing_min'], 
          grid_symmetries = py_dict['grid_symmetries'], 
          grid_shells = py_dict['grid_shells'],
          grid_shells_radial_npoints = py_dict['grid_shells_radial_npoints'], 
          grid_shells_angular_npoints = py_dict['grid_shells_angular_npoints'], 
          grid_conservative_amr = py_dict['grid_conservative_amr'], 
          metric_scheme = py_dict['metric_scheme'],
          metric_boundary_conditions = py_dict['metric_boundary_conditions'], 
          hydro_flux = py_dict['hydro_flux'], 
          hydro_reconstruction = py_dict['hydro_reconstruction'], 
          hydro_atmosphere_level = py_dict['hydro_atmosphere_level'],
          hydro_atmosphere_factor = py_dict['hydro_atmosphere_factor'], 
          number_of_orbits = py_dict['number_of_orbits'], 
          evolution_mol_scheme = py_dict['evolution_mol_scheme'],
          eos_evolution_Gamma_thermal = py_dict['eos_evolution_Gamma_thermal']
          )
    else:
        print("Working on database model...")
        py_dict['database_key'] = os.path.basename(path)
        if py_dict['available_resolutions'] == None:
            dir_res = []
            for ddir in os.listdir(path):
                if ddir[0]=='R' and len(ddir)==3:
                    dir_res.append(ddir)
                #
            #
            dir_res.sort()
            av_res = ''
            for r in dir_res:
                if len(av_res)==0:
                    av_res = r
                else:
                    av_res = av_res + ', '+r
                #
            #
            py_dict['available_resolutions'] = av_res
        #
        s = """database_key            = {db_key}
available_resolutions   = {av_res}
simulation_name         = {sim_name}
reference_bibkeys       = {ref_bibkey}
# -------------------------------
# Initial data (ID)
# -------------------------------
id_code                     = {id_code}
id_type                     = {id_type}
id_mass                     = {id_mass} 
id_rest_mass                = {id_rest_mass}
id_mass_ratio               = {id_mass_ratio}
id_ADM_mass                 = {id_ADM_mass}
id_ADM_angularmomentum      = {id_ADM_angularmomentum}
id_gw_frequency_Hz          = {id_gw_frequency_Hz}
id_gw_frequency_Momega22    = {id_gw_frequency_Momega22}
id_eos                      = {id_eos}
id_kappa2T                  = {id_kappa2T}
id_Lambda                   = {id_Lambda}
id_mass_starA               = {id_mass_starA}
id_rest_mass_starA          = {id_rest_mass_starA}
id_spin_starA               = {id_spin_starA}
id_LoveNum_kell_starA       = {id_LoveNum_kell_starA}
id_Lambdaell_starA          = {id_Lambdaell_starA}
id_mass_starB               = {id_mass_starB}
id_rest_mass_starB          = {id_rest_mass_starB}
id_spin_starB               = {id_spin_starB}
id_LoveNum_kell_starB       = {id_LoveNum_kell_starB}
id_Lambdaell_starB          = {id_Lambdaell_starB}
""".format(
          db_key = py_dict['database_key'],
          av_res = py_dict['available_resolutions'],
          sim_name = py_dict['simulation_name'],
          ref_bibkey = py_dict['reference_bibkeys'],
          id_code = py_dict['id_code'],
          id_type = py_dict['id_type'],
          id_mass = py_dict['id_mass'],
          id_rest_mass = py_dict['id_rest_mass'], 
          id_mass_ratio = py_dict['id_mass_ratio'], 
          id_ADM_mass = py_dict['id_ADM_mass'], 
          id_ADM_angularmomentum = py_dict['id_ADM_angularmomentum'],
          id_gw_frequency_Hz = py_dict['id_gw_frequency_Hz'], 
          id_gw_frequency_Momega22 = py_dict['id_gw_frequency_Momega22'],
          id_eos = py_dict['id_eos'],
          id_kappa2T = py_dict['id_kappa2T'], 
          id_Lambda = py_dict['id_Lambda'],
          id_mass_starA = py_dict['id_mass_starA'], 
          id_rest_mass_starA = py_dict['id_rest_mass_starA'],
          id_spin_starA = py_dict['id_spin_starA'], 
          id_LoveNum_kell_starA = py_dict['id_LoveNum_kell_starA'],
          id_Lambdaell_starA = py_dict['id_Lambdaell_starA'],
          id_mass_starB = py_dict['id_mass_starB'],
          id_rest_mass_starB = py_dict['id_rest_mass_starB'], 
          id_spin_starB = py_dict['id_spin_starB'], 
          id_LoveNum_kell_starB = py_dict['id_LoveNum_kell_starB'], 
          id_Lambdaell_starB = py_dict['id_Lambdaell_starB']
          )
    #
    open(os.path.join(path,filename), "w").write(s)
#






def initialize_metadict(keys, values, main):
    """
    Initialize an empty dict apart from the 
    initial keys.
    """
    s = {}
    for k in keys:
        s[k] = None
    #
    s['database_key']      = values[0]
    s['simulation_name']   = values[1]
    s['reference_bibkeys'] = values[2]
    s['evolution_code']    = values[3]
    if main:
        s['available_resolutions'] = values[4]
    #
    return s
#


def metadatafile_add_item(filename, s, key,val):
    """ 
    Add/modify simulation item in metadata file 
    """
    s[key]=val # change entry in s
    return metadatafile_write(s, filename)
#

def metadatafile_remove_item(filename, s, key):
    """ 
    Remove item in metadata file 
    """
    del s["key"] #  Remove entry in s
    return metadatafile_write(s, filename)
#

def metadatafile_dump_from_simlist(sl, BASE='./'):
    """ 
    Write metadatafiles from simulation list 
    """ 
    for s in sl:
        fname = BASE+s['database_key']+"/metadata.txt"
        print('-> writing:',fname)
        metadatafile_write(s,fname)
    #
    return None
#