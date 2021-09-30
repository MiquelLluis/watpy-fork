#!/usr/bin/python

"""
Clone Hybrid waveforms from core database
FZ 09/2021
"""

from watpy.coredb.coredb import *

import os
os.makedirs('./CoRe_DB_clone', exist_ok=True)

db_path = './CoRe_DB_clone/'
cdb = CoRe_db(db_path)

idb = cdb.idb
cdb = CoRe_db(db_path, ifile = "json/DB_Hyb.json")

print(idb.dbkeys) # show the database_key for each simulation

# show the metadata in the CoRe DB index for each simulation
entries = 0
for i in idb.index:
    entries += 1
    for k, v in i.data.items():
        print('  {} = {}'.format(k,v))

    break # uncomment to see all ... large output
print('Shown {} entries'.format(entries))

cdb.sync(lfs=True, verbose=False)
