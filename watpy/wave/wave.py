from ..utils.ioutils import *
from ..utils.num import diff1, diffo
from ..utils.viz import wplot
from .gwutils import fixed_freq_int_2, waveform2energetics, ret_time
import numpy as np


# ------------------------------------------------------------------
# Routines for waveform files
# ------------------------------------------------------------------

# Value for extraction radius at infinity
rInf = -1.

def write_headstr(radius,mass):
    if(radius==rInf):
        headstr  = "r=Infinity\nM=%e\n" % (mass)
    else:
        headstr  = "r=%e\nM=%e\n" % (radius, mass)
    return headstr

def write_key(l, m, r):
    """
    Writes key string 'l#_m#_r#'
    """
    if(r==rInf):
        key = 'l%d_m%d_rInf' % (l, m)
    else:
        key = 'l%d_m%d_r%05d' % (l, m, r)
    return key

def rinf_float_to_str(radius):
    """
    Converts detector radius (float) to string
    """
    if(radius==rInf):
        rad_str = 'Inf'
    else:
        rad_str = '%05d' % int(radius)
    return rad_str

def rinf_str_to_float(rad_str):
    """
    Converts detector radius (string) to float
    """
    opt = ['rInf','Inf','Infinity']
    if rad_str in opt:
        radius = rInf
    else:
        radius = float(rad_str)
    return radius

def wave_prop_default():
    """
    Default properties for wave
    """
    return {
        'lmode': None,
        'mmode': None,
        'mass': 1.0,
        'detector.radius': None,
        'init.frequency' : None,
        'var': None
    }

def wfile_parse_name(fname):
    """
    Parse waveform filename, return var,(l,m)-indexes, detector radius
    and data type 
    ------
    Input
    -----
    fname  : Name of the file to parse for information
    """
    t = ['bam','cactus','core','core','core-energy']
    s = [r'R(\w+)mode(\d)(\w+)_r(\d+).l(\d+)',
         r'mp_(\w+)_l(\d)_m(.\d|\d)_r(\d+\.\d\d).asc',
         r'R(\w+)_l(\d+)_m(\d+)_r(\d+).txt',
         r'R(\w+)_l(\d+)_m(\d+)_r(\w+).txt',
         r'EJ_r(\d+).txt']
    vlmr = None
    for tp, sm in zip(t,s):
        name = re.match(sm, os.path.basename(fname))
        if name is not None:
            if tp == 'core-energy':
                v    = 'EJ'
                r    = rinf_str_to_float(name.group(1))
                vlmr = (v,None,None,r,tp)
                return vlmr
            else:
                v    = name.group(1)
                l    = int(name.group(2))
                m    = negmode_bam(name.group(3))
                r    = rinf_str_to_float(name.group(4))
                vlmr = (v,l,m,r,tp)
                return vlmr
    return vlmr


# CoRe specials

def wfile_get_detrad(fname):
    """
    Get detector radius from CoRe file header
    ------
    Input
    -----
    fname  : Name of the file to parse for information
    """
    s = extract_comments(fname, '#')
    return rinf_str_to_float(s[0].split("=")[1])
              

def wfile_get_mass(fname):
    """
    Get binary mass from CoRe file header
    ------
    Input
    -----
    fname  : Name of the file to parse for information
    """
    s = extract_comments(fname, '#')
    return float(s[1].split("=")[1])


# BAM specials

def wfile_get_detrad_bam(fname):
    """
    Get radius from wf BAM file header
    '" Rpsi4:   r =     700.000000 "'
    ------
    Input
    -----
    fname  : Name of the file to parse for information
    """
    s = extract_comments(fname, '"')
    try:
        rad_str = re.findall("\d+\.\d+",s[0])[2]
    except:
        rad_str = re.findall("\w+",s[0])[2]
    return rinf_str_to_float(rad_str)

def negmode_bam(mode):
    """
    Gets the mmode considering the BAM convention
    used for negative mmodes
    """
    try:
        mod = int(mode)
    except:
        name = re.match(r'm(\d)', mode)
        mod = int(name.group(1))*(-1)
    return mod
        

# Cactus/THC specials

def cactus_to_core(path, prop):
    """
    Read data from Cactus/WhiskyTHC simulation directory,
    collate into a single file, load Psi4, evaluate h
    and rewrite it into a CoRe-formatted file.
    """
    v   = prop['var']
    l   = prop['lmode']
    m   = prop['mmode']
    r   = prop['detector.radius']

    seg_tmpl = r'output-\d\d\d\d'
    det      = float(r)

    t   = np.array([])
    var = np.array([])
    for seg in os.listdir(path):
        if re.match(seg_tmpl, seg):
            key = write_key(l,m,det)
            fpath = '/data/mp_Psi4_'+key+'.asc'
            #fpath = '/data/mp_Psi4_l%d_m%d_r%.2f.asc' % (l, m, det)
            raw   = np.loadtxt(os.path.join(path,seg+fpath))
            t     = np.append(t, raw[:,0])
            var   = np.append(var, raw[:,1]+raw[:,2]*1.0j)

    t, msk = np.unique(t, axis=0, return_index=True)
    var    = r * var[msk]
    if v=='h':
        fcut = prop['init.frequency']
        var  = fixed_freq_int_2(var, fcut, dt=t[1]-t[0])

    return t, var.real, var.imag


# ------------------------------------------------------------------
# Main classes for waveforms
# ------------------------------------------------------------------


class mwaves(object):
    """ 
    Class for multipolar or multiple waveform data
    -----------
    Input
    -----------
    path      : Path to the data directory
    code      : Which code/format the data are saved in (core, cactus, bam)
    filenames : List of files to be loaded
    mass      : Binary mass (solar masses)
    f0        : Initial gravitational wave frequency of the system (mass rescaled, geom.units)
    ignore_negative_m : Whether or not to load the negative m modes

    -----------
    Contains
    -----------
    * vars  : list of variables, ['Psi4', 'h']
    * modes : list of available (l, m) multipoles
    * lmode : list of available l multipoles
    * mmode : list of available m multipoles
    * radii : list of available extraction radii
    * data  : python dictionary of files loaded into the class

    FIXME: this assumes every radius has the same modes
    """
    def __init__(self, path='.', code='core', filenames=None, 
                 mass=None, f0=None, ignore_negative_m=False):
        """
        Init info from files
        """        
        self.data  = {}
        
        self.path  = path
        self.mass  = mass
        self.f0    = f0
        self.code  = code

        self.var  = set([])
        self.modes = set([])
        self.lmode = set([])
        self.mmode = set([])
        self.radii = set([])
        self.files = set([])
        self.dtype = set([])

        if self.code not in ['bam','cactus','core']:
            raise ValueError("unknown code {}".format(self.code))
        
        for fname in filenames:
            vlmr = wfile_parse_name(fname)
            if vlmr:
                var, l, m, r, tp = vlmr
                if ignore_negative_m and m < 0:
                    continue

                # take care of special conventions, 
                # overwrite better values if possible
                if tp == 'bam':
                    r = wfile_get_detrad_bam(os.path.join(self.path,fname))
                    if var == 'psi4': var = 'Psi4'
                if tp == 'core':
                    r = wfile_get_detrad(os.path.join(self.path,fname))
                    if var == 'psi4': var = 'Psi4'
                    
                self.var.add(var)
                self.lmode.add(l)
                self.mmode.add(m)
                self.modes.add((l,m))
                self.radii.add(r)
                #self.dtype.add(tp)

                #key = "%s_l%d_m%d_r%.2f" % (var, l, m, r)
                subkey = write_key(l,m,r)
                key = var+"_"+subkey               
                if key in self.data:
                    self.data[key].append(fname)
                else:
                    self.data[key] = [fname]

        self.var   = sorted(list(self.var))
        self.modes = sorted(list(self.modes))
        self.lmode = sorted(list(set([m[0] for m in self.modes])))
        self.mmode = sorted(list(set([m[1] for m in self.modes])))
        self.radii = sorted(list(self.radii))
        self.dtype = sorted(list(self.dtype))

    def type(self):
        return type(self)

    def get(self, var=None, l=None, m=None, r=None):
        """
        Get the multipole output for the given variable/multipole at the given
        extraction radius
        * var : if not specified it defaults to the first variable
        * l   : if not specified it defaults to 2 
        * m   : if not specified it defaults to 2 
        * r   : if not specified it defaults to the maximum radius
        """
        #FIXME: this assumes all radii have the same modes!

        if r is None:
            r = self.radii[-1]
        
        if var is None:
            var = self.var[0]

        if l is None:
            l = 2
        if l not in self.lmode:
            raise ValueError("Unknown l-index {}".format(l))
            
        if m is None:
            m = 2
        if m not in self.mmode:
            raise ValueError("Unknown m-index {}".format(m))

        #key = "%s_l%d_m%d_r%.2f" % (var, l, m, r)
        subkey = write_key(l,m,r)
        key = var+"_"+subkey
        return wave(path = self.path, code = self.code, filename = self.data[key][0],
                    mass = self.mass, f0 = self.f0)

    def energetics(self, m1, m2, madm, jadm, 
                   radii = None, path_out = None):
        """
        Compute energetics from multipolar waveform
        """
        #FIXME: this assumes all radii have the same modes!
        
        h     = {}
        h_dot = {}
        u     = {}
        if radii is None: radii = self.radii

        for rad in radii:
            
            for lm in self.modes: 
                w         = self.get(l=lm[0], m=lm[1], r=rad)
                t         = w.time
                u[lm]     = w.time_ret()
                h[lm]     = w.h
                h_dot[lm] = diff1(t, h[lm])
                        
            self.e, self.edot, self.j, self.jdot = waveform2energetics(h, h_dot, t, 
                                                                       self.modes,
                                                                       self.mmode)
            self.eb   = (madm - self.e - m1 -m2) / (m1*m2/(m1+m2))
            self.jorb = (jadm - self.j) / (m1*m2) 

            if path_out:
                headstr  = write_headstr(rad,self.mass)
                headstr += "J_orb:0 E_b:1 u/M:2 E_rad:3 J_rad:4 t:5"
                data = np.c_[self.jorb, self.eb, u[(2,2)]/self.mass,
                             self.e, self.j, t]
                rad_str = rinf_float_to_str(rad)
                fname = "EJ_r"+rad_str+".txt"
                np.savetxt('{}/{}'.format(path_out,fname), data, header=headstr)



class wave(object):
    """ 
    Class describing discrete 1d wave functions 
    
    -----------
    Input
    -----------
    path      : Path to the data directory
    code      : Waveform data format (['bam','cactus','core'])
    filenames : List of waveform files to be loaded
    mass      : Binary mass (solar masses)
    f0        : Initial gravitational wave frequency of the system (mass rescaled, geom.units)
    -----------
    Contains
    -----------
    || On initialization ||
    * prop : python dictionary containing the wave properties
    || After reading data ||
    * p4   : Psi4 scalar field (complex-valued)
    * h    : Wave strain (complex-valued)
    """
    
    def __init__(self, path='.', code='core', filename=None, 
                 mass=None, f0=None):
        """
        Initialise a waveform
        """
        self.path = path
        
        self.code = code
        if self.code not in ['bam','cactus','core']:
            raise ValueError("unknown code {}".format(self.code))

        self.prop = wave_prop_default()

        if filename is not None:
            self.prop_read_from_file(filename)
            self.prop['init.frequency'] = f0
            if mass:
                self.prop['mass'] = mass
            self.readtxt(filename)

    def type(self):
        return type(self)

    def readtxt(self, fname):
        """
        Read waveform data from ASCII file (columns 0,1,2)
        ------
        Input
        -----
        fname  : Name of the file to be loaded
        """
        self.time, re, im = np.loadtxt(os.path.join(self.path,fname),
                                       unpack=True,
                                       usecols=[0,1,2],
                                       comments=['#','"'])
        self.time, uniq = np.unique(self.time, axis=0, return_index=True)
        re, im = re[uniq], im[uniq]

        if self.prop['var'] in ['Psi4','psi4']:
            self.prop['var'] = 'Psi4'

            self.p4   = np.array(re) + 1j *np.array(im)

            # take care of special conventions
            if self.code == 'cactus':
                self.p4 *= self.prop['detector.radius']
            if self.code == 'bam':
                self.prop['detector.radius'] = wfile_get_detrad_bam(os.path.join(self.path,fname))

            self.h    = self.get_strain()

        else:
            if self.code != 'core':
                raise ValueError("Strain can be read only from CoRe data format.")
            self.h    = np.array(re) + 1j *np.array(im)
            rp4, ip4  = np.loadtxt(os.path.join(self.path,fname.replace('Rh', 'Rpsi4')),
                                   unpack=True, usecols=[1,2])
            self.p4   = np.array(re) + 1j *np.array(im)

    def write_to_txt(self, var, path):
        """ 
        Writes waveform data (h) in ASCII file standard format (CoRe)
        ------
        Input
        -----
        var  : Which variable to write to txt, ['Psi4', 'h']
        path : Where to save the txt files
        """
        M        = self.prop["mass"]
        R        = self.prop['detector.radius']
        headstr = write_headstr(R,M)
        key = write_key(self.prop['lmode'], self.prop['mmode'], R)
        if var == 'Psi4':
            headstr += "u/M:0 RePsi4/M:1 ImPsi4/M:2 Momega:3 A/M:4 phi:5 t:6"
            data = np.c_[self.time_ret()/M, self.p4.real*R/M, self.p4.imag*R/M, M*self.phase_diff1(var),
                     self.amplitude(var)*R/M, self.phase(var), self.time]
            #fname = 'Rpsi4_l%d_m%d_r%05d.txt' % (self.prop['lmode'], self.prop['mmode'], R)
            fname = 'Rpsi4_'+key+'.txt'
        elif var == 'h':
            headstr += "u/M:0 Reh/M:1 Imh/M:2 Momega:3 A/M:4 phi:5 t:6"
            data = np.c_[self.time_ret()/M, self.h.real*R/M, self.h.imag*R/M, M*self.phase_diff1(var),
                     self.amplitude(var)*R/M, self.phase(var), self.time]
            #fname = 'Rh_l%d_m%d_r%05d.txt' % (self.prop['lmode'], self.prop['mmode'], R)
            fname = 'Rh_'+key+'.txt'
        else:
            raise ValueError("var can be only 'Psi4' or 'h'")
        return np.savetxt(os.path.join(path,fname), data, header=headstr)

    def show_strain(self, to_file=None):
        """
        Show strain and instantaneous frequency
        """
        u = self.time_ret()/self.prop['mass']
        Rh = self.h /self.prop['mass']
        omega = self.prop['mass'] * self.phase_diff1()
        return wplot(u, Rh, omega=omega, to_file = to_file)

    def show_psi4(self, to_file=None):
        """
        Show Psi4 and instantaneous frequency
        """
        u = self.time_ret()/self.prop['mass']
        psi4 = self.p4 
        omega = self.prop['mass'] * self.phase_diff1(var='Psi4')
        return wplot(u, psi4, omega=omega, to_file = to_file)

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
        if vlmr:
            var, l, m, r, tp = vlmr
            self.prop['var']             = var
            self.prop['lmode']           = l
            self.prop['mmode']           = m
            self.prop['detector.radius'] = r

    def prop_list(self):
        """
        Print the properties
        """
        for key, val in self.prop.items():  
            print(key+":"+str(val))

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

    def prop_get(self, key):
        """
        Get property
        ------
        Input
        -----
        key  : Which property to get
        """
        return self.prop[key]

    def prop_get_all(self):
        """
        Get all properties (return a dict)
        """
        return self.prop

    def data_clean(self):
        """
        Cleanup data
        """
        self.time = []
        self.h    = []
        self.p4   = []

    def amplitude(self,var=None):
        """
        Return amplitude
        ------
        Input
        -----
        var  : Which variable to return (Psi4 or h)
        """
        if var=='Psi4':
            return np.abs(self.p4)
        else:
            return np.abs(self.h)

    def phase(self,var=None):
        """
        Return unwrapped phase
        ------
        Input
        -----
        var  : Which variable to return (Psi4 or h)
        """
        if var=='Psi4':
            return -np.unwrap(np.angle(self.p4))
        else:
            return -np.unwrap(np.angle(self.h))

    def phase_diff1(self, var=None, pad=True):
        """
        Return frequency wrt to time using finite diff 2nd order
        centered (works for nonuniform time). 
        ------
        Input
        -----
        var  : Which variable to return (Psi4 or h)
        pad  : Set to True to obtain an array of the same lenght as self.time.
        """
        return diff1(self.time,self.phase(var),pad=pad)

    def phase_diffo(self, var=None, o=4):
        """
        Return frequency wrt to time using finite differencing centered of
        higher order (works with uniform time)
        ------
        Input
        -----
        var  : Which variable to return (Psi4 or h)
        o    : Specify order for the finite differencing (defaults to 4)        
        """
        return diffo(self.time,self.phase(var), o)

    def time_ret(self):
        """
        Retarded time based on tortoise Schwarzschild coordinate
        """
        return ret_time(self.time,np.abs(self.prop["detector.radius"]), self.prop["mass"])

    def data_interp1(self, timei, useu=0, kind='linear'):
        """
        Return data interpolated on time 
        ------
        Input
        -----
        timei  : New time array over which to interpolate the data
        useu   : If set to True (or a positive value) assumes that time = (retarded time)/M
        """
        if useu:
            return np.interp1(timei, self.time_ret()/self.prop["mass"], self.h,kind=kind)
        else:
            return np.interp1(timei, self.time, self.h,kind=kind)

    def get_strain(self, fcut=-1, win=1.):
        """
        Return strain. Compute it first, if Psi4 is stored.
        """
        if self.prop['var']=='Psi4':
            if fcut < 0. :
                fcut = 2 * self.prop['init.frequency'] / max(1,abs(self.prop['mmode']))
            dt = self.time[1] - self.time[0]
            return win * fixed_freq_int_2( win * self.p4, fcut, dt = dt)
        else:
            return self.h

