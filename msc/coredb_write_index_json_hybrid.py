#!/usr/bin/python

"""
Write the index JSON from the metadata_main.txt in the DB
SB 09/2021
"""

from watpy.coredb.coredb import *
import os # mkdirs

db_path = './CoRe_DB_clone/'
os.makedirs(db_path, exist_ok=True)

cdb = CoRe_db(db_path, ifile = "json/DB_Hyb.json") #Use this for Hybrids!
idb = cdb.idb

# make sure the DB is up-to-date!
cdb.sync()

# read metadata_main in a list
mdlist = []
for key in idb.dbkeys:
    mdlist.append(cdb.sim[key].md)

# update the index 
idb.update_from_mdlist(mdlist)

# write the index to JSON with the appropriate template 
idb.to_json_tmplk(tmpl = TXT_HYB)  #Use this for Hybrids!
