import sys, os, re, datetime
import warnings as wrn
from subprocess import Popen, PIPE
import shutil
import json, csv
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


def remove_template_missed_keys(string):
    """
    Remove the matches to ${ .*? } 
    in a string with multiple lines
    """
    clean = ""
    for line in string.splitlines():
        substr = re.search("\$\{(.*?)\}", line)
        if substr:
            line = re.sub("\$\{"+substr.group(1)+"}","",line)
        clean += line+'\n'
    return clean

def template_to_keys(templ, delim = '=', comments='#'):
    """
    Return list of keys (strings) from a multiline template string like

    # commment
    key1 = val1
    key2 = val2
    ...

    """
    return [l.split(delim)[0].strip() for l in templ.splitlines() if not l.startswith(comments)]


#---------------------------------------------------------------------------
# CSV, JSON, TXT files & dict
#---------------------------------------------------------------------------


def read_csv_into_dict(filename):
    """ 
    Read a CSV file into a python dictionary
    """
    data = [] 
    with open(filename) as f:
        reader = csv.DictReader(f, delimiter=',')
        for line in reader:
            data.append(line)
    return data


def write_dict_into_csv(filename, fieldnames, data):
    """ 
    Writes a python dictionary into a CSV file 
    """
    with open(filename, "wb") as f:
        writer = csv.DictWriter(f, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def write_dict_into_json(filename, d):
    """ 
    Write python dictionary to JSON file 
    """
    with open(filename, 'w') as f:
        json.dump(d, f)
    return 


def read_json_into_dict(filename):
    """ 
    Read JSON file into a python dictionary 
    """
    with open(filename) as f:
        d = json.load(f, strict=False) 
    return d


def read_txt_header(filename, comm_char='#'):
    """ Read TXT file header lines into list """
    h = []
    with open(filename) as data:
        for line in data:
            if line[0]==comm_char:
                h.append(line[1::].strip())
    return h


def read_txt_into_dict(filename, sep_char='=', comm_char='#'):
    """ 
    Read a TXT file with lines 'parameter = value', return a dict 
    """
    d = dict()
    with open(filename) as data:
        for line in data:
            if line[0]==comm_char:
                continue
            if sep_char in line:
                key,value = line.split(sep_char, 1)
                d[key.strip()] = value.strip()
            else:
                pass # skip empty/bad lines
    return d


def write_dict_into_txt(d, filename, sep_char='='):
    """ 
    Write dict into a TXT file with lines 'parameter = value' 
    """
    with open(filename, 'w') as f:
        for key, value in d.items():
            f.write('%s = %s\n' % (key, value))
    return None


def dlist_to_dd(dlist, dlist_key):
    """
    Given a list of dictionaries and one of its keys 'dlist_key'
    generates a dictionary with main keys given by 'dlist_key'
    """
    if dlist_key not in dlist.keys():
        raise ValueError("key not in dictionary")
    dd = {}
    for entry in dlist:
        key = entry[d_list_key]
        dd[key] = entry
    return dd


def dd_find(ddic, key, val):
    """
    Returns the sub-dictionary of the input dictionary containing 
    all entries with the specified key = val
    """
    dsub = {}
    for k in ddic:
        entry = ddic[k]
        if entry[key] == val:
            dsub[k] = entry
    return dsub


#    return dict((k, dd[k]) for k in keys if k in dd)
    

#---------------------------------------------------------------------------
# os, bash, git, etc 
#---------------------------------------------------------------------------


def runcmd(cmd, workdir, out, verbose=False):
    """
    Given a command and a working directory, run the command
    from the bash shell in the given directory.
    --------
    Input:
    --------
    cmd      : Command to be run in the bash shell as a list of strings
    workdir  : Directory where to run the command
    out      : If not None, standard output/error are given as output
    verbose  : If True, print more information on screen while running.

    --------
    Output:
    --------
    sl_out   : Standard output from the bash command
    sl_err   : Standard error from the bash command
    """
    proc = Popen(cmd, cwd=workdir, stdout=PIPE,
                 stderr=PIPE, universal_newlines=True)
    if verbose:
        sl_out = []
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            else:
                if line is not None:
                    sys.stdout.write(line)
                    sl_out.append(line)
        sl_out = "".join(sl_out)
    else:
        sl_out, sl_err = proc.communicate()
    if type(out)==str:
        open(os.path.join(workdir, out), "w").write(out)
        return out
    elif out is not None:
        return sl_out, sl_err


def git_clone(path = '.',
              server = "core-gitlfs.tpi.uni-jena.de",
              gitbase = "core_database",
              protocol = 'https',
              repo = 'core_database_index',
              lfs = False,
              verbose = True):
    """
    Clones a git repository 

    git@core-gitlfs.tpi.uni-jena.de:core_database/core_database_index.git
    https://core-gitlfs.tpi.uni-jena.de/core_database/core_database_index.git
    """
    pre = {'ssh': 'git@', 'https': 'https://'}
    sep = {'ssh': ':'   , 'https': '/'}
    if protocol not in pre.keys():
        raise NameError("Protocol not supported!")
    git_repo = '{}{}{}{}/{}.git'.format(pre[protocol],server,
                                       sep[protocol],gitbase,repo)
    print('git-clone {} ...'.format(git_repo))
    if lfs:
        # 'git lfs clone' is deprecated and will not be updated
        #  with new flags from 'git clone'
        out, err = runcmd(['git','lfs', 'clone',git_repo],path,True)
        #
    else:
        out, err = runcmd(['git','clone', git_repo],path, True)
    if verbose:
        print(out, err)
    print('done!')


def git_pull(path = '.',
             repo = 'core_database_index',
             lfs = False,
             verbose = True):
    """
    Pulls changes in a git repository located in a path
    """
    workdir = os.path.join(path, repo)
    print('git-pull {} ...'.format(repo))
    if lfs:
        out, err = runcmd(['git', 'lfs', 'install'], workdir, True)
        out, err = runcmd(['git', 'lfs', 'pull', 'origin', 'master'], workdir, True)
    else:
        out, err = runcmd(['git', 'pull', 'origin', 'master'], workdir, True)
    if verbose:
        print(out, err)
    print('done!')
