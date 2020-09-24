#!/usr/local/bin/python

import numpy as np
import scipy as sp
import math
import num_utils as num

# ------------------------------------------------------------------
# Waveform analysis utilities
# ------------------------------------------------------------------


def align_phase(t, Tf, phi_a_tau, phi_b):
    """
    Align two waveforms in phase by minimizing the chi^2

        \chi^2 = \int_0^Tf [\phi_a(t + \tau) - phi_b(t) - \Delta\phi]^2 dt

    as a function of \Delta\phi.

    * t         : time, must be equally spaced
    * Tf        : final time
    * phi_a_tau : time-shifted first phase evolution
    * phi_b     : second phase evolution

    This function returns \Delta\phi.
    """
    dt = t[1] - t[0]
    weight = np.double((t >= 0) & (t < Tf))
    return np.sum(weight * (phi_a_tau - phi_b) * dt) / \
           np.sum(weight * dt)
#

def align(t, Tf, tau_max, t_a, phi_a, t_b, phi_b):
    """
    Align two waveforms in phase by minimizing the chi^2

        chi^2 = \sum_{t_i=0}^{t_i < Tf} [phi_a(t_i + tau) - phi_b(t_i) - dphi]^2 dt

    as a function of dphi and tau.

    * t          : time
    * Tf         : final time
    * tau_max    : maximum time shift
    * t_a, phi_a : first phase evolution
    * t_b, phi_b : second phase evolution

    The two waveforms are re-sampled using the given time t

    This function returns a tuple (tau_opt, dphi_opt, chi2_opt)
    """
    dt = t[1] - t[0]
    N = int(tau_max/dt)
    weight = np.double((t >= 0) & (t < Tf))

    res_phi_b = np.interp(t, t_b, phi_b)

    tau = []
    dphi = []
    chi2 = []
    for i in range(-N, N):
        tau.append(i*dt)
        res_phi_a_tau = np.interp(t, t_a + tau[-1], phi_a)
        dphi.append(align_phase(t, Tf, res_phi_a_tau, res_phi_b))
        chi2.append(np.sum(weight*
            (res_phi_a_tau - res_phi_b - dphi[-1])**2)*dt)

    chi2 = np.array(chi2)
    imin = np.argmin(chi2)

    return (tau[imin], dphi[imin], chi2[imin])
#

# From Reisswig and Pollney, Class. Quantum Grav. 28 (2011) 195015
def fixed_freq_int_1(signal, cutoff, dt=1):
    """
    Fixed frequency time integration

    * signal : a np array with the target signal
    * cutoff : the cutoff frequency
    * dt     : the sampling of the signal
    """
    from scipy.fftpack import fft, ifft, fftfreq

    f = fftfreq(signal.shape[0], dt)

    idx_p = np.logical_and(f >= 0, f < cutoff)
    idx_m = np.logical_and(f <  0, f > -cutoff)

    f[idx_p] = cutoff
    f[idx_m] = -cutoff

    return ifft(-1j*fft(signal)/(2*math.pi*f))
#

# From Reisswig and Pollney, Class. Quantum Grav. 28 (2011) 195015
def fixed_freq_int_2(signal, cutoff, dt=1):
    """
    Fixed frequency double time integration

    * signal : a np array with the target signal
    * cutoff : the cutoff frequency
    * dt     : the sampling of the signal
    """
    from scipy.fftpack import fft, ifft, fftfreq

    f = fftfreq(signal.shape[0], dt)

    idx_p = np.logical_and(f >= 0, f < cutoff)
    idx_m = np.logical_and(f <  0, f > -cutoff)

    f[idx_p] = cutoff
    f[idx_m] = -cutoff

    return ifft(-fft(signal)/(2*math.pi*f)**2)
#

def unwrap_shift0(x, dp, t0=0.):
    """ 
    Find shift s = 2 Pi n such that dp(t0) = p_1(t0) - p_2(t0) + s = 0 
    """
    dp0 = np.interp(t0, x,dp)
    return np.pi*np.round(dp0/(np.pi))
#

def norm_dp_dt(x, t1,p1,t2,p2,tab):
    """ 
    Distance L_2 between phases with time and phase shifts 
    """
    deltat = x[0] 
    deltap = x[1]
    p2i = np.interp(t1, t2-deltat,p2)
    idx = np.where(np.logical_and(t1>=tab[0], t1<=tab[1]))
    return np.trapz( (p1[idx]-p2i[idx]-deltap)**2 )
#

def min_phasediff_L2(t1,p1,t2,p2, tab, guess=[0.,0.], tol=1e-9):
    """ 
    Minimize L_2 distance varying time and phase shifts 
    """
    xopt = sp.optimize.fmin(func=norm_dp_dt, x0=guess, 
                            args=(t1,p1,t2,p2,tab),
                            xtol=tol)
    p2i = np.interp(t1, t2-xopt[0],p2) + xopt[1]
    Dphi = p1 - p2i
    return p2i, xopt[1], xopt[0], Dphi
#

def radius_extrap():
    """
    Perform extrapolation in radius
    """
    
    ## TODO

    return None

def richardson_extrap(p, h, t, y, kref=0, wrtref=True):


    """
    Richardson extrapolation 

    Given different datasets yi, i=1...N, collected as 
             y = [y0, y1, y2, ... , yN]
    and the relative time arrays
             t = [t0, t1, t2, ... , tN],
    corresponding to different resolutions
             h = [h1, h1, h2, ... , hN]
    performs Richardson extrapolation assuming order of convergence "p". 

    Return extrapolated value ye and residuals for each Richardson 
    step wrt a reference resolution dataset (default is kref = 0), 
    if wrtref=True. Otherwise returns extrapolated values and residuals
    each evauated between subsequent sets in increasing resolution.     

    NOTE: the data needs not to be of the same size (interpolated)
    """
    idx = np.argsort(h)
    idx = idx[::-1] # descending ordered
    #kref = idx(kref)
    if wrtref:
        msk    = tuple([idx!=kref])
        sn     = (h[kref]/h[msk])**p
        dn     = 1./(s-1)
        re     = []#np.empty_like(y)
        ye     = []
        for yk,sk,dk in zip(y[msk],sn,dn):
            yk = num.linterp(t[kref], tk, yk)
            ye.append((sk*yk - y[kref])*dk)
            re.append((sk*yk - y[kref])*dk-y[kref])
        #
    else:
        re     = []#np.empty_like(y)
        ye     = []        
        for k in range(0,len(y)-1):
            fk = (h[k]/h[k+1])**p
            dk = 1./(fk - 1.0)
            yt = num.linterp(t[k], t[k+1], y[k+1])
            ye.append((fk*yt - y[k])*dk)
            re.append(ye[k] - y[k])
        #
    #
    return ye, re
#

def mnfactor(m):
    """
    Factor to account for negative m modes
    """
    return 1 if m == 0 else 2
#

def waveform2energetics(h, h_dot, t, modes, mmodes):
    """
    Compute GW energy and angular momentum from multipolar waveform

    * h[l,m], h_dot[l,m] : multipolar strain and its derivative
    * t                  : time array
    * modes              : (l,m) indexes
    * mmodes             :   m   indexes
    """
    dtime = t[1]-t[0]

    E_GW_dot_ff = {}
    E_GW_ff = {}
    J_GW_dot_ff = {}
    J_GW_ff = {}    
    for l, m in modes:
        E_GW_dot_ff[(l,m)] = 1.0/(16.*np.pi) * np.abs(h_dot[l,m])**2 
        E_GW_ff[(l,m)] = num.integrate(E_GW_dot_ff[l,m]) * dtime
        J_GW_dot_ff[(l,m)] = 1.0/(16.*np.pi) * m * np.imag(h[l,m].h * np.conj(h_dot[l,m])) 
        J_GW_ff[(l,m)] = num.integrate(J_GW_dot_ff[l,m]) * dtime
    #
    E_GW_dot = {}
    E_GW = {}
    J_GW_dot = {}
    J_GW = {}
    for m in mmodes:
        E_GW_dot[m] = np.zeros_like(t)
        E_GW[m] = np.zeros_like(t)
        J_GW_dot[m] = np.zeros_like(t)
        J_GW[m] = np.zeros_like(t)
    #
    for l, m in modes:
        E_GW_dot[m] += mnfactor(m) * E_GW_dot_ff[l,m]
        E_GW[m] += mnfactor(m) * E_GW_ff[l,m]
        J_GW_dot[m] += mnfactor(m) * J_GW_dot_ff[l,m]
        J_GW[m] += mnfactor(m) * J_GW_ff[l,m]
    #
    E_GW_dot_all = np.zeros_like(t)
    E_GW_all = np.zeros_like(t)
    J_GW_dot_all = np.zeros_like(t)
    J_GW_all = np.zeros_like(t)
    for m in mmodes:
        E_GW_dot_all += E_GW_dot[m]
        E_GW_all += E_GW[m]
        J_GW_dot_all += J_GW_dot[m]
        J_GW_all += J_GW[m]
    #
    return E_GW_all, E_GW_dot_all, J_GW_all, J_GW_dot_all
# #
    return E_GW_all, E_GW_dot_all, J_GW_all, J_GW_dot_all
#