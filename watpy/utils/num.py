import sys
import numpy as np
from numpy import inf


# ------------------------------------------------------------------
# Numerical utilities 
# ------------------------------------------------------------------


def linterp(ti,t,y):
    """
    Linear interpolation of y(t) on ti
    """
    idx_min = np.argmin(abs(t-ti.min()))
    idx_max = np.argmin(abs(t-ti.max()))

    yi   = np.interp(ti, t[idx_min-1:idx_max+1], y[idx_min-1:idx_max+1])
    return yi


def findmax(x):
    """
    Finds max and grid index location
    """
    idx = np.argmax(x)
    return x[idx], idx


def findmax_abs(x):
    """
    Finds grid index location of absolute discrete maximum
    """
    idx = np.argmax(np.fabs(x))
    return x[idx], idx


def isarrayuniform(x, tol=1e-21):
    """ 
    Test if grid is uniform 
    """
    xu = linspace(x[0],x[::],len(x))
    return np.all(np.abs(x-xu)<=np.fabs(xu*tol))


# from scivis
class Struct(object):
    """ 
    Mimic Matlab structure
    """
    pass


# from scivis
def makelist(stuff):
    """
    Smarter converter to list
    """
    try:
        return list(stuff)
    except:
        return [stuff]


# from scivis
def bisection(func, domain, eps=sys.float_info.epsilon, nmax=52):
    """
    A simple one-dimensional root finder based on the bisection method

    * func   : must be a callable function returning a float
    * domain : must be a tuple (xmin, xmax) within which the zero of func
               is located
    * eps    : stop when the residual falls below this value
    * nmax   : maximum number of iterations
    """
    x1, x2 = domain

    fx1 = func(x1)
    fx2 = func(x2)

    if fx1*fx2 > 0:
        raise ValueError("func does not change sign between the extrema " +
                "of the domain")
    elif fx1 == 0:
        return x1
    elif fx2 == 0:
        return x2

    it  = 0
    xm  = 0.5*(x1 + x2)
    fxm = func(xm)

    while(it < nmax and abs(fxm) > eps):
        it += 1

        if fxm*fx1 > 0:
            x1 = xm
        elif fxm == 0:
            return xm
        else:
            x2 = xm

        xm  = 0.5*(x1 + x2)
        fxm = func(xm)

    return xm


# from scivis
def diff(ff):
    """
    Computes the undivided difference of ff using a 2nd order formula
    """
    if len(ff.shape) != 1:
        raise ValueError("diff only operates on 1D arrays")
    out = np.empty_like(ff)
    out[1:-1] = ff[2:] - ff[:-2]
    out[0] = -1.5*ff[0] + 2*ff[1] - 0.5*ff[2]
    out[-1] = 1.5*ff[-1] - 2*ff[-2] + 0.5*ff[-3]
    return out


# from scivis
def diff1(xp, yp, pad=True):
    """
    Computes the first derivative of y(x) using centered 2nd order
    accurate finite-differencing

    This function returns an array of yp.shape[0]-2 elements

    NOTE: the data needs not to be equally spaced
    """
    dyp = [(yp[i+1] - yp[i-1])/(xp[i+1] - xp[i-1]) \
            for i in range(1, xp.shape[0]-1)]
    dyp = np.array(dyp)
    if pad==True:
        dyp = np.insert(dyp, 0, dyp[0])
        dyp = np.append(dyp, dyp[-1])
    return dyp


# from scivis
def diff2(xp, yp, pad=False):
    """
    Computes the second derivative of y(x) using centered 2nd order
    accurate finite-differencing

    This function returns an array of yp.shape[0]-2 elements

    NOTE: the data needs not to be equally spaced
    """
    ddyp = [4*(yp[i+1] - 2*yp[i] + yp[i-1])/((xp[i+1] - xp[i-1])**2) \
            for i in range(1, xp.shape[0]-1)]
    ddyp = np.array(ddyp)
    if pad==True:
        ddyp = np.insert(ddyp, 0, ddyp[0])
        ddyp = np.append(ddyp, ddyp[-1])
    return ddyp


def diffo(t,f, o=2):
    """ 
    Compute finite differences of f(t) at a given order
    Works on uniform data, orders are hardcoded
    """
    d1f = np.empty_like(f)
    d2f = np.empty_like(f)
    if not isarrayuniform():
        wrn.warn('nonuniform grid!')
        return d1f, d2f 
    dt = t[1]-t[0]
    oodt  = 1./dt  
    oodt2 = oodt**2      
    if o==1:
        i = np.arange(1,n)
        d1f[i] = np.diff(f)*oodt
        d2f[i] = np.diff(d1f)*oodt
    elif o==2:
        i = np.arange(1,n-1)
        d1f[i] = (f[i+1]-f[i-1])*0.5*oodt
        d2f[i] = (f[i+1] - 2*f[i] + f[i-1])*oodt2
        i = 0
        d1f[i] = -(3*f[i]-4*f[i+1]+f[i+2])*0.5*oodt
        d2f[i] =  (2*f[i]-5*f[i+1]+4*f[i+2]-f[i+3])*oodt2
        i = n-1
        d1f[i] =  (3*f[i]-4*f[i-1]+f[i-2])*0.5*oodt
        d2f[i] =  (2*f[i]-5*f[i-1]+4*f[i-2]-f[i-3])*oodt2
    elif o==4:
        c = 1./12.
        i = np.arange(2,n-2)
        d1f[i] = c*(8*(f[i+1]-f[i-1]) - f[i+2] + f[i-2])*oodt
        d2f[i] = c*(-30*f[i]+16*(f[i+1]+f[i-1])-(f[i+2]+f[i-2]))*oodt2  
        i = 0
        d1f[i] = c*(-25*f[i]+48*f[i+1]-36*f[i+2]+16*f[i+3]-3*f[i+4])*oodt
        d2f[i] = c*(45*f[i]-154*f[i+1]+214*f[i+2]-156*f[i+3]+61*f[i+4]-10*f[i+5])*oodt2
        i = 1
        d1f[i] = c*(-3*f[i-1]-10*f[i]+18*f[i+1]-6*f[i+2]+f[i+3])*oodt
        d2f[i] = c*(10*f[i-1]-15*f[i]-4*f[i+1]+14*f[i+2]-6*f[i+3]+f[i+4])*oodt2
        i = n-1
        d1f[i] = - c*(-3*f[i+1]-10*f[i]+18*f[i-1]-6*f[i-2]+f[i-3])*oodt
        d2f[i] = c*(10*f[i+1]-15*f[i]-4*f[i-1]+14*f[i-2]-6*f[i-3]+f[i-4])*oodt2
        i = n-2
        d1f[i] = - c*(-25*f[i]+48*f[i-1]-36*f[i-2]+16*f[i-3]-3*f[i-4])*oodt
        d2f[i] = c*(45*f[i]-154*f[i-1]+214*f[i-2]-156*f[i-3]+61*f[i-4]-10*f[i-5])*oodt2
    else:
        wrn.warn("order not implemented, return empty arrays")
    return d1f, d2f


# from scivis
def integrate(ff):
    """
    Computes the anti-derivative of a discrete function using a
    2nd order accurate formula
    """
    out = np.empty_like(ff)
    out[0] = 0.0
    out[1:] = np.cumsum(0.5*(ff[:-1] + ff[1:]))
    return out


# from scivis
def maskdata(data, stencil):
    """
    Creates a masked array representing a subsample of the data on the given
    stencil

    * data    : must be a multidimensional np.array
    * stencil : must be an array containing the stencil width in every
                direction
    """
    sl = []
    for d in range(len(data.shape)):
        sl.append(slice(0, data.shape[d], stencil[d]))
    sl = tuple(sl)

    mask     = np.isfinite(data)
    mask[sl] = np.logical_not(mask[sl])
    return np.ma.masked_array(data, mask=mask)


# from scivis
def subsample(data, stencil):
    """
    Subsample the data on a given stencil

    * data    : must be a multidimensional numpy.array
    * stencil : must be an array containing the stencil width in every
                direction
    """
    sl = []
    for d in range(len(data.shape)):
        sl.append(slice(0, data.shape[d], stencil[d]))
    sl = tuple(sl)
    return data[sl]


# from scivis
## {{ http://stackoverflow.com/questions/8560440/removing-duplicate-columns-and-rows-from-a-numpy-2d-array
def sorted_array(array):
    """
    Returns a copy of the original vector which is

    * Sorted according to the lexicographical ordering
    * Purged of all duplicated elements
    """
    idx  = np.lexsort(array.T[::-1])
    da   = np.diff(array[idx], axis=0)
    cond = np.any(da, axis=1)
    cond = np.append(cond, True)
    return array[idx][cond]
## end of http://stackoverflow.com/questions/8560440/removing-duplicate-columns-and-rows-from-a-numpy-2d-array }}


# from scivis
def unmask(array):
    """
    Unmasks an numpy.array
    """
    if type(array) == np.ma.core.MaskedArray:
        return array[array.mask == False].data
    else:
        return array
