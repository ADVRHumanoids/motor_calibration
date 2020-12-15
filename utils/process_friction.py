#!/usr/bin/python3

import yaml
import os
import json
import pandas as pd
import numpy as np

from os import path
from math import sqrt
from pprint import pprint
from copy import deepcopy
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

from friction_calibration_tool.utils_module.motor import MotorData
from friction_calibration_tool.utils_module.trajectory import TrjInfo, MultisineTrjInfo
from friction_calibration_tool.utils_module.simulation import Simulation
from friction_calibration_tool.utils_module.logimport import MotorDf
from friction_calibration_tool.models.base import CompositeModel
from friction_calibration_tool.models import concrete as motor_terms
from friction_calibration_tool.regression.concrete import ( NonLinearRegression,
                                                              LinearRegression,
                                                              LinearRegressor,
                                                              huber_regr_strategy,
                                                              lsq_pseudoinv_strategy,
                                                              scipy_lsq_linear_strategy)


#calculate RMSE
def RMSE(actual, pred):
    return sqrt(mean_squared_error(actual, pred))

#process friction and inertia
def process(yaml_file,
            min_gamma=1000.,
            max_gamma=np.inf,
            min_const_vel=-1.,
            max_const_vel=1.,
            const_vel_lowpass_cutoff=None,
            plot_all=False):
    # read parameters from yaml file
    print('[i] Using yaml_file: ' + yaml_file)
    with open(yaml_file) as f:
        try:
            motor_yaml = yaml.safe_load(f)

        except Exception as e:
            raise Exception('error in yaml parsing')

    # find logs
    head, tail = path.split(yaml_file)
    code_string = tail[:-len("-results.yaml")]
    const_vel_log_fname = path.join(head, f"{code_string}-friction_calib.log")
    multisine_log_fname = path.join(head, f"{code_string}-inertia_calib.log")

    save_path = f'{head}/images/'

    # motor parameters
    samp_freq = 1e9 / (motor_yaml['ec_board_ctrl']['sync_cycle_time_ns'])
    k_tau = float(motor_yaml['results']['flash_params']['motorTorqueConstant']),
    gear_ratio = float(motor_yaml['results']['flash_params']['Motor_gear_ratio'])

    # import constant velocity trjs from log
    motor_df = MotorDf.ConstVelTrj(const_vel_log_fname).range('motor_vel', min_const_vel, max_const_vel)

    # filter motor current and link torque
    if const_vel_lowpass_cutoff is not None:
        dfs = []
        for batch in range(motor_df.df['batch_id'].nunique()):
            df = motor_df.range('batch_id', batch, batch).filter(['aux'], const_vel_lowpass_cutoff)
            df = df.range('batch_id', batch, batch).filter(['torque'], const_vel_lowpass_cutoff)
            dfs.append(df.df)

        motor_df = MotorDf.Concat(dfs)

    const_vel_data_dict = motor_df.to_dict()
    const_vel_trj = TrjInfo(samp_freq)
    const_vel_trj.set_trj_data(
        time=np.array(const_vel_data_dict['time']) - const_vel_data_dict['time'][0],
        pos=const_vel_data_dict['motor_pos'],
        vel=const_vel_data_dict['motor_vel'],
        acc=np.zeros(len(const_vel_data_dict['motor_pos'])))

    const_vel_trj_tau_m = np.array(const_vel_data_dict['aux']) * k_tau * gear_ratio
    const_vel_trj_tau_l = np.array(const_vel_data_dict['torque'])

    const_vel_trj_iterator = zip(const_vel_trj.pos, const_vel_trj.vel, const_vel_trj.acc, const_vel_trj.time)
    tau_l_offset = motor_yaml['results']['ripple']['c']
    no_offset_const_vel_trj_tau_l = const_vel_trj_tau_l - tau_l_offset
    cons_vel_trj_lhs = const_vel_trj_tau_m - no_offset_const_vel_trj_tau_l
    motor_df.df['lhs'] = cons_vel_trj_lhs

    multisine_data_dict = MotorDf.MultisineTrj(multisine_log_fname).to_dict()
    multisine_trj = MultisineTrjInfo(freq0=motor_yaml['calib_inertia']['freq0'],
                                     num_of_sinusoids=len(motor_yaml['calib_inertia']['A']),
                                     samp_freq=samp_freq,
                                     trans_time=motor_yaml['calib_inertia']['trans_time'])
    multisine_motor = MotorData.from_dict(multisine_data_dict, multisine_trj, k_tau=k_tau, gear_ratio=gear_ratio)

    non_lin_friction_model = motor_terms.NonLinearFriction(const_vel_trj.pos, const_vel_trj.vel, const_vel_trj.acc, cons_vel_trj_lhs,
                                                           const_vel_trj.samp_freq, init_gamma=1000)

    non_linear_regression = NonLinearRegression(lower_bound=min_gamma, upperbound=max_gamma)
    non_linear_regression.set_pos_vel_acc(const_vel_trj.pos, const_vel_trj.vel, const_vel_trj.acc)
    non_linear_regression.set_samp_freq(const_vel_trj.samp_freq)
    non_linear_regression.set_lhs(cons_vel_trj_lhs)
    non_linear_regression.add_model(non_lin_friction_model)
    non_lin_param_dict = non_linear_regression.solve()
    pprint(non_lin_param_dict)

    friction_model = non_linear_regression.get_model_copy()
    predicted_friction = [friction_model.predict(None, vel, None, None) for vel in motor_df['motor_vel']]
    actual_friction = cons_vel_trj_lhs
    friction_rmse = RMSE(actual_friction, predicted_friction)

    multisine_trj_zip = list(zip(multisine_motor.pos, multisine_motor.vel, multisine_motor.acc))
    no_offset_multisine_trj_tau_l = multisine_motor.torque - tau_l_offset

    multisine_trj_friction = [friction_model.predict(None, vel, None, None) for pos, vel, acc in multisine_trj_zip]
    multisine_trj_lhs = multisine_motor.tau_m - np.array(multisine_trj_friction) - no_offset_multisine_trj_tau_l

    inertia = motor_terms.MotorInertia()
    regressor = LinearRegressor(huber_regr_strategy)
    linear_regression = LinearRegression(regressor)
    linear_regression.add_model(inertia)
    linear_regression.set_pos_vel_acc(multisine_motor.pos, multisine_motor.vel, multisine_motor.acc)
    linear_regression.set_samp_freq(multisine_motor.samp_freq)
    linear_regression.set_lhs(multisine_trj_lhs)
    param_dict = linear_regression.solve()
    pprint(param_dict)

    inertia_model = linear_regression.get_model_copy()

    predicted_inertia_torque = [inertia_model.predict(pos, vel, acc, None) for pos, vel, acc in multisine_trj_zip]
    actual_inertia_torque = multisine_trj_lhs
    inertia_rmse = RMSE(actual_inertia_torque, predicted_inertia_torque)

    motor_model = CompositeModel()
    motor_model.push(friction_model)
    motor_model.push(inertia)
    print('Motor Model:', f'gamma_c: {non_lin_param_dict["gamma_c"]}', f'gamma_v: {non_lin_param_dict["gamma_v"]}',
          f'{motor_model.get_param_dict()}', sep='\n')

    title =  code_string + '_gear_ratio_{}_k_tau_{}_cutoff_{}'.format(int(gear_ratio), k_tau[0], const_vel_lowpass_cutoff)

    if os.path.isdir(save_path) is False:
        try:
            os.makedirs(save_path)
        except OSError:
            print("Creation of the directory %s failed" % save_path)
        else:
            print("Successfully created the directory %s" % save_path)

    results = {'min_gamma': min_gamma, 'max_gamma': max_gamma,
               'min_const_vel': min_const_vel, 'max_const_vel': max_const_vel}
    results.update(non_linear_regression.get_param_dict())
    results.update(non_lin_friction_model.coulomb_frict.get_param_dict())
    results.update(non_lin_friction_model.viscous_frict.get_param_dict())
    results.update(linear_regression.get_param_dict())
    results.update({'actual_motor_inertia': motor_yaml['results']['flash_params']['gearedMotorInertia']})
    results.update({'friction_RMSE': friction_rmse, 'inertia_RMSE': inertia_rmse})

    df = pd.DataFrame(results, index=(code_string[:-6],))

    with open(os.path.join(save_path, 'params.csv') , 'w') as file:
        df.to_csv(file, float_format="%.6f")



    figsize = (18,12)
    extension = ".png"
    dpi = 100

    f = plt.figure(figsize=figsize, dpi=dpi)
    params = non_lin_friction_model.coulomb_frict.get_param_dict()
    params.update(non_lin_friction_model.viscous_frict.get_param_dict())
    plt.plot(motor_df['motor_vel'], motor_df['lhs'], 'b*', label='tau_m - tau_l')
    vel_range = np.arange(min(const_vel_trj.vel), max(const_vel_trj.vel), 1 / const_vel_trj.samp_freq)
    modeled_friction = [friction_model.predict(None, vel, None, None) for vel in vel_range]
    plt.plot(vel_range, modeled_friction, 'r', label='modeled_friction:\n - gamma_c: {:.3f}\n - gamma_v: {:.3f}\n - dc_minus: {:.3f}\n - dc_plus {:.3f}\n - dv_minus: {:.3f}\n - dv_plus {:.3f}'.format(
        non_lin_param_dict["gamma_c"], non_lin_param_dict["gamma_v"], params["dc_minus"], params["dc_plus"], params["dv_minus"], params["dv_plus"]))
    plt.xlabel('w [rad/s]'),  plt.ylabel('Torque [Nm]')
    plt.title(title)
    plt.legend()
    fname = f"{code_string}-torque_vs_w{extension}"
    f.savefig(os.path.join(save_path, fname), bbox_inches='tight')

    f = plt.figure(figsize=figsize, dpi=dpi)
    plt.plot(motor_df['time'], motor_df['lhs'], 'b*', label='actual: tau_m - tau_l')
    plt.plot(motor_df['time'], [friction_model.predict(None, vel, None, None) for vel in motor_df['motor_vel']],'r*' , label='predicted: tau_m - tau_l')
    plt.xlabel('time [s]'), plt.ylabel('Torque [Nm]')
    plt.title(title)
    plt.legend()
    fname = f"{code_string}-torque_vs_time{extension}"
    f.savefig(os.path.join(save_path, fname), bbox_inches='tight')

    error = np.array(actual_friction) - np.array(predicted_friction) #motor_df.df['lhs'].to_numpy() - np.array([friction_model.predict(None, vel, None, None) for vel in motor_df['motor_vel']])

    f = plt.figure(figsize=figsize, dpi=dpi)
    plt.hist(error, 200, label='error [Nm]')
    plt.xlabel('Torque [Nm]')
    plt.title(title)
    plt.legend()
    fname = f"{code_string}-error_hist{extension}"
    f.savefig(os.path.join(save_path, fname), bbox_inches='tight')

    f = plt.figure(figsize=figsize, dpi=dpi)
    plt.plot(motor_df['motor_vel'], error, '*', label='error [Nm]')
    plt.xlabel('w [rad/s]'), plt.ylabel('Torque [Nm]')
    plt.title(title)
    plt.legend()
    fname = f"{code_string}-error_vs_w{extension}"
    f.savefig(os.path.join(save_path, fname), bbox_inches='tight')

    # simulation = Simulation()
    # simulation.set_init_conditions(multisine_motor)
    # simulation.set_time_interval(multisine_trj)
    # simulation.set_model(motor_model)
    # simulation.set_motor_torque(multisine_motor)
    # pos, vel = simulation.solve_ODE()
    #
    # plt.figure()
    # plt.plot(pos, label='model (simulation)')
    # plt.plot(multisine_motor.pos[:-2], label='original')
    # plt.xlabel('time [ms]'), plt.ylabel('Theta [rad]')
    # plt.legend()

    if plot_all:
        plt.show()


if __name__ == '__main__':
    min_gamma = 1000.
    max_gamma = np.inf
    min_const_vel = -1.
    max_const_vel = 1.
    const_vel_lowpass_cutoff = None

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('yaml_file', type=str, help="the path of the calibration yaml file")
    args = parser.parse_args()
    process(yaml_file=args.yaml_file,
            min_gamma=min_gamma,
            max_gamma=max_gamma,
            min_const_vel=min_const_vel,
            max_const_vel=max_const_vel,
            const_vel_lowpass_cutoff=const_vel_lowpass_cutoff)