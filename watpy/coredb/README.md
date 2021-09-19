# Scripts for managing the CoRe DB

Database structure

     + DBDIR/
     | + <database_key>/
     | |	        * metadata.txt 
     | |                * data.h5

The database key is composed as
    <database_key> = <code>:<simulation_number>:R<run_number>

Typical workflow for adding new simulations:
1. Generate the h5 data from raw data
2. Deploy new simlation to the repository

An example is provided in tutorials/



The directory './TESTDB/' is supposed to have the same structure of the db and can be used to test some of these scripts. 
(read the README inside) 

Simulation metadata are managed with Python scripts. Metadata are stored as dictionary, so the "simulation list" is a list of dictionary. 

