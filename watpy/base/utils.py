#!/usr/local/bin/python

import os
import re

import argparse
from numpy import inf
import numpy as np
import sys

from . import phys_utils as phu
from . import num_utils as num
from . import gw_utils as gwu

# ------------------------------------------------------------------
# Strings, files manipulation
# ------------------------------------------------------------------

# from scivis
def indent(string):
    """
    Indents one string
    ------
    Input
    -----
    string : String to be intented
    """
    s = ""
    for q in string.split("\n"):
        s += "\t" + q + "\n"
    return s[0:-1]

# from scivis
def print_table(table):
    """
    Prints a table using printtable.Printtable
    ------
    Input
    -----
    table  : must be a list of columns
    """
    widths = []
    for i in range(len(table[0])):
        w = 1
        for x in table:
            y = x[i].split('\n')
            w = max([w] + [len(q) for q in y])
        widths.append(w)

    import texttable

    ttable = texttable.Texttable()
    ttable.add_rows(table)
    ttable.set_cols_width(widths)
    return ttable.draw()

# from scivis
def basename(filename):
    """
    Get the base name of the given filename
    ------
    Input
    -----
    filename  : Path from which to extract the base name
    """
    return re.match(r"(.+)\.(\w+)", filename).group(1)

# from scivis
def extension(filename):
    """
    Get the extension of the given filename
    ------
    Input
    -----
    filename  : File from which to get the extension
    """
    return re.match(r"(.+)\.(\w+)", filename).group(2)

# from scivis
## {{{ http://code.activestate.com/recipes/499305/ (r3)
def ilocate(pattern, root=os.curdir, followlinks=False):
    """
    Locate all files matching supplied filename pattern in and below supplied root directory
    """
    for path, dirs, files in os.walk(os.path.abspath(root),
            followlinks=followlinks):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)
## end of http://code.activestate.com/recipes/499305/ }}}

# from scivis
def locate(pattern, root=os.curdir, followlinks=False):
    """ 
    Locate all files matching supplied filename pattern in and below supplied root directory. 
    """
    myp = pattern.replace("[", "?")
    myp = myp.replace("]", "?")
    return sorted([f for f in ilocate(myp, root, followlinks)])

# from scivis
def collate(fnames, outf, tidx=0, comments=["#", "%"], include_comments=False,
        epsilon=1e-15):
    """
    Merge a list of files from multiple segments

    * fnames   : list of file names, must be sorted from earlier to later
                 output
    * tidx     : time column number (starting from zero)
    * comments : lines beginning with a comment symbol are considered to be
                 comments
    * include_comments :
                 include comments in the output
    * epsilon  : two output times are the same if they differ by less than
                 epsilon

    Returns a string with the merged files
    """
    sout = []
    told  = None
    
    for fname in reversed(fnames): # Read backwards so new data 'overwrites' old.
        for dline in reversed(open(fname).readlines()):
            skip = False
            for c in comments:
                if dline[:len(c)] == c:
                    if include_comments:
                        sout.append(dline)
                    skip = True
                    break
            if skip:
                continue

            try:
                tnew = float(dline.split()[tidx])
            except IndexError:
                continue
            if told is None or tnew < told*(1 - epsilon):
                sout.append(dline)
                told = tnew
    return ''.join(reversed(sout)) # Reverse again to time-ordered

def extract_comments(fname, com_str="#"):
    """
    Extract comments from a file and return a list
    """
    with open(fname) as f:
        c = re.findall(com_str+'.*$', f.read(), re.MULTILINE)
    return c

def loadtxt_comments(fname, com_str=['#','"']):
    """ 
    Read txt file and its comments
    """
    comments = []
    for c in com_str:
        comments.append(extract_comments(fname, c))
    data = np.loadtxt(fname, delimiter=comm_str)
    return data, comments

# ------------------------------------------------------------------
# Waveform files
# ------------------------------------------------------------------

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
#

def wfile_parse_name(fname):
    """
    Parse waveform filename, return var,(l,m)-indexes, detector radius
    and data type 
    ------
    Input
    -----
    fname  : Name of the file to parse for information
    """
    #FIXME: negative modes?!
    t = ['bam','cactus','core','core-energy']
    s = [r'R(\w+)mode(\d)(\d)_r(\d+).l(\d+)',
         r'mp_(\w+)_l(\d)_m(\d)_r(\d+\.\d\d).asc',
         r'R(\w+)_l(\d+)_m(\d+)_r(\d+).txt',
         r'EJ_r(\d+).txt']
    vlmr = None
    for tp, sm in zip(t,s): #t.items():
        name = re.match(sm, os.path.basename(fname))
        if name is not None:
            if tp == 'core-energy':
                v    = 'EJ'
                r    = float(name.group(1))
                vlmr = (v,None,None,r,tp)
                return vlmr
            else:
                v    = name.group(1)
                l    = int(name.group(2))
                m    = int(name.group(3))
                r    = float(name.group(4))
                vlmr = (v,l,m,r,tp)
                return vlmr
            #
        #
    #
    return vlmr

#     SB I think the logic of this routine is wrong
#     the 'core'energy' match is compatible with the 'core' 
#     and has random behaviour
#     re-written above
#
# def wfile_parse_name(fname):
#     """
#     Parse waveform filename, return var,(l,m)-indexes, detector radius
#     and data type 
#     ------
#     Input
#     -----
#     fname  : Name of the file to parse for information
#     """
#     #FIXME: negative modes?!
#     t = {}
#     t['bam']    = r'R(\w+)mode(\d)(\d)_r(\d+).l(\d+)'
#     #t['bam']    = r'(\w+)mode(\d)(m?)(\d)_r(\d+).l(\d+)'
#     t['core']   = r'R(\w+)_l(\d+)_m(\d+)_r(\d+).txt'
#     t['cactus'] = r'mp_(\w+)_l(\d+)_m(\d+)_r(\d+\.\d\d).asc'
#     t['core-energy']  = r'(\w+)_r(\d+).txt'
#     vlmr = ()
#     for tp, sm in t.items():
#         name = re.match(sm, os.path.basename(fname))
#         if name is not None:
#             if tp != 'core-energy':
#                 v    = name.group(1)
#                 l    = int(name.group(2))
#                 m    = int(name.group(3))
#                 r    = float(name.group(4))
#                 vlmr = (v,l,m,r,tp)
#                 return vlmr
#             else:
#                 v    = name.group(1)
#                 r    = float(name.group(2))
#                 vlmr = (v,None,None,r,tp)
#                 return vlmr
#             #
#         #
#     #
#     return None

def wfile_get_detrad(fname):
    """
    Get detector radius from wf file header
    ------
    Input
    -----
    fname  : Name of the file to parse for information
    """
    s = extract_comments(fname, '"')
    s = re.sub(r' ', '',s[0]).upper() 
    return float(re.match('#R=%s', s))
              
def wfile_get_mass(fname):
    """
    Get binary mass from wf file header
    ------
    Input
    -----
    fname  : Name of the file to parse for information
    """
    s = extract_comments(fname, '"')
    s = re.sub(r' ', '',s[1]).upper() 
    return float(re.match('#M=%s', s))

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
    return float(re.findall("\d+\.\d+",s[0])[0])

# THC/cactus specials

def thc_to_core(path, prop):
    """
    Read data from WhiskyTHC simulation directory,
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
            fpath = '/data/mp_Psi4_l%d_m%d_r%.2f.asc' % (l, m, det)
            raw   = np.loadtxt(os.path.join(path,seg+fpath))
            t     = np.append(t, raw[:,0])
            var   = np.append(var, raw[:,1]+raw[:,2]*1.0j)
        #
    #

    t, msk = np.unique(t, axis=0, return_index=True)
    var    = r * var[msk]
    if v=='h':
        fcut = prop['init.frequency']
        var  = gwu.fixed_freq_int_2(var, fcut, dt=t[1]-t[0])
    #
    return t, var.real, var.imag
#
