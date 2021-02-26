#!/usr/bin/env python

""" Various utilities to manage database, simulations and runs """

"""
Notes:
- Simulations' metadata are stored in dictionaries 
- The database can be accessed either as a dictionary of dictionaries
  or a list of dictionaries
"""

__author__      = "S.Bernuzzi"
__copyright__   = "Copyright 2017"

import numpy as np
import datetime
import os, sys
import re

from . import h5_utils as h5u
from . import metadata_utils as mdu
from . import simlist_utils as slu
from . import viz_utils as vu


class CoRe_database():
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
        return  slu.simlist_setup_new(self.sim_list, self.path, new_sim, code)
    #
#

class CoRe_run():
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
        self.h5    = h5u.h5(self.path,self.mdata, self.dfile)
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

class CoRe_simulation():
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
