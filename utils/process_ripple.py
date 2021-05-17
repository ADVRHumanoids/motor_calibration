#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import yaml
import statistics
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

#import costum
from utils import plot_utils
from utils import fit_sine

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
    head, tail =os.path.split(yaml_file)

    if 'location' in out_dict['log']:
        head = out_dict['log']['location']
    else:
        head, _ =os.path.split(yaml_file)

    if 'name' in out_dict['log']:
        code_string = out_dict['log']['name']
    else:
        _, tail =os.path.split(yaml_file)
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
    image_base_path= new_head +f'{code_string}_ripple-calib'


    if 'calib_ripple' in out_dict:
        yaml_dict = out_dict['calib_ripple']
    else:
        raise Exception("missing 'calib_ripple' in yaml parsing")

    if 'trj_error' in yaml_dict:
        trj_error = yaml_dict['trj_error']
    if 'pos_step' in yaml_dict:
        pos_step = yaml_dict['pos_step']

    log_file=head+f'{code_string}_ripple-calib.log'
    print('[i] Reading log_file: ' + log_file)

    # '%u64\t%u\t%u\t%u\t%u\t%f\t%f\t%d\t%f\t%f\t%f'
    ts = [np.uint64(x.split('\t')[0]) for x in open(log_file).readlines()]
    is_moving  = [np.uint32(x.split('\t')[ 1]) for x in open(log_file).readlines()]
    trj_cnt    = [np.uint32(x.split('\t')[ 2]) for x in open(log_file).readlines()]
    curr_ref   = [    float(x.split('\t')[ 3]) for x in open(log_file).readlines()]
    torque     = [    float(x.split('\t')[ 4]) for x in open(log_file).readlines()]
    pos_target = [    float(x.split('\t')[ 5]) for x in open(log_file).readlines()]
    pos_motor  = [    float(x.split('\t')[ 6]) for x in open(log_file).readlines()]
    pos_link   = [    float(x.split('\t')[ 7]) for x in open(log_file).readlines()]
    vel_motor  = [ np.int16(x.split('\t')[ 8]) for x in open(log_file).readlines()]
    vel_link   = [ np.int16(x.split('\t')[ 9]) for x in open(log_file).readlines()]
    aux_var    = [    float(x.split('\t')[10]) for x in open(log_file).readlines()]

    print('[i] Processing data')
    # find where we start testing id instead of iq
    ii = 0
    cc = []

    # Plot full test --------------------------------------------------------------

    fig, axs = plt.subplots(2)
    #fig.suptitle('RAW')

    plt_max = max([max(torque), -min(torque)]) * 1.1

    axs[0].plot(ts, torque,
                label='Motor Vel',
                color='b',
                marker='.')
    axs[0].set_ylim(min(torque), max(torque))
    axs[0].set_ylabel('torque (Nm)')
    axs[0].set_xlabel('timestamp (ns)')
    axs[0].grid(b=True, which='major', axis='y', linestyle='-')
    axs[0].grid(b=True, which='minor', axis='y', linestyle=':')

    axs[0].set_xlim(ts[0], ts[-1])
    axs[0].set_ylim(-plt_max, plt_max)
    axs[0].yaxis.set_major_locator(plt.MultipleLocator(plt_max / 2))
    axs[0].yaxis.set_minor_locator(plt.MultipleLocator(plt_max / 6))
    axs[0].spines['top'].set_visible(False)
    axs[0].spines['right'].set_visible(False)
    axs[0].spines['left'].set_visible(False)

    axs[1].plot(pos_motor, torque,
                label='Motor Vel',
                color='b',
                marker='.')
    axs[1].set_ylim(-plt_max, plt_max)
    axs[1].set_xlim(min(pos_motor), max(pos_motor))
    axs[1].set_ylabel('torque (Nm)')
    axs[1].set_xlabel('position (rad)')
    axs[1].grid(b=True, which='major', axis='y', linestyle='-')
    axs[1].grid(b=True, which='minor', axis='y', linestyle=':')
    axs[1].yaxis.set_major_locator(plt.MultipleLocator(plt_max / 2))
    axs[1].yaxis.set_minor_locator(plt.MultipleLocator(plt_max / 6))
    axs[1].spines['top'].set_visible(False)
    axs[1].spines['right'].set_visible(False)
    axs[1].spines['left'].set_visible(False)
    if plot_all:
        plt.show()

    # split trajectories in individual motions -----------------------------------------------------
    trj_v = [ i for i in range(0, len(trj_cnt)) if (trj_cnt[i] == 1) ]

    #ns = [ [s - ts[trj_v[j - 1]] for s in ts[trj_v[j - 1] : trj_v[j]]] for j in range(1, len(trj_v)) ]
    temp11=[]
    temp12=[]
    temp21=[]
    temp22=[]
    is_there=False
    for j in range(1, len(trj_v)):
        is_there=False
        if is_moving[trj_v[j]]:
            for ii in range(0, len(temp11)):
                if (abs(temp11[ii][0] - pos_motor[trj_v[j - 1]]) < 2*trj_error) and not(is_there):
                    temp11[ii].extend([v for v in pos_motor[trj_v[j - 1]:trj_v[j]]] )
                    temp21[ii].extend([v for v in torque[trj_v[j - 1] : trj_v[j]]])
                    is_there = True
            if not is_there:
                temp11.append([v for v in pos_motor[trj_v[j - 1] : trj_v[j]]])
                temp21.append([v for v in  torque[trj_v[j - 1] : trj_v[j]]])
        else:
            for ii in range(0, len(temp12)):
                if (abs(temp12[ii][0] - pos_motor[trj_v[j - 1]]) < 2*trj_error) and not (is_there):
                    temp12[ii].extend([v for v in pos_motor[trj_v[j - 1]:trj_v[j]]] )
                    temp22[ii].extend([v for v in torque[trj_v[j - 1] : trj_v[j]]])
                    is_there = True
            if not is_there:
                temp12.append([v for v in pos_motor[trj_v[j - 1] : trj_v[j]]])
                temp22.append([v for v in torque[trj_v[j - 1] : trj_v[j]]])

    ts1 = [sum(v)/len(v) for v in temp11]
    tq1 = [sum(v)/len(v) for v in temp21]
    key_order = np.argsort(ts1)
    ts1.sort()
    tq1 = [tq1[key] for key in key_order]

    ts2 = [sum(v)/len(v) for v in temp12]
    tq2 = [sum(v)/len(v) for v in temp22]
    key_order = np.argsort(ts2)
    ts2.sort()
    tq2 = [tq2[key] for key in key_order]

    fig, axs = plt.subplots(2)



    #axs[0].plot(ts1, tq1, label='Torque$_{raw}$', color='k', marker='.')
    for t, q in zip(temp11, temp21):
        axs[0].plot(t, q, label='raw data', color='#8e8e8e')
    axs[0].plot(ts1, tq1, label='median', color='#1f77b4', marker='.')
    axs[0].set_ylabel('torque (Nm)')
    axs[0].set_xlabel('position (rad)')
    axs[0].grid(b=True, which='major', axis='y', linestyle='-')
    axs[0].grid(b=True, which='minor', axis='y', linestyle=':')
    axs[0].grid(b=True, which='major', axis='x', linestyle=':')

    plt_pad = (max(torque) - min(torque)) * 0.02
    axs[0].set_ylim(min(torque) - plt_pad, max(torque) + plt_pad)
    #plt_pad = (max(ts1) - min(ts1)) * 0.02
    #axs[0].set_xlim(min(ts1) - plt_pad, max(ts1) + plt_pad)
    axs[0].set_xlim(-np.pi, np.pi)
    axs[0].spines['top'].set_visible(False)
    axs[0].spines['right'].set_visible(False)
    axs[0].spines['left'].set_visible(False)
    axs[0].yaxis.set_major_locator(plt.MultipleLocator((max(torque) - min(torque)) / 4))
    axs[0].yaxis.set_minor_locator(plt.MultipleLocator((max(torque) - min(torque)) / 12))
    axs[0].xaxis.set_major_locator(plt.MultipleLocator(np.pi / 4))
    axs[0].xaxis.set_minor_locator(plt.MultipleLocator(np.pi / 12))
    axs[0].xaxis.set_major_formatter(
        plt.FuncFormatter(
            plot_utils.multiple_formatter(denominator=4,
                                          number=np.pi,
                                          latex='\pi')))
    axs[0].ticklabel_format(axis="y",
                            style="plain",#"sci",
                            scilimits=(0, 0),
                            useOffset=False)

    legend_elements = [
        Line2D([0], [0], label='Raw torque', color='#8e8e8e'),
        Line2D([0], [0], label='Median',     color='#1f77b4', marker='.'),
    ]
    axs[0].legend(handles=legend_elements, loc='best')

    # fit multisine waves
    ts_exended = [ph - 2 * np.pi for ph in ts1]
    ts_exended += ts1
    ts_exended += [t + 2 * np.pi for t in ts1]
    tq_exended = tq1 + tq1 + tq1

    s1 = fit_sine.fit_sin1(ts_exended, tq_exended)
    s2 = fit_sine.fit_sin2(ts_exended, tq_exended)
    s3 = fit_sine.fit_sin3(ts_exended, tq_exended)
    print("1 sin:" + str(s1["c"]) + " + " + str(s1["a1"]) + "*sin(" + str(s1["w1"]) + "*t + " + str(s1["p1"]) + ")")
    print("2 sin:" + str(s2["c"]) + " + " + str(s2["a1"]) + "*sin(" + str(s2["w1"]) + "*t + " + str(s2["p1"]) + ") + " + \
                                            str(s2["a2"]) + "*sin(" + str(s2["w2"]) + "*t + " + str(s2["p2"]) + ")")
    print("3 sin:" + str(s3["c"]) + " + " + str(s3["a1"]) + "*sin(" + str(s3["w1"]) + "*t + " + str(s3["p1"]) + ") + " + \
                                            str(s3["a2"]) + "*sin(" + str(s3["w2"]) + "*t + " + str(s3["p2"]) + ") + " + \
                                            str(s3["a3"]) + "*sin(" + str(s3["w3"]) + "*t + " + str(s3["p3"]) + ")")



    sin1 = [
        fit_sine.sine_1(t=t,
                         A1=s1["a1"],
                         w1=s1["w1"],
                         p1=s1["p1"],
                         c=s1["c"])
        for t in ts1
    ]
    sin2 = [
        fit_sine.sine_2(t=t,
                          A1=s2["a1"],
                          A2=s2["a2"],
                          w1=s2["w1"],
                          w2=s2["w2"],
                          p1=s2["p1"],
                          p2=s2["p2"],
                          c=s2["c"])
        for t in ts1
    ]
    sin3 = [
        fit_sine.sine_3(t=t,
                          A1=s3["a1"],
                          A2=s3["a2"],
                          A3=s3["a3"],
                          w1=s3["w1"],
                          w2=s3["w2"],
                          w3=s3["w3"],
                          p1=s3["p1"],
                          p2=s3["p2"],
                          p3=s3["p3"],
                          c=s3["c"])
        for t in ts1
    ]

    #compute Root Mean Squared Error
    RMSE=[]
    RMSE.append(np.sqrt(np.mean(np.square([tq1[v] - sin1[v] for v in range(0,len(tq1))]))))
    RMSE.append(np.sqrt(np.mean(np.square([tq1[v] - sin2[v] for v in range(0,len(tq1))]))))
    RMSE.append(np.sqrt(np.mean(np.square([tq1[v] - sin3[v] for v in range(0,len(tq1))]))))
    RMSE =[v/min(RMSE) for v in RMSE]

    print('RMSE:' + str(RMSE))

    axs[1].plot(ts1, tq1, label='mean', marker='.')
    axs[1].plot(ts1, sin1, label='1 sin', marker='.')
    axs[1].plot(ts1, sin2, label='2 sin', marker='.')
    axs[1].plot(ts1, sin3, label='3 sin', marker='.')

    plt_pad = (max(tq1) - min(tq1)) * 0.02
    axs[1].set_ylim(min(tq1) - plt_pad, max(tq1) + plt_pad)
    axs[1].set_xlim(-np.pi, np.pi)
    axs[1].set_ylabel('torque (Nm)')
    axs[1].set_xlabel('position (rad)')
    axs[1].grid(b=True, which='major', axis='y', linestyle='-')
    axs[1].grid(b=True, which='minor', axis='y', linestyle=':')
    axs[1].grid(b=True, which='major', axis='x', linestyle=':')
    axs[1].spines['top'].set_visible(False)
    axs[1].spines['right'].set_visible(False)
    axs[1].spines['left'].set_visible(False)
    axs[1].yaxis.set_major_locator(plt.MultipleLocator((max(tq1) - min(tq1)) / 4))
    axs[1].yaxis.set_minor_locator(plt.MultipleLocator((max(tq1) - min(tq1)) / 12))
    axs[1].xaxis.set_major_locator(plt.MultipleLocator(np.pi / 4))
    axs[1].xaxis.set_minor_locator(plt.MultipleLocator(np.pi / 12))
    axs[1].xaxis.set_major_formatter(
        plt.FuncFormatter(
            plot_utils.multiple_formatter(denominator=4,
                                          number=np.pi,
                                          latex='\pi')))

    axs[1].ticklabel_format(axis="y",
                            style="plain",#"sci",
                            scilimits=(0, 0),
                            useOffset=False)
    axs[1].legend()
    plt.tight_layout()
    if plot_all:
        plt.show()

    # Save the graph
    fig_name = image_base_path + '.png'
    plt.savefig(fname=fig_name, format='png', bbox_inches='tight')
    print('[i] Saving graph as: ' + fig_name)

    # Save result
    if 'name' in out_dict['log']:
        yaml_name = yaml_file
        print('Adding result to: ' + yaml_name)
    else:
        out_dict['log']['location']= head
        out_dict['log']['name'] = code_string
        yaml_name =  head + code_string + '_results.yaml'
        print('Saving yaml as: ' + yaml_name)

    if not('results' in out_dict):
        out_dict['results'] = {}

    num_of_sinusoids = int(np.argsort(RMSE)[0]) + 1

    out_dict['results']['ripple']={}
    out_dict['results']['ripple']['num_of_sinusoids'] = num_of_sinusoids
    if num_of_sinusoids == 1:
        out_dict['results']['ripple']['c']  = float(s1['c'])
        out_dict['results']['ripple']['a1'] = float(s1['a1'])
        out_dict['results']['ripple']['w1'] = float(s1['w1'])
        out_dict['results']['ripple']['p1'] = float(s1['p1'])
    if num_of_sinusoids == 2:
        out_dict['results']['ripple']['c']  = float(s2['c'])
        out_dict['results']['ripple']['a1'] = float(s2['a1'])
        out_dict['results']['ripple']['w1'] = float(s2['w1'])
        out_dict['results']['ripple']['p1'] = float(s2['p1'])
        out_dict['results']['ripple']['a2'] = float(s2['a2'])
        out_dict['results']['ripple']['w2'] = float(s2['w2'])
        out_dict['results']['ripple']['p2'] = float(s2['p2'])
    if num_of_sinusoids == 3:
        out_dict['results']['ripple']['c']  = float(s3['c'])
        out_dict['results']['ripple']['a1'] = float(s3['a1'])
        out_dict['results']['ripple']['w1'] = float(s3['w1'])
        out_dict['results']['ripple']['p1'] = float(s3['p1'])
        out_dict['results']['ripple']['a2'] = float(s3['a2'])
        out_dict['results']['ripple']['w2'] = float(s3['w2'])
        out_dict['results']['ripple']['p2'] = float(s3['p2'])
        out_dict['results']['ripple']['a3'] = float(s3['a3'])
        out_dict['results']['ripple']['w3'] = float(s3['w3'])
        out_dict['results']['ripple']['p3'] = float(s3['p3'])

    with open(yaml_name, 'w', encoding='utf8') as outfile:
        yaml.dump(out_dict, outfile, default_flow_style=False, allow_unicode=True)
    return yaml_name

if __name__ == "__main__":
    plot_utils.print_alberobotics()

    print(plot_utils.bcolors.OKBLUE + "[i] Starting process_ripple" + plot_utils.bcolors.ENDC)
    yaml_file = process(yaml_file=sys.argv[1], plot_all=False)

    print(plot_utils.bcolors.OKGREEN + u'[\u2713] Ending program successfully' + plot_utils.bcolors.ENDC)
