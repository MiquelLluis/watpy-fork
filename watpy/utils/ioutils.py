import sys, os, re 
import warnings as wrn

import numpy as np
from numpy import inf


# ------------------------------------------------------------------
# Strings & files manipulation
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




