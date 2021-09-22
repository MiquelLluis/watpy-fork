# Classes for managing the CoRe DB

Database structure

     <path_db>/
     |--- <code>_<simulation_number>/
     |	  |--- R??/
     |	  |    | --- data.h5
     |	  |    | --- metadata.txt 
     ...   
     |	   | --- metadata_main.txt

The `database_key` of a simulation is composed as `<code>:<simulation_number>`, and as `<code>:<simulation_number>:R<run_number>` for a run in a simulation.

The `data.h5` contains groups and datasets as in the following example:

```
$ h5dump -n data.h5

HDF5 "data.h5" {
FILE_CONTENTS {
 group      /
 group      /energy
 dataset    /energy/EJ_r00550.txt
 dataset    /energy/EJ_r00600.txt
 dataset    /energy/EJ_r00650.txt
 dataset    /energy/EJ_r00700.txt
 dataset    /energy/EJ_r00800.txt
 dataset    /energy/EJ_r00850.txt
 group      /horizon
 dataset    /horizon/horizon_0
 group      /rh_22
 dataset    /rh_22/Rh_l2_m2_r00550.txt
 dataset    /rh_22/Rh_l2_m2_r00600.txt
 dataset    /rh_22/Rh_l2_m2_r00650.txt
 dataset    /rh_22/Rh_l2_m2_r00700.txt
 dataset    /rh_22/Rh_l2_m2_r00800.txt
 dataset    /rh_22/Rh_l2_m2_r00850.txt
 group      /rpsi4_22
 dataset    /rpsi4_22/Rpsi4_l2_m2_r00550.txt
 dataset    /rpsi4_22/Rpsi4_l2_m2_r00600.txt
 dataset    /rpsi4_22/Rpsi4_l2_m2_r00650.txt
 dataset    /rpsi4_22/Rpsi4_l2_m2_r00700.txt
 dataset    /rpsi4_22/Rpsi4_l2_m2_r00800.txt
 dataset    /rpsi4_22/Rpsi4_l2_m2_r00850.txt
 }
}
```

The naming convention and structure of the waveform .txt data is as follows.

Psi4 mode:

```
$ head Rpsi4_l2_m2_r00550.txt

# r=5.500000e+02
# M=2.728000e+00
# u/M:0 Reh/M:1 Imh/M:2 Momega:3 A/M:4 phi:5 t:6
-1.551895954766290515e+02 4.952638982383438915e+00 -3.107133889787561110e+00 -4.581621383784686453e-03 5.846615593562694002e+00 5.603013021802030202e-01 0.000000000000000000e+00
-1.540165749487698008e+02 4.822284490267165324e+00 -2.986663714318995133e+00 -4.581621383784686453e-03 5.672264789967142562e+00 5.545233476776169068e-01 3.200000000000000178e+00
...
``

Mode strain:

``
$ head Rh_l2_m2_r00650.txt

# r=6.500000e+02
# M=2.728000e+00
# u/M:0 RePsi4/M:1 ImPsi4/M:2 Momega:3 A/M:4 phi:5 t:6
-1.551895954766290515e+02 -8.419801343884962815e-06 5.956452012731991777e-05 9.405315902998562889e-04 6.015667138953406765e-05 -1.711221937370974056e+00 0.000000000000000000e+00
-1.540165749487698008e+02 -8.418294706221636761e-06 6.003670635339642699e-05 9.405315902998562889e-04 6.062403645027893980e-05 -1.710107178985631693e+00 3.200000000000000178e+00
...
```

Energy

```
$ head EJ_r00550.txt

# r=4.000000e+02
# M=2.728000e+00
# J_orb:0 E_b:1 u/M:2 E_rad:3 J_rad:4 t:5
3.977433974596021216e+00 -3.665689149560168864e-02 -1.551895954766290515e+02 0.000000000000000000e+00 0.000000000000000000e+00 0.000000000000000000e+00
3.977434294645028956e+00 -3.665692520332061721e-02 -1.540165749487698008e+02 2.298866436277792839e-08 -5.954498992288903310e-07 3.200000000000000178e+00
...
```
