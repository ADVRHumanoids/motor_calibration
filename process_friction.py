import os
import sys
import glob
#import yaml
#import time
#import datetime
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

#import costum
import plot_utils
from friction_calibration_tool.utils_module import motor_eqn_models as motor_terms
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

    list_of_files = glob.glob('/logs/*-friction-calib.log')
    fname = max(list_of_files, key=os.path.getctime)
    motor = MotorData.from_motor_log(fname,
                                     trj_info,
                                     gear_ratio=80,
                                     k_tau=0.040250)

    # From dynamic_characterization.py
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

    print(param_dict)

    plt.figure()
    plt.plot(Xp, label='Xp')
    plt.plot(err + Xp, label='y')
    plt.legend()

    plt.figure()
    plt.plot(err, label='y -Xp')
    plt.legend()

    plt.figure()
    plt.hist(err, 100, label='y -Xp')
    plt.legend()

    non_linear_regression = NonLinearRegression()

    non_linear_regression.set_pos_vel_acc(motor.pos, motor.vel, motor.acc)
    non_linear_regression.set_samp_freq(trj_info.samp_freq)
    non_linear_regression.set_lhs(motor.tau_m)

    linear_model1 = linear_regression.get_model_copy()
    non_linear_regression.add_model(linear_model1)

    torque_ripple = motor_terms.TorqueRippleSinPhase(num_of_sin=num_of_sin,
                                                     init_ampl=5.0,
                                                     init_freq=10.0)
    #torque_ripple = motor_terms.TorqueRippleVelDependent(num_of_sin=3, init_ampl=5.0)
    non_linear_regression.add_model(torque_ripple)
    non_lin_param_dict = non_linear_regression.solve()
    print(non_lin_param_dict)

    err = non_linear_regression.get_prediction_error()
    y = non_linear_regression.get_y()
    predictions = non_linear_regression.get_prediction_array()

    plt.figure()
    plt.plot(predictions, label='prediction')
    plt.plot(y, label='y')
    plt.legend()

    plt.figure()
    plt.plot(err, label='y - prediction')
    plt.legend()

    plt.figure()
    plt.hist(err, 100, label='y - prediction')
    plt.legend()

    simulation.set_init_conditions(motor)
    simulation.set_time_interval(trj_info)

    simulation.set_model(linear_model)
    simulation.set_motor_torque(motor)

    pos, vel = simulation.solve_ODE()

    plt.figure()
    plt.plot(pos, label='simulation')
    plt.plot(motor.pos[:-2], label='original')
    plt.legend()

    non_linear_model = non_linear_regression.get_model_copy()
    simulation.set_model(non_linear_model)

    pos, vel = simulation.solve_ODE()

    plt.figure()
    plt.plot(pos, label='simulation')
    plt.plot(motor.pos[:-2], label='original')
    plt.legend()

    plt.show()