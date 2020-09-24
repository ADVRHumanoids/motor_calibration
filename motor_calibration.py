#!/usr/bin/python3

import os
import sys
import glob
import yaml
import numpy as np
from matplotlib import pyplot as plt

#import costum files
import phase_postprocess
import plot_utils

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#parameters:
cmd1 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/phase-calib/phase-calib')
cmd2 = os.path.expanduser('~/ecat_dev/ec_master_app/build/examples/motor-calib/set-phase/set-phase')
config_file = os.path.expanduser('~/ecat_dev/ec_master_app/examples/motor-calib/config.yaml')

#plot logo
plot_utils.print_alberobotics()

# test phase angles
print(bcolors.OKBLUE + "[i] Starting phase-calib" + bcolors.ENDC)
if os.system(cmd1 + ' ' + config_file):
    sys.exit(bcolors.FAIL + u'[\u2717] Error during phase-calib' + bcolors.ENDC)
print(bcolors.OKBLUE + "[i] Ended phase-calib successfully" + bcolors.ENDC)

# process extracted data
print(bcolors.OKBLUE + "[i] Starting postprocessing" + bcolors.ENDC)
config_file = phase_postprocess.postprocess(yaml_file=config_file, plot_all=False)

# Upload to motor the best phase angle
print(bcolors.OKBLUE + "[i] Sending phase angle to motor using set-phase" +  bcolors.ENDC)
if os.system(cmd2 + ' ' + config_file):
    sys.exit(bcolors.FAIL + u'[\u2717] Error during set-phase' +
             bcolors.ENDC)
print(bcolors.OKBLUE + "[i] Ended set-phase successfully" + bcolors.ENDC)

print(bcolors.OKBLUE + "[i] Ending program" + bcolors.ENDC)