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
import plot_utils
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


def move_log(new_name='null'):
    list_of_files = glob.glob('/tmp/CentAcESC_*_log.txt')
    tmp_file = max(list_of_files, key=os.path.getctime)
    if new_name == 'null':
        list_of_files = glob.glob('/logs/*-ripple_calib.log')
        last_log = max(list_of_files, key=os.path.getctime)[:-31]
        new_name = last_log + datetime.now().strftime(
            "%Y%m%d%H%M%S") + '-friction-calib.log'
    cmd = 'cp ' + tmp_file + ' ' + new_name
    if os.system(cmd):
        sys.exit(plot_utils.bcolors.FAIL +
                 u'[\u2717] Error while copying logs' +
                 plot_utils.bcolors.ENDC)


def process(yaml_file, plot_all=False):

    freq0 = 0.1
    samp_freq = 1000
    num_of_sinusoids = 5
    trans_time = 5.0

    # read parameters from yaml file
    with open(yaml_file, 'r') as stream:
        out_dict = yaml.safe_load(stream)
        yaml_dict = out_dict['calib_friction']
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

    trj_info = TrjInfo(freq0=freq0,
                       num_of_sinusoids=num_of_sinusoids,
                       samp_freq=samp_freq,
                       trans_time=trans_time)

    # load data from log
    list_of_files = glob.glob('/logs/*-friction-calib.log')
    fname = max(list_of_files, key=os.path.getctime)
    #motor = MotorData.from_motor_log(fname,
    data_dict = dict_from_log(fname)
    motor = MotorData.from_dict (    data_dict,
                                     trj_info,
                                     gear_ratio=80,
                                     k_tau=0.040250)

    ## Linear model
    inertia = motor_terms.MotorInertia()
    viscous_frict = motor_terms.AsymmetricViscousFriction(gamma=1000.0)
    coulomb_strib_frict = motor_terms.AsymmetricCoulombStribeckFriction(gamma=1000.0)
    tau_off = motor_terms.TauOffset()

    regressor = LinearRegressor(huber_regr_strategy)
    linear_regression = LinearRegression(regressor)
    simulation = Simulation()

    models = [inertia, coulomb_strib_frict, viscous_frict, tau_off]
    for model in models:
        linear_regression.add_model(model)

    linear_regression.set_pos_vel_acc(motor.pos, motor.vel, motor.acc)
    linear_regression.set_samp_freq(trj_info.samp_freq)
    linear_regression.set_lhs(motor.tau_m)

    param_dict = linear_regression.solve()

    err = linear_regression.get_prediction_error(equalized=False)
    _, X = linear_regression.get_y_and_regr_matrix(equalized=False)
    params = np.array(list(linear_regression.get_param_dict().values()))
    Xp = X.dot(params)

    linear_model = linear_regression.get_model_copy()

    print('param_dict:')
    for k, v in param_dict.items():
        print('\t'+str(k)+str(v))

    fig, axs = plt.subplots()
    axs.plot(err + Xp, color='#ff7f0e', label='Reference')
    axs.plot(      Xp, color='#1f77b4', label='Linear Model')
    axs.legend()

    axs.set_ylabel('torque (Nm)')
    axs.set_xlabel('Timestamp (ms)')
    axs.axvline(0, color='black', lw=1.2)
    axs.axhline(0, color='black', lw=1.2)

    axs.set_xlim(0, len(Xp))
    plt_pad = (max(Xp) - min(Xp)) * 0.02
    axs.set_ylim(min(Xp) - plt_pad, max(Xp) + plt_pad)
    axs.grid(b=True, which='major', axis='y', linestyle='-')
    axs.grid(b=True, which='minor', axis='y', linestyle=':')
    axs.grid(b=True, which='major', axis='x', linestyle=':')
    axs.xaxis.set_major_locator(plt.MultipleLocator(len(Xp)/5))
    axs.xaxis.set_minor_locator(plt.MultipleLocator(len(Xp)/15))
    axs.spines['top'].set_visible(False)
    axs.spines['right'].set_visible(False)
    axs.spines['left'].set_visible(False)

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
        pdf_name = fname[:-4] + '-1.pdf'
        print('Saving graph as: ' + pdf_name)
        plt.savefig(fname=pdf_name, format='pdf')

    # ## Nonlinear model
    # non_linear_regression = NonLinearRegression()

    # non_linear_regression.set_pos_vel_acc(motor.pos, motor.vel, motor.acc)
    # non_linear_regression.set_samp_freq(trj_info.samp_freq)
    # non_linear_regression.set_lhs(motor.tau_m)

    # linear_model1 = linear_regression.get_model_copy()
    # non_linear_regression.add_model(linear_model1)

    # torque_ripple = motor_terms.TorqueRippleSinPhase(num_of_sin=3,
    #                                                  init_ampl=5.0,
    #                                                  init_freq=10.0)
    # #torque_ripple = motor_terms.TorqueRippleVelDependent(num_of_sin=3, init_ampl=5.0)
    # non_linear_regression.add_model(torque_ripple)
    # non_lin_param_dict = non_linear_regression.solve()
    # print(non_lin_param_dict)

    # err = non_linear_regression.get_prediction_error()
    # y = non_linear_regression.get_y()
    # predictions = non_linear_regression.get_prediction_array()

    # fig, axs = plt.subplots()
    # axs.plot(predictions, color='#ff7f0e', label='Reference')
    # axs.plot(          y, color='#1f77b4', label='Nonlinear Model')
    # axs.legend()

    # axs.set_ylabel('torque (Nm)')
    # axs.set_xlabel('Timestamp (ms)')
    # axs.axvline(0, color='black', lw=1.2)
    # axs.axhline(0, color='black', lw=1.2)

    # axs.set_xlim(0, len(Xp))
    # plt_pad = (max(Xp) - min(Xp)) * 0.02
    # axs.set_ylim(min(Xp) - plt_pad, max(Xp) + plt_pad)
    # axs.grid(b=True, which='major', axis='y', linestyle='-')
    # axs.grid(b=True, which='minor', axis='y', linestyle=':')
    # axs.grid(b=True, which='major', axis='x', linestyle=':')
    # axs.xaxis.set_major_locator(plt.MultipleLocator(len(Xp) / 5))
    # axs.xaxis.set_minor_locator(plt.MultipleLocator(len(Xp) / 15))
    # axs.spines['top'].set_visible(False)
    # axs.spines['right'].set_visible(False)
    # axs.spines['left'].set_visible(False)

    # if plot_all:
    #     plt.show()

    #     fig, axs = plt.subplots()
    #     axs.title('Torque Error - Nonlinear Model')
    #     axs.set_ylabel('Error (Nm)')
    #     axs.set_xlabel('Timestamp (ms)')

    #     axs.plot(err, label='y -Xp')
    #     axs.axvline(0, color='black', lw=1.2)
    #     axs.axhline(0, color='black', lw=1.2)

    #     axs.set_xlim(0, len(err))
    #     plt_pad = (max(err) - min(err)) * 0.02
    #     axs.set_ylim(min(err) - plt_pad, max(err) + plt_pad)
    #     axs.grid(b=True, which='major', axis='y', linestyle='-')
    #     axs.grid(b=True, which='minor', axis='y', linestyle=':')
    #     axs.grid(b=True, which='major', axis='x', linestyle=':')
    #     axs.xaxis.set_major_locator(plt.MultipleLocator(len(err) / 5))
    #     axs.xaxis.set_minor_locator(plt.MultipleLocator(len(err) / 15))
    #     axs.spines['top'].set_visible(False)
    #     axs.spines['right'].set_visible(False)
    #     axs.spines['left'].set_visible(False)
    #     plt.show()

    #     fig, axs = plt.subplots()
    #     axs.title('Error Distribution - Nonlinear Model')
    #     axs.set_xlabel('Error (Nm)')
    #     axs.hist(err, 100, label='y -Xp')

    #     plt_pad = (max(err) - min(err)) * 0.02
    #     axs.set_xlim(min(err) - plt_pad, max(err) + plt_pad)
    #     axs.grid(b=True, which='major', axis='y', linestyle=':')
    #     axs.spines['top'].set_visible(False)
    #     axs.spines['right'].set_visible(False)
    #     axs.spines['left'].set_visible(False)
    #     plt.show()
    # else:
    #     # Save the graph
    #     pdf_name = fname[:-4] + '-2.pdf'
    #     print('Saving graph as: ' + pdf_name)
    #     plt.savefig(fname=pdf_name, format='pdf')

    ## Run simulation
    print('Running simulation')
    simulation.set_init_conditions(motor)
    simulation.set_time_interval(trj_info)

    simulation.set_model(linear_model)
    simulation.set_motor_torque(motor)
    pos_lin, vel_lin = simulation.solve_ODE()

    # non_linear_model = non_linear_regression.get_model_copy()
    # simulation.set_model(non_linear_model)
    # pos_non, vel_non = simulation.solve_ODE()

    fig, axs = plt.subplots()
    axs.plot(motor.pos[:-2], label='original')
    axs.plot(pos_lin, label='Linear Model')
    # axs.plot(pos_non, label='Nonlinear Model')
    plt.legend()
    axs.legend()

    axs.set_ylabel('Position (rad)')
    axs.set_xlabel('Timestamp (ms)')
    axs.axvline(0, color='black', lw=1.2)
    axs.axhline(0, color='black', lw=1.2)

    axs.set_xlim(0, len(Xp))
    plt_pad = (max(Xp) - min(Xp)) * 0.02
    axs.set_ylim(min(Xp) - plt_pad, max(Xp) + plt_pad)
    axs.grid(b=True, which='major', axis='y', linestyle='-')
    axs.grid(b=True, which='minor', axis='y', linestyle=':')
    axs.grid(b=True, which='major', axis='x', linestyle=':')
    axs.xaxis.set_major_locator(plt.MultipleLocator(len(Xp) / 5))
    axs.xaxis.set_minor_locator(plt.MultipleLocator(len(Xp) / 15))
    axs.spines['top'].set_visible(False)
    axs.spines['right'].set_visible(False)
    axs.spines['left'].set_visible(False)

    if plot_all:
        plt.show()
    else:
        # Save the graph
        pdf_name = fname[:-4] + '.pdf'
        print('Saving graph as: ' + pdf_name)
        plt.savefig(fname=pdf_name, format='pdf')

if __name__ == "__main__":
    config_file = os.path.expanduser('~/ecat_dev/ec_master_app/examples/motor-calib/config.yaml')
    process(config_file)
