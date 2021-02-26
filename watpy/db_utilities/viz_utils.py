import matplotlib.pyplot as plt
import numpy as np

index_keys = ["id_eos", "id_gw_frequency_Momega22", "id_mass_ratio", "grid_spacing_min"]

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


h5_labels = {'rh_22' : 'h',
			 'rpsi4_22' : r'\Psi^4'}

def read_float_mdata(db, key, dbtype='index'):
	"""
	Given a database and key, reads the values corresponding
	to the given key for all entries in the database and 
	returns them as a numpy array.
	--------
	Input:
	--------
	db  	 : Database to consider 
	key 	 : Metadata key to plot [string]
	label 	 : Label to use for the metadata attribute [string]
	dbtype   : Type of database (defaults to 'index')
	
	--------
	Output:
	--------
	arr 	 : Numpy array of floating-point values

	"""
	arr = np.array([])
	for sim in db.values():
		if dbtype=='index':
			val = float(sim[key])
		else:
			val = float(sim.mdata[key])
		#
		arr = np.append(arr, val)
	#
	return arr
#

def read_mdata(db, key, dbtype='index'):
	"""
	Given a database and key, reads the values corresponding
	to the given key for all entries in the database and 
	returns them as a list.
	--------
	Input:
	--------
	db  	 : Database to consider
	key 	 : Metadata key to plot
	label 	 : Label to use for the metadata attribute
	dbtype   : Type of database (defaults to 'index')
	
	--------
	Output:
	--------
	arr 	 : List of literal metadata values
	
	"""
	arr = []
	for sim in db.values():
		if dbtype=='index':
			val = sim[key]
		else:
			val = sim.mdata[key]
		#
		arr.append(val)
	#
	return arr
#

def plot_float(db, key, label, dbtype='index', output=None):
	"""
	Plot histograms representing database population 
	distribution in terms of a given floating-point 
	metadata attribute.
	--------
	Input:
	--------
	db  	 : Database to consider
	key 	 : Metadata key to plot
	label 	 : Label to use for the metadata attribute
	dbtype   : Type of database (defaults to 'index')
	output   : If not None, saves the figure under the given name
			   (Specify extension in the output name, e.g. 'test.pdf')
	"""
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
		arr = read_float_mdata(db, key, dbtype)
		#
	ax.set_xlabel(label)
	ax.set_ylabel(r'$N_\mathrm{models}$')

	ax.hist(arr)

	if output:
		plt.savefig(output)
	#
#

def plot_literal(db, key, dbtype='index', output=None):
	"""
	Plot histograms representing database population 
	distribution in terms of a given floating-point 
	metadata attribute.
	--------
	Input:
	--------
	db  	 : Database to consider
	key 	 : Metadata key to plot
	label 	 : Label to use for the metadata attribute
	dbtype   : Type of database (defaults to 'index')
	output   : If not None, saves the figure under the given name
			   (Specify extension in the output name, e.g. 'test.pdf')
	"""	
	fig_s = plt.figure()
	ax    = fig_s.add_subplot(111)

	par = []

	par = read_mdata(db, key, dbtype)	

	labels, counts = np.unique(par,return_counts=True)

	ticks = range(len(counts))
	ax.bar(ticks,counts, align='center')
	ax.set_ylabel(r'$N_\mathrm{models}$')
	plt.xticks(ticks, labels, rotation='vertical')

	if output:
		plt.savefig(output)
	#
#

def plot_single(u, var, lbl, output=None):
	"""
	Plot a single variable (h or Psi4).
	---------
	Input:
	---------
	u        : Tortoise coordinate
	var		 : Complex-valued variable to plot
	output   : If not None, saves the figure under the given name
			   (Specify extension in the output name, e.g. 'test.pdf')
	"""
	# Set legend font
	params = {'legend.fontsize': 14,
	          'legend.handlelength': 2}
	plt.rcParams.update(params)

	fig = plt.figure()
	ax  = fig.add_subplot(111)

	# Set axis labels
	ax.set_xlabel(r'$u\, M_\odot$', fontsize=14)
	ax.set_ylabel(r'$r\, %s_{22}$' % h5_labels[lbl], fontsize=14)

	# Plot real and imaginary part of the strain
	ax.plot(u,var.real, color='b', 
		label=r'$r \mathcal{Re}\, (%s)$' % h5_labels[lbl])
	ax.plot(u,var.imag, color='g', 
		label=r'$r \mathcal{Ie}\, (%s)$' % h5_labels[lbl])

	# Plot legend
	ax.legend(ncol=1, loc='upper right')

	# Fix range
	ax.set_xlim([u.min(), u.max()])

	if output:
		plt.savefig(output)
	#
#

def plot_both(hu, hy, pu, py, output=None):
	"""
	Plot both variables (h and Psi4), if available.
	---------
	Input:
	---------
	hu       : Tortoise coordinate for the strain
	hy		 : Complex-valued strain
	pu       : Tortoise coordinate for the Weyl Scalar
	py		 : Complex-valued Weyl Scalar
	output   : If not None, saves the figure under the given name
			   (Specify extension in the output name, e.g. 'test.pdf')
	"""
	# Set legend font
	params = {'legend.fontsize': 14,
	          'legend.handlelength': 2}
	plt.rcParams.update(params)

	fig, axes = plt.subplots(2, 1, sharex=True)

	# Set axis labels
	axes[1].set_xlabel(r'$u\, M_\odot$', fontsize=14)
	axes[1].set_ylabel(r'$r\, %s_{22}$' % h5_labels['rpsi4_22'], fontsize=14)
	axes[0].set_ylabel(r'$r\, %s_{22}$' % h5_labels['rh_22'], fontsize=14)

	# Plot real and imaginary part of strain and Weyl scalar
	axes[0].plot(hu,hy.real, color='b', 
		label=r'$\mathcal{Re}$')
	axes[0].plot(hu,hy.imag, color='g', 
		label=r'$\mathcal{Im}$')

	axes[1].plot(pu,py.real, color='b')
	axes[1].plot(pu,py.imag, color='g')

	# Plot legend
	axes[0].legend(ncol=1, loc='upper right')

	# Fix range
	axes[0].set_xlim([hu.min(), hu.max()])

	if output:
		plt.savefig(output)
	#
#
