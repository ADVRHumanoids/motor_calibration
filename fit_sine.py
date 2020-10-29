#!/usr/bin/python3

import numpy, scipy.optimize


def sinfunc(t, A1, p1, c):
    return sine_1(t=t, A1=A1, w1=1., p1=p1, c=c)

def sine_1(t, A1, w1, p1, c):
    return A1 * numpy.sin(w1 * t + p1) + c

def fit_sin1(tt, yy, fit_w=False):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
    tt = numpy.array(tt)
    yy = numpy.array(yy)
    ff = numpy.fft.fftfreq(len(tt), (tt[1]-tt[0]))   # assume uniform spacing
    Fyy = abs(numpy.fft.fft(yy))
    guess_amp = numpy.std(yy) * 2.**0.5
    guess_offset = numpy.mean(yy)

    if fit_w:
        guess_freq = abs(ff[numpy.argmax(Fyy[1:])+1])   # excluding the zero frequency "peak", which is related to offset
        guess = numpy.array([guess_amp, 2.*numpy.pi*guess_freq, 0., guess_offset])
        popt, pcov = scipy.optimize.curve_fit(sine_1, tt, yy, p0=guess)
        A1, w1, p1, c = popt
    else:
        guess = numpy.array([guess_amp, 0., guess_offset])
        popt, pcov = scipy.optimize.curve_fit(sinfunc, tt, yy, p0=guess)
        A1, p1, c = popt
        w1 = 1.

    f1 = w1/(2.*numpy.pi)
    # fitfunc = lambda t: A * numpy.sin(w*t + p) + c
    return {
        "c" : c, # offset
        "a1" : A1, # amp
        "w1" : w1, # omega
        "p1" : p1, # phase
        "f1" : f1, # freq
        "per1": 1. / f1, #period
        # "fitfunc": fitfunc,
        "maxcov": numpy.max(pcov),
        "rawres": (guess, popt, pcov)
    }


def sin2func(t, A1, A2, p1, p2, c):
    return sine_2(t=t, A1=A1, A2=A2, w1=1., w2=2., p1=p1, p2=p2, c=c)

def sine_2(t, A1, A2, w1, w2, p1, p2, c):
    return A1 * numpy.sin(w1 * t + p1) + \
           A2 * numpy.sin(w2 * t + p2) + c

def fit_sin2(tt, yy, fit_w=False):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
    tt = numpy.array(tt)
    yy = numpy.array(yy)
    ff = numpy.fft.fftfreq(len(tt), (tt[1] - tt[0]))  # assume uniform spacing
    Fyy = abs(numpy.fft.fft(yy))
    guess_a = numpy.std(yy) * 2.**0.5
    guess_c = numpy.mean(yy)

    if fit_w:
        guess_w = 2. * numpy.pi * abs(ff[numpy.argmax(Fyy[1:]) + 1])  # excluding the zero frequency "peak", which is related to offset
        guess = numpy.array([
            guess_a/2, guess_a / 4,
            guess_w  , guess_w * 2,
            0., 0.,
            guess_c
        ])
        popt, pcov = scipy.optimize.curve_fit(sine_2, tt, yy, p0=guess)
        A1, A2, w1, w2, p1, p2, c = popt

    else:
        guess = numpy.array([
            guess_a/2, guess_a / 4,
            0., 0.,
            guess_c
        ])
        popt, pcov = scipy.optimize.curve_fit(sin2func, tt, yy, p0=guess)
        A1, A2, p1, p2, c = popt
        w1 = 1.
        w2 = 2.
    
    f1 = w1 / (2. * numpy.pi)
    f2 = w2 / (2. * numpy.pi)
    # fitfunc =  lambda t: A1 * numpy.sin(w1 * t + p1) + A2 * numpy.sin(w2 * t + p2) + c
    return {
        "c" : c, # offset
        "a1" : A1, # amp
        "a2" : A2, # amp
        "w1" : w1, # omega
        "w2" : w2, # omega
        "p1" : p1, # phase
        "p2" : p2, # phase
        "f1" : f1, # freq
        "f2" : f2, # freq
        "per1": 1. / f1, #period
        "per2": 1. / f2, #period
        # "fitfunc": fitfunc,
        "maxcov": numpy.max(pcov),
        "rawres": (guess, popt, pcov)
    }


def sin3func(t, A1, A2, A3, w3, p1, p2, p3, c):
    return sine_3(t=t, A1=A1, A2=A2, A3=A3, w1=1., w2=2., w3=4., p1=p1, p2=p2, p3=p3, c=c)

def sine_3(t, A1, A2, A3, w1, w2, w3, p1, p2, p3, c):
    return A1 * numpy.sin(w1 * t + p1) + \
           A2 * numpy.sin(w2 * t + p2) + \
           A3 * numpy.sin(w3 * t + p3) + c

def fit_sin3(tt, yy, fit_w=False):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
    tt = numpy.array(tt)
    yy = numpy.array(yy)
    ff = numpy.fft.fftfreq(len(tt), (tt[1] - tt[0]))  # assume uniform spacing
    Fyy = abs(numpy.fft.fft(yy))
    guess_a = numpy.std(yy) * 2.**0.5
    guess_c = numpy.mean(yy)

    if fit_w:
        guess_w = 2. * numpy.pi * abs(ff[numpy.argmax(Fyy[1:]) + 1])  # excluding the zero frequency "peak", which is related to offset
        guess = numpy.array([
            guess_a / 2, guess_a / 4, guess_a / 8,
            guess_w    , guess_w * 2, guess_w * 4,
            0., 0., 0.,
            guess_c
        ])
        popt, pcov = scipy.optimize.curve_fit(sine_3, tt, yy, p0=guess)
        A1, A2, A3, w1, w2, w3, p1, p2, p3, c = popt

    else:
        guess_w3 = 4.
        guess = numpy.array([
            guess_a / 2, guess_a / 4, guess_a / 8,
            guess_w3,
            0., 0., 0.,
            guess_c
        ])
        popt, pcov = scipy.optimize.curve_fit(sin3func, tt, yy, p0=guess)
        A1, A2, A3, w3, p1, p2, p3, c = popt
        w1 = 1.
        w2 = 2.
        #w3 = 4.

    f1 = w1 / (2. * numpy.pi)
    f2 = w2 / (2. * numpy.pi)
    f3 = w3 / (2. * numpy.pi)
    # fitfunc =  lambda t: A1 * numpy.sin(w1 * t + p1) + A2 * numpy.sin(w2 * t + p2) + A3 * numpy.sin(w3 * t + p3) + c
    return {
        "c" : c, # offset
        "a1" : A1, # amp
        "a2" : A2, # amp
        "a3" : A3, # amp
        "w1" : w1, # omega
        "w2" : w2, # omega
        "w3" : w3, # omega
        "p1" : p1, # phase
        "p2" : p2, # phase
        "p3" : p3, # phase
        "f1" : f1, # freq
        "f2" : f2, # freq
        "f3" : f3, # freq
        "per1": 1. / f1, #period
        "per2": 1. / f2, #period
        "per3": 1. / f3, #period
        # "fitfunc": fitfunc,
        "maxcov": numpy.max(pcov),
        "rawres": (guess, popt, pcov)
    }
