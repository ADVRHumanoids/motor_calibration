#!/usr/bin/python3

import os
import sys
import glob
import yaml
import statistics
import numpy as np
from matplotlib import pyplot as plt

#import costum
import plot_utils
import fit_sine

def process(yaml_file, plot_all=False):
    repeat = 3
    steps_1 = 13
    steps_2 = 6

    # read parameters from yaml file
    with open(yaml_file, 'r') as stream:
        out_dict = yaml.safe_load(stream)
        yaml_dict = out_dict['calib_ripple']
    if 'trj_error' in yaml_dict:
        trj_error = yaml_dict['trj_error']
    if 'pos_step' in yaml_dict:
        pos_step = yaml_dict['pos_step']

    # read data from latest file --------------------------------------------------------------
    list_of_files = glob.glob('/logs/*-ripple_calib.log')
    file = max(list_of_files, key=os.path.getctime)
    print(plot_utils.bcolors.OKBLUE + '[i] Reading file: ' + file + plot_utils.bcolors.ENDC)

    print(plot_utils.bcolors.OKBLUE + '[i] Processing data' + plot_utils.bcolors.ENDC)
    # '%u64\t%u\t%u\t%u\t%u\t%f\t%f\t%d\t%f\t%f\t%f'
    ts = [np.uint64(x.split('\t')[0]) for x in open(file).readlines()]
    is_moving  = [np.uint32(x.split('\t')[ 1]) for x in open(file).readlines()]
    trj_cnt    = [np.uint32(x.split('\t')[ 2]) for x in open(file).readlines()]
    curr_ref   = [    float(x.split('\t')[ 3]) for x in open(file).readlines()]
    torque     = [    float(x.split('\t')[ 4]) for x in open(file).readlines()]
    pos_target = [    float(x.split('\t')[ 5]) for x in open(file).readlines()]
    pos_motor  = [    float(x.split('\t')[ 6]) for x in open(file).readlines()]
    pos_link   = [    float(x.split('\t')[ 7]) for x in open(file).readlines()]
    vel_motor  = [ np.int16(x.split('\t')[ 8]) for x in open(file).readlines()]
    vel_link   = [ np.int16(x.split('\t')[ 9]) for x in open(file).readlines()]
    aux_var    = [    float(x.split('\t')[10]) for x in open(file).readlines()]

    # find where we start testing id instead of iq
    ii = 0
    cc = []

    # Plot full test --------------------------------------------------------------

    fig, axs = plt.subplots(2)
    fig.suptitle('RAW')

    plt_max = max([max(torque), -min(torque)]) * 1.1

    axs[0].plot(ts, torque,
                label='Motor Vel',
                color='b',
                marker='.')
    #axs[0].set_ylim(min(torque), max(torque))
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

    ts1 = [statistics.median(v) for v in temp11]
    tq1 = [statistics.median(v) for v in temp21]
    ts2 = [statistics.median(v) for v in temp12]
    tq2 = [statistics.median(v) for v in temp22]

    fig, axs = plt.subplots(2)
    fig.suptitle('Torque offset & ripple')



    #axs[0].plot(ts1, tq1, label='Torque$_{raw}$', color='k', marker='.')
    for t, q in zip(temp11, temp21):
        axs[0].plot(t, q, label='raw data', color='#5fb7f4')
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

    # fit multisine waves

    ts_exended = [ph - 2 * np.pi for ph in ts1]
    ts_exended += ts1
    ts_exended += [t + 2 * np.pi for t in ts1]
    tq_exended = tq1 + tq1 + tq1

    s1 = fit_sine.fit_sin1(ts_exended, tq_exended)
    s2 = fit_sine.fit_sin2(ts_exended, tq_exended)
    s3 = fit_sine.fit_sin3(ts_exended, tq_exended)

    sin1 = [
        fit_sine.sinfunc(t=t,
                         A1=s1["a1"],
                         w1=s1["w1"],
                         p1=s1["p1"],
                         c=s1["c"])
        for t in ts1
    ]
    sin2 = [
        fit_sine.sin2func(t=t,
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
        fit_sine.sin3func(t=t,
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

    axs[1].plot(ts1, tq1, label='median', marker='.')
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
    pdf_name = file[:-4] + '.pdf'
    print('Saving graph as: ' + pdf_name)
    plt.savefig(fname=pdf_name, format='pdf')

    #alpha = 0.1
    #smooth = steps
    #for i in range(0, len(steps)):
    #    for j in range(1, len(steps[i])):
    #        smooth[i][j] = alpha * steps[i][j] + (1 - alpha) * smooth[i][j - 1]

    # Plot individual trajectories ----------------------------------------------------------------------
    if False: #plot_all:
        fig, axs = plt.subplots()
        fig.suptitle('Individual trajectories')
        for i in range(0, len(ns)):
            axs.plot(ns[i], steps[i], label='diff')
            axs.plot(ns[i], smooth[i], label='diff')

        axs.set_ylabel('motor_vel (mrad/s)')
        axs.set_xlabel('timestamp (ns)')

        axs.grid(b=True, which='major', axis='y', linestyle='-')
        axs.grid(b=True, which='minor', axis='y', linestyle=':')
        axs.yaxis.set_major_locator(
            plt.MultipleLocator((max(motor_vel) - min(motor_vel)) * 1.1 / 6))
        axs.yaxis.set_minor_locator(
            plt.MultipleLocator((max(motor_vel) - min(motor_vel)) * 1.1 / 18))
        axs.spines['top'].set_visible(False)
        axs.spines['right'].set_visible(False)
        axs.spines['left'].set_visible(False)
        plt.show()

    # evaluate performance of each trajectory -----------------------------------------------------------
    #score = [[], [], []]
    #for i in range(0, len(steps)):
    #    score[0].append(phase[i])
    #    tmp = sum(steps[i][0:int(len(steps[i]) / 2)])
    #    if tmp > 0:
    #        score[1].append((max(steps[i][:]) - min(steps[i][:])) / 2)
    #        score[2].append((max(smooth[i][:]) - min(smooth[i][:])) / 2)
    #    else:
    #        score[1].append(-(max(steps[i][:]) - min(steps[i][:])) / 2)
    #        score[2].append(-(max(smooth[i][:]) - min(smooth[i][:])) / 2)

if __name__ == "__main__":
    plot_utils.print_alberobotics()
    yaml_file = os.path.expanduser('~/ecat_dev/ec_master_app/examples/motor-calib/config.yaml')

    print(plot_utils.bcolors.OKBLUE + "[i] Starting process_ripple" +
          plot_utils.bcolors.ENDC)
    yaml_file = process(yaml_file=yaml_file, plot_all=False)

    print(plot_utils.bcolors.OKGREEN + u'[\u2713] Ending program successfully' + plot_utils.bcolors.ENDC)