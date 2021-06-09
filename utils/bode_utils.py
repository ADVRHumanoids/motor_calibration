import math
import numpy as np
from scipy.fftpack import fft
from scipy.interpolate import interp1d

def nextpow2(x): return math.ceil(math.log2(abs(x)))
def mag2db(mag): return [20*math.log10(np.abs(m)) for m in mag]
def rangeFloat(start, stop, step): return [start+n*step for n in range(0,round((stop-start)/step))]

def bode(t, u, y, roi = [0.1, 100]):
    # Resample data based on timestep
    u, dt, _  = resampleUniformedData(t, u)
    y, dt, _  = resampleUniformedData(t, y, dt=dt)

    # FFT
    Fs      = 1/dt
    L       = len(t)
    NFFT    = 2**nextpow2(L)
    NFFT_2  = int(NFFT/2)
    Y       = fft(y,NFFT)/L
    f       = Fs/2*np.linspace(0, 1, NFFT_2)# NFFT/2+1)
    U       = fft(u,NFFT)/L
    H       = [y/u for y,u in zip(Y,U)]

    # Calculate amplitude in decibels
    mag     = [abs(h) for h in H[:NFFT_2]]
    mag_db  = mag2db(mag)

    # Calculate phase and unwrap it to obtain a continuous phase plot.
    phase = np.unwrap([np.angle(h) for h in H[:NFFT_2]]) # [:NFFT/2+1]
    #phase = [np.angle(h) for h in H[:NFFT_2]]
    # make sure phase is within [-2pi,0)
    #phase = [p-2*np.pi if p>0 else p for p in phase]

    return f, mag_db, phase


from matplotlib.mlab import csd, psd
def tfestimate(t, u, y, *args, **kwargs):
    """estimate transfer function from x to y, see csd for calling convention"""
    # Resample data based on timestep
    u, dt, _ = resampleUniformedData(t, u)
    y, dt, _ = resampleUniformedData(t, y, dt=dt)
    Fs    = 1/dt

    # https://stackoverflow.com/questions/28462144/
    Pyx, f = csd(u, y, Fs=Fs, *args, **kwargs)
    Pxx, f = psd(u, Fs=Fs, *args, **kwargs)
    return  Pyx/Pxx, f

def resampleUniformedData(time, data, dt=None):
    if dt==None:
        dt  = np.mean(np.diff(time))
    t_RS = rangeFloat(min(time), max(time), dt)
    data = interp1d(time, data)(t_RS)

    return data, dt, t_RS
