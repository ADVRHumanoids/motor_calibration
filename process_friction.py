import os
import sys
import glob
import yaml
#import time
#import datetime
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

#import costum
import fit_sine
import plot_utils
from friction_calibration_tool.utils_module import freq_domain
from friction_calibration_tool.utils_module import motor_eqn_models as motor_terms
from friction_calibration_tool.utils_module.logimport import dict_from_log
from friction_calibration_tool.utils_module.motor import MotorData
from friction_calibration_tool.utils_module.regression import (NonLinearRegression,
                                                               LinearRegression,
                                                               LinearRegressor,
                                                               huber_regr_strategy,
                                                               lsq_pseudoinv_strategy,
                                                               scipy_lsq_linear_strategy)
from friction_calibration_tool.utils_module.simulation import Simulation
from friction_calibration_tool.utils_module.trajectory import TrjInfo


def move_log(new_name='NULL'):
    '''Moves lastest CentAcESC_*_log.txt log file to new_name location, default is taken'''
    list_of_files = glob.glob('/tmp/CentAcESC_*_log.txt')
    tmp_file = max(list_of_files, key=os.path.getctime)
    if new_name == 'NULL':
        list_of_files = glob.glob('/logs/*-results.yaml')
        last_log = max(list_of_files, key=os.path.getctime)
        new_name = last_log[:-13] + '-friction-calib.log'
    cmd = 'cp ' + tmp_file + ' ' + new_name
    if os.system(cmd):
        sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error while copying logs' + plot_utils.bcolors.ENDC)

def get_ripple(pos, yaml_='NULL'):
    if isinstance(yaml_, dict):
        pass
    elif isinstance(yaml_, str):
        if yaml_ == 'NULL':
            list_of_files = glob.glob('/logs/*.yaml')
            yaml_file = max(list_of_files, key=os.path.getctime)
        yaml_dict = yaml.safe_load(open(yaml_file, 'r'))['results']['ripple']
    else:
        sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Unsupported type for given yaml' + plot_utils.bcolors.ENDC)

    num_of_sinusoids = 0
    if 'num_of_sinusoids' in yaml_dict:
        num_of_sinusoids = yaml_dict['num_of_sinusoids']
    if num_of_sinusoids > 0:
        c = yaml_dict['c']
        A1 = yaml_dict['a1']
        w1 = yaml_dict['w1']
        p1 = yaml_dict['p1']
    if num_of_sinusoids > 1:
        A2 = yaml_dict['a2']
        w2 = yaml_dict['w2']
        p2 = yaml_dict['p2']
    if num_of_sinusoids > 2:
        A3 = yaml_dict['a3']
        w3 = yaml_dict['w3']
        p3 = yaml_dict['p3']

    t=[]
    if num_of_sinusoids == 1:
        for p in pos:
            t.append(fit_sine.sine_1(p, A1, w1, p1, c))
    elif num_of_sinusoids == 2:
        for p in pos:
            t.append(fit_sine.sine_2(p, A1, A2, w1, w2, p1, p2, c))
    elif num_of_sinusoids == 3:
        for p in pos:
            t.append(fit_sine.sine_3(p, A1, A2, A3, w1, w2, w3, p1, p2, p3, c))
    else:
        for k, v in yaml_dict.items():
            print('\t' + str(k) + '\t' + str(v))
        sys.exit(
            '[get_ripple] no sine fuction existing for num_of_sinusoids = '
            + str(num_of_sinusoids))
    return t

def remove_ripple(tor, pos, yaml_='NULL'):
    ripple = get_ripple(pos, yaml_=yaml_)
    new_tor = [t - r for t, r in zip(tor, ripple)]
    return new_tor


def get_from_log(log_file, yaml_file='NULL', remove_ripple=False, filter_type='NULL', filter_freq=None, samp_freq=None, plot_all=False):
    data_dict = {
        'time' :      [float(x.split('\t')[ 0]) / 1000000000 for x in open(log_file).readlines()],
        'trj_cnt' :   [  int(x.split('\t')[ 1]) for x in open(log_file).readlines()],
        'log_cnt' :   [  int(x.split('\t')[ 2]) for x in open(log_file).readlines()],
        'loop_cnt' :  [  int(x.split('\t')[ 3]) for x in open(log_file).readlines()],
        'pos_abs' :   [float(x.split('\t')[ 4]) for x in open(log_file).readlines()],
        'link_pos' :  [float(x.split('\t')[ 5]) for x in open(log_file).readlines()],
        'motor_pos' : [float(x.split('\t')[ 6]) for x in open(log_file).readlines()],
        'link_vel' :  [float(x.split('\t')[ 7]) /1000 for x in open(log_file).readlines()],
        'motor_vel' : [float(x.split('\t')[ 8]) /1000 for x in open(log_file).readlines()],
        'torque' :    [float(x.split('\t')[ 9]) for x in open(log_file).readlines()],
        'aux':        [float(x.split('\t')[10]) for x in open(log_file).readlines()]
    }

    if remove_ripple:
        ripple = get_ripple(data_dict['motor_pos'], yaml_=yaml_file)
        fig, axs = plt.subplots(2)
        axs[0].plot(data_dict['torque'], color='#1f77b4', label='PDO')
        axs[0].plot(ripple             , color='#ff7f0e', label='ripple')
        axs[0].legend()
        axs[0].set_ylabel('torque (Nm)')
        axs[0].set_xlabel('Timestamp (ms)')
        axs[0].grid(b=True, which='major', axis='y', linestyle='-')
        axs[0].grid(b=True, which='major', axis='x', linestyle=':')
        axs[0].spines['top'].set_visible(False)
        axs[0].spines['right'].set_visible(False)
        axs[0].spines['left'].set_visible(False)

        data_dict['torque'] = [t - r for t, r in zip(data_dict['torque'], ripple)]
        axs[1].plot(data_dict['torque'], color='#2ca02c', label='diff')
        axs[1].legend()
        axs[1].set_ylabel('torque (Nm)')
        axs[1].set_xlabel('Timestamp (ms)')
        axs[1].grid(b=True, which='major', axis='y', linestyle='-')
        axs[1].grid(b=True, which='major', axis='x', linestyle=':')
        axs[1].spines['top'].set_visible(False)
        axs[1].spines['right'].set_visible(False)
        axs[1].spines['left'].set_visible(False)
        if plot_all:
            plt.show()
        else:
            if yaml_file == 'NULL':
                list_of_files = glob.glob('/logs/*.yaml')
                yaml_file = max(list_of_files, key=os.path.getctime)

            # Save the graph
            plt.tight_layout()
            fig_name = log_file[:-4] + '-0.png'
            print('Saving graph as: ' + fig_name)
            plt.savefig(fname=fig_name, format='png', bbox_inches='tight')

    if filter_type != 'NULL':
        ids = [0] + [i
                     for i in range(1, len(data_dict['loop_cnt']) - 1)
                     if data_dict['loop_cnt'][i] != data_dict['loop_cnt'][i - 1]
                    ] + [len(data_dict['loop_cnt'])-1]
        ts   = [data_dict[     'time'][ids[i-1]:ids[i]] for i in range(1, len(ids))]

        vels = [data_dict['motor_vel'][ids[i-1]:ids[i]] for i in range(1, len(ids))]
        vels_f = [freq_domain.filtered(v, max_freq=filter_freq, samp_freq=samp_freq, method=filter_type) for v in vels]
        data_dict['motor_vel'] = []
        for v in vels_f:
            data_dict['motor_vel'] += list(v)

        accs = []
        data_dict['motor_acc'] = []
        for t, v in zip(ts, vels):
            accs += [[0.0] + [(v[i] - v[i - 1]) / (t[i] - t[i - 1]) for i in range(1, len(t) - 1)] + [0.0]]
        for a in accs:
            data_dict['motor_acc'] += list(a)

        aux = [data_dict['aux'][ids[i-1]:ids[i]] for i in range(1, len(ids))]
        aux_f = [freq_domain.filtered(v, max_freq=filter_freq, samp_freq=samp_freq, method=filter_type) for v in aux]
        data_dict['aux'] = []
        for a in aux_f:
            data_dict['aux'] += list(a)

        tors = [data_dict['torque'][ids[i - 1] : ids[i]] for i in range(1, len(ids))]
        tors_f = [freq_domain.filtered(v, max_freq=filter_freq, samp_freq=samp_freq, method=filter_type) for v in tors]
        for t in tors_f:
            data_dict['torque'] += list(t)

    return data_dict


def process(yaml_file='NULL', log_file='NULL', plot_all=False):
    # load results
    if yaml_file == 'NULL':
        list_of_files = glob.glob('/logs/*.yaml')
        yaml_file = max(list_of_files, key=os.path.getctime)
        print('Loading: ' + yaml_file)

    plt.rcParams['savefig.dpi'] = 300
    freq0 = 0.1
    samp_freq = 1000
    num_of_sinusoids = 5
    trans_time = 5.0
    init_dv = 1.0
    init_dc = 2.0
    init_sigma = 4.0


    # read parameters from yaml file
    with open(yaml_file, 'r') as stream:
        out_dict = yaml.safe_load(stream)
        yaml_dict = out_dict['calib_friction']

    # read parameters from yaml file
    if 'location' in out_dict['log']:
        len_loc = len(out_dict['loc']['location'])
    else:
        len_loc = len('/logs/')
    motor_type = yaml_file[len_loc + 1:len_loc + 3]

    if 'freq0' in yaml_dict:
        freq0 = yaml_dict['freq0']
    if 'samp_freq' in yaml_dict:
        samp_freq = yaml_dict['samp_freq']
    if 'num_of_sinusoids' in yaml_dict:
        num_of_sinusoids = yaml_dict['num_of_sinusoids']
    if 'trans_time' in yaml_dict:
        trans_time = yaml_dict['trans_time']
    if 'secs' in yaml_dict:
        secs = yaml_dict['secs']
    if 'Motor_gear_ratio' in out_dict['results']['flash_params']:
        gear_ratio = out_dict['results']['flash_params']['Motor_gear_ratio']
    elif 'gear_ratio' in yaml_dict:
        gear_ratio = yaml_dict['gear_ratio']
    else:
        gear_ratio = 80
        print("no k_tau found, using default value: "+str(gear_ratio))
    if 'motorTorqueConstant' in out_dict['results']['flash_params']:
        k_tau = out_dict['results']['flash_params']['motorTorqueConstant']
    elif 'k_tau' in yaml_dict:
        k_tau = yaml_dict['k_tau']
    else:
        k_tau = 0.078
        print("no k_tau found, using default value: "+str(k_tau))
    if 'gamma' in yaml_dict:
        gamma = yaml_dict['gamma']
    else:
        gamma = 1000.0

    #initial guesses,
    inertia_dict = {'LI': 1.18, 'AV': 1.48, 'LE': 3.01, 'OR': 4.71, 'PO': 8.63, \
                    'Li': 1.18, 'Av': 1.48, 'Le': 3.01, 'Or': 4.71, 'Po': 8.63, \
                    'li': 1.18, 'av': 1.48, 'le': 3.01, 'or': 4.71, 'po': 8.63, \
                    'lI': 1.18, 'aV': 1.48, 'lE': 3.01, 'oR': 4.71, 'pO': 8.63, }
    # if motor_type in inertia_dict:
    #     warm_start = True
    #     init_inertia = inertia_dict[motor_type] * gear_ratio * gear_ratio / 100000
    #     if 'init_dv' in yaml_dict:
    #         init_dv = yaml_dict['init_dv']
    #     else:
    #         init_dv = 1.0
    #     if 'init_dc' in yaml_dict:
    #         init_dc = yaml_dict['init_dc']
    #     else:
    #         init_dc = 2.0
    #     if 'init_sigma' in yaml_dict:
    #         init_sigma = yaml_dict['init_sigma']
    #     else:
    #         init_sigma = 4.0
    #     bounds = ([0.75 * init_inertia,  0., 0.,  0., 0., 0., 0.],
    #               [1.25 * init_inertia, 10.,10., 10.,10.,10.,10.])
    #     print('bounds:' + str(bounds))
    # else:
    if motor_type in inertia_dict:
        print('Found no default values for motor type: ' + motor_type)
        warm_start = False
        init_dv = None
        init_dc = None
        init_sigma = None
        init_inertia = None
        bounds = ([0, np.inf])

    trj_info = TrjInfo(freq0=freq0,
                       num_of_sinusoids=num_of_sinusoids,
                       samp_freq=samp_freq,
                       trans_time=trans_time)

    # load data from log
    if log_file=='NULL':
        list_of_files = glob.glob('/logs/*-friction-calib.log')
        log_file = max(list_of_files, key=os.path.getctime)

    print('Using log: ' + log_file)
    #data_dict = dict_from_log(log_file)
    data_dict = get_from_log(log_file,
                             remove_ripple=True,
                             filter_type='simple',
                             samp_freq=trj_info.samp_freq,
                             filter_freq=10.0)
    motor = MotorData.from_dict(motor_dict=data_dict,
                                trj_info=trj_info,
                                gear_ratio=gear_ratio,
                                k_tau=k_tau)

    ## Linear model
    inertia = motor_terms.MotorInertia(init_inertia = out_dict['results']['flash_params']['gearedMotorInertia'])
    viscous_frict = motor_terms.AsymmetricViscousFriction(gamma=gamma)
    coulomb_strib_frict = motor_terms.AsymmetricCoulombStribeckFriction(gamma=gamma)
    #tau_off = motor_terms.TauOffset()

    regressor = LinearRegressor(huber_regr_strategy)
    linear_regression = LinearRegression(regressor)
    simulation = Simulation()

    #models = [inertia, coulomb_strib_frict, viscous_frict, tau_off]
    models = [coulomb_strib_frict, viscous_frict]
    for model in models:
        linear_regression.add_model(model)

    linear_regression.set_pos_vel_acc(motor.pos, motor.vel, motor.acc)
    linear_regression.set_samp_freq(trj_info.samp_freq)
    linear_regression.set_lhs(motor.tau_m)
    if warm_start:
        print('Using values: '+ str([init_inertia, init_dv, init_dc, init_sigma, gamma]) +' for motor type: ' + motor_type)
    param_dict = linear_regression.solve()#warm_start=warm_start, bounds=bounds)

    err = linear_regression.get_prediction_error(equalized=False)
    _, X = linear_regression.get_y_and_regr_matrix(equalized=False)
    params = np.array(list(linear_regression.get_param_dict().values()))
    Xp = X.dot(params)

    print('param_dict:')
    for k, v in param_dict.items():
        print('\t' + str(k) + '\t' + str(v))

    # RMSE
    RMSE = np.sqrt(np.mean(np.square(err)))
    NRMSE = RMSE / np.std(Xp + err)
    print('NRMSE: {NRMSE:.4f}\nRMSE: {RMSE:.4f}'.format(NRMSE=NRMSE, RMSE=RMSE))

    err = [i / (gear_ratio * k_tau) for i in (err)]
    Xp  = [i / (gear_ratio * k_tau) for i in (Xp)]
    fig, axs = plt.subplots()
    axs.plot(err + Xp, color='#ff7f0e', label='Reference')
    axs.plot(      Xp, color='#1f77b4', label='Linear Model')
    axs.legend()

    axs.set_ylabel('Current (A)')
    axs.set_xlabel('Timestamp (ms)')
    axs.axvline(0, color='black', lw=1.2)
    axs.axhline(0, color='black', lw=1.2)

    axs.set_xlim(0, len(Xp))
    plt_pad = (max(Xp) - min(Xp)) * 0.02
    axs.set_ylim(min(err + Xp) - plt_pad, max(err + Xp) + plt_pad)
    axs.grid(b=True, which='major', axis='y', linestyle='-')
    axs.grid(b=True, which='minor', axis='y', linestyle=':')
    axs.grid(b=True, which='major', axis='x', linestyle=':')
    axs.xaxis.set_major_locator(plt.MultipleLocator(len(Xp)/5))
    axs.xaxis.set_minor_locator(plt.MultipleLocator(len(Xp)/15))
    axs.spines['top'].set_visible(False)
    axs.spines['right'].set_visible(False)
    axs.spines['left'].set_visible(False)

    plt.tight_layout()
    if plot_all:
        plt.show()

        fig, axs = plt.subplots()
        axs.title('Torque reference - predicted')
        axs.set_ylabel('Error (Nm)')
        axs.set_xlabel('Timestamp (ms)')

        axs.plot(err, label='y -Xp')
        axs.axvline(0, color='black', lw=1.2)
        axs.axhline(0, color='black', lw=1.2)

        axs.set_xlim(0, len(err))
        plt_pad = (max(err) - min(err)) * 0.02
        axs.set_ylim(min(err) - plt_pad, max(err) + plt_pad)
        axs.grid(b=True, which='major', axis='y', linestyle='-')
        axs.grid(b=True, which='minor', axis='y', linestyle=':')
        axs.grid(b=True, which='major', axis='x', linestyle=':')
        axs.xaxis.set_major_locator(plt.MultipleLocator(len(err) / 5))
        axs.xaxis.set_minor_locator(plt.MultipleLocator(len(err) / 15))
        axs.spines['top'].set_visible(False)
        axs.spines['right'].set_visible(False)
        axs.spines['left'].set_visible(False)
        plt.show()

        fig, axs = plt.subplots()
        axs.title('Error Distribution - Linear Model')
        axs.set_xlabel('Error (Nm)')
        axs.hist(err, 100, label='y -Xp')

        plt_pad = (max(err) - min(err)) * 0.02
        axs.set_xlim(min(err) - plt_pad, max(err) + plt_pad)
        axs.grid(b=True, which='major', axis='y', linestyle=':')
        axs.spines['top'].set_visible(False)
        axs.spines['right'].set_visible(False)
        axs.spines['left'].set_visible(False)
        plt.show()
    else:
        # Save the graph
        fig_name = log_file[:-4] + '-1.png'
        print('Saving graph as: ' + fig_name)
        plt.savefig(fname=fig_name, format='png', bbox_inches='tight')


    ## Run simulation
    print('Running simulation')
    linear_regression.add_model(inertia)  # add inertia for simulation
    linear_model = linear_regression.get_model_copy()
    simulation.set_init_conditions(motor)
    simulation.set_time_interval(trj_info)

    simulation.set_model(linear_model)
    simulation.set_motor_torque(motor)
    pos_lin, vel_lin = simulation.solve_ODE()

    # non_linear_model = non_linear_regression.get_model_copy()
    # simulation.set_model(non_linear_model)
    # pos_non, vel_non = simulation.solve_ODE()

    fig, axs = plt.subplots()
    axs.plot(motor.pos[:-2],color='#ff7f0e', label='original')
    axs.plot(pos_lin,       color='#1f77b4', label='Linear Model')
    # axs.plot(pos_non, label='Nonlinear Model')
    plt.legend()
    axs.legend()

    axs.set_ylabel('Position$_{link}$ (rad)')
    axs.set_xlabel('Timestamp (ms)')
    axs.axvline(0, color='black', lw=1.2)
    axs.axhline(0, color='black', lw=1.2)

    axs.set_xlim(0, len(motor.pos[:-2]))
    plt_pad = (max(motor.pos) - min(motor.pos)) * 0.05
    #axs.set_ylim(min(motor.pos) - plt_pad, max(motor.pos) + plt_pad)
    axs.grid(b=True, which='major', axis='y', linestyle='-')
    axs.grid(b=True, which='minor', axis='y', linestyle=':')
    axs.grid(b=True, which='major', axis='x', linestyle=':')
    axs.xaxis.set_major_locator(plt.MultipleLocator(len(motor.pos) / 5))
    axs.xaxis.set_minor_locator(plt.MultipleLocator(len(motor.pos) / 15))
    axs.spines['top'].set_visible(False)
    axs.spines['right'].set_visible(False)
    axs.spines['left'].set_visible(False)

    plt.tight_layout()
    if plot_all:
        plt.show()
    else:
        # Save the graph
        fig_name = log_file[:-4] + '.png'
        print('Saving graph as: ' + fig_name)
        plt.savefig(fname=fig_name, format='png', bbox_inches='tight')

        # savign results
    if yaml_file[-12:] != 'results.yaml':
        yaml_file = log_file[:-16] + 'results.yaml'
        out_dict['results']={}

    out_dict['results']['friction'] = {}
    # FIXME: put back : float(param_dict['motor_inertia'])
    out_dict['results']['friction']['motor_inertia'] = out_dict['results']['flash_params']['gearedMotorInertia']

    out_dict['results']['friction']['viscous_friction'] = {}
    if 'dv' in param_dict:
        out_dict['results']['friction']['viscous_friction']['dv_plus'] = float(param_dict['dv'])
        out_dict['results']['friction']['viscous_friction']['dv_minus'] = float(param_dict['dv'])
    else:
        out_dict['results']['friction']['viscous_friction']['dv_plus'] = float(param_dict['dv_plus'])
        out_dict['results']['friction']['viscous_friction']['dv_minus'] = float(param_dict['dv_minus'])

    out_dict['results']['friction']['coulomb_and_stribeck_friction'] = {}
    if 'dc' in param_dict:
        out_dict['results']['friction']['coulomb_and_stribeck_friction']['dc_plus'] = float(param_dict['dc'])
        out_dict['results']['friction']['coulomb_and_stribeck_friction']['dc_minus'] = float(param_dict['dc'])
    else:
        out_dict['results']['friction']['coulomb_and_stribeck_friction']['dc_plus'] = float(param_dict['dc_plus'])
        out_dict['results']['friction']['coulomb_and_stribeck_friction']['dc_minus'] = float(param_dict['dc_minus'])
    out_dict['results']['friction']['coulomb_and_stribeck_friction']['sigma_plus'] = float(param_dict['sigma_plus'])
    out_dict['results']['friction']['coulomb_and_stribeck_friction']['sigma_minus'] = float(param_dict['sigma_minus'])

    out_dict['results']['friction']['friction_model_RMSE'] = float(RMSE)
    out_dict['results']['friction']['friction_model_NRMSE'] = float(NRMSE)

    print('Saving results in: ' + yaml_file)
    with open(yaml_file, 'w', encoding='utf8') as outfile:
        yaml.dump(out_dict, outfile, default_flow_style=False, allow_unicode=True)

    return yaml_file

if __name__ == "__main__":
    list_of_files = glob.glob('/logs/*-results.yaml')
    config_file = max(list_of_files, key=os.path.getctime)
    process(config_file)
