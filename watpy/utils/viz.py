import matplotlib.pyplot as plt
import numpy as np


def wplot(t,h, omega=None, to_file=None):
        """
	Plot a waveform
	---------
	Input:
	---------
	t        : time
	var	 : complex-valued variable to plot
        omega    : frequency. If provided, produce two panels plot
	to_file  : filename to write (optional)
	---------
	Output:
	---------
        return the figure and axes object
	"""
        if omega is not None:
                fig, ax = plt.subplots(2,1, sharex=True)
                ax[0].plot(t, h.real, label='Real part')
                ax[0].plot(t, np.abs(h), label='Amplitude')
                ax[1].plot(t, omega)
                ax[1].set_ylabel('Frequency')
                ax[1].set_xlabel('time')
                ax[0].set_ylabel('Waveform')
                ax[0].set_xlim([0, t.max()])
                ax[1].set_xlim([0, t.max()])
                ax[0].legend()
        else:
                fig, ax = plt.subplots(1,1)
                ax.plot(t, h.real, label='Real part')
                ax.plot(t, h.imag, label='Imag part')
                ax.set_xlabel('time')
                ax.set_ylabel('Waveform')
                ax.set_xlim([0, t.max()])
                ax.legend()
        if to_file: plt.savefig(to_file)                
        return fig, ax
        

def mplot(mdlist, key, to_float=False, to_file=None):
        """
        Attempt plot of metadata list, given a key
        """
        fig, ax = plt.subplots(1,1)
        if to_float:
                val = np.array([float(m.data[key]) for m in mdlist])
                ax.hist(val)
                ax.set_xlabel(key)
        else:
                val = [m.data[key] for m in mdlist]
                labels, counts = np.unique(val,return_counts=True)
                ticks = range(len(counts))
                ax.bar(ticks,counts, align='center')
                ax.set_xticks(ticks)
                ax.set_xticklabels(labels,rotation=90, ha='center')
        if to_file: plt.savefig(to_file)
        return fig, ax
