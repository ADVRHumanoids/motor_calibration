#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import yaml
import numpy as np
# tell matplotlib not to try to load up GTK as it returns errors over ssh
from matplotlib import use as plt_use
plt_use("Agg")
from matplotlib import pyplot as plt

#import costum files
from utils import process_phase
from utils import process_torque
from utils import process_ripple
from utils import process_friction
from utils import process_frequency
from utils import plot_utils
from utils import move_utils
from utils.prompt_utils import single_yes_or_no_question as prompt_user

## Parameters:
# path to test-pdo
cmd0 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/calib-test-pdo/calib-test-pdo')
# path to phase-calib to test phase angle and log data
cmd1 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/phase-calib/phase-calib')
# path to set-phase to set the optimized value to the motor
cmd1b = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/set-phase/set-phase')
# path to ripple-calib to test test ripple and positionl offset
cmd2 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/torque-calib/torque-calib')
# path to set-phase to set the optimized value to the motor
cmd2b = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/set-torque/set-torque')
# path to ripple-calib to test test ripple and positionl offset
cmd3 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/ripple-calib/ripple-calib')
# path to friction-calib for friction identification
cmd4 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/friction-calib/friction-calib')
# path to inertia-calib for inertia identification
cmd4b = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/inertia-calib/inertia-calib')
# path to frequency-calib for frequecy response calibration
cmd5 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/frequency-calib/frequency-calib')
# path to the configuration file for the motor and the test variables
config_file = os.path.expanduser('~/ecat_dev/ec_master_app/examples/motor-calib/config.yaml')

#print logo
plot_utils.print_alberobotics()

## test pdo
print(plot_utils.bcolors.OKBLUE + "[i] Starting test-pdo" + plot_utils.bcolors.ENDC)
if os.system(cmd0 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during test-pdo' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended test-pdo successfully" + plot_utils.bcolors.ENDC)

#get updated yaml file
list_of_files = glob.glob('/logs/**/*_results.yaml', recursive=True)
config_file = max(list_of_files, key=os.path.getctime)

## test phase angles
print(plot_utils.bcolors.OKBLUE + "[i] Starting phase-calib" + plot_utils.bcolors.ENDC)
if os.system(cmd1 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during phase-calib' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended phase-calib successfully" + plot_utils.bcolors.ENDC)

# process extracted data
print(plot_utils.bcolors.OKBLUE + "[i] Processing phase data" + plot_utils.bcolors.ENDC)
config_file = process_phase.process(yaml_file=config_file, plot_all=False)

# Upload to motor the best phase angle
print(plot_utils.bcolors.OKBLUE + "[i] Sending phase angle to motor using set-phase" +  plot_utils.bcolors.ENDC)
if os.system(cmd1b + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during set-phase' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended set-phase successfully" + plot_utils.bcolors.ENDC)

## test torquecell's torsion bar stiffness and torque constant
# prompt user to connect loadcell before continuing
print("For torsion bar stiffness and torque constant calibration, the loadcell is needed.")
while not prompt_user("""Before continuing make sure the loadcell is properly connected and the motor's flange is in contact with it.
Continue?"""):
    pass

#run test
print(plot_utils.bcolors.OKBLUE + "[i] Starting torque-calib" + plot_utils.bcolors.ENDC)
if os.system(cmd2 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during torque-calib' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended torque-calib successfully" + plot_utils.bcolors.ENDC)

# process extracted data
print(plot_utils.bcolors.OKBLUE + "[i] Processing torque data" + plot_utils.bcolors.ENDC)
config_file = process_torque.process(yaml_file=config_file, plot_all=False)

# Upload to motor the updated torsion bar stiffness (and torque constant?)
print(plot_utils.bcolors.OKBLUE + "[i] Sending torsion bar stiffness to motor using set-torque" +  plot_utils.bcolors.ENDC)
if os.system(cmd2b + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during set-torque' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended set-torque successfully" + plot_utils.bcolors.ENDC)

## test ripple and position dependant torque
# prompt user to disconnect loadcell before continuing
print("For ripple and position dependant torque, the motor must be free to move.")
while not prompt_user("""Before continuing make sure the motor's output flange has nothing connected.
Continue?"""):
    pass

# run test
print(plot_utils.bcolors.OKBLUE + "[i] Starting ripple-calib" + plot_utils.bcolors.ENDC)
if os.system(cmd3 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during ripple-calib' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended ripple-calib successfully" + plot_utils.bcolors.ENDC)

# process extracted data
print(plot_utils.bcolors.OKBLUE + "[i] Processing ripple data" + plot_utils.bcolors.ENDC)
config_file = process_ripple.process(yaml_file=config_file, plot_all=False)

## Friction identification
print(plot_utils.bcolors.OKBLUE + "[i] Starting friction-calib" + plot_utils.bcolors.ENDC)
if os.system(cmd4 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during friction-calib' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended friction-calib successfully" + plot_utils.bcolors.ENDC)

## Inertia identification
print(plot_utils.bcolors.OKBLUE + "[i] Starting inertia-calib" + plot_utils.bcolors.ENDC)
if os.system(cmd4b + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during inertia-calib' + plot_utils.bcolors.ENDC)
move_utils.move_log(yaml_file=config_file)
print(plot_utils.bcolors.OKBLUE + "[i] Ended inertia-calib successfully" + plot_utils.bcolors.ENDC)

# process extracted data
print(plot_utils.bcolors.OKBLUE + "[i] Processing friction and inertia data" + plot_utils.bcolors.ENDC)
process_friction.process(yaml_file=config_file, plot_all=False)

## Frequency response calibration
# prompt user to fully lock the motor before continuing
print("For frequency response calibration, the motor must be fully locked")
while not prompt_user("""Before continuing make sure the motor's output flange is properly locked.
Continue?"""):
    pass

# run test
print(plot_utils.bcolors.OKBLUE + "[i] Starting frequency-calib" + plot_utils.bcolors.ENDC)
if os.system(cmd5 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during frequency-calib' + plot_utils.bcolors.ENDC)
move_utils.move_log(yaml_file=config_file)
print(plot_utils.bcolors.OKBLUE + "[i] Ended frequency-calib successfully" + plot_utils.bcolors.ENDC)

# process extracted data
print(plot_utils.bcolors.OKBLUE + "[i] Processing frequency response data" + plot_utils.bcolors.ENDC)
process_frequency.process(yaml_file=config_file, plot_all=False)

## All done
print(plot_utils.bcolors.OKGREEN + u'[\u2713] Ended calibraiton successfully' + plot_utils.bcolors.ENDC)
