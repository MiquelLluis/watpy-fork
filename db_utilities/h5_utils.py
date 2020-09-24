""" HDF5 
https://www.hdfgroup.org/
https://support.hdfgroup.org/HDF5/whatishdf5.html
https://support.hdfgroup.org/HDF5/examples/intro.html
"""
import h5py
import os
import re
import numpy as np

def write_dset(filename, groupname, 
                   dsname, data, 
                   attr_names, attr_list, 
                   mode="r+"):
    """ Write HDF5 file/group/dataset """
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
    #
    if mode=="a":
        print("-> append to file:", filename)
    #
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
    #
    f.close() 
    print("done")
#

def show_h5attr(filename):
    f = h5py.File(filename,  "r")
    for item in f.attrs.keys():
        print(item)
    #
    return
#

class h5():
    """
    Subclass containing HDF5 archive manipulation
    """ 
    def __init__(self, path, mdata, dfile):
        self.path  = path
        self.mdata = mdata
        self.dfile = dfile
        if self.dfile is None:
            print("No .h5 file found!")
        #
    #

    def create(self, path=None):
        """
        Create HDF5 archive containing all gw data in self.path
        """
        #Create new file or open existing one
        if path is None: path==self.path
        fn = h5py.File(self.path+'/data.h5', 'w-')
        fn.close()
        #Loop over all available files, and add each of them as a dataset
        fn = h5py.File(self.path+'/data.h5', 'a')
        for f in os.listdir(path):
            if re.match(r'EJ*',f):
                if u'energies' not in fn.keys():
                    fn.create_group('energies')
                if f not in fn['energies'].keys():
                    data = np.loadtxt(os.path.join(path,f))
                    fn['energies'].create_dataset(name=f, data=data)
                #
            elif re.match(r'Rpsi4*',f):
                if u'rpsi4_22' not in fn.keys():
                    fn.create_group('rpsi4_22')
                if f not in fn['rpsi4_22'].keys():
                    data = np.loadtxt(os.path.join(path,f))
                    fn['rpsi4_22'].create_dataset(name=f, data=data)
                #
            elif re.match(r'Rh*',f):
                if u'rh_22' not in fn.keys():
                    fn.create_group('rh_22')
                if f not in fn['rh_22'].keys():
                    data = np.loadtxt(os.path.join(path,f))
                    fn['rh_22'].create_dataset(name=f, data=data)
                #
            #
        #            


    def extract_h(self, return_h=False):
        """
        Extract r*h_{22} from the .h5 archive into separate .txt
        files, one per saved radius. If return_h==True, it also
        returns retarded time and complex h at the farthest 
        extraction radius.
        """
        mass = float(self.mdata['id_mass'])

        for f in self.dfile['rh_22']:
            rad  = float(f[-8:-4])
            headstr  = "# r=%e\n # M=%e\n " % (rad, mass)
            headstr += "# u/M:0 Reh/M:1 Imh/M:2 Momega:3 A/M:4 phi:5 t:6"
                
            dset = self.dfile['rh_22'][f]
                
            data = np.c_[dset[:,0],dset[:,1],dset[:,2],
                        dset[:,3],dset[:,4],dset[:,5],dset[:,6]]

            np.savetxt(os.path.join(self.path,f),
                       data, header=headstr)
        #
        if return_h:
            return dset[:,0], dset[:,1] + 1j*dset[:,2]
        #
    #

    def extract_p4(self, return_p4=False):
        """
        Extract r*Psi4_{22} from the .h5 archive into separate .txt
        files, one per saved radius. If return_p4==True, it also
        returns retarded time and complex Psi4 at the farthest 
        extraction radius.
        """
        mass = float(self.mdata['id_mass'])

        for f in self.dfile['rpsi4_22']:
            rad  = float(f[-8:-4])
            headstr  = "# r=%e\n # M=%e\n " % (rad, mass)
            headstr += "# u/M:0 RePsi4/M:1 ImPsi4/M:2 Momega:3 A/M:4 phi:5 t:6"
                
            dset = self.dfile['rpsi4_22'][f]
                
            data = np.c_[dset[:,0],dset[:,1],dset[:,2],
                        dset[:,3],dset[:,4],dset[:,5],dset[:,6]]

            np.savetxt(os.path.join(self.path,f), 
                       data, header=headstr)
        #
        if return_p4:
            return dset[:,0], dset[:,1] + 1j*dset[:,2]
        #
    #


    def extract_ej(self, return_ej=False):
        """
        Extract energetics from the .h5 archive into separate .txt
        files, one per saved radius. If return_ej==True, it also
        returns retarded time, energy and angular momentum at the 
        farthest extraction radius.
        """
        mass = float(self.mdata['id_mass'])
        for f in self.dfile['energy']:
            rad  = float(f[-8:-4])
            headstr  = "# r=%e\n # M=%e\n " % (rad, mass)
            headstr += "# u/M:0 E:1 E_dot:2 J:3 J_dot:4 t:5"
                
            dset = self.dfile['energy'][f]
                
            data = np.c_[dset[:,0],dset[:,1],dset[:,2],
                        dset[:,3],dset[:,4],dset[:,5]]

            np.savetxt(os.path.join(self.path,f), 
                       data, header=headstr)
        #
        if return_ej:
            return dset[:,0], dset[:,1], dset[:,3]
        #
    #

    def extract_all(self):
        """
        Extract all data in the .h5 archive.
        """
        self.extract_h()
        self.extract_p4()
        self.extract_ej()
    #
#