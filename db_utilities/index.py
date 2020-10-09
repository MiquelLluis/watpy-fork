#!/usr/bin/env python

""" Various utilities to manage the Core Database Index """


__author__      = "S.Bernuzzi"
__copyright__   = "Copyright 2017"

import os
import sys
import json
from subprocess import Popen, PIPE

def run(cmd, workdir, out, verbose=False):
    proc = Popen(cmd, cwd=workdir, stdout=PIPE,
                 stderr=PIPE, universal_newlines=True)
    
    if verbose:
        sl_out = []
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            else:
                if line is not None:
                    sys.stdout.write(line)
                    sl_out.append(line)
                #
            #
        #
        sl_out = "".join(sl_out)
    else:
        sl_out, sl_err = proc.communicate()
    #
    if type(out)==str:
        open(os.path.join(workdir, out), "w").write(out)
        return out
    #
    elif out is not None:
        return sl_out, sl_err
    #
#

class CoRe_index:
    """
    Contains routines to manage and manipulate the database index, 
    as well as 
    """
    def __init__(self, path, lfs=False, verbose=True, prot='https'):
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
        #self.hyb_dict = self.list_to_dict(self.hyb_list)
        
    #
      
    def clone(self, dbdir='core_database_index', verbose=True, lfs=False,
                protocol='https'):
        """
        Clones the git repository of the index at self.path
        """
        if lfs:
            if protocol=='ssh':
                git_repo = 'git@core-gitlfs.tpi.uni-jena.de:core_database/%s.git' % dbdir
            elif protocol=='https':
                git_repo = 'https://core-gitlfs.tpi.uni-jena.de/core_database/%s.git' % dbdir
            else:
                raise NameError("Protocol not supported!")
            #
            out, err = run(['git', 'lfs', 'clone', git_repo], self.path, True)
        #
        else:
            if protocol=='ssh':
                git_repo = 'git@core-gitlfs.tpi.uni-jena.de:core_database/%s.git' % dbdir
            elif protocol=='https':
                git_repo = 'https://core-gitlfs.tpi.uni-jena.de/core_database/%s.git' % dbdir
            else:
                raise NameError("Protocol not supported!")
            #
            out, err = run(['git', 'clone', git_repo], self.path, True)
        if verbose:
            print(out, err)
        #
    #
    
    def pull(self, dbdir='core_database_index', verbose=True, lfs=False):
        """
        Pulls changes in the git repository of the index at self.path
        """
        workdir  = os.path.join(self.path, dbdir)
        if lfs:
            out, err = run(['git', 'lfs', 'install'], workdir, True)
            out, err = run(['git', 'lfs', 'pull', 'origin', 'master'], workdir, True)
        else:
            out, err = run(['git', 'pull', 'origin', 'master'], workdir, True)
        if verbose:
            print(out, err)
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
        nr_db_json  = json.load(open(os.path.join(self.path, 'core_database_index/json/DB_NR.json')))
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