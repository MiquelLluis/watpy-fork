from ..utils.ioutils import *
from ..utils.coreh5 import CoRe_h5
from .metadata import CoRe_md
from ..utils.viz import mplot


# ------------------------------------------------------------------
# Main classes to manage the CoRe DB 
# ------------------------------------------------------------------


class CoRe_run():
    """
    Contains metadata (md) and data for a CoRe simulation run located
    in 'path'.

    Metadata are a CoRe_md() object 
    Data are a CoRe_h5() object
    These objects can be used to read, modify and write into the DB.
    """
    def __init__(self, path):
        self.path = path
        self.md = CoRe_md(path = self.path)
        self.data = CoRe_h5(self.path, self.md, 'data.h5')

    def type(self):
        """
        Returns the class type
        """
        return type(self)

    def write_metadata(self):
        """
        Helper for writing run's 'metadata.txt'
        """
        self.md.write(path = self.path)

    def clean_txt(self):
        """
        Removes all .txt files that are created when extracting
        waveform data from the HDF5 archive 
        Note: these .txt files should NOT be pushed to the git DB.
        """
        txt_files = [file for file in self.path if file.endswith(".txt")]
        txt_files.remove('metadata.txt')
        for file in txt_files:
            os.remove(os.path.join(self.path, file))


class CoRe_sim():
    """
    Contains a dictionary of CoRe_run() objects for a given simulation
    whose keys are the runs 'R??'
    This class mirrors the content of a CoRe git repo located in 'path'
    """
    def __init__(self, path):
        self.path   = path
        self.dbkey  = os.path.basename(path).replace('_',':')
        self.code   = self.dbkey.split(':')[0]
        self.key    = self.dbkey.split(':')[1]

        self.md = CoRe_md(path = self.path, md = "metadata_main.txt")

        self.run = {}
        self.run = self.update_runs()
        #print("Available runs: {}".format(self.run.keys()))

    def type(self):
        """
        Returns the class type
        """
        return type(self)

    def update_runs(self):
        """
        Update the CoRe_run() dict with all the 'R??' folders in 'self.path'
        """
        for r in os.listdir(self.path):
            if r[0]=='R' and len(r)==3:
                self.run[r] = CoRe_run(os.path.join(self.path, r))
        if not self.run:
            print('Found no runs ''R??'' folders in {}'.format(self.path))

    def add_run(self, path, overwrite = 0,
                dfile ='data.h5', md = 'metadata.txt'):
        """
        Add h5 and meta data in 'path' to this simulation.
        The run number is incremented. Overwriting an existing run is
        possible by explicitely give the run number to overwrite.
        The 'databse_key' and 'available_resolutions' in the metadta
        are corrected.
        """
        r = sorted(self.run.keys())
        n = len(r)
        if overwrite > 0 and overwrite < n:
            print("Overwriting run {}".format(overwrite))
            n = overwrite 
        else:
            n += 1
        r.append('R{:02d}'.format(n))
        dpath = '{}/{}'.format(self.path,r[-1]) # e.g. BAM_0001/R01
        
        # Dump the data
        if not os.path.isfile(os.path.join(path,dfile)):
            raise ValueError('File {}/{} not found'.format(path,dfile))
        os.makedirs(dpath, exist_ok=True)
        shutil.copy('{}/{}'.format(path,dfile), '{}/{}'.format(dpath,'data.h5'))

        # Dump the correct metadata
        md = CoRe_md(path = path, md = md)
        md['database_key'] = self.dbkey+':'+r[-1]
        md.write(path = dpath)

        # Update the run 
        self.run[r[-1]] = CoRe_run(dpath)
        
        # Need to update also the metadata_main.tex
        self.md.data['available_resolutions'] += ', '+r[-1]
        self.write_metadata()
        
    def del_run(self,r):
        """
        Delete a run object
        """
        if r in self.run.keys():
            del self.run[r]
            print("Deleted {} from object".format(r))
        else:
            raise ValueError("run {} does not exists".format(r))
    
    def write_metadata(self, also_runs_md=False):
        """
        Helper for writing simulation's 'metadata_main.txt' and
        optionally the 'metadata.txt' 
        """
        self.md.write(path = self.path,
                      fname = 'metadata_main.txt',
                      templ = TXT_MAIN)
        if also_runs_md:
            for r in self.run:
                r.md.write_metadata()


class CoRe_idx():
    """
    Contains the CoRe DB index 'core_database_index' as a list of
    metadata objects (dictionaries) and a list of DB keys. 
    The metadata can be modified and updated with the methods in CoRe_md() 
    """
    def __init__(self, db_path = '.', ifile='json/DB_NR.json'):
        self.path = '{}/{}'.format(db_path,'core_database_index')
        self.index = self.read(path = self.path, ifile = ifile)        
        self.dbkeys = get_val('database_key')
        self.N = len(self.index)
        
    def read(self, path = None, ifile = None):
        """
        Reads the index JSON file into a list of metadata (dictionaries)
        """
        if path == None: path = self.path
        if ifile == None: ifile = self.ifile
        dl = json.load(open(os.path.join(path, ifile)))
        if 'data' in dl.keys(): dl = dl["data"]
        index = []
        for d in dl:
            md = CoRe_md(path = self.path, md = None) # init to None
            index.append(md.update_fromdict(d['data']))
        return index

    def get_val(self, key):
        """
        Get values list for a given key
        """
        dbk = []
        for i in self.index:
            dbk.append(i[key])
        return dbk
    
    def to_json(self, fname, path = None, ifile = None):
        """
        Writes the index to a JSON file
        The index is sorted by 'database_key' before writing
        """
        if path == None: path = self.path
        if ifile == None: ifile = self.ifile
        sort_index = sorted(self.index, key=lambda k: k['database_key']) 
        with open(os.path.join(path, ifile), 'w') as f:
            json.dump({"data": sort_index}, f)

    def dbkey_new(self,code):
        """
        Generate a new DB key
        """
        self.dbkeys = get_val('database_key') # make sure this up-to-date
        code_list = [x.split(':')[0] for x in self.dbkeys]
        n = code_list.count(code)
        if n == 0:
            print("Adding first entry from new code {}".format(code))
            return '{}:{:4d}'.format(code,n)
        return '{}:{:4d}'.format(code,n+1)
            
    def add(self, code, name, md = None):
        """
        Adds an entry in the DB index.
        This creates a new DB key by incrementing the last entry
        associated to 'code'.
        Optional metadata can be passed either from a file or a
        dictionary. 
        """
        newkey = self.dbkey_new(self,code)
        newmd = CoRe_md(path = self.path, md = md)
        newmd['database_key'] = newkey
        newmd['simulation_name'] = name
        self.index.append(md)
        self.dbkeys = get_val('database_key') # make sure this up-to-date
        return newmd
        
    def show(self, key, to_float = to_float, to_file = to_file):
        """
        Show histogram of metadata available in the index
        """
        return mplot(self.index, key, to_float = to_float, to_file = to_file)

        
class CoRe_db():
    """
    Contains routines to clone and manage the CoRe database.

    CoRe_db() initialization is done by cloning a special repo:
    'core_database_index'
    that contains the DB index (essential information). 
    This information is stored in a CoRe_idx() object.

    Based on this metadata the user can 
    - clone individual CoRe DB repo, a group of them or the entire database
    - extract metadata and data from a run of a simulation
    - add or modify simulation data and metadata

    Simulations are stores as a dictionary of CoRe_sim() objects
    labelled by 'database_key'. 

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

        # Index 
        if not os.path.isdir(os.path.join(self.path,'core_database_index')):
            print("Index not found, cloning...\n")
            self.clone(protocol = prot, lfs = lfs, verbose = verbose)
        else:
            print("Index found, updating...\n")
            self.pull(lfs = lfs, verbose = verbose)

        self.idb = CoRe_idx()

        # Simulations
        self.sim = self.update_simulations()
      
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
            dbkeys = self.idb.dbkeys

        for dbk in dbkeys:
            repo = dbk.replace(':','_')
            if os.path.isdir(os.path.join(path, repo)):
                self.pull(repo = repo, lfs=lfs, verbose=verbose)
            else:
                self.clone(repo = repo, protocol = prot, lfs=lfs, verbose=verbose)

    def update_simulations(self):
        """
        Update the CoRe_sim() dict with all the folders in the DB 
        that match the index's DB keys. The latter must be updated
        before updating a simulation here! 
        """
        for k in os.listdir(self.path):
            if k in self.idb.dbkeys:
                self.sim[k] = CoRe_sim(os.path.join(self.path,k))
            else:
                print('skip {}, not a DB keys'.format(k))
        if not self.sim:
            print('Found no simulation folders in {}'.format(self.path))

    def update_simulations_from_dbkeys(self):
        """
        Update the CoRe_sim() dict with all the DB keys in 'dbkeys'
        """
        for k in self.idb.dbkeys:
            path = os.path.join(self.path,k)
            if os.path.isdir(path):
                self.sim[k] = CoRe_sim(path)
            else:
                print('Data folder {} not found'.format(path))
        if not self.sim:
            print('Found no simulation folders in {}'.format(self.path))
            
    def add_simulation(self, code, name, metadata = None):
        """
        Add a simulation. This increments the DB keys for 'code',
        creates the simulation's folder and drops the 'metadata_main.txt'. 
        Metadata for the latter can be optionally passed as file or dictionary.
        It is then possible to add runs using the CoRe_sim() 'add_run' method.
        """
        newmd = self.idb.add(code, name, metadata)
        dbkey = newmd['database_key']

        # Make dir
        path = '{}/{}'.format(self.path,dbkey)
        os.makedirs(path) #, exist_ok=True)

        # Drop the metadata_main.tex
        newmd.write(path = path,
                    fname = 'metadata_main.txt',
                    templ = TXT_MAIN)

        self.sim[dbkey] = CoRe_sim(os.path.join(self.path,dbkey))
        print('Added {}. Now you can add runs!'.format(dbkey))
        return dbkey
    
    def show(self, key, to_float, to_file = None):
        """
        Show histogram of metadata available in the DB
        """
        mdlist = []
        for s in self.sim:
            for r in s.run:
                mdlist.append(r.md.data)
        return mplot(mdlist, key, to_float = to_float, to_file = to_file)

