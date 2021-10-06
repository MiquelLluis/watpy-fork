import numpy as np
import scipy as sp
import math
from ..utils import num as num 
import warnings as wrn
try:
    from scipy import factorial2
except:  
    from scipy.special import factorial2


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


def unwrap_shift0(x, dp, t0=0.):
    """ 
    Find shift s = 2 Pi n such that dp(t0) = p_1(t0) - p_2(t0) + s = 0 
    """
    dp0 = np.interp(t0, x,dp)
    return np.pi*np.round(dp0/(np.pi))


def norm_dp_dt(x, t1,p1,t2,p2,tab):
    """ 
    Distance L_2 between phases with time and phase shifts 
    """
    deltat = x[0] 
    deltap = x[1]
    p2i = np.interp(t1, t2-deltat,p2)
    idx = np.where(np.logical_and(t1>=tab[0], t1<=tab[1]))
    return np.trapz( (p1[idx]-p2i[idx]-deltap)**2 )


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


def richardson_extrap(p, y0, h0, y1, h1):
    """
    Richardson extrapolation.

    Given two data points 
        `y0` and `y1`,
    compute with grid spacings 
        `h0` and `h1`,
    performs Richardson extrapolation assuming order of convergence `p`.

    Returns extrapolated value `ye`.

    NOTE: If you are only given the number of points, then pass 
        `1/n0` and `1/n1` 
    instead of
        `h0` and `h1`
    where `ni` is the number of points corresponding to `hi`.
    """
    s = (h0/h1)**p
    yextrp = (s*y1 - y0) / (s - 1.0)
    return yextrp


def richardson_extrap_series(p, y, t, h):
    """
    Richardson extrapolation in resolution.

    Given data sets yi, i=1...N, collected as
             y = [y0, y1, y2, ... , yN],
    with corresponding relative time arrays
             t = [t0, t1, t2, ... , tN],
    computed with (descendingly ordered) grid spacings
             h = [h1, h1, h2, ... , hN],
    performs Richardson extrapolation assuming order of convergence `p`.

    Returns extrapolated dataset `ye` and estimated error `err`
    computed wrt second to last extrapolation step at each point.

    NOTE: `h` is the grid spacing, not the number of points `n`. In the latter case
    just pass `1/n` instead.
    NOTE: A data set consists out of `yi` and `ti` and both arrays have to be 
    of the same length. However, the length of a data set does not have to agree
    among different resolutions.
    """

    N = len(h) # number of data sets passed
    if N != len(t) or len(t) != len(y):
        raise ValueError("Inconsistent number of data sets received: Arrays h, t, p must have same length!")

    # extrapolated result will be sampled on grid of highest resolution data
    te = t[-1]; n = len(te)
    ye = np.zeros(n); err = np.zeros(n)

    # interpolate all data sets on time grid of extrapolated result
    intrp_y = [ num.linterp(te, t[k], y[k]) for k in range(N-1) ]
    intrp_y.append(y[-1])

    # compute Richardson extrapolation pointwise
    for i in range(n):
        # procedure is similar to Romberg integration
        # but instead of recomputing integrals for different resolutions, here
        # we just use the provided data to populate the first column to build 
        # up the iteration
        extrp_y = np.zeros((N,N))
        extrp_y[:,0] = [ intrp_y[k][i] for k in range(N) ]

        # iterate each row with Richardson extrapolation and systematically
        # reduce higher order errors
        for k in range(1,N):
            for j in range(0, k):
                extrp_y[k,j+1] = richardson_extrap(p+j, extrp_y[k-1,j], h[k-1], extrp_y[k,j], h[k])

        # error estimate wrt to second to last extrapolation
        err[i] = extrp_y[-1,-1] - extrp_y[-2,-2]
        ye[i] = extrp_y[-1,-1]
    return ye, te


def radius_extrap(t, psi4, r0, l=2, m=2, m0=1):
    """
    Perform extrapolation in radius

    Extrapolates Psi4 to infinite radius following

        Lousto et al. PRD 82 104057 (2010)
        Kiuchi et al. PRD 96 084060 (2017)

    Input
        * t, psi4   : time and complex (l,m)-mode of R psi4 
        * r0        : extraction radius
        * l, m      : multipole index
        * m0        : ADM mass
    Output
        * Psi4_inf  : extrapolated R psi4 to R -> oo
    """
    rA = r0*(1. + m0/(2.*r0))**2
    C  = 1. - 2.*m0/rA
    dt = np.concatenate(([0], np.diff(t)))
    return C*(psi4 - (l-1)*(l+2)/(2*rA)*np.cumsum(psi4*dt))


def radius_extrap_polynomial(ys, rs, K):
    """
    Given different datasets yi, i=1...N, collected as
             ys = [y0, y1, y2, ... , yN]
    and array containing extraction radii
             rs = [r0, r1, r2, ... , rN],
    compute the asymptotic value of y as r goes to infinity from an Kth
    order polynomial in 1/r, e.g.

        yi = y_infty + \sum_i=k^K ci / ri^k,

    where y_infty and the K coefficients ci are determined through a least
    squares polynomial fit from the above data.

    ys ... collection of data sets yi which all are of the same length,
           e.g. all sampled on the same grid u.
    rs ... extraction radii of the data samples yi
    K  ... maximum polynomial order of 1/r polynomial
    """
    N = len(ys)
    if N != len(rs):
        raise ValueError("Mismatch in number of data sets ys and radii rs encountered!")
    L = len(ys[0])
    for i in range(1,N):
        if len(ys[i]) != L:
            raise ValueError("Inhomogenuous data set encountered! Check if all ys are sampled " *
                             "on the same grid")

    yinfty = np.zeros(L)
    # implementation relies on example given at 
    # https://docs.scipy.org/doc/scipy/reference/reference/generated/scipy.linalg.lstsq.html#scipy.linalg.lstsq
    M = np.array(rs)[:, np.newaxis]**(-np.array(range(K+1))) # inverse powers of rs
    for i in range(L):
        ys_i = [ ys[k][i] for k in range(N) ] # gather data for common radius
        p, *_ = sp.linalg.lstsq(M, ys_i)
        yinfty[i] = p[0] # zeroth coefficient equals value at r -> infty
        
    return yinfty


def _richardson_extrap_old(p, h, t, y, kref=0, wrtref=True):
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

    return ye, re


def mnfactor(m):
    """
    Factor to account for negative m modes
    """
    return 1 if m == 0 else 2


def waveform2energetics(h, h_dot, t, modes, mmodes):
    """
    Compute GW energy and angular momentum from multipolar waveform

    * h[(l,m)]     : multipolar strain 
    * h_dot[(l,m)] : time-derivative of multipolar strain
    * t            : time array
    * modes        : (l,m) indexes
    * mmodes       :   m   indexes
    """
    dtime = t[1]-t[0]

    E_GW_dot_ff = {}
    E_GW_ff = {}
    J_GW_dot_ff = {}
    J_GW_ff = {}    
    for l, m in modes:
        E_GW_dot_ff[(l,m)] = 1.0/(16.*np.pi) * np.abs(h_dot[l,m])**2 
        E_GW_ff[(l,m)] = num.integrate(E_GW_dot_ff[l,m]) * dtime
        J_GW_dot_ff[(l,m)] = 1.0/(16.*np.pi) * m * np.imag(h[l,m] * np.conj(h_dot[l,m])) 
        J_GW_ff[(l,m)] = num.integrate(J_GW_dot_ff[l,m]) * dtime

    E_GW_dot = {}
    E_GW = {}
    J_GW_dot = {}
    J_GW = {}
    for m in mmodes:
        E_GW_dot[m] = np.zeros_like(t)
        E_GW[m] = np.zeros_like(t)
        J_GW_dot[m] = np.zeros_like(t)
        J_GW[m] = np.zeros_like(t)

    for l, m in modes:
        E_GW_dot[m] += mnfactor(m) * E_GW_dot_ff[l,m]
        E_GW[m] += mnfactor(m) * E_GW_ff[l,m]
        J_GW_dot[m] += mnfactor(m) * J_GW_dot_ff[l,m]
        J_GW[m] += mnfactor(m) * J_GW_ff[l,m]

    E_GW_dot_all = np.zeros_like(t)
    E_GW_all = np.zeros_like(t)
    J_GW_dot_all = np.zeros_like(t)
    J_GW_all = np.zeros_like(t)
    for m in mmodes:
        E_GW_dot_all += E_GW_dot[m]
        E_GW_all += E_GW[m]
        J_GW_dot_all += J_GW_dot[m]
        J_GW_all += J_GW[m]

    return E_GW_all, E_GW_dot_all, J_GW_all, J_GW_dot_all


# ------------------------------------------------------------------
# Various useful routines
# ------------------------------------------------------------------


def ret_time(t,r,M=1.):
    """
    Retarded time on Schwarzschild
    """
    if(r==1.0 or r==-1.0):
        rs = 0 # For the case when r=-1 (extrapolated at infinity)
    else:
        rs = r + 2.*M*np.log(r/(2.*M) -1.)
    return t - rs


def q_to_nu(q):
    """
    Return symm. mass ratio, given mass ratio nu(q)
    """
    return q/((1.+q)**2)


#  dummy (double notation)
def q_to_eta(q):
    """
    Return symmetric-mass ratio given mass-ratio
    assume q>=1
    """
    return q_to_nu(q)


def nu_to_q(nu):
    """
    Return symmetric mass-ratio given mass-ratio 
    assume q>=1
    """
    if nu<=0.:
        return float('Inf')
    return (1. + np.sqrt(1. - 4.*nu) - 2.*nu)/(2.*nu);


# dummy (double notation)
def eta_to_q(nu):
    """
    Return symmetric mass-ratio given mass-ratio 
    assume q>=1
    """
    return nu_to_q(nu)


def m12_to_x12(m1,m2):
    """ 
    Compute X_i=m_i/M 
    """
    M = m1 + m2
    if m2>m1:
        m1,m2 = m2,m1
    x1 = m1/M
    x2 = m2/M
    nu = x1*x2 # m1*m2/M**2
    q = m1/m2
    return x1,x2,M,q,nu


def clm(l,m, x1,x2):
    """ 
    Leading order in nu depedency of Newtonian waveform 
    """
    e = np.mod(l+m,2) 
    p = l + e - 1
    return x2**p + (-1)**m * x1**p


def rwz_norm(l):
    """ 
    Normalization factor between RWZ and hlm
    """
    return np.sqrt((l+2)*(l+1)*l*(l-1))


def Ebj(nu, M, Madm,Jadm, Erad,Jrad):
    """ 
    Eb(j) reduced binding energy and orbital angular momentum 
    """
    Eb = ((Madm-Erad)/M-1)/nu;
    j = (Jadm-Jrad)/(M**2*nu);
    return Eb,j


def lamtilde_of_eta_lam1_lam2(eta, lam1, lam2):
    """
    $\tilde\Lambda(\eta, \Lambda_1, \Lambda_2)$.
    Lambda_1 is assumed to correspond to the more massive (primary) star m_1.
    Lambda_2 is for the secondary star m_2.
    """
    return (8.0/13.0)*((1.0+7.0*eta-31.0*eta**2)*(lam1+lam2) + np.sqrt(1.0-4.0*eta)*(1.0+9.0*eta-11.0*eta**2)*(lam1-lam2))


def deltalamtilde_of_eta_lam1_lam2(eta, lam1, lam2):
    """
    This is the definition found in Les Wade's paper.
    Les has factored out the quantity \sqrt(1-4\eta). It is different from Marc Favata's paper.
    $\delta\tilde\Lambda(\eta, \Lambda_1, \Lambda_2)$.
    Lambda_1 is assumed to correspond to the more massive (primary) star m_1.
    Lambda_2 is for the secondary star m_2.
    """
    return (1.0/2.0)*(np.sqrt(1.0-4.0*eta)*(1.0 - 13272.0*eta/1319.0 + 8944.0*eta**2/1319.0)*(lam1+lam2)
                      + (1.0 - 15910.0*eta/1319.0 + 32850.0*eta**2/1319.0 + 3380.0*eta**3/1319.0)*(lam1-lam2))


def lam1_lam2_of_pe_params(eta, lamt, dlamt):
    """
    lam1 is for the the primary mass m_1.
    lam2 is for the the secondary mass m_2.
    m_1 >= m2.
    """
    a = (8.0/13.0)*(1.0+7.0*eta-31.0*eta**2)
    b = (8.0/13.0)*np.sqrt(1.0-4.0*eta)*(1.0+9.0*eta-11.0*eta**2)
    c = (1.0/2.0)*np.sqrt(1.0-4.0*eta)*(1.0 - 13272.0*eta/1319.0 + 8944.0*eta**2/1319.0)
    d = (1.0/2.0)*(1.0 - 15910.0*eta/1319.0 + 32850.0*eta**2/1319.0 + 3380.0*eta**3/1319.0)
    den = (a+b)*(c-d) - (a-b)*(c+d)
    lam1 = ( (c-d)*lamt - (a-b)*dlamt )/den
    lam2 = (-(c+d)*lamt + (a+b)*dlamt )/den
    # Adjust lam1 and lam2 if lam1 becomes negative
    # lam2 should be adjusted such that lamt is held fixed
    if lam1<0:
        wrn.warn('lam1<0')
        lam1 = 0
        lam2 = lamt / (a-b)
    return lam1, lam2


def Yagi13_fitcoefs(ell):
    """
    Coefficients of Yagi 2013 fits for multipolar
    $\bar{\lambda}_\ell = 2 k_\ell/(C^{2\ell+1} (2\ell-1)!!)$
    Tab.I (NS) http://arxiv.org/abs/1311.0872
    """
    if ell==3:
        c = [-1.15,1.18,2.51e-2,-1.31e-3,2.52e-5];
    elif ell==4:
        c = [-2.45,1.43,3.95e-2,-1.81e-3,2.8e-5];
    else:
        c = [];
    return c;


def Yagi13_fit_barlamdel(barlam2, ell):
    """
    Yagi 2013 fits for multipolar
    $\bar{\lambda}_\ell$ = 2 k_\ell/(C^{2\ell+1} (2\ell-1)!!)$
    Eq.(10),(61); Tab.I; Fig.8 http://arxiv.org/abs/1311.0872
    """
    lnx = np.log(barlam2);
    coefs = Yagi13_fitcoefs(ell);
    lny = np.polyval(coefs[::-1], lnx);
    return np.exp(lny)


def barlamdel_to_kappal(q, barlamAl, barlamBl, ell):
    """
    $\kappa^{A,B}_\ell(\bar{\lambda}_\ell)$
    Assume $q=M_A/M_B>=1$
    """
    XA = q/(1.+q);
    XB = 1. - XA;
    f2l1 = factorial2(2*ell-1);
    p = 2*ell + 1;
    kappaAl = f2l1 * barlamAl * XA**p / q; 
    kappaBl = f2l1 * barlamBl * XB**p * q; 
    #kappaTl = kappaAl + kappaBl;
    return  kappaAl, kappaBl


def LoveC_to_barlamdel(C, kell, ell):
    """
    $\bar{\lambda}_\ell(k_\ell,C)$
    Compactness and Love numbers to Yagi tidal parameters  
    """
    f2l1 = factorial2(2*ell-1);
    return  2. * kell /( f2l1 * (C**(2*ell + 1)) );

