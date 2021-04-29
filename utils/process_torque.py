#!/usr/bin/python3

import os
import sys
import glob
import yaml
import statistics
import numpy as np
from scipy import odr
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt

#import costum
from utils import plot_utils

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
    image_base_path= new_head +f'{code_string}_torque-calib'

    # load params
    Torsion_bar_stiff = float(out_dict['results']['flash_params']['Torsion_bar_stiff'])
    torque_const = float(out_dict['results']['flash_params']['motorTorqueConstant']) * float(out_dict['results']['flash_params']['Motor_gear_ratio'])

    log_file=head+f'{code_string}_torque-calib.log'
    print('[i] Reading log_file: ' + log_file)

    # log format: '%u64\t%u\t%f\t%f\t%f\t%f\t%f\t%f'
    ns_        = [np.uint64(x.split('\t')[0]) for x in open(log_file).readlines()]
    stationary = [np.uint32(x.split('\t')[1]) for x in open(log_file).readlines()]
    tor_cell_  = [    float(x.split('\t')[2]) for x in open(log_file).readlines()]
    tor_motor_ = [    float(x.split('\t')[3]) for x in open(log_file).readlines()]
    pos_link   = [    float(x.split('\t')[4]) for x in open(log_file).readlines()]
    pos_motor  = [    float(x.split('\t')[5]) for x in open(log_file).readlines()]
    i_ref_     = [    float(x.split('\t')[6]) for x in open(log_file).readlines()]
    i_fb_      = [    float(x.split('\t')[7]) for x in open(log_file).readlines()]

    print('loaded ',len(ns_), ' points')

    print('[i] Processing data')
    # Plot current, mototr torque and loadcell torque oveer the all experiment ---------------------------------------------------------------------------
    fig, axs = plt.subplots()
    l0, = axs.plot(ns_, [i*torque_const for i in i_fb_], color='#8e8e8e', marker='.', markersize=0.5, linestyle='')
    l1, = axs.plot(ns_, [i*torque_const for i in i_ref_], color='#000000', marker='.', markersize=0.5, linestyle='')
    l2, = axs.plot(ns_, tor_motor_, color='#1f77b4',marker='.', markersize=0.5, linestyle='')
    l3, = axs.plot(ns_, tor_cell_, color='#ff7f0e',marker='.', markersize=0.5, linestyle='')

    axs.set_ylabel('Torque (Nm)')
    axs.set_xlabel('Time (ns)')
    plt_max = (max(ns_) -min(ns_)) * 0.05
    axs.set_xlim(min(ns_)-plt_max, max(ns_)+plt_max)
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    axs.set_ylim(min([i*torque_const for i in i_fb_]), max([i*torque_const for i in i_fb_]))
    axs.grid(b=True, which='major', axis='y', linestyle='-')
    axs.grid(b=True, which='minor', axis='y', linestyle=':')
    axs.grid(b=True, which='major', axis='x', linestyle=':')
    axs.spines['top'].set_visible(False)
    axs.spines['right'].set_visible(False)
    axs.spines['left'].set_visible(False)
    axs.legend(handles=(l0,l1,l2,l3), labels=('i_fb', 'i_ref','tor_motor','tor_loadcell'))
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    if plot_all:
        plt.show()

    # Save the graph
    fig_name = image_base_path + '1.png'
    print('Saving graph as: ' + fig_name)
    plt.savefig(fname=fig_name, format='png', bbox_inches='tight')


    # Torsion_bar_stiff: torque read from the loadcell vs the motor's torque cell deflexion --------------------------------------------------------------
    tor_motor=[tor_motor_[v] for v in range(0,len(ns_)) if stationary[v]]
    tor_cell=[tor_cell_[v] for v in range(0,len(ns_)) if stationary[v]]
    ns=[ns_[v] for v in range(0,len(ns_)) if stationary[v]]
    tor_cell_np = np.array(tor_cell)
    tor_displ = np.array([t/Torsion_bar_stiff for t in tor_motor]).reshape((-1, 1))
    tor_SDO = [Torsion_bar_stiff*t+tor_cell[0]-tor_motor[0] for t in tor_displ]

    model = LinearRegression().fit(tor_displ,tor_cell)
    r_sq = model.score(tor_displ,tor_cell)
    tor_linear = model.predict(tor_displ)

    def linear_func(p, x):
        m, c = p
        return m*x + c

    odr_linear = odr.Model(linear_func)
    tor_x = [t/Torsion_bar_stiff for t in tor_motor]
    sx=statistics.stdev(tor_x)
    sy=statistics.stdev(tor_cell)
    odr_data = odr.RealData(np.array(tor_x), tor_cell_np, sx=sx, sy=sy)
    odr_obj = odr.ODR(odr_data, odr_linear, beta0=[Torsion_bar_stiff, tor_cell[0]-tor_motor[0]])
    odr_out = odr_obj.run()
    tor_odr = [linear_func(odr_out.beta,x) for x in tor_x]

    # store results
    RESULT = []
    RESULT.append(Torsion_bar_stiff)
    RESULT.append(model.coef_[0])
    RESULT.append(odr_out.beta[0])
    #compute Root Mean Squared Error
    NRMSE=[]
    NRMSE.append(np.sqrt(np.mean(np.square([tor_cell[v] - tor_SDO[v] for v in range(0,len(tor_displ))])))/(max(tor_cell)-min(tor_cell)))
    NRMSE.append(np.sqrt(np.mean(np.square([tor_cell[v] - tor_linear[v] for v in range(0,len(tor_displ))])))/(max(tor_cell)-min(tor_cell)))
    NRMSE.append(np.sqrt(np.mean(np.square([tor_cell[v] - tor_odr[v] for v in range(0,len(tor_displ))])))/(max(tor_cell)-min(tor_cell)))
    #RMSE =[v/min(RMSE) for v in RMSE]

    print('SDO                    :{:.3f}\tNRMSE:{:.5f}'.format(RESULT[0], NRMSE[0]))
    print('sklean.LinearRegression:{:.3f}\tNRMSE:{:.5f}'.format(RESULT[1], NRMSE[1]))
    print('scipy.ord              :{:.3f}\tNRMSE:{:.5f}'.format(RESULT[2], NRMSE[2]))

    ## plot
    fig, axs = plt.subplots()
    axs.axhline(0, color='black', lw=1.2)
    axs.axvline(0, color='black', lw=1.2)

    l0, = axs.plot([t/Torsion_bar_stiff for t in tor_motor_], tor_cell_, color='#8e8e8e', marker='.', markersize=0.5, linestyle='')
    l1, = axs.plot(tor_displ, tor_cell, color='#000000', marker='.', markersize=0.5, linestyle='')
    #axs.legend(handles=(l1, l2), labels=('full test','t_log only'))
    # l1, = axs.plot(tor_displ, tor_cell, color='#8e8e8e', marker='.', markersize=0.5, linestyle='')
    l2, = axs.plot(tor_displ,tor_SDO, color='#1f77b4', linestyle='-', linewidth=1)
    l3, = axs.plot(tor_displ, tor_linear, color='#ff7f0e', linestyle='-', linewidth=1)
    l4, = axs.plot(tor_displ, tor_odr, color='#2ca02c', linestyle='-', linewidth=1)
    axs.legend(handles=(l0, l1, l2, l3, l4), labels=('full test datapoints', 't_log datapoints', 'SDO', 'sklean.LinearRegression','scipy.odr'))

    axs.set_ylabel('Torque form loadcell reading (Nm)')
    axs.set_xlabel('Motor torque sensor displacement (rad)')
    plt_max = (max(tor_displ) -min(tor_displ)) * 0.05
    axs.set_xlim(min(tor_displ)-plt_max, max(tor_displ)+plt_max)
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    plt_max = (max(tor_cell) -min(tor_cell)) * 0.05
    axs.set_ylim(min(tor_cell)-plt_max, max(tor_cell)+plt_max)
    axs.grid(b=True, which='major', axis='y', linestyle='-')
    axs.grid(b=True, which='minor', axis='y', linestyle=':')
    axs.grid(b=True, which='major', axis='x', linestyle=':')
    axs.spines['top'].set_visible(False)
    axs.spines['right'].set_visible(False)
    axs.spines['left'].set_visible(False)
    axs.spines['bottom'].set_visible(False)

    if plot_all:
        plt.show()

    Torsion_bar_stiff=RESULT[int(np.argsort(NRMSE)[0])]
    print(plot_utils.bcolors.OKGREEN + u'[\u2713] Result: Torsion_bar_stiff = ' + str(Torsion_bar_stiff) + plot_utils.bcolors.ENDC)


    # Save the graph
    fig_name = image_base_path + '2.png'
    print('Saving graph as: ' + fig_name)
    plt.savefig(fname=fig_name, format='png', bbox_inches='tight')

    # Plot currentvs loadcell torque oveer the all experiment --------------------------------------------------------------------------------------------
    i_ref = [i_ref_[v] for v in range(0,len(i_ref_)) if stationary[v]]
    #i_steps = list(dict.fromkeys(i_ref))

    # find avarage torque for a ginve current ref
    i_steps = []
    i_reps = []
    tor_avar = []
    for t,i in zip(tor_cell,i_ref):
        i=round(i,2)
        if i not in i_steps:
            i_steps.append(i)
            i_reps.append(1)
            tor_avar.append(t)
        else:
            tor_avar[i_steps.index(i)] += t
            i_reps[i_steps.index(i)] += 1
    tor_avar = [t/i for t,i in zip(tor_avar, i_reps)]
    tor_SDO = [i*torque_const + tor_avar[0] for i in i_steps]



    def poly2_func(p, x):
        a, b, c = p
        return a*x*x + b*x + c
    odr_linear = odr.Model(poly2_func)
    sx=statistics.stdev(i_ref)
    sy=statistics.stdev(tor_cell)
    odr_data = odr.RealData(np.array(i_ref), np.array(tor_cell), sx=sx, sy=sy)
    odr_obj = odr.ODR(odr_data, odr_linear, beta0=[-1,-max(i_steps),-max(tor_avar)])
    odr_out = odr_obj.run()
    tor_odr = [poly2_func(odr_out.beta,x) for x in i_steps]


    fig, axs = plt.subplots()
    axs.axhline(0, color='black', lw=1.0)
    axs.axvline(0, color='black', lw=1.0)

    #l0, = axs.plot(i_fb_, [i*torque_const for i in i_fb_], color='#8e8e8e', marker='.', markersize=0.5, linestyle='')
    l0, = axs.plot(i_ref_, tor_cell_, color='#8e8e8e', marker='.', markersize=0.5, linestyle='')
    l1, = axs.plot(i_ref, tor_cell, color='#000000', marker='.', markersize=0.5, linestyle='')
    l2, = axs.plot(i_steps, tor_SDO, color='#ff7f0e', marker='.', markersize=3.0, linestyle='')
    for i,t in zip(i_steps, tor_SDO):
        axs.plot([i, i], [t*0.9, t*1.1], color='#ff7f0e', alpha=0.2, marker='', linestyle='-')
    #axs.fill_between(i_ref, [t*0.9 for t in tor_SDO], [t*1.1 for t in tor_SDO], color='#ff7f0e', alpha=0.2, interpolate=True)
    l3, = axs.plot(i_steps, tor_avar, color='#1f77b4', marker='.', markersize=3.0, linestyle='')
    # axs.plot(i_steps, tor_avar, color='#1f77b4', marker='', linestyle='--', alpha=0.5)


    # l1, = axs.plot(i_ref_, [i*torque_const for i in i_ref_], color='#000000', marker='.', markersize=0.5, linestyle='')
    # l1, = axs.plot(i_ref, [i*torque_const for i in i_ref], color='#000000', marker='.', markersize=0.5, linestyle='')
    # l1, = axs.plot(i_ref, tor_cell, color='#8e8e8e', marker='.', markersize=0.5, linestyle='')
    # l2 = axs.plot(i_ref, tor_SDO, color='#1f77b4', linestyle='-', linewidth=1)
    # l3, = axs.plot(i_ref, tor_linear, color='#ff7f0e', linestyle='-', linewidth=1)
    # l4, = axs.plot(i_steps, tor_odr, color='#2ca02c', linestyle='--', linewidth=1, alpha=0.5)
    # l4, = axs.plot(i_rising, t_rising, color='#ff0000', marker='.', markersize=0.5, linestyle='')
    axs.legend(handles=(l0, l1, l2, l3), labels=('full test datapoints', 't_log datapoints', 'expected (10% tollerance)', 'test avarage'))
    # axs.legend(handles=(l0, l1, l3, l2, l4), labels=('full test datapoints', 't_log datapoints', 'avarage', 'SDO','scipy.odr'))
    # axs.legend(handles=(l0, l1, l2, l4), labels=('full test datapoints', 't_log datapoints', 'SDO','t_log w/ rising current only'))

    axs.set_ylabel('Torque form loadcell reading (Nm)')
    axs.set_xlabel('Current reference (A)')
    plt_max = (max(i_ref) -min(i_ref)) * 0.05
    axs.set_xlim(min(i_ref)-plt_max, max(i_ref)+plt_max)
    #plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    plt_max = (max(tor_cell) -min(tor_cell)) * 0.05
    axs.set_ylim(min(tor_cell)-plt_max, max(max(tor_cell),max(i_ref)*torque_const)+plt_max)
    axs.grid(b=True, which='major', axis='y', linestyle='-')
    axs.grid(b=True, which='minor', axis='y', linestyle=':')
    axs.grid(b=True, which='major', axis='x', linestyle=':')
    axs.spines['top'].set_visible(False)
    axs.spines['right'].set_visible(False)
    axs.spines['left'].set_visible(False)
    axs.spines['bottom'].set_visible(False)

    # Save the graph
    fig_name = image_base_path + '3.png'
    print('Saving graph as: ' + fig_name)
    plt.savefig(fname=fig_name, format='png', bbox_inches='tight')

    #-----------------------------------------------------------------------------------
    # get values only for rising current
    i_rising = []
    t_rising = []
    rising = True
    for i in range(1,len(i_ref)):
        if i_ref[i] < i_ref[i-1]:
            rising = False
        elif i_ref[i] == 0.0:
            rising= True

        if rising:
            i_rising.append(i_ref[i])
            t_rising.append(tor_cell[i])

    tor_SDO_rising=[i*torque_const + tor_avar[0] for i in i_rising]
    efficiency = [100*t1/t2 for t1, t2 in zip(t_rising,tor_SDO_rising) if t2 > 0]
    i_plot = [i for i, t2 in zip(i_rising,tor_SDO_rising) if t2 > 0]

    fig, axs = plt.subplots()
    axs.axhline(0, color='black', lw=1.2)
    axs.axvline(0, color='black', lw=1.2)

    l0, = axs.plot(i_plot, efficiency, color='#ff7f0e', marker='.', markersize=3.0, linestyle='')

    #axs.set_ylabel('Static Efficiency (%)')
    axs.set_ylabel('Red dots / Orange dots (%)')
    axs.set_xlabel('Current reference (A)')
    plt_max = (max(i_ref) -min(i_ref)) * 0.05
    axs.set_xlim(min(i_ref)-plt_max, max(i_ref)+plt_max)
    #plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    #plt_max = (max(tor_cell) -min(tor_cell)) * 0.05
    #axs.set_ylim(min(tor_cell)-plt_max, max(max(tor_cell),max(i_ref)*torque_const)+plt_max)
    axs.grid(b=True, which='major', axis='y', linestyle='-')
    axs.grid(b=True, which='minor', axis='y', linestyle=':')
    axs.grid(b=True, which='major', axis='x', linestyle=':')
    axs.spines['top'].set_visible(False)
    axs.spines['right'].set_visible(False)
    axs.spines['left'].set_visible(False)
    axs.spines['bottom'].set_visible(False)

    # Save the graph
    fig_name = image_base_path + '4.png'
    print('Saving graph as: ' + fig_name)
    plt.savefig(fname=fig_name, format='png', bbox_inches='tight')


    # Save result ------------------------------------------------------------------------------------------
    if 'name' in out_dict['log']:
        yaml_name = yaml_file
        print('Adding result to: ' + yaml_name)
    else:
        out_dict['log']['name'] = log_file[:-16]
        yaml_name =  log_file[:-16] + '-results.yaml'
        print('Saving yaml as: ' + yaml_name)
        out_dict['results'] = {}
    out_dict['results']['torque']={}
    out_dict['results']['torque']['Torsion_bar_stiff'] = float(Torsion_bar_stiff)
    with open(yaml_name, 'w', encoding='utf8') as outfile:
        yaml.dump(out_dict, outfile, default_flow_style=False, allow_unicode=True)
    return yaml_name

if __name__ == "__main__":
    #yaml_file = os.path.expanduser('~/ecat_dev/ec_master_app/examples/motor-calib/config.yaml')
    yaml_file = '/logs/AOR01-EOR01-H6236-20210421112049-results.yaml'

    print(plot_utils.bcolors.OKBLUE + "[i] Starting process_torque" + plot_utils.bcolors.ENDC)
    yaml_file = process(yaml_file=yaml_file, plot_all=False)

    print(plot_utils.bcolors.OKGREEN + u'[\u2713] Ending program successfully' + plot_utils.bcolors.ENDC)
