#!/usr/local/bin/python

import numpy as np
import warnings as wrn
try:
    from scipy import factorial2
except:  
    from scipy.misc import factorial2

# ------------------------------------------------------------------
# Physics utilities 
# ------------------------------------------------------------------

def ret_time(t,r,M=1.):
    """
    Retarded time on Schwarzschild
    """
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

## dummy (double notation)
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
#