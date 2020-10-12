import matplotlib.pyplot as plt
import numpy as np

index_keys = ["id_eos", "id_gw_frequency_Momega22", "id_mass_ratio"]

database_keys = ['id_code', 'id_type', 'id_mass', 'id_rest_mass', 'id_mass_ratio', 'id_ADM_mass', 'id_ADM_angularmomentum', 
				 'id_gw_frequency_Hz', 'id_gw_frequency_Momega22', 'id_eos', 'id_kappa2T', 'id_Lambda', 'id_mass_starA', 
				 'id_rest_mass_starA', 'id_mass_starB', 'id_rest_mass_starB']

labels = {'id_mass' : r'$M_{g}\, [\mathrm{M}_\odot]$',
		  'id_rest_mass' : r'$M_{b}\, [\mathrm{M}_\odot]$',
		  'id_mass_ratio' : r'$M_{g}^{1} / M_{g}^{2}\, [\mathrm{M}_\odot]$',
		  'id_ADM_mass' : r'$M_\mathrm{ADM}\, [\mathrm{M}_\odot]$', 
		  'id_ADM_angularmomentum' : r'$J_{ADM}\, [\mathrm{M}_\odot]$', 
		  'id_gw_frequency_Hz' : r'$f_{22}^{ID}\, [\mathrm{Hz}]$', 
		  'id_gw_frequency_Momega22' : r'$M\omega_{22}^{ID}$',
		  'id_kappa2T' : r'$k2T$',
		  'id_Lambda' : r'$\Lambda$',
		  'id_mass_starA' : r'$M_{g}^{1}\, [\mathrm{M}_\odot]$',
		  'id_rest_mass_starA' : r'$M_{b}^{1}\, [\mathrm{M}_\odot]$',
		  'id_mass_starB' : r'$M_{g}^{2}\, [\mathrm{M}_\odot]$', 
		  'id_rest_mass_starB' : r'$M_{g}^{1}\, [\mathrm{M}_\odot]$'}


def read_float_mdata(db, key):
	arr = np.array([])
	for sim in db.values():
	    val = float(sim[key])
	    arr = np.append(arr, val)
	#
	return arr
#

def read_mdata(db, key):
	arr = np.array([])
	for sim in db.values():
	    val = sim[key]
	    arr = np.append(arr, val)
	#
	return arr
#

def plot_float(db, key, label, dbtype='index'):
	fig = plt.figure()
	ax = fig.add_subplot(111)

	if key == 'id_mass_ratio' and dbtype=='index':
		arr1 = read_float_mdata(db, 'id_mass_starA')
		arr2 = read_float_mdata(db, 'id_mass_starB')

		arr = np.zeros_like(arr1)
		arr = np.divide(arr1, arr2)

		for i in range(len(arr)):
			if arr[i]<1.0:
				arr[i] = 1./arr[i]
			#
		#
	else:
		arr = read_float_mdata(db, key)
	#
	ax.set_xlabel(label)
	ax.set_ylabel(r'$N_\mathrm{models}$')

	ax.hist(arr)
#

def plot_literal(db, key):
	fig_s = plt.figure()
	ax    = fig_s.add_subplot(111)

	par = []

	for sim in db.values():
	    var = sim[key]
	    par.append(var)
	#
	labels, counts = np.unique(par,return_counts=True)

	ticks = range(len(counts))
	ax.bar(ticks,counts, align='center')
	ax.set_ylabel(r'$N_\mathrm{models}$')
	plt.xticks(ticks, labels, rotation='vertical')
#