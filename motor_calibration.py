#!/usr/bin/python3

import os
import sys
import glob
import yaml
import numpy as np
from matplotlib import pyplot as plt

#import costum files
import process_phase
import plot_utils

## Parameters:
# path to phase-calib script to test phase angle and log data
cmd1 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/phase-calib/phase-calib')
# path to set-phase script to set the optimized value to the motor
cmd2 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/set-phase/set-phase')
# path to the configuration file for the motor and the test variables
config_file = os.path.expanduser('~/ecat_dev/ec_master_app/examples/motor-calib/config.yaml')

#print logo
plot_utils.print_alberobotics()

# test phase angles
print(plot_utils.bcolors.OKBLUE + "[i] Starting phase-calib" + plot_utils.bcolors.ENDC)
#if False:
if os.system(cmd1 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during phase-calib' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended phase-calib successfully" + plot_utils.bcolors.ENDC)

# process extracted data
print(plot_utils.bcolors.OKBLUE + "[i] Starting postprocessing" + plot_utils.bcolors.ENDC)
config_file = process_phase.postprocess(yaml_file=config_file, plot_all=False)

# Upload to motor the best phase angle
print(plot_utils.bcolors.OKBLUE + "[i] Sending phase angle to motor using set-phase" +  plot_utils.bcolors.ENDC)
#if False:
if os.system(cmd2 + ' ' + config_file):
    sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error during set-phase' + plot_utils.bcolors.ENDC)
print(plot_utils.bcolors.OKBLUE + "[i] Ended set-phase successfully" + plot_utils.bcolors.ENDC)

print(plot_utils.bcolors.OKGREEN + u'[\u2713] Ending program successfully' + plot_utils.bcolors.ENDC)
