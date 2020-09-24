import os
import re
import sys
import numpy as np
import metadata_utils as mdu

""" 
ROUTINES TO MANAGE SIMULATIONS and SIMULATION LISTS
"""

def get_sim(sim_key, db_path, mdf="metadata_main.txt"):
    """ 
    Get simulation from metadata files given the 
    simulation key and the database directory (walk in)
    """
    s = []
    for root, dirs, files in os.walk(db_path + "/"):
        for name in files:
            if name == mdf:
                sdir = os.path.basename(root)
                if sdir == sim_key:
                    s         = mdu.read_txt_into_dict(os.path.join(root,name))
                    s['path'] = root 
                    print("-> Found metadata for: ", sdir)
                #
                break
            #
        #
    #
    return s
#

def get_simlist_ls(sim_key_list, db_path, mdf="metadata_main.txt"):
    """ 
    Get simulation list from metadata files given a list of 
    simulation keys and the database directory (walk in) 
    """
    sl = []
    for k in sim_key_list:
        sl.append(get_sim(k, db_path, mdf))
    #
    return sl
#

def get_simlist_re(sim_key, db_path, mdf="metadata_main.txt"):
    """ 
    Get simulation list from metadata files given a regular 
    expression as the simulation key and the database 
    directory (walk in) 
    """
    sl = []
    for root, dirs, files in os.walk(db_path + "/"):
        for name in files:
            if name == mdf:
                sdir = os.path.basename(root)
                #print sdir, name, root+name
                if re.match(sim_key, sdir):
                    sl.append(mdu.read_txt_into_dict(root + "/" + name))
                    #print "-> Found metadata for:", sdir
                #
                break
            #
        #
    #
    return sl
#

def get_simlist(sim_key, db_path, mdf="metadata_main.txt"):
    """ 
    Get simulation list from metadata files given 
    either a list of simulation keys or a
    regular expression for the simulation key and
    the database directory (wrapper) 
    """
    if type(sim_key).__name__=='list':
        sl = get_simlist_ls(sim_key, db_path)
    else:
        sl = get_simlist_re(sim_key, db_path)
    #
    return sl
#

def simlist_add_item(sl, key, val):
    """ 
    Add/modify single item in all simulations of a list, 
    return simulation list with new items from input dictionary 
    """
    skeys = sl[0].keys()
    for s, in sl:
        s[key]==val
    #
    return sl
#

def simlist_remove_item(sl, key):
    """ 
    Remove item from all simulations of a list 
    """
    skeys = sl[0].keys()
    if key in skeys:
        for s in sl:
            del s[key]
        #
    #
    return sl
#

def simlist_find(sl, key, val):
    """ 
    Find simulation(s) from simulation list, 
    return simulation (sub)-list matching the input dictionary 
    """
    ssub = []

    for s in sl:
        if s[key] == val:
            ssub.append(s)
        #
    #
    return ssub
#

def simlist_remove_sim(sl, sim=None, key=None):
    """ 
    Remove simulation from simulation list 
    (wrapper)
    """
    if sim:
        return simlist_remove_sim_(sl, sim)
    elif key:
        return simlist_remove_sim_sk(sl, key)
    else: 
        print("No simulation or simulation key selected!")
    #
#

def simlist_remove_sim_(sl, s1):
    """ 
    Remove simulation s1 from simulation list 
    """
    snew = []
    for s in sl:
        if not s == s1:
            snew.append(s)
        #
    #
    return snew
#

def simlist_remove_sim_sk(sl, sim_key):
    """ 
    Remove simulation with sim_key from simulation list 
    """
    snew = []
    for s in sl:
        if s['database_key']==sim_key:
            continue
        else:
            snew.append(s)
        #
    #
    return snew
#

def simlist_remove_dir(sl, db_path="./"):
    """ 
    Remove simulation dir(s) from simulation list 
    Deprecated (?)
    """
    for s in sl:
        # assume simdir = database_key
        print(s["database_key"][0:8])
        os.system("rm -rvf " + db_path + s["database_key"][0:8])
    #
    return None
#
def simlist_setup_new(sl, db_path, sim_name, code):
    """
    Returns the progressive simulation and run numbers
    for the 'sim_name' run perfomed with code 'code'.
    """
    runs    = []
    new_dir = None
    for sim in sl:
        if sim['simulation_name'] == sim_name:
            simnum = sim['database_key'].split(':')[1]
            runkey = sim['available_resolutions'].split(', ')[-1]
            runnum = int(runkey[1:])+1
            run_path = os.path.join(sim['database_key'].replace(':', '_'),
                                    'R%02d' % runnum)
            new_dir = os.path.join(db_path, run_path)
            os.mkdir(new_dir)
            sim['database_key'].replace('_', ':')
            print("Added run R%02d to model %s." % (runnum, sim['database_key']))
            return sim['database_key']
        #
        elif sim['database_key'].split(':')[0]==code:
            runs.append(sim['database_key'].split(':')[1])
        #
    #
    if len(runs) != 0:
        path = "%s_%04d" % (code, 
                    np.array(runs,dtype='int').max()+1)
        run_path = os.path.join(path,'R01')
        new_dir = os.path.join(db_path, run_path)
        os.mkdir(os.path.join(db_path,path))
        os.mkdir(new_dir)
        print("Created new database entry %s." % path.replace('_',':'))
        return path.replace('_', ':')
    #    
    if not new_dir:
        print("Run exists!")
        return None
    #
#