
import math

class Units:
  """Class representing unit conversion. Unit system is specified by 
  length, time, and mass units. From this, derived units are computed.
  There are two uses: specifying and absolute unit system by interpreting
  the base units as given in SI units, or specifying nits transformation
  by interpreting the base units as given in another unit system.
  This is only by convention. It is up to the user to keep track of the 
  meaning. 
  To create an object representing the transformation from one system
  into another, the division operator is defined for this class.
  """
  def __init__(self,ulength, utime, umass):
    """Create a unit system based on length unit ulength, time unit utime,
    and mass unit umass.
    """
    self.length   = float(ulength)
    self.time     = float(utime)
    self.mass     = float(umass)
    self.freq     = 1.0 / self.time
    self.velocity = self.length / self.time
    self.accel    = self.velocity / self.time
    self.force    = self.accel * self.mass
    self.area     = self.length**2
    self.volume   = self.length**3
    self.density  = self.mass / self.volume
    self.pressure = self.force / self.area
    self.power    = self.force * self.velocity
    self.energy   = self.force * self.length
    self.edens    = self.energy / self.volume
    self.angmom   = self.energy * self.time
    self.minertia = self.mass * self.area
  #
  def __div__(self,base):
    """Express the unit system represented by this class in terms of the unit 
    system base. This is only meaningful if both are expressed in SI units,
    or at least with respect to the same unit (although we recomment the convention
    of expressing absolute unit systems always in SI)
    """
    return Units(self.length / base.length, self.time / base.time, self.mass/base.mass)
  #
#


# The following constants are all given in SI units
C_SI          = 299792458.0           # Vacuum speed of light
G_SI          = 6.673e-11             # Gravitational constant
M_SOL_SI      = 1.98892e30            # Solar mass
EV_SI         = 1.602176565e-19       # Electron volt
MEV_SI        = 1e6 * EV_SI           
UAMU_SI       = 931.494061 * MEV_SI / (C_SI**2)   # Unified atomic mass unit
KB_SI         = 1.3806488e-23         # Boltzmann constant [J/K]
M_ELECTRON_SI = 9.10938291e-31        # Electron mass
M_PROTON_SI   = 1.672621777e-27       # Proton mass
M_NEUTRON_SI  = 1.674927351e-27       # Neutron mass
LIGHTYEAR_SI  = 9460730472580800.0    # Lightyear
PARSEC_SI     = 30.856776e15          # Parsec
N_AVOGADRO    = 6.02214129e23         # 1/mol
H_SI          = 6.62606957e-34        # Planck constant [J s]
HBAR_SI       = 1.054571726e-34       # H_SI / (2 pi)

def geom_ulength(ulength):
  """Create a geometric unit system, expressed in SI, where the length unit
  is given by ulength, expressed in SI units as well.
  """
  return Units(ulength, ulength/C_SI, ulength * (C_SI **2) / G_SI)
#

def geom_udensity(udensity):
  """Create a geometric unit system, expressed in SI, where the density unit
  is given by udensity, expressed in SI units as well.
  """
  return geom_ulength( C_SI / math.sqrt(G_SI*udensity))
#

def geom_umass(umass):
  """Create a geometric unit system, expressed in SI, where the mass unit
  is given by umass, expressed in SI units as well.
  """
  return geom_ulength(umass*G_SI/(C_SI**2))
#

SI_UNITS      = Units(1.0,1.0,1.0)
CGS_UNITS     = Units(1e-2, 1.0, 1e-3)
CACTUS_UNITS  = geom_umass(M_SOL_SI)

#Abbreviations

SI  = SI_UNITS
CU  = CACTUS_UNITS
CGS = CGS_UNITS

CU_CGS = CU/CGS
CGS_CU = CGS/CU

KM_CU  = 1e3 / CU.length
PARSEC_CU = PARSEC_SI / CU.length
MS_CU  = 1e-3 / CU.time
HZ_CU  = 1.0 / CU.freq
KHZ_CU  = 1e3 / CU.freq

GAUSS_CU = 1/(8.351966458327302e+15 * 1e4)

TEX_KM    = r'\mathrm{km}'
TEX_MS    = r'\mathrm{ms}'
TEX_GAUSS = r'\mathrm{G}'
TEX_MEV   = r'\mathrm{MeV}'
TEX_DENS_CGS = r'\mathrm{g}/\mathrm{cm}^{3}'}^{3}'