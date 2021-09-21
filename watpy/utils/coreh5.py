# HDF5 stuff

""" HDF5 
https://www.hdfgroup.org/
https://support.hdfgroup.org/HDF5/whatishdf5.html
https://support.hdfgroup.org/HDF5/examples/intro.html
"""

import h5py
import os
import os.path
import re
import numpy as np

from ..wave.wave import wfile_parse_name
from .viz import wplot


class CoRe_h5():
    """
    Class to read/write CoRe HDF5 archives
    """ 
    def __init__(self, path, mdata, dfile = 'data.h5'):
        self.path  = path
        self.mdata = mdata
        self.dfile = dfile
        if not os.path.isfile(os.path.join(path,dfile)):
            print("No .h5 file found!")

    def create_dset(self, groups_and_files, path = None, dfile = None):
        """
        Generic routine to create HDF5 archive from a list of (group,file)
        e.g. [(group1, file1),(group1,file2),(group2,file3), ... ]
        the files are text files
        """
        if path is None: path == self.path
        if not dfile: self.dfile = 'data.h5'
        with h5py.File(os.path.join(self.path,self.dfile), 'a') as fn:
            for (g,f) in groups_and_files:
                if g not in fn.keys():
                    fn.create_group(group)
                if f not in fn[g].keys():
                    data = np.loadtxt(os.path.join(path,f))
                    fn[g].create_dataset(name=f, data=data)
        return

    def read_dset(self, groups_and_dsets):
        """
        Generic routine to read HDF5 archive from a list of (group,dset)
        e.g. [(group1, dset1),(group1,dset2),(group2,dset3), ... ]
        Return a dictionary
        """
        dset = {}
        with h5py.File(os.path.join(self.path,self.dfile), 'a') as fn:
            for (g,d) in groups_and_dsets:
                if g not in fn.keys():
                    print("Group {} does not exists, skip".format(g))
                    continue
                if d not in fn[g].keys():
                    print("Dataset {} in group {} does not exists, skip".format(g,d))
                    continue
                dset[g][d] = fn[g][d][()]
        return dset

    def create(self, path = None):
        """
        Create HDF5 archive using .txt CoRe files under 'path'. 
        If path is not specified, search the .txt files under self.path
        Always write .h5 files to self.path

        This enforces the group/datasets convention in the CoRe DB.
        It is very specific and limited, use the create_dset if possible.
        """
        if path is None: path == self.path
        self.dfile = 'data.h5'
        with h5py.File(os.path.join(self.path,self.dfile), 'a') as fn:

            # Loop over all available files, add each as a dataset 
            for f in os.listdir(path):

                # check this has some chances to be CoRe data
                if '.txt' != os.path.splitext(f)[-1]: continue
                vlmr = wfile_parse_name(f)
                if vlmr == None: continue
                var,l,m,r,c = vlmr
                
                if var == 'EJ':
                    group = 'energy'
                    if group not in fn.keys():
                        fn.create_group(group)
                    if f not in fn[group].keys():
                        data = np.loadtxt(os.path.join(path,f))
                        fn['energy'].create_dataset(name=f, data=data)
                
                elif var == 'psi4':
                    group = 'rpsi4_{}{}'.format(l,m)
                    if group not in fn.keys():
                        fn.create_group(group)
                    if f not in fn[group].keys():
                        data = np.loadtxt(os.path.join(path,f))
                        fn[group].create_dataset(name=f, data=data)
                
                elif var == 'h':
                    group = 'rh_{}{}'.format(l,m)
                    if group not in fn.keys():
                        fn.create_group(group)
                    if f not in fn[group].keys():
                        data = np.loadtxt(os.path.join(path,f))
                        fn[group].create_dataset(name=f, data=data)

        print('wrote CoRe {}/{}'.format(self.path,self.dfile))

    def dump(self):
        """
        h5dump -n
        """
        with h5py.File(os.path.join(self.path,self.dfile), 'r') as f:
            f.visit(print)
        return

    def lm_from_group(self,group):
        """
        Returns l,m strings from group
        No check for failures
        """
        lm = group.split('_')[1]
        return lm[0], lm[1:]
    
    def dset_radii(self, fp, group='rh_22', det=None):
        """
        Reads extraction radii available in dset and returns the one
        corresponding to det or the largest
        """
        radii = []
        for ds in fp[group].keys(): 
             radii = np.append(radii,float(ds[-8:-4]))
        if det in radii:
            return det
        else:
            return radii.max()
    
    def read(self, group, det = None):
        """
        Read a dataset from the .h5 archive files at the selected
        extraction radius (deafults to farthest). 
        --------
        Input:
        --------
        group   : e.g. 'rh_22' for the 22-strain mode, 'rpsi4_22' for the Weyl
                  scalar, 'energy' for the energy curves etc
        det     : Extraction radius
        --------
        Output:
        --------
        dataset as numpy array

        This enforces the group/datasets convention in the CoRe DB.
        It is very specific and limited, use the create_dset if possible.
        """
        dset = None
        fn = h5py.File(os.path.join(self.path,self.dfile), 'r')
        if group not in fn.keys():
            raise ValueError("Group {} not available".format(group))
        rad = self.dset_radii(fn,group=group, det=det)
        if group.startswith('rh_'):
            l,m = self.lm_from_group(group)
            dset = fn[group]['Rh_l{}_m{}_r{:05d}.txt'.format(l,m,int(rad))] 
        elif group.startswith('rpsi4_'):
            l,m = self.lm_from_group(group)
            dset = fn[group]['Rpsi4_l{}_m{}_r{:05d}.txt'.format(l,m,int(rad))]
        elif group.startswith('EJ_'):
            dset = fn[group]['EJ__r{:05d}.txt'.format(int(rad))]
        else:
            raise ValueError("Unknown group {}".format(group))
        return np.array(dset)

    def write_strain_to_txt(self, lm=[(2,2)]):
        """
        Extract r*h_{22} from the .h5 archive into separate .txt
        files, one per saved radius. 
        """
        mass = float(self.mdata.data['id_mass'])
        with h5py.File(os.path.join(self.path,self.dfile), 'r') as fn:
            for l,m in lm:
                group = 'rh_{}{}'.format(l,m)
                if group not in fn.keys(): continue
                for f in fn[group]:
                    rad  = float(f[-8:-4])
                    headstr  = "r=%e\nM=%e\n " % (rad, mass)
                    headstr += "u/M:0 Reh/M:1 Imh/M:2 Redh/M:3 Imdh/M:4 Momega:5 A/M:6 phi:7 t:8"
                    dset = fn[group][f]
                    data = np.c_[dset[:,0],dset[:,1],dset[:,2],
                                 dset[:,3],dset[:,4],dset[:,5],
                                 dset[:,6],dset[:,7],dset[:,8]]
                    np.savetxt(os.path.join(self.path,f),
                               data, header=headstr)
 
    def write_psi4_to_txt(self, lm=[(2,2)]):
        """
        Extract r*Psi4_{22} from the .h5 archive into separate .txt
        files, one per saved radius. 
        """
        mass = float(self.mdata.data['id_mass'])
        with h5py.File(os.path.join(self.path,self.dfile), 'r') as fn:
            for l,m in lm:
                group = 'rh_{}{}'.format(l,m)
                if group not in fn.keys(): continue
                for f in fn[group]:
                    rad  = float(f[-8:-4])
                    headstr = "r=%e\nM=%e\n " % (rad, mass)
                    dset = fn[group][f]
                    try:
                        headstr += "u/M:0 RePsi4/M:1 ImPsi4/M:2 Momega:3 A/M:4 phi:5 t:6"
                        data = np.c_[dset[:,0],dset[:,1],dset[:,2],
                                     dset[:,3],dset[:,4],dset[:,5],dset[:,6]]
                    except:
                        headstr += "u/M:0 RePsi4/M:1 ImPsi4/M:2 t:4"
                        data = np.c_[dset[:,0],dset[:,1],dset[:,2],
                                     dset[:,3]]            
                    np.savetxt(os.path.join(self.path,f), 
                               data, header=headstr)

    def write_EJ_to_txt(self):
        """
        Extract energetics from the .h5 archive into separate .txt
        files, one per saved radius. 
        """
        mass = float(self.mdata.data['id_mass'])
        group = 'energy'
        with h5py.File(os.path.join(self.path,self.dfile), 'r') as fn:
            if group not in fn.keys():
                print("No group {}".format(group))
                return
            for f in fn[group]:
                rad  = float(f[-8:-4])
                headstr = "r=%e\nM=%e\n " % (rad, mass)
                dset = fn['energy'][f]
                try:
                    headstr += "J_orb:0 E_b:1 u/M:2 E_rad:3 J_rad:4 t:5"
                    data = np.c_[dset[:,0],dset[:,1],dset[:,2],
                                 dset[:,3],dset[:,4],dset[:,5]]
                except:
                    headstr += "J_orb:0 E_b:1 u/M:2 E_rad:3 J_rad:4"
                    data = np.c_[dset[:,0],dset[:,1],dset[:,2],
                                 dset[:,3],dset[:,4]]
                np.savetxt(os.path.join(self.path,f), 
                           data, header=headstr)
 
    def write_to_txt(self):
        """
        Extract all data in the .h5 archive.
        """
        self.write_strain_to_txt()
        self.write_psi4_to_txt()
        self.write_EJ_to_txt()
    
    def show(self, group, det=None):
        """
        Plot r*h_{lm}, r*Psi4_{lm} from the .h5 archive files,
        at the selected extraction radius (defaults to largest).
        --------
        Input:
        --------
        group : e.g. 'rh_22' for the strain, 'rpsi4_22', etc.
        det   : Extraction radius
        """
        with h5py.File(os.path.join(self.path,self.dfile), 'r') as fn:
            if group not in fn.keys():
                raise ValueError("Group {} not available".format(group))
            rad = self.dset_radii(fn,group=group, det=det)
            if group.startswith('rh_'):
                l,m = self.lm_from_group(group)
                dset = fn[group]['Rh_l{}_m{}_r{:05d}.txt'.format(l,m,int(rad))] 
            elif group.startswith('rpsi4_'):
                l,m = self.lm_from_group(group)
                dset = fn[group]['Rpsi4_l{}_m{}_r{:05d}.txt'.format(l,m,int(rad))]
            else:
                raise ValueError("Group {} is now a waveform".format(group))
            x = dset[:,0]
            y = dset[:,1] + 1j*dset[:,2]
        return wplot(x,y)
