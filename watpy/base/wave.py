from base.utils import *
from base.units import *

class mwaves(object):
    """ 
    Class for multipolar or multiple waveform data
    -----------
    Input
    -----------
    path      : Path to the data directory
    code      : Which code/format the data are saved in (core, cactus, bam)
    filenames : List of files to be loaded
    mass      : ADM mass of the system
    f0        : Initial garvitational wave frequency of the system

    ignore_negative_m : Whether or not to load the negative m modes

    -----------
    Contains
    -----------
    * vars  : list of variables
    * modes : list of available (l, m) multipoles
    * lmode : list of available l multipoles
    * mmode : list of available m multipoles
    * radii : list of available extraction radii
    * data  : python dictionary of files loaded into the class
    """

    def __init__(self, path='./', code='core', filenames=None, 
                 mass=None, f0=None, ignore_negative_m=False):
        """
        Init info from files
        """        
        self.data  = {}
        
        self.path  = path
        self.mass  = mass
        self.f0    = f0
        self.code  = code

        self.vars  = set([])
        self.modes = set([])
        self.lmode = set([])
        self.mmode = set([])
        self.radii = set([])
        self.files = set([])
        self.dtype = set([])
   
        for fname in filenames:
            vlmr = wfile_parse_name(fname)
            if vlmr:
                var, l, m, r, tp = vlmr
                if ignore_negative_m and m < 0:
                    continue
                # overwrite r with better value if possible
                if tp == 'bam':  r = wfile_get_detrad_bam(fname)
                if tp == 'core': r = wfile_get_detrad(fname)

                self.vars.add(var)
                self.lmode.add(l)
                self.mmode.add(m)
                self.modes.add((l,m))
                self.radii.add(r)
                #self.dtype.add(tp)

                key = "%s_l%d_m%d_r%.2f" % (var, l, m, r)
                if self.data.has_key(key):
                    self.data[key].append(fname)
                else:
                    self.data[key] = [fname]

        self.vars  = sorted(list(self.vars))
        self.modes = sorted(list(self.modes))
        self.lmode = sorted(list(set([m[0] for m in self.modes])))
        self.mmode = sorted(list(set([m[1] for m in self.modes])))
        self.radii = sorted(list(self.radii))
        self.dtype = sorted(list(self.dtype))
    #

    def type(self):
        return type(self)
    #

    def get(self, var=None, l=None, m=None, r=None):
        """
        Get the multipole output for the given variable/multipole at the given
        extraction radius
        * var : if not specified it defaults to the first variable
        * l   : if not specified it defaults to 2 (or the minimum l
        if 2 is not available)
        * m   : if not specified it defaults to 2 (or the minimum m
        if 2 is not available)
        * r   : if not specified it defaults to the maximum radius
        """
        if var is None:
            var = self.vars[0]
        if l is None:
            if 2 in self.lmode:
                l = 2
            else:
                l = self.modes[0][0]
        if m is None:
            if 2 in self.mmode:
                m = 2
            else:
                m = self.modes[0][1]
        if r is None:
            r = self.radii[-1]
        key = "%s_l%d_m%d_r%.2f" % (var, l, m, r)
        #return np.loadtxt(self.data[key])
        return wave(self.path, self.code, self.data[key][0],
                    self.mass, self.f0)
    #
    def energetics(self, m1, m2, madm, jadm, 
                   radius=None, txt_out=None):
        h     = {}
        h_dot = {}
        if radius is None: radius = self.radii[-1]
        for lm in self.modes:
            h[lm]     = self.get(l=lm[0], m=lm[1], r=radius)
            h_dot[lm] = num.diff1(h[lm].time, h[lm].h)
        #
        t = h[lm].time
        self.e, self.edot, self.j, self.jdot = gwu.waveform2energetics(h, h_dot, t, 
                                                            self.modes, self.mmode)

        self.eb   = (madm - self.e - m1 -m2) / (m1*m2/(m1+m2))
        self.jorb = (jadm - self.j) / (m1*m2) 

        if txt_out:
            headstr  = "# r=%e\n # M=%e\n " % (radius, self.mass)
            headstr += "# J_orb:0 E_b:1 u/M:2 E_rad:3 J_rad:4 t:5"

            data = np.c_[self.jorb, self.eb, h[(2,2)].time_ret()/self.mass,
                         self.e, self.j, h[(2,2)].time]
            fname = "EJ_r%05d.txt" % int(radius)

            np.savetxt(fname, data, header=headstr)
        #
    #    
#

class wave(object):
    """ 
    Class describing discrete 1d wave functions 
    
    -----------
    Input
    -----------
    path      : Path to the data directory
    code      : Which code/format the data are saved in (core, cactus, bam)
    filenames : List of files to be loaded
    mass      : ADM mass of the system
    f0        : Initial garvitational wave frequency of the system

    ignore_negative_m : Whether or not to load the negative m modes

    -----------
    Contains
    -----------
    || On initialization ||
    * prop : python dictionary containing the wave properties
    || After reading data ||
    * e    : Energy
    * j    : Angular momentum
    * p4   : Psi4 scalar field (complex-valued)
    * h    : Wave strain (complex-valued)
    """
    
    def __init__(self, path='./', code='core', filename=None, 
                 mass=None, f0=None):
        """
        Initialise a waveform
        """
        self.path = path
        self.code = code
        self.prop = wave_prop_default()
        if filename is not None:
            self.prop_read_from_file(filename)
            self.prop['init.frequency'] = f0
            if mass:
                self.prop['mass']       = mass
            #
            if self.prop['var']=='EJ':
                self.readEJ(filename)
            else:
                #print "wait"
                self.readtxt(filename)
            #
        #
    #

    def type(self):
        return type(self)
    #
    
    def readEJ(self, fname):
        """
        Read waveform energetics from ASCII file (columns 0,1,2)
        ------
        Input
        -----
        fname  : Name of the file to be loaded
        """
        if self.code=='cactus':
            print( "Energetics are not a direct output in cactus simulations!")
        #
        else:
            self.time, self.e, self.j = np.loadtxt(os.path.join(self.path,fname), unpack=True, usecols=[0,1,2])
        #
    #        
    def readtxt(self, fname):
        """
        Read waveform data from ASCII file (columns 0,1,2)
        ------
        Input
        -----
        fname  : Name of the file to be loaded
        """
        if self.code=='cactus':
            self.time, re, im = thc_to_core(self.path, self.prop)
        #
        else:
            self.time, re, im = np.loadtxt(os.path.join(self.path,fname), unpack=True, usecols=[0,1,2])
        #
        
        if self.prop['var']=='Psi4':
            self.p4   = np.array(re) + 1j *np.array(im)
            self.h    = self.get_strain()
        #
        elif self.prop['var']=='Rpsi4':
            self.p4   = (np.array(re) + 1j *np.array(im))/self.prop['detector.radius']
            self.h    = self.get_strain()
        #
        else:
            self.h    = np.array(re) + 1j *np.array(im)
            rp4, ip4  = np.loadtxt(os.path.join(self.path,fname.replace('Rh', 'Rpsi4')),
                                   unpack=True, usecols=[1,2])
            self.p4   = np.array(re) + 1j *np.array(im)
        #
    #        
    def write_to_txt(self, var, path):
        """ 
        Writes waveform data (h) in ASCII file standard format (CoRe)
        ------
        Input
        -----
        var  : Which variable to write to txt (Psi4 or h)
        path : Where to save the txt files
        """
        M        = self.prop["mass"]
        R        = self.prop['detector.radius']
        headstr  = "# r=%e\n" %(self.prop["detector.radius"])
        headstr += "# M=%e\n" %(M)
        if var=='Psi4':
            headstr += "# u/M:0 RePsi4/M:1 ImPsi4/M:2 Momega:3 A/M:4 phi:5 t:6"
            data = np.c_[self.time_ret()/M, self.p4.real*R/M, self.p4.imag*R/M, M*self.phase_diff1(var),
                     self.amplitude(var)*R/M, self.phase(var), self.time]
            fname = 'Rpsi4_l%d_m%d_r%05d.txt' % (self.prop['lmode'], self.prop['mmode'], R)
        else:
            headstr += "# u/M:0 Reh/M:1 Imh/M:2 Momega:3 A/M:4 phi:5 t:6"
            data = np.c_[self.time_ret()/M, self.h.real*R/M, self.h.imag*R/M, M*self.phase_diff1(var),
                     self.amplitude(var)*R/M, self.phase(var), self.time]
            fname = 'Rh_l%d_m%d_r%05d.txt' % (self.prop['lmode'], self.prop['mmode'], R)
        
        return np.savetxt(os.path.join(path,fname), data, header=headstr)
    #
    def show(self):
        """
        Show l=2 m=2 strain and instantaneous frequency
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(2,1, sharex=True)

        ax[0].plot(self.time_ret()/self.prop['mass'], 
                   self.real()*self.prop['detector.radius']/self.prop['mass'])
        ax[1].plot(self.time_ret()/self.prop['mass'], 
                   np.abs(self.prop['mass']*self.phase_diff1()))

        ax[1].set_xlabel(r'$u\, /\, M$')
        ax[0].set_ylabel(r'$r_{ext}\, \mathcal{R} (h_{2,2})\, /\, M$')
        ax[1].set_ylabel(r'$M\, \omega$')

        ax[0].set_xlim([0, self.time_ret().max()/self.prop['mass']])

        plt.savefig('h_f_l2m2.pdf')
    #
    def prop_read_from_file(self, filename):
        """
        Read wf properties from file
        ------
        Input
        -----
        filename  : Name of the file where to read the wave properties from
        """
        fname= os.path.join(self.path,filename)
        vlmr = wfile_parse_name(fname)
        #
        if vlmr:
            var, l, m, r, tp = vlmr

            self.prop['var']             = var
            self.prop['lmode']           = l
            self.prop['mmode']           = m
            self.prop['detector.radius'] = r
        #
    #
    def prop_list(self):
        """
        Print the properties
        """
        for key, vak in self.prop.items():
            print(key+":"+val)
        #
    #
    def prop_set(self, key, val):
        """
        Set property
        ------
        Input
        -----
        key  : Which property to change
        val  : New value for the property
        """
        self.prop[key] = val
    #                         
    def prop_get(self, key):
        """
        Get property
        ------
        Input
        -----
        key  : Which property to get
        """
        return self.prop[key]
    #
    def prop_get_all(self):
        """
        Get all properties (return a dict)
        """
        return self.prop
    #
    def data_clean(self):
        """
        Cleanup data
        """
        self.time = []
        self.h    = []
        self.p4   = []
    #                         
    def amplitude(self,var):
        """
        Return amplitude
        ------
        Input
        -----
        var  : Which variable to return (psi4 or h)
        """
        if var=='psi4':
            return np.abs(self.p4)
        else:
            return np.abs(self.h)
    #
    def phase(self,var):
        """
        Return unwrapped phase
        ------
        Input
        -----
        var  : Which variable to return (psi4 or h)
        """
        if var=='psi4':
            return -np.unwrap(np.angle(self.p4))
        else:
            return -np.unwrap(np.angle(self.h))
    #
    def phase_diff1(self, var, pad=True):
        """
        Return frequency wrt to time using finite diff 2nd order
        centered (works for nonuniform time). 
        ------
        Input
        -----
        var  : Which variable to return (psi4 or h)
        pad  : Set to True to obtain an array of the same lenght as self.time.
        """
        return num.diff1(self.time,self.phase(var),pad=pad)
    #                         
    def phase_diffo(self, var, o=4):
        """
        Return frequency wrt to time using finite differencing centered of
        higher order (works with uniform time)
        ------
        Input
        -----
        var  : Which variable to return (psi4 or h)
        o    : Specify order for the finite differencing (defaults to 4)        
        """
        return num.diffo(self.time,self.phase(var), o)
    #        
###############################################################################
# These below are quite redundant and way inefficient                         #
###############################################################################                 
    def get_complex(self, var):
        """
        Return complex waveform
        ------
        Input
        -----
        var  : Which variable to return (psi4 or h)
        """
        if var=='psi4':
            return self.p4
        else:
            return self.h
    #                         
    def real(self, var):
        """
        Return real part
        ------
        Input
        -----
        var  : Which variable to return (psi4 or h)
        """
        if var=='psi4':
            return self.p4.real
        else:
            return self.h.real
    #                         
    def imag(self, var):
        """
        Return imag part
        ------
        Input
        -----
        var  : Which variable to return (psi4 or h)
        """
        if var=='psi4':
            return self.p4.imag
        else:
            return self.h.imag
    #                    
#################################################################################     
    def time_ret(self):
        """
        Retarded time based on tortoise Schwarzschild coordinate
        """
        return phu.ret_time(self.time,self.prop["detector.radius"], self.prop["mass"])
    #                         
    def data_interp1(self, timei, useu=0):
        """
        Return data interpolated on time (linear iterp)
        ------
        Input
        -----
        timei  : New time array over which to interpolate the data
        useu   : If set to True (or a positive value) assumes that time = (retarded time)/M
        """
        if useu:
            return np.interp1(timei, self.time_ret()/self.prop["mass"], self.h)
        else:
            return np.interp1(timei, self.time, self.h)
    #                         
    def data_interpN(self, timei):
        """
        Return data interpolated on time at high order
        ------
        Input
        -----
        timei  : New time array over which to interpolate the data        
        """
        return None #TODO high-order interp
    #
    def get_strain(self):
        """
        Return strain. Compute it first, if Psi4 is stored.
        """
        if self.prop['var']=='Psi4':
            return gwu.fixed_freq_int_2(self.p4, self.prop['init.frequency'], 
                        dt=self.time[1]-self.time[0])
        else:
            return self.h
        #
    #
