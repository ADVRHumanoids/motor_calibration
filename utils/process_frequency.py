#!/usr/bin python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import math
import numpy as np
from scipy import signal
from scipy.optimize import leastsq
# tell matplotlib not to try to load up GTK as it returns errors over ssh
from matplotlib import use as plt_use
plt_use("Agg")
from matplotlib import pyplot as plt
import control

# custom files
try:
    from utils import bode_utils
    from utils import plot_utils
except ImportError:
    import plot_utils
    import bode_utils

def process(yaml_file, plot_all=False):
    plt.rcParams['savefig.dpi'] = 300

    # read parameters from yaml file
    print('[i] Using yaml_file: ' + yaml_file)
    with open(yaml_file) as f:
        try:
            out_dict = yaml.safe_load(f)
        except Exception:
            raise Exception('error in yaml parsing')

    # find logs
    if 'location' in out_dict['log']:
        head = out_dict['log']['location']
    else:
        head, _ = os.path.split(yaml_file)

    if 'name' in out_dict['log']:
        code_string = out_dict['log']['name']
    else:
        _, tail = os.path.split(yaml_file)
        code_string = tail[:-len("-results.yaml")]

    # set path to save graphs
    if len(head)>6 and head[-6:]=='/logs/':
        new_head = f'{head[:-6]}/images/'
    else:
        new_head = f'{head}/images/'

    if os.path.isdir(new_head) is False:
        try:
            os.makedirs(new_head)
        except OSError:
            print("Creation of the directory %s failed" % new_head)
    image_base_path = new_head +f'{code_string}_frequency-calib'

    log_file = head + f'{code_string}_frequency-calib.log'
    print('[i] Reading log_file: ' + log_file)

    # log format: '%u64\t%f\t%f\t%f\t%f'
    ns        = [np.uint64(x.split('\t')[0]) for x in open(log_file).readlines()]
    motor_tor = [    float(x.split('\t')[1]) for x in open(log_file).readlines()]
    i_q       = [    float(x.split('\t')[2]) for x in open(log_file).readlines()]
    i_fb      = [    float(x.split('\t')[3]) for x in open(log_file).readlines()]

    if not 'calib_freq' in out_dict:
        raise Exception("missing 'calib_freq' in yaml parsing")

    print(f'[i] Processing data (loaded {len(ns)} points)')

    fig, axs = plt.subplots(2)
    l0 = axs[0].plot([s/1e9 for s in ns[0:10000]], i_fb[0:10000], color='#8e8e8e', marker='.', markersize=0.2, linestyle="", label='current out fb (A)')
    l1 = axs[0].plot([s/1e9 for s in ns[0:10000]], i_q[0:10000], color='#1e1e1e', marker='.', markersize=0.2, linestyle="-", label='current reference (A)')
    l2 = axs[0].plot([s/1e9 for s in ns[0:10000]], motor_tor[0:10000], color='#1f77b4', marker='.', markersize=0.2, label='motor torque (Nm)', zorder=1)
    l3 = axs[1].plot([s/1e9 for s in ns], motor_tor, color='#1f77b4', marker='.', markersize=0.2, label='motor torque (Nm)')
    lgnd = axs[0].legend(loc='lower left')
    for handle in lgnd.legendHandles:
        handle._legmarker.set_markersize(6)

    # make plot pretty
    axs[0].set_xlabel('Time (s)')
    axs[1].set_xlabel('Time (s)')
    axs[1].set_ylabel('motor torque (Nm)')

    axs[0].set_xlim(ns[0]/1e9, ns[10000]/1e9)# first 15s
    axs[1].set_xlim(ns[0]/1e9, ns[-1]/1e9)

    plt_max = (max(motor_tor) -min(motor_tor)) * 0.05
    axs[1].set_ylim(min(motor_tor)-plt_max,max(motor_tor)+plt_max)
    plt_max = (max(motor_tor[0:10000]) -min(motor_tor[0:10000])) * 0.05
    axs[0].set_ylim(min(motor_tor[0:10000])-plt_max,max(motor_tor[0:10000])+plt_max)
    plt_max = (max(i_q[0:10000]) -min(i_q[0:10000])) * 0.05

    axs[0].grid(b=True, which='major', axis='x', linestyle=':')
    axs[0].grid(b=True, which='major', axis='y', linestyle='-')
    axs[0].grid(b=True, which='minor', axis='y', linestyle=':')
    axs[1].grid(b=True, which='major', axis='x', linestyle=':')
    axs[1].grid(b=True, which='major', axis='y', linestyle='-')
    axs[1].grid(b=True, which='minor', axis='y', linestyle=':')

    axs[0].spines['top'].set_visible(False)
    axs[0].spines['right'].set_visible(False)
    axs[1].spines['top'].set_visible(False)
    axs[1].spines['right'].set_visible(False)

    # Save the graph
    plt.tight_layout()
    fig_name = image_base_path + '_1.png'
    plt.savefig(fname=fig_name, format='png')
    print('[i] Saved graph as: ' + fig_name)
    if plot_all:
        plt.show()

    ## bode plot ----------------------------------------------------------------------------------------------------------------
    #bode wants even numer of data
    if len(ns)%2 !=0:
        ns = ns[:-1]
        motor_tor = motor_tor[:-1]
        i_q = i_q[:-1]

    # Only select frequencies used touched by the chirp
    w, mag, phase = bode_utils.bode([s/1e9 for s in ns],i_q,motor_tor)
    id_0= (np.abs(w - 0.1) <= 0.01).argmax()
    id_1= (np.abs(w - 50) <= 0.01).argmax()
    w_f = w[id_0:id_1+1]
    mag_f = mag[id_0:id_1+1]
    phase_f = phase[id_0:id_1+1]
    if np.mean(phase_f)<-2*np.pi:
        phase_f = [p+2*np.pi for p in phase_f]
    elif np.mean(phase_f)>0:
        phase_f = [p-2*np.pi for p in phase_f]
    complex_f = [(10**(m/20))*np.exp(1j*p) for m,p in zip(mag_f,phase_f)]

    # Filter signal
    b,a = signal.butter(2, 0.002, btype='lowpass')
    # padlen is needed: see https://dsp.stackexchange.com/questions/11466/#47945
    mag_filt = signal.filtfilt(b,a, mag_f, padlen=3*(max(len(b),len(a))-1))
    phase_filt = signal.filtfilt(b,a, phase_f, padlen=3*(max(len(b),len(a))-1))
    # while testing we found that using complex_f form filtered frequencies gave worse results
    # complex_f = [(10**(m/20))*np.exp(1j*p) for m,p in zip(mag_filt, phase_filt)]

    # get first estimate of natural freq and dc gain
    wf_0=w_f[np.where(mag_filt == max(mag_filt))][0]
    torque_const = float(out_dict['results']['flash_params']['motorTorqueConstant']) * float(out_dict['results']['flash_params']['Motor_gear_ratio'])

    print("[i] Starting scipy.leastsq")
    # 2poles 0zeros system
    def tf20(p,w):
        s=1j*w
        k,wf,z = p #p=[g,ωf,ζ]
        return k*(wf**2)/(s**2+s*z*wf+wf**2)
    def residuals20(p,y,x):
        a = y-tf20(p,x)
        return a.real**2 + a.imag**2

    p_lsq20=[torque_const, wf_0, 1/math.sqrt(wf_0)]
    print("guess_lsq20: ", p_lsq20)
    (p_lsq20, _) = leastsq(residuals20, x0=p_lsq20, args=(complex_f,w_f))
    h_lsq20 = [tf20(p_lsq20,w) for w in w_f]
    print("param_lsq20: ", p_lsq20)
    NRMSE_lsq20 = np.abs(np.sqrt(np.mean(np.square([complex_f[v] - h_lsq20[v] for v in range(0,len(w_f))])))/(max(complex_f)-min(complex_f)))
    print("NRMSE_lsq20: ", NRMSE_lsq20)
    tf_lsq20 = p_lsq20[0]*(p_lsq20[1]**2)/(control.TransferFunction.s**2+control.TransferFunction.s*2*p_lsq20[1]*p_lsq20[2]+p_lsq20[1]**2)
    print("TF_lsq20: ", tf_lsq20)

    # 3poles 1zero system
    def tf31(p,w):
        s=1j*w
        k,b0,a0,a1,a2 = p
        return k*(s+b0)/(s**3+(s**2)*a0+s*a1+a2)
    def residuals31(p,y,x):
        a = y-tf31(p,x)
        return a.real**2 + a.imag**2

    p_lsq31= [torque_const, 0.0, 2*p_lsq20[1]*p_lsq20[2], p_lsq20[1]**2, 0.0]
    (p_lsq31, _) = leastsq(residuals31, x0=p_lsq31, args=(complex_f,w_f), maxfev=20000)
    h_lsq31 = [tf31(p_lsq31,w) for w in w_f]
    print("param_lsq31: ", p_lsq31)
    NRMSE_lsq31 = np.abs(np.sqrt(np.mean(np.square([complex_f[v] - h_lsq31[v] for v in range(0,len(w_f))])))/(max(complex_f)-min(complex_f)))
    print("NRMSE_lsq31: ", NRMSE_lsq31)
    tf_lsq31 = p_lsq31[0]*(control.TransferFunction.s+p_lsq31[1])/(control.TransferFunction.s**3+(control.TransferFunction.s**2)*p_lsq31[2]+control.TransferFunction.s*p_lsq31[3]+p_lsq31[4])
    print("TF_lsq31: ", tf_lsq31)

    Ts = 0.001
    from matplotlib import mlab
    def tfestimate(x, y, *args, **kwargs):
        """estimate transfer function from x to y, see csd for calling convention"""
        # https://stackoverflow.com/questions/28462144/python-version-of-matlab-signal-toolboxs-tfestimate
        Pyx, f = mlab.csd(x, y, *args, **kwargs)
        Pxx, f = mlab.psd(x, *args, **kwargs)
        return  [pyx / pxx for pyx, pxx in zip(Pyx, Pxx)], f
    tf_est, f_est = tfestimate(i_q, motor_tor, Fs=1/Ts)

    from statsmodels.tsa.arima.model import ARIMA
    import pandas as pd
    exog_data,  dt, t_RS = bode_utils.resampleUniformedData(ns, i_q, dt=1e6) # 1ms = 10^6ns
    endog_data, dt, t_RS = bode_utils.resampleUniformedData(ns, motor_tor, dt=dt)
    t_RS=[np.uint64(s)-ns[0] for s in t_RS]

    exog=pd.DataFrame({'i_q': exog_data}, index=t_RS)
    exog.index=pd.to_datetime(exog.index)
    exog.index.name = 'Time'
    exog = exog.resample("L").last()
    #print(exog.head())
    #print("\n")

    endog=pd.DataFrame({'motor_tor':endog_data}, index=t_RS)
    endog.index=pd.to_datetime(endog.index)
    endog.index.name = 'Time'
    endog = endog.resample("L").last()
    #print(endog.head())

    model = ARIMA(endog=endog, exog=exog.dropna(), order=(4, 0, 3), enforce_stationarity=True, enforce_invertibility=False)#, freq='L')
    # model = ARIMA(endog=endog, exog=exog, order=(2, 0, 0), enforce_stationarity=True, enforce_invertibility=False)#, freq='L')
    print("[i] Started ARMA parameter estimation")
    results = model.fit()
    print(results.summary())


    predictions_ARIMA_diff = pd.Series(results.fittedvalues, copy=True)
    # predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()
    # predictions_ARIMA = pd.Series(endog['motor_tor'].iloc[0], index=endog.index)
    # predictions_ARIMA = predictions_ARIMA.add(predictions_ARIMA_diff_cumsum, fill_value=0)
    # print('predictions_ARIMA.head():\n',predictions_ARIMA.head())

    fig, axs = plt.subplots(2)
    axs[0].plot(endog, '.', label='motor_tor')
    axs[0].plot(predictions_ARIMA_diff, '.', label='predictions_ARIMA_diff', alpha=0.5)
    axs[1].plot(t_RS, [v-v_est for v,v_est in zip(endog['motor_tor'],predictions_ARIMA_diff)])

    axs[0].grid(b=True, which='major', axis='x', linestyle='-')
    axs[0].grid(b=True, which='minor', axis='x', linestyle=':')
    axs[0].grid(b=True, which='major', axis='y', linestyle='-')
    axs[1].grid(b=True, which='major', axis='x', linestyle='-')
    axs[1].grid(b=True, which='minor', axis='x', linestyle=':')
    axs[1].grid(b=True, which='major', axis='y', linestyle='-')

    # Save the graph
    fig_name = image_base_path + '_2b.png'
    plt.savefig(fname=fig_name, format='png', bbox_inches='tight')
    print('[i] Saved graph as: ' + fig_name)
    if plot_all:
        plt.show()

    print('results:', results.specification)
    print('\naic',results.aic)
    print('\naicc',results.aicc)
    print('\narfreq',results.arfreq)
    print('\narparams',results.arparams)
    print('\narroots',results.arroots)
    print('\nbic',results.bic)
    print('\nbse',results.bse)
    print('\nhqic',results.hqic)
    print('\nllf',results.llf)
    print('\nllf_obs',results.llf_obs)
    print('\nmae',results.mae)
    print('\nmafreq',results.mafreq)
    print('\nmaparams',results.maparams)
    print('\nmaroots',results.maroots)
    print('\nmse',results.mse)
    print('\npvalues',results.pvalues)
    print('\nsse',results.sse)
    print('\ntvalues',results.tvalues)
    print('\nuse_t',results.use_t)
    print('\nzvalues',results.zvalues)
    #print('\nstates',results.states)

    print('\npoles: ', np.roots(results.polynomial_ar[::-1]))
    print('zeros: ', np.roots(results.polynomial_ma[::-1]))

    import control
    #z= control.TransferFunction.z
    z = control.tf([1, 0], 1, 0.001)

    Az = 1/ (sum(a * (z**(k)) for k, a in enumerate(results.polynomial_ar[::-1])))
    Bz = sum(b * (z**(k)) for k, b in enumerate(results.polynomial_ma[::-1]))
    Hz=Bz*Az*z
    print('Hz:\n',Hz)

    magz, phasez, omegaz = control.bode(Hz, dB=True, Hz=True, plot=False)
    omegaz = omegaz/(2*np.pi) # convert form rad/s to Hz

    # plot bode
    fig, axs = plt.subplots(2)
    axs[0].semilogx(w_f, mag_f, color='#8e8e8e', marker='.', markersize=0.5, linestyle="", label='datapoints') # Bode magnitude plot
    axs[0].semilogx(w_f, mag_filt, color='#1e1e1e', marker='.', markersize=0.5, linestyle="", label='filtered')
    axs[0].semilogx(w_f, [20*math.log10(np.abs(m)) for m in h_lsq20], marker='.', markersize=0.5, linestyle="", label='model(2,0)')
    axs[0].semilogx(w_f, [20*math.log10(np.abs(m)) for m in h_lsq31], marker='.', markersize=0.5, linestyle="", label='model(3,1)')
    axs[0].semilogx(omegaz, [20*math.log10(m) for m in magz], color='#ff2f0e', marker='.', markersize=0.5, linestyle="", label=f"ARMA[{results.specification.k_ar}, {results.specification.k_ma}]")
    lgnd = axs[0].legend()
    for handle in lgnd.legendHandles:
        handle._legmarker.set_markersize(6)

    axs[1].semilogx(w_f, phase_f, color='#8e8e8e', marker='.', markersize=0.5, linestyle="", label='datapoints') # Bode phase plot
    axs[1].semilogx(w_f, phase_filt, color='#1e1e1e', marker='.', markersize=0.5, linestyle="", label='filtered')
    axs[1].semilogx(w_f, np.unwrap([np.angle(p) for p in h_lsq20]), marker='.', markersize=0.5, linestyle="", label='model(2,0)')
    axs[1].semilogx(w_f, np.unwrap([np.angle(p) for p in h_lsq31]), marker='.', markersize=0.5, linestyle="", label='model(3,1)')
    axs[1].semilogx(omegaz, phasez, color='#ff2f0e', marker='.', markersize=0.5, linestyle="", label=f"ARMA[{results.specification.k_ar}, {results.specification.k_ma}]")
    lgnd = axs[1].legend()
    for handle in lgnd.legendHandles:
        handle._legmarker.set_markersize(6)

    # make plot pretty
    axs[0].set_ylabel('Magnitude (dB)')
    axs[1].set_ylabel('Phase (rad)')
    axs[1].set_xlabel('Frequency (Hz)')

    axs[0].set_xlim(1, 50)
    axs[0].set_ylim(math.floor(min(mag_f)/10)*10,math.ceil(max(mag_f)/10)*10)
    axs[0].grid(b=True, which='major', axis='x', linestyle='-')
    axs[0].grid(b=True, which='minor', axis='x', linestyle=':')
    axs[0].grid(b=True, which='major', axis='y', linestyle='-')
    axs[0].yaxis.set_major_locator(plt.MultipleLocator(10))
    axs[0].yaxis.set_minor_locator(plt.MultipleLocator(10/3))

    axs[1].set_xlim(1, 50)
    axs[1].set_ylim(-2*np.pi,0)
    axs[1].grid(b=True, which='major', axis='x', linestyle='-')
    axs[1].grid(b=True, which='minor', axis='x', linestyle=':')
    axs[1].grid(b=True, which='major', axis='y', linestyle='-')
    axs[1].yaxis.set_major_locator(plt.MultipleLocator(np.pi / 2))
    axs[1].yaxis.set_minor_locator(plt.MultipleLocator(np.pi / 6))
    axs[1].yaxis.set_major_formatter(
        plt.FuncFormatter(
            plot_utils.multiple_formatter(denominator=4,
                                          number=np.pi,
                                          latex='\pi')))


    # Save the graph
    fig_name = image_base_path + '_2.png'
    plt.savefig(fname=fig_name, format='png', bbox_inches='tight')
    print('[i] Saved graph as: ' + fig_name)
    if plot_all:
        plt.show()

    # plot
    fig, axs = plt.subplots(2)
    axs[0].plot(w_f, mag_f, color='#8e8e8e', marker='.', markersize=0.5, linestyle="", label='datapoints') # Bode magnitude plot
    axs[0].plot(w_f, mag_filt, color='#1e1e1e', marker='.', markersize=0.5, linestyle="", label='filtered')
    axs[0].plot(w_f, [20*math.log10(np.abs(m)) for m in h_lsq20], marker='.', markersize=0.5, linestyle="", label='model(2,0)')
    axs[0].plot(w_f, [20*math.log10(np.abs(m)) for m in h_lsq31], marker='.', markersize=0.5, linestyle="", label='model(3,1)')
    lgnd = axs[0].legend()
    for handle in lgnd.legendHandles:
        handle._legmarker.set_markersize(6)

    axs[1].plot(w_f, phase_f, color='#8e8e8e', marker='.', markersize=0.5, linestyle="", label='datapoints') # Bode phase plot
    axs[1].plot(w_f, phase_filt, color='#1e1e1e', marker='.', markersize=0.5, linestyle="", label='filtered')
    axs[1].plot(w_f, np.unwrap([np.angle(p) for p in h_lsq20]), marker='.', markersize=0.5, linestyle="", label='model(2,0)')
    axs[1].plot(w_f, np.unwrap([np.angle(p) for p in h_lsq31]), marker='.', markersize=0.5, linestyle="", label='model(3,1)')
    lgnd = axs[1].legend()
    for handle in lgnd.legendHandles:
        handle._legmarker.set_markersize(6)

    # make plot pretty
    axs[0].set_ylabel('Magnitude (dB)')
    axs[1].set_ylabel('Phase (rad)')
    axs[1].set_xlabel('Frequency (Hz)')

    axs[0].set_xlim(1, 50)
    axs[0].set_ylim(math.floor(min(mag_f)/10)*10,math.ceil(max(mag_f)/10)*10)
    axs[0].grid(b=True, which='major', axis='x', linestyle=':')
    axs[0].grid(b=True, which='major', axis='y', linestyle='-')
    axs[0].yaxis.set_major_locator(plt.MultipleLocator(10))
    axs[0].yaxis.set_minor_locator(plt.MultipleLocator(10/3))

    axs[1].set_xlim(1, 50)
    axs[1].set_ylim(-2*np.pi,0)
    axs[1].grid(b=True, which='major', axis='x', linestyle=':')
    axs[1].grid(b=True, which='major', axis='y', linestyle='-')
    axs[1].yaxis.set_major_locator(plt.MultipleLocator(np.pi / 2))
    axs[1].yaxis.set_minor_locator(plt.MultipleLocator(np.pi / 6))
    axs[1].yaxis.set_major_formatter(
        plt.FuncFormatter(
            plot_utils.multiple_formatter(denominator=4,
                                          number=np.pi,
                                          latex='\pi')))

    # Save the graph
    fig_name = image_base_path + '_3.png'
    plt.savefig(fname=fig_name, format='png', bbox_inches='tight')
    print('[i] Saved graph as: ' + fig_name)
    if plot_all:
        plt.show()

    if not('results' in out_dict):
        out_dict['results'] = {}

    out_dict['results']['frequency_response']={}
    out_dict['results']['frequency_response']['lsq20'] = {}
    out_dict['results']['frequency_response']['lsq20']['k'] = float(p_lsq20[0])
    out_dict['results']['frequency_response']['lsq20']['wn'] = float(p_lsq20[1])
    out_dict['results']['frequency_response']['lsq20']['zeta'] = float(p_lsq20[2])
    out_dict['results']['frequency_response']['lsq20']['num'] = [float(v) for v in tf_lsq20.num[0][0]]
    out_dict['results']['frequency_response']['lsq20']['den'] = [float(v) for v in tf_lsq20.den[0][0]]
    out_dict['results']['frequency_response']['lsq20']['NRMSE'] = float(NRMSE_lsq20)
    out_dict['results']['frequency_response']['lsq31'] = {}
    out_dict['results']['frequency_response']['lsq31']['k'] = float(tf_lsq31.dcgain())
    out_dict['results']['frequency_response']['lsq31']['num'] = [float(v) for v in tf_lsq31.num[0][0]]
    out_dict['results']['frequency_response']['lsq31']['den'] = [float(v) for v in tf_lsq31.den[0][0]]
    out_dict['results']['frequency_response']['lsq31']['NRMSE'] = float(NRMSE_lsq31)

    with open(yaml_file, 'w', encoding='utf8') as outfile:
        yaml.dump(out_dict, outfile, default_flow_style=False, allow_unicode=True)
    return yaml_file

if __name__ == "__main__":
    plot_utils.print_alberobotics()
    print(plot_utils.bcolors.OKBLUE + "[i] Starting process_current_free_smooth" + plot_utils.bcolors.ENDC)
    yaml_file = process(yaml_file=sys.argv[1], plot_all=False)

    print(plot_utils.bcolors.OKGREEN + u'[\u2713] Ending program successfully' + plot_utils.bcolors.ENDC)
