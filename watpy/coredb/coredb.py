from ..utils.ioutils import *
from ..utils.coreh5 import CoRe_h5
from .metadata import *
from ..utils.viz import wplot, mplot


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
        self.data = CoRe_h5(self.path, metadata = self.md)

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
        txt_files = [f for f in os.listdir(self.path) if f.endswith(".txt")]
        if 'metadata.txt' in txt_files: txt_files.remove('metadata.txt')
        for f in txt_files:
            os.remove(os.path.join(self.path, f))
        print("Removed {} files".format(len(txt_files)))


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

        self.md = CoRe_md(path = self.path, metadata = "metadata_main.txt")

        self.run = {}
        self.update_runs()
        
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
                print(' Found {}'.format(r))
        if not self.run:
            print(' Found no runs ''R??'' folders in {}'.format(self.path))

    def add_run(self, path, overwrite = 0,
                dfile ='data.h5', metadata = 'metadata.txt'):
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
        md = CoRe_md(path = path, metadata = metadata)
        md.data['database_key'] = self.dbkey+':'+r[-1]
        md.write(path = dpath)

        # Update the run 
        self.run[r[-1]] = CoRe_run(dpath)
        
        # Need to update also the metadata_main.tex
        if len(r)==1: sep = ''
        else:         sep = ', '
        self.md.data['available_runs'] += sep + r[-1]
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
        self.dbkeys = self.get_val('database_key')
        self.N = len(self.index)
        self.ifile = ifile
        
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
            index.append(CoRe_md(path = self.path, metadata = d))
        return index

    def update_from_mdlist(self, mdlist, overwrite = True):
        """
        Update the index from a list of CoRe_md() metadata objects
        (Currently only overwrite) 
        """
        self.index = mdlist
        self.dbkeys = self.get_val('database_key')
        self.N = len(self.index)        
        return
    
    def get_val(self, key):
        """
        Get values list for a given key
        """
        dbk = []
        for i in self.index:
            if(i==None):
                continue
            else:
                dbk.append(i.data[key])
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

    def to_json_tmplk(self, tmpl = TXT_MAIN, path = None, ifile = None):
        """
        As 'to_json()' but filters the output based on the keys from a template
        """
        if path == None: path = self.path
        if ifile == None: ifile = self.ifile
        keys = template_to_keys(tmpl)
        sort_index = [{key:val for key, val in ele.data.items() if key in keys} for ele in self.index]
        sort_index = sorted(sort_index, key=lambda k: k['database_key']) 
        with open(os.path.join(path, ifile), 'w') as f:
            json.dump({"data": sort_index}, f, indent=2)
            
    def dbkey_new(self,code):
        """
        Generate a new DB key
        """
        self.dbkeys = self.get_val('database_key') # make sure this up-to-date
        code_list = [x.split(':')[0] for x in self.dbkeys]
        n = code_list.count(code)
        if n == 0:
            print("Adding first entry from new code {}".format(code))
            return '{}:{:04d}'.format(code,n)
        return '{}:{:04d}'.format(code,n+1)
            
    def add(self, code, name, metadata = None):
        """
        Adds an entry in the DB index.
        This creates a new DB key by incrementing the last entry
        associated to 'code'.
        Optional metadata can be passed either from a file or a
        dictionary. 
        """
        newkey = self.dbkey_new(code)
        newmd = CoRe_md(path = self.path, metadata = metadata)
        newmd.data['database_key'] = newkey
        newmd.data['simulation_name'] = name
        self.index.append(newmd)
        self.dbkeys = self.get_val('database_key') # make sure this up-to-date
        return newmd #, newkey
        
    def show(self, key, to_float, to_file = None):
        """
        Show histogram of metadata available in the index
        """
        return mplot(self.index, key, to_float, to_file = to_file)

        
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
    def __init__(self, db_path, lfs=True, verbose=True, prot='https', ifile = 'json/DB_NR.json'):

        self.path = db_path

        # Index 
        if not os.path.isdir(os.path.join(self.path,'core_database_index')):
            print("Index not found, cloning...\n")
            self.clone(protocol = prot, lfs = lfs, verbose = verbose)
        else:
            print("Index found, updating...\n")
            self.pull(lfs = lfs, verbose = verbose)

        self.idb = CoRe_idx(db_path, ifile = ifile)

        # Simulations
        self.sim = {}
        self.update_simulations()
        if not self.sim:
            print('Found no simulation folders in {}'.format(self.path))

        
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
    
    def sync(self, path = None, dbkeys = None,
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
            
        # Now we have the data, update!
        self.update_simulations()
                
    def update_simulations(self):
        """
        Update the CoRe_sim() dict with all the folders in the DB 
        that match the index's DB keys. The latter must be updated
        before updating a simulation here! 
        """
        for k in os.listdir(self.path):
            dbk = k.replace('_',':')
            if dbk in self.idb.dbkeys:
                self.sim[dbk] = CoRe_sim(os.path.join(self.path,k))
                print('Found {}'.format(dbk))
            else:
                print('skip {}, not a DB key'.format(k))

    def update_simulations_from_dbkeys(self):
        """
        Update the CoRe_sim() dict with all the DB keys in 'dbkeys'
        """
        for dbk in self.idb.dbkeys:
            path = os.path.join(self.path,dbk.replace(':','_'))
            if os.path.isdir(path):
                self.sim[dbk] = CoRe_sim(path)
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
        newmd = self.idb.add(code, name, metadata = metadata)
        newdbkey = newmd.data['database_key']

        # Make dir
        path = '{}/{}'.format(self.path,newdbkey.replace(':','_'))
        os.makedirs(path) #, exist_ok=True) # should not exist!

        # Drop the metadata_main.tex
        newmd.write(path = path,
                    fname = 'metadata_main.txt',
                    templ = TXT_MAIN)

        self.sim[newdbkey] = CoRe_sim(os.path.join(self.path,newdbkey.replace(':','_')))
        print('Added {}. Now you can add runs!'.format(newdbkey))
        return newdbkey
    
    def show(self, key, to_float, to_file = None):
        """
        Show histogram of metadata available in the DB
        """
        mdlist = []
        for k in self.sim.keys():
            runs = self.sim[k].run
            for r in runs.keys():
                mdlist.append(runs[r].md)
        return mplot(mdlist, key, to_float = to_float, to_file = to_file)

