#!/usr/bin/python

"""
Computes strain in 'physical units' using multipoles in c=G=Msun=1

SB 09/2021
"""

import os, sys, glob, re
import numpy as np
from scipy.special import factorial as fact

import matplotlib
import matplotlib.pyplot as plt

MSun_meter = 1.476625061404649406193430731479084713e3 # m
MSun_sec = 4.925491025543575903411922162094833998e-6 # s
PC_SI  = 3.085677581491367e+16 # m
MPC_SI = 1e6 * PC_SI

def conv_freq_to_Hz(Mf,M=1):
    """ 
    Convert frequency from mass-rescaled, geom.units to Hz 
    """ 
    return Mf/(M * MSun_sec)

def conv_freq_to_geom(fHz,M=1):
    """
    Convert frequency from Hz to mass-rescaled, geom.units
    """
    return M * fHz * MSun_sec

def wigner_d_function(l, m, s, incl):
    """
    Wigner-d functions
    """
    costheta = np.cos(incl*0.5)
    sintheta = np.sin(incl*0.5)
    norm = np.sqrt( (fact(l+m) * fact(l-m) * fact(l+s) * fact(l-s)) )
    ki = np.amax([0,m-s])
    kf = np.amin([l+m,l-s])
    k = np.arange(ki,kf+1)
    div = 1.0/( fact(k) * fact(l+m-k) * fact(l-s-k) * fact(s-m+k) );
    dWig = div*( np.power(-1.,k) * np.power(costheta,2*l+m-s-2*k) * np.power(sintheta,2*k+s-m) )
    return norm * np.sum(dWig)

def spinw_spherical_harm(s, l, m, incl,phi):
    """ 
    Spin-weighted spherical harmonics
    E.g. https://arxiv.org/abs/0709.0093
    """
    if ((l<0) or (m<-l) or (m>l)):
        raise ValueError("wrong (l,m)")
    c = np.power(-1.,-s) * np.sqrt( (2.*l+1.)/(4.*np.pi) )
    dWigner = c * wigner_d_function(l,m,-s,incl)
    exp_mphi = ( np.cos(m*phi) + 1j * np.sin(m*phi) )
    return dWigner * exp_mphi

def modes_to_strain(modes,
                    Mtot, # Mo
                    distance, # Mpc
                    inclination, phi,# sky loc.
                    add_negative_modes=False):
    """
    Build strain from time-domain modes in mass rescaled, geom. units
    Return result in SI units

    modes is a special dictionary, see example below

    Negative m-modes can be added using positive m-modes, 
    h_{l-m} = (-)^l h^{*}_{lm}
    """
    distance *= MPC_SI
    amplitude_prefactor = Mtot * MSun_meter / distance
    time = modes[(2,2)]['time'] * Mtot * MSun_sec
    h = np.zeros_like( 1j* time  )
    for (l,m) in modes.keys():
        sYlm = spinw_spherical_harm(-2, l, m, phi, inclination)
        Alm = amplitude_prefactor * modes[(l,m)]['amplitude']
        philm = modes[(l,m)]['phase']
        hlm = Alm * np.exp( - 1j * philm )
        h += hlm * sYlm
        if (add_negative_modes):            
            sYlm_neg = spinw_spherical_harm(-2, l, -m, phi, inclination)            
            hlm_neg = (-1)**l * np.conj(hlm) 
            h += hlm_neg * sYlm_neg            
    hplus = np.real(h)
    hcross = - np.imag(h)
    return time, hplus, hcross

def dummy_waveform(t, fpeak, flow):
    """
    Return amplitude and phase
    """
    f = t/t.max() * (fpeak - flow) + flow
    return t/t.max(), - np.pi * f * t


if __name__ == "__main__":

    
    t = np.arange(0, 500)    
    A, Phi = dummy_waveform(t, 0.15, 0.01)

    # h = A * np.exp( -1j * 2 * Phi)    
    # fig, ax = plt.subplots()
    # ax.plot(t, h.real, t, h.imag)
    # ax.grid()
    # fig.savefig("nrmodes2strain_dummywvf.pdf")
    # plt.show()
    # plt.close()

    modes = {}
    for (l,m) in [(2,2),(3,2),(4,4)]:
        wvf = {}
        wvf['time'] = t
        wvf['amplitude'] = A/np.exp(m - 2*l)
        wvf['phase'] = m * Phi
        modes[(l,m)] = wvf

    Mtot = 80.
    distance = 100.
    inclination = 0.
    phi = 0.
    time, hplus, hcross = modes_to_strain(modes,Mtot,distance,inclination,phi)

    fig, ax = plt.subplots()
    ax.plot(time, hplus, time, hcross)
    ax.grid()
    fig.savefig("nrmodes2strain_test.pdf")
    plt.show()
    plt.close()

