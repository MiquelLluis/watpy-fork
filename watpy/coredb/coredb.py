#!/usr/bin/env python

""" Various utilities to manage database, simulations and runs """

"""
Notes:
- Simulations' metadata are stored in dictionaries 
- The database can be accessed either as a dictionary of dictionaries
  or a list of dictionaries
"""

from ..utils.ioutils import *


#from . import h5_utils as h5u
#from . import metadata_utils as mdu
#from . import simlist_utils as slu
#from . import viz_utils as vu






class CoRe_db():
    """
    Contains routines to clone and manage the CoRe database.

    CoRe_db() initialization is done by cloning a special repo
    'core_database_index'
    that contains essential information on the database. 

    Based on this metadata the user can 
    - clone individual CoRe simulations, a group of them or the entire database
    - extract complete metadata and data from a run of a simulation
    - modify or add simulation data and metadata

    ## ...Simulations can be Class containing a list of objects each representing a simulation
    of the CoRe database as a CoRe_simulation object. Only requires 
    the path to where the CoRe Database is stored (i.e.: where the 
    'core_database_index' Project folder is).

    ----------------
    Initialization:
    ----------------
    path     : Where the CoRe DB is (or should be put).
    lfs      : If True, installs LFS in each project. 
    verbose  : If True, prints more information on screen. Might not 
               work as intended if lfs=True.
    prot     : Protocol to be used for syncronization via git. 
               Defaults to https, which is needed for git-LFS.
               
    """

    
    def __init__(self, db_path, lfs=True, verbose=True, prot='https'):

        self.path = db_path

        # Index repo
        if not os.path.isdir(os.path.join(self.path,'core_database_index')):
            print("Index not found, cloning...\n")
            self.clone(protocol = prot, lfs = lfs, verbose = verbose)
        else:
            print("Index found, updating...\n")
            self.pull(lfs = lfs, verbose = verbose)

        # Index data
        self.index = self.read_index()
        self.index_dbkey = self.dlist_to_dd(self.index, 'database_key')

        
        #self.sim_list = self.get_simulation_list()
        #self.sims     = {}
        #self.load_simulations()
      
    def type(self):
        """
        Returns the class type
        """
        return type(self)

    def clone(self, repo = 'core_database_index', protocol = 'https',
              lfs = False, verbose=True):
        """
        Clone a repo of the CoRe DB in self.path
        """
        return git_clone(self.path,
                         protocol = protocol,
                         repo = repo,
                         lfs = lfs, verbose = verbose)

    def pull(self, repo = 'core_database_index', lfs = False, verbose=True):
        """
        Pull a repo of the CoRe DB in self.path
        """
        return git_pull(self.path,
                        repo = repo,
                        lfs = lfs, verbose = verbose)

    def read_index(self, jsonfile='core_database_index/json/DB_NR.json'):
        """
        Reads the index .json file into a list of dictionaries.
        """
        index  = json.load(open(os.path.join(self.path, jsonfile)))
        return index['data']

    def find_index(self, key, val):
        """
        From the index dictionary, return a dictionary of all the
        entries that match a specific key/value
        """
        return dd_find(self.index_dbkey, key, val)

    def show_index(self, key):
        """
        Show histogram of metadata available in the index
        """
        # if key in vu.index_keys:
        #     try: 
        #         if key=='id_mass_ratio': 
        #             vu.plot_float(self.nr_dict, key, vu.labels[key])    
        #         else:
        #             float(self.nr_dict[key])
        #             vu.plot_float(self.nr_dict, key, vu.labels[key])
        #         #
        #     except:
        #         vu.plot_literal(self.nr_dict, key)
        #     #
        # else:
        #     print("Requested value not available for visualization.\nAvailable values are:")
        #     print(vu.index_keys)
    
    def sync_db(self, path = None, dbkeys = None,
                prot = 'https', lfs = False, verbose = True):
        """
        Syncronizes the CoRe DB repos specified in the list of database keys 'dbkeys'
         - If the repo is present, then it is updated (pull)with the git repository
         - Else, the repo is cloned 
        """
        if not path: 
            path = self.path
            
        if not dbkeys:
            dbkeys = self.index_dbkey

        for dbk in dbkeys:
            repo = dbk.replace(':','_')
            if os.path.isdir(os.path.join(path, repo)):
                self.pull(repo = repo, lfs=lfs, verbose=verbose)
            else:
                self.clone(repo = repo, protocol = prot, lfs=lfs, verbose=verbose)

    ###################
    
    def read_metadata(self, in_list=None, out_sims=None):
        """
        Reads metadata for all DB database keys in 'dbkeys'
        """
        if in_list==None:
            in_list = self.sim_list
        #
        if out_sims==None:
            out_sims = self.sims
        #
        for sim_id in in_list:
            loc  = sim_id['database_key'].replace(':', '_')
            path = os.path.join(self.path, loc)
            sim = CoRe_simulation(path)
            out_sims[sim.dbkey] = sim
        #
        return out_sims
    #
    def get_simulation_list(self):
        return slu.get_simlist(r'(\w+)_\d\d\d\d', self.path)
    #
    def find(self, key, value):
        """
        For a given pair (key, value), returns a subset of the database 
        containing only the entries whose metadata attribute 'key' corresponds
        to the required value.
        """
        sub_db = {}
        sub_list = slu.simlist_find(self.sim_list, key, value)
        sub_db = self.load_simulations(in_list=sub_list, out_sims=sub_db)
        return sub_db
    #
    def add_key(self, key, val):
        self.sim_list = slu.simlist_add_item(self.sim_list, key, val)
    #
    def rm_key(self, key):
        self.sim_list =  slu.simlist_remove_item(self.sim_list, key)
    #
    def rm_sim(self, sim=None, key=None):
        self.sim_list = slu.simlist_remove_sim(self.sim_list, sim, key)
        self.load_simulations()
    #
    def setup_new_run(self, new_sim, code):
        return slu.simlist_setup_new(self.sim_list, self.path, new_sim, code)
    #
#











##



class CoRe_index_old:
    """
    Contains routines to manage and manipulate the database index, 
    and visualize the distribution of basic model parameters.
    ----------------
    Initialization:
    ----------------
    path     : Where the core_database_index Project is (or should be)
    lfs      : If True, installs LFS in each Project (recommendend)
    verbose  : If True, prints more information on screen. Might not 
               work as intended if lfs=True.
    prot     : Which protocol to use for syncronization via git. 
               Defaults to https, which is needed for git-LFS.
               
    """
    def __init__(self, path, lfs=True, verbose=True, prot='https'):
        self.path = path
        if not os.path.isdir(os.path.join(self.path,'core_database_index')):
            print("Index not found, cloning...\n")
            self.clone(verbose=verbose, lfs=lfs, protocol=prot)
        else:
            print("Index found, updating...\n")
            self.pull(verbose=verbose, lfs=lfs)
        #
        self.nr_list, self.hyb_list = self.read_index()
        self.nr_dict = self.list_to_dict(self.nr_list)
        self.hyb_dict = self.list_to_dict(self.hyb_list)
        
    #
    def type(self):
        return type(self)
    # 
    def show(self, key):
        if key in vu.index_keys:
            try: 
                if key=='id_mass_ratio': 
                    vu.plot_float(self.nr_dict, key, vu.labels[key])    
                else:
                    float(self.nr_dict[key])
                    vu.plot_float(self.nr_dict, key, vu.labels[key])
                #
            except:
                vu.plot_literal(self.nr_dict, key)
            #
        else:
            print("Requested value not available for visualization.\nAvailable values are:")
            print(vu.index_keys)
        #
    #
    def clone(self, dbdir='core_database_index', verbose=True, lfs=False,
              protocol='https'):
        """
        Clones the git repository of the index at self.path
        """
        if protocol=='ssh':
            git_repo = 'git@core-gitlfs.tpi.uni-jena.de:core_database/%s.git' % dbdir
        elif protocol=='https':
            git_repo = 'https://core-gitlfs.tpi.uni-jena.de/core_database/%s.git' % dbdir
        else:
            raise NameError("Protocol not supported!")
        print('git-clone {} ...'.format(dbdir))
        if lfs:
            # 'git lfs clone' is deprecated and will not be updated
            #  with new flags from 'git clone'
            out, err = run(['git', 'lfs', 'clone',git_repo],self.path, True)
        #
        else:
            out, err = run(['git','clone', git_repo], self.path, True)
        if verbose:
            print(out, err)
        print('done!')
        #
    #
    def pull(self, dbdir='core_database_index', verbose=True, lfs=False):
        """
        Pulls changes in the git repository of the index at self.path
        """
        workdir  = os.path.join(self.path, dbdir)
        print('git-pull {} ...'.format(dbdir))
        if lfs:
            out, err = run(['git', 'lfs', 'install'], workdir, True)
            out, err = run(['git', 'lfs', 'pull', 'origin', 'master'], workdir, True)
        else:
            out, err = run(['git', 'pull', 'origin', 'master'], workdir, True)
        if verbose:
            print(out, err)
        print('done!')
        #
    #
    def sync_database(self, path=None, db_list=None, verbose=True, lfs=False,
                        prot='https'):
        """
        Syncronizes the entries specified by the db_list argument:
         - Found entries are updated with the git repository
         - Missing entries are cloned from the git repository
        """
        if not path: 
            path = self.path
        if not db_list: 
            db_list = self.nr_dict
        for sim in db_list:
            repo = sim.replace(':','_')
            if os.path.isdir(os.path.join(path, repo)):
                if lfs:
                    self.pull(dbdir=repo, verbose=verbose, lfs=lfs)
                else:
                    self.pull(dbdir=repo, verbose=verbose)
            else:
                if lfs:
                    self.clone(dbdir=repo, verbose=verbose, lfs=lfs,
                                 protocol=prot)
                else:
                    self.clone(dbdir=repo, verbose=verbose, 
                                 protocol=prot)
            #
        #
    #   
    def read_index(self):
        """
        Reads the .json file into a list of dictionaries.
        """
        nr_db_json = json.load(open(os.path.join(self.path, 'core_database_index/json/DB_NR.json')))
        hyb_db_json = json.load(open(os.path.join(self.path, 'core_database_index/json/DB_Hyb.json')))
        return nr_db_json['data'], hyb_db_json['data']
    #
    def find(self, key, value):
        """
        Returns a subset of the index with the entries
        that have the given value for the given key as 
        a python dictionary.
        """
        subset = {}
        for sim in self.nr_dict:
            entry = self.nr_dict[sim]
            if entry[key] == value:
                subset[sim] = entry
            #
        #
        return subset
    #            
    def list_to_dict(self, i_list):
        """
        Ports a list of python dictionaries into a dictionary
        where the main keys are the database_key values of the 
        single dictionaries (easier to sort).
        """
        py_dict = {}
        for entry in i_list:
            key = entry['database_key']
            py_dict[key] = entry
        #
        return py_dict
    #
#






class CoRe_database_old():
    """
    Class containing a list of objects each representing a simulation
    from the CoRe database as a CoRe_simulation object. Only requires 
    the path to where the CoRe Database is stored (i.e.: where the 
    core_database_index Project folder is).
    """
    def __init__(self, db_path):
        self.path     = db_path
        self.sim_list = self.get_simulation_list()
        self.sims     = {}
        self.load_simulations()
    #    
    def type(self):
        """
        Returns the class type
        """
        return type(self)
    #
    def show(self, key, out=None):
        """
        For a given key, checks whether it is available for visualization
        and returns the histogram plot.
        --------
        Inputs:
        --------
        key      : Database key to visualize [string]  
        out      : If not None, saves the image as 'out' 
                   (Specify format in the string) [string] 
        """
        if key in vu.database_keys:
            try: 
                float(list(self.sims.values())[0].mdata[key])
                vu.plot_float(self.sims, key, vu.labels[key], dbtype='database')
            except:
                vu.plot_literal(self.sims, key, dbtype='database')
            #
        else:
            print("Requested value not available for visualization.\nAvailable values are:")
            print(vu.database_keys)
        #
    #
    def load_simulations(self, in_list=None, out_sims=None):
        """
        Loads metadata information for all database entries in a list.
        """
        if in_list==None:
            in_list = self.sim_list
        #
        if out_sims==None:
            out_sims = self.sims
        #
        for sim_id in in_list:
            loc  = sim_id['database_key'].replace(':', '_')
            path = os.path.join(self.path, loc)
            sim = CoRe_simulation(path)
            out_sims[sim.dbkey] = sim
        #
        return out_sims
    #
    def get_simulation_list(self):
        return slu.get_simlist(r'(\w+)_\d\d\d\d', self.path)
    #
    def find(self, key, value):
        """
        For a given pair (key, value), returns a subset of the database 
        containing only the entries whose metadata attribute 'key' corresponds
        to the required value.
        """
        sub_db = {}
        sub_list = slu.simlist_find(self.sim_list, key, value)
        sub_db = self.load_simulations(in_list=sub_list, out_sims=sub_db)
        return sub_db
    #
    def add_key(self, key, val):
        self.sim_list = slu.simlist_add_item(self.sim_list, key, val)
    #
    def rm_key(self, key):
        self.sim_list =  slu.simlist_remove_item(self.sim_list, key)
    #
    def rm_sim(self, sim=None, key=None):
        self.sim_list = slu.simlist_remove_sim(self.sim_list, sim, key)
        self.load_simulations()
    #
    def setup_new_run(self, new_sim, code):
        return slu.simlist_setup_new(self.sim_list, self.path, new_sim, code)
    #
#


class CoRe_run_old():
    """
    Class that contains routines to manipulate data and 
    metadata from a single run of a given ID set.
    """
    def __init__(self, path):
        self.path  = path
        
        if os.path.isfile(os.path.join(self.path, "metadata.txt")):
            self.mdata = self.get_metadata()
        else:
            self.mdata = {}
        #
        if os.path.isfile(os.path.join(self.path,'data.h5')):
            self.dfile = h5u.h5py.File(os.path.join(self.path,'data.h5'), 'r')
        else:
            self.dfile = None
        #
        self.h5 = h5u.h5(self.path,self.mdata, self.dfile)
    #
    def type(self):
        """
        Returns the class type
        """
        return type(self)
    #
    def create_metadata(self, new_dict=None):
        """
        Creates a new metadata file for the specific run. 
        If new_dict is not set, the existing 
        metadata dictionary is used (might be empty).
        """
        if new_dict:
            mdu.metadata_write(self.path, py_dict=new_dict, 
                                filename="metadata.txt")
        else:
            mdu.metadata_write(self.path, py_dict=None, 
                                filename="metadata.txt")
        self.mdata = self.get_metadata()
        return self.mdata
    #
    def update_metadata(self, new_dict=None):
        """
        Updates the metadata file for the specific run. 
        If new_dict is not set, the existing 
        metadata dictionary is used (might be empty).
        """
        if new_dict:
            self.mdata = new_dict
            return mdu.metadata_write(self.path, 
                py_dict=self.mdata, filename="metadata.txt")
        else:
            return mdu.metadata_write(self.path, 
                py_dict=self.mdata, filename="metadata.txt")
        #
    #
    def get_metadata(self):
        return mdu.get_metadata(self.path, 
            mdata_file='metadata.txt')
    #
    def clean_txt(self):
        """
        Removes all .txt files that are created when extracting
        waveform data from the HDF5 archive (note these .txt files 
        should NEVER be pushed to the database).
        """
        txt_files = [file for file in self.path if file.endswith(".txt")]
        txt_files.remove('metadata.txt')
        for file in txt_files:
            os.remove(os.path.join(self.path, file))
        #
    #

class CoRe_simulation_old():
    """
    Class that contains routines to manipulate metadata
    as extracted from a CoRe database archive.
    """
    def __init__(self,path):
        self.path     = path
        self.runs     = {}
        self.mdata    = {}
        self.dbkey    = os.path.basename(path).replace('_',':')
        self.code     = self.dbkey.split(':')[0]
        self.nsim     = self.dbkey.split(':')[1]
        self.runs_id  = []

        if os.path.isfile(os.path.join(self.path, "metadata_main.txt")):
            self.mdata = self.get_metadata()
 
        else:
            self.runs_id = ['R01']
            print("Empty database entry!")
            r_path = os.path.join(self.path, self.runs_id[0])
            run = CoRe_run(r_path)
            self.runs['R01'] = run
        #
    #
    def type(self):
        """
        Returns the class type
        """
        return type(self)
    #
    def create_metadata(self, new_dict=None):
        """
        Creates a new metadata file for the database 
        entry. If new_dict is not set, the existing 
        metadata dictionary is used (might be empty).
        """
        if new_dict:
            mdu.metadata_write(self.path, py_dict=new_dict, 
                                filename="metadata_main.txt")
        else:
            mdu.metadata_write(self.path, py_dict=None, 
                                filename="metadata_main.txt")
        self.mdata = self.get_metadata()
        return self.mdata
    #
    def update_metadata(self, new_dict=None):
        """
        Updates the metadata file for the database 
        entry. If new_dict is not set, the existing 
        metadata dictionary is used (might be empty).
        """
        if new_dict:
            self.mdata = new_dict
            return mdu.metadata_write(self.path, 
                py_dict=self.mdata, filename="metadata_main.txt")
        else:
            return mdu.metadata_write(self.path, 
                py_dict=self.mdata, filename="metadata_main.txt")
        #
    #
    def get_metadata(self):
        self.mdata =  mdu.get_metadata(self.path)
        for ddir in os.listdir(self.path):
            if ddir[0]=='R':
                self.runs_id.append(ddir)
            #
        #
        for r in self.runs_id:
            r_path = os.path.join(self.path, r)
            run    = CoRe_run(r_path)

            self.runs[r] = run
        #
        return self.mdata
    #
#
