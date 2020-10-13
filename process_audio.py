import os
import glob
import numpy as np
import scipy.fftpack
from matplotlib import pyplot as plt

import record_utils


def process(fname='null', max_freq=200, x_scale=0, sample_rate=48000, plot_all=False):
    if fname=='null':
        list_of_files = glob.glob('/logs/*.npy.gz')
        fname = max(list_of_files, key=os.path.getctime)
    print('[i] processing audio')
    audio = record_utils.read_compressed(fname)

    n = len(audio)           # Number of samplepoints
    yf =scipy.fft(audio)
    T = 1/sample_rate
    xf = np.linspace(0.0, 1.0/(2.0 * T), n/2)

    fig, axs = plt.subplots()
    #axs.plot(xf, 2.0 / n * np.abs(yf[:n // 2]))
    axs.set_xlim(0, max_freq)
    for ii in range(0,len(xf)):
        if xf[ii]>=max_freq:
            break
    if x_scale!=0:
        axs.set_ylim(0, x_scale)

    axs.plot(xf[:ii], 2.0 / n * np.abs(yf[:ii]))

    axs.set_ylabel('Magnitude - log')
    axs.set_xlabel('Frequency (Hz)')
    axs.set_title('FFT', fontsize=16, fontweight="bold")
    axs.grid()
    #plt.xscale('log')

    if plot_all:
        plt.show()
    else:
        # Save the graph
        pdf_name = fname[:-7] + '.pdf'
        print('Saving graph as: ' + pdf_name)
        plt.savefig(fname=pdf_name, format='pdf')


if __name__ == "__main__":
    process()
