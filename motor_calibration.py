#!/usr/bin/python3

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
import process_phase
import process_ripple
import process_friction
import plot_utils

## Parameters:
# path to test-pdo
cmd0 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/test-pdo/test-pdo')
# path to phase-calib to test phase angle and log data
cmd1 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/phase-calib/phase-calib')
# path to set-phase to set the optimized value to the motor
cmd2 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/set-phase/set-phase')
# path to ripple-calib to test test ripple and positionl offset
cmd3 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/ripple-calib/ripple-calib')
# path to friction-calib for inertia and friction identification
cmd4 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/friction-calib/friction-calib')
# path to the configuration file for the motor and the test variables
config_file = os.path.expanduser('~/ecat_dev/ec_master_app/examples/motor-calib/config.yaml')

#print logo
plot_utils.print_alberobotics()

## test pdo
print(plot_utils.bcolors.OKBLUE + "[i] Starting test-pdo" + plot_utils.bcolors.ENDC)
if os.system(cmd0 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during test-pdo' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended test-pdo successfully" + plot_utils.bcolors.ENDC)

## test phase angles
print(plot_utils.bcolors.OKBLUE + "[i] Starting phase-calib" + plot_utils.bcolors.ENDC)
if os.system(cmd1 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during phase-calib' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended phase-calib successfully" + plot_utils.bcolors.ENDC)

# process extracted data
print(plot_utils.bcolors.OKBLUE + "[i] Processing phase data" + plot_utils.bcolors.ENDC)
config_file2 = process_phase.process(yaml_file=config_file, plot_all=False)

## Upload to motor the best phase angle
print(plot_utils.bcolors.OKBLUE + "[i] Sending phase angle to motor using set-phase" +  plot_utils.bcolors.ENDC)
if os.system(cmd2 + ' ' + config_file2):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during set-phase' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended set-phase successfully" + plot_utils.bcolors.ENDC)

## test ripple and position dependant torque
print(plot_utils.bcolors.OKBLUE + "[i] Starting ripple-calib" + plot_utils.bcolors.ENDC)
if os.system(cmd3 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during ripple-calib' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended ripple-calib successfully" + plot_utils.bcolors.ENDC)

# process extracted data
print(plot_utils.bcolors.OKBLUE + "[i] Processing ripple data" + plot_utils.bcolors.ENDC)
process_ripple.process(yaml_file=config_file, plot_all=False)

## Inertia and friction identification
print(plot_utils.bcolors.OKBLUE + "[i] Starting friction-calib" + plot_utils.bcolors.ENDC)
if os.system(cmd4 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during friction-calib' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended friction-calib successfully" + plot_utils.bcolors.ENDC)

# process extracted data
print(plot_utils.bcolors.OKBLUE + "[i] Processing friction data" + plot_utils.bcolors.ENDC)
process_friction.move_log()
process_friction.process(yaml_file=config_file, plot_all=False)

print(plot_utils.bcolors.OKGREEN + u'[\u2713] Ending program successfully' + plot_utils.bcolors.ENDC)
