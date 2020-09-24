# Scripts for managing the db #

Database structure

     + DBDIR/
     | + <database_key>/
     | |	       * metadata.txt 
     | |         * data.h5

The database key is composed as
    <database_key> = <id_code>:<simulation_number>:R<run_number>

Typical workflow for adding new simulations:
1. Generate the h5 data from raw data
2. Deploy new simlation to the repository

(An example is provided in examples/db_examples.py)

The directory './TESTDB/' is supposed to have the same structure of the db and can be used to test some of these scripts. 
(read the README inside) 

Simulation metadata are managed with Python scripts. Metadata are stored as dictionary, so the "simulation list" is a list of dictionary. 


## db_utilities

### dbutils.py

Contains classes for database and single simulation handling.

### h5_utils.py

Contains the class wrapping the HDF5-related routines.

### metadata_utils.py

Contains all metadata handling routines.

### simlist_utils.py

Contains the routines called upon by the database and simulation classes.
