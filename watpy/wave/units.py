# Basic unit conversion tools
# Frequent-use conversion factors given as routines
# Units/conversion factors routines of basic quantities


uts= {
  'Msun_sec': 4.925794970773135e-06,
}

def MSun_sec():
  return uts['Msun_sec']


# For plots:
TEX_KM    = r'\mathrm{km}'
TEX_MS    = r'\mathrm{ms}'
TEX_GAUSS = r'\mathrm{G}'
TEX_MEV   = r'\mathrm{MeV}'
TEX_DENS_CGS = r'\mathrm{g}/\mathrm{cm}^{3}'


# ------------------------------------------------------------------
# Unit systems
# ------------------------------------------------------------------


class geom:
    """
    Geometric units + Msun = 1
    """
    grav_constant       = 1.0
    light_speed         = 1.0
    solar_mass          = 1.0
    MeV                 = 1.0

class cgs:
    """
    CGS units
    """
    grav_constant       = 6.673e-8
    light_speed         = 29979245800.0
    solar_mass          = 1.988409902147041637325262574352366540e33
    MeV                 = 1.1604505e10

class metric:
    """
    Standard SI units
    """
    grav_constant       = 6.673e-11
    light_speed         = 299792458.0
    solar_mass          = 1.988409902147041637325262574352366540e30
    MeV                 = 1.1604505e10


# ------------------------------------------------------------------
# Unit routines
# ------------------------------------------------------------------


def unit_dens(ua):
    """
    Compute the unit density in the given units
    """
    return unit_mass(ua)/((unit_length(ua))**3)

def unit_energy(ua):
    """
    Compute the unit energy in the given units
    """
    return unit_mass(ua) * (unit_length(ua) / unit_time(ua))**2

def unit_force(ua):
    """
    Compute the unit force in the given units
    """
    return unit_mass(ua) * unit_length(ua) / (unit_time(ua))**2

def unit_press(ua):
    """
    Compute the unit pressure in the given units
    """
    return unit_force(ua) / (unit_length(ua))**2

def unit_length(ua):
    """
    Computes the unit length in the given units
    """
    return ua.solar_mass * ua.grav_constant / ua.light_speed**2

def unit_luminosity(ua):
    """
    Computes the unit luminosity in the given units
    """
    return unit_energy(ua)/unit_time(ua)

def unit_mass(ua):
    """
    Computes the unit mass in the given units
    """
    return ua.solar_mass

def unit_spec_energy(ua):
    """
    Computes the unit specific energy in the given units
    """
    return (unit_length(ua) / unit_time(ua))**2

def unit_temp(ua):
    """
    Computes the unit temperature in the given units
    """
    return ua.MeV

def unit_time(ua):
    """
    Computes the unit time in the given units
    """
    return unit_length(ua) / ua.light_speed

def unit_velocity(ua):
    """
    Computes the unit velocity in the given units
    """
    return unit_length(ua) / unit_time(ua)


# ------------------------------------------------------------------
# Conversion routines
# ------------------------------------------------------------------


def conv_dens(ua, ub, rho):
    """
    Converts a density from units ua to units ub
    """
    return rho / unit_dens(ua) * unit_dens(ub)

def conv_emissivity(ua, ub, Q):
    """
    Converts an emissivity from units ua to units ub
    """
    uua = unit_energy(ua) / (unit_length(ua)**3 * unit_time(ua))
    uub = unit_energy(ub) / (unit_length(ub)**3 * unit_time(ub))
    return Q / uua * uub

def conv_energy(ua, ub, E):
    """
    Converts energy from units ua to units ub
    """
    return E / unit_energy(ua) * unit_energy(ub)

def conv_energy_density(ua, ub, e):
    """
    Converts an energy density from units ua to units ub
    """
    uua = unit_energy(ua) / (unit_length(ua)**3)
    uub = unit_energy(ub) / (unit_length(ub)**3)
    return e / uua * uub

def conv_frequency(ua, ub, f):
    """
    Converts a frequency from units ua to units ub
    """
    return 1.0/conv_time(ua, ub, 1.0/f)

def conv_length(ua, ub, l):
    """
    Converts a length from units ua to units ub
    """
    return l / unit_length(ua) * unit_length(ub)

def conv_luminosity(ua, ub, L):
    """
    Converts a luminosity (power) from units ua to units ub
    """
    return L / unit_luminosity(ua) * unit_luminosity(ub)

def conv_force(ua, ub, F):
    """
    Converts a force from units ua to units ub
    """
    return F / unit_force(ua) * unit_force(ub)

def conv_press(ua, ub, p):
    """
    Converts a pressure from units ua to units ub
    """
    return p / unit_press(ua) * unit_press(ub)

def conv_mass(ua, ub, m):
    """
    Converts a mass from units ua to units ub
    """
    return m / unit_mass(ua) * unit_mass(ub)

def conv_number_density(ua, ub, n):
    """
    Converts a number density from units ua to units ub
    """
    uua = 1.0 / (unit_length(ua)**3)
    uub = 1.0 / (unit_length(ub)**3)
    return n / uua * uub

def conv_number_emissivity(ua, ub, R):
    """
    Converts the number emissivity from units ua to units ub
    """
    uua = 1.0/(unit_length(ua)**3 * unit_time(ua))
    uub = 1.0/(unit_length(ub)**3 * unit_time(ub))
    return R /uua * uub

def conv_opacity(ua, ub, kappa):
    """
    Converts an opacity (1/Length) from units ua to units ub
    """
    return kappa * unit_length(ua) / unit_length(ub)

def conv_spec_energy(ua, ub, eps):
    """
    Converts the specific energy from units ua to units ub
    """
    return eps / unit_spec_energy(ua) * unit_spec_energy(ub)

def conv_temperature(ua, ub, T):
    """
    Converts a temperature from units ua to units ub
    """
    return T / unit_temp(ua) * unit_temp(ub)

def conv_time(ua, ub, t):
    """
    Converts a time from units ua to units ub
    """
    return t / unit_time(ua) * unit_time(ub)

def conv_velocity(ua, ub, vel):
    """
    Convers a velocity from units ua to units ub
    """
    return vel / unit_velocity(ua) * unit_velocity(ub)

