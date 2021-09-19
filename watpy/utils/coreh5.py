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


def write_dset(filename, groupname, 
                   dsname, data, 
                   attr_names, attr_list, 
                   mode="r+"):
    """ 
    Write HDF5 file/group/dataset 
    """
    timestamp = "T".join( str( datetime.datetime.now() ).split() )
    print(timestamp)
    # file and attributes
    f = h5py.File(filename, mode) 
    if mode=="w":
        print("-> writing file:", filename)
        f.attrs['file_name']      = filename
        f.attrs['file_created']   = timestamp
        f.attrs['HDF5_Version']   = h5py.version.hdf5_version
        f.attrs['h5py_version']   = h5py.version.version
    if mode=="a":
        print("-> append to file:", filename)
    
    f.attrs['file_last_modified'] = timestamp

    # group/dataset
    # note this is harcoded as float
    print("-> write dataset:","/"+groupname+"/"+dsname)
    dset = f.create_dataset("/"+groupname+"/"+dsname, data.shape, dtype=np.float64) 
    dset[...] = data

    # add attributes from list
    # (names/data must be same length!)
    for a,d in zip(attr_names, attr_list):
        print("-> write attribute:",a)
        dset.attrs[a] = d
    
    f.close() 
    print("done")
    

def show_h5attr(filename):
    f = h5py.File(filename,  "r")
    for item in f.attrs.keys():
        print(item)
    return


class CoRe_h5():
    """
    Class to read/write CoRe HDF5 archives
    """ 
    def __init__(self, path, mdata, dfile):
        self.path  = path
        self.mdata = mdata
        self.dfile = dfile
        if self.dfile is None:
            print("No .h5 file found!")

    def create(self, path = None):
        """
        Create HDF5 archive using .txt CoRe files under 'path'. 
        If path is not specified, search the .txt files under self.path

        Always write .h5 files to self.path
        """
        #Create new file or open existing one
        if path is None: path == self.path
        fn = h5py.File(self.path+'/data.h5', 'a')
        
        #Loop over all available files, and add each of them as a dataset
        for f in os.listdir(path):

            # check this has some chances to be CoRe data
            if '.txt' != os.path.splitext(f)[-1]: continue
            vlmr = wfile_parse_name(f)
            if vlmr == None: continue

            var,l,m,r,c = vlmr 
            if var == 'EJ':
                if u'energies' not in fn.keys():
                    fn.create_group('energies')
                if f not in fn['energies'].keys():
                    data = np.loadtxt(os.path.join(path,f))
                    fn['energies'].create_dataset(name=f, data=data)
                
            elif var == 'psi4':
                gname = 'rpsi4_{}{}'.format(l,m)
                if gname not in fn.keys():
                    fn.create_group(gname)
                if f not in fn[gname].keys():
                    data = np.loadtxt(os.path.join(path,f))
                    fn[gname].create_dataset(name=f, data=data)
                
            elif var == 'h':
                gname = 'rh_{}{}'.format(l,m)
                if gname not in fn.keys():
                    fn.create_group(gname)
                if f not in fn[gname].keys():
                    data = np.loadtxt(os.path.join(path,f))
                    fn[gname].create_dataset(name=f, data=data)
  
        print('wrote CoRe {}'.format(self.path+'/data.h5'))
 
    def read(self, var, det=None):
        """
        Read r*h_{lm} or r*Psi4_{lm} from the .h5 archive files,
        at the selected extraction radius (deafults to farthest).

        Extended from the previous version (now 'read_22') for multiples modes
        Backward compatible
        --------
        Input:
        --------
        var     : e.g. 'rh_22' for the strain, 'rpsi4_22' for the Weyl scalar
        det     : Extraction radius
        --------
        Output:
        --------
        u       : Retarded time / binary mass
        y       : Complex-valued strain (or weyl scalar)
        """
        lm = var.split('_')[1]
        l,m = lm[0], lm[1:] #TODO: this might work also m<0 modes
        radii = []
        for f in self.dfile[var]:
            radii.append(float(f[-8:-4]))
        
        if det in radii:
            rad = det
        else:
            rad   = np.array(radii).max()
        
        try:
            dset  = self.dfile[var]['Rh_l{}_m{}_r{:05d}.txt'.format(l,m,int(rad))] 
        except:
            dset  = self.dfile[var]['Rpsi4_l{}_m{}_r{:05d}.txt'.format(l,m,int(rad))] 
        
        u     = dset[:,0]
        y     = dset[:,1] + 1j*dset[:,2]
        return u, y

    def extract_strain(self, lm=[(2,2)]):
        """
        Extract r*h_{22} from the .h5 archive into separate .txt
        files, one per saved radius. 
        """
        mass = float(self.mdata['id_mass'])
        for l,m in lm:
            gname = 'rh_{}{}'.format(l,m)
            if gname not in self.dfile.keys(): continue
            for f in self.dfile[gname]:
                rad  = float(f[-8:-4])
                headstr  = "r=%e\nM=%e\n " % (rad, mass)
                headstr += "u/M:0 Reh/M:1 Imh/M:2 Redh/M:3 Imdh/M:4 Momega:5 A/M:6 phi:7 t:8"
                dset = self.dfile[gname][f]
                data = np.c_[dset[:,0],dset[:,1],dset[:,2],
                             dset[:,3],dset[:,4],dset[:,5],
                             dset[:,6],dset[:,7],dset[:,8]]
                np.savetxt(os.path.join(self.path,f),
                           data, header=headstr)
 
    def extract_psi4(self, lm=[(2,2)]):
        """
        Extract r*Psi4_{22} from the .h5 archive into separate .txt
        files, one per saved radius. 
        """
        mass = float(self.mdata['id_mass'])
        for l,m in lm:
            gname = 'rh_{}{}'.format(l,m)
            if gname not in self.dfile.keys(): continue
            for f in self.dfile[gname]:
                rad  = float(f[-8:-4])
                headstr  = "r=%e\nM=%e\n " % (rad, mass)
                dset = self.dfile[gname][f]
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

    def extract_EJ(self):
        """
        Extract energetics from the .h5 archive into separate .txt
        files, one per saved radius. 
        """
        mass = float(self.mdata['id_mass'])
        for f in self.dfile['energy']:
            rad  = float(f[-8:-4])
            headstr = "r=%e\nM=%e\n " % (rad, mass)
            dset = self.dfile['energy'][f]
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
 
    def extract_all(self):
        """
        Extract all data in the .h5 archive.
        """
        self.extract_strain()
        self.extract_psi4()
        self.extract_ej()
    
    def show(self, var, lm=(2,2), det=None):
        """
        Plot r*h_{lm}, r*Psi4_{lm} or both from the .h5 archive files,
        at the selected extraction radius (deafults to farthest).
        --------
        Input:
        --------
        var     : 'strain' or 'psi4'
        """
        if var == 'strain':
            gname =  'rh_{}{}'.format(lm[0],lm[1])
            ds = 'Rh_l{}_m{}'.format(l,m)
        elif var == 'psi4':
            gname =  'rpsi4_{}{}'.format(lm[0],lm[1])
            ds = 'Rpsi4_l{}_m{}'.format(l,m)
        else:
            raise ValueError("unknown var")
        radii = []
        for f in self.dfile[gname]:
            radii.append(float(f[-8:-4]))
        if det in radii:
            rad = det
        else:
            rad   = np.array(radii).max()

        data = self.dfile['rpsi4_22']['{}_r{:05d}.txt'.format(ds,int(rad))] 
        u = data[:,0]
        y = data[:,1] + 1j*data[:,2]
        return wplot(u,y)
