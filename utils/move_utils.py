#!/usr/bin/python3

import os
import sys
import glob
import yaml

from utils import plot_utils
from datetime import datetime

def move_yaml(yaml_file):
    # read parameters from yaml file
    with open(yaml_file) as f:
        try:
            out_dict = yaml.safe_load(f)
        except Exception:
            raise Exception('error in yaml parsing')

    # make log dir
    t=datetime.now()
    if 'log' in out_dict:
        if 'name' in out_dict['log']:
            tail = out_dict['log']['name']
        else:
            _, tail = os.path.split(yaml_file)
            if len(tail)>len('_results.yaml') and tail[len('_results.yaml'):]=='_results.yaml':
                tail = tail[len('_results.yaml'):]
            else:
                if 'A_serial' in out_dict['log']:
                    tail=out_dict['log']['A_serial']
                else:
                    tail='A0000'
                if 'E_serial'in out_dict['log']:
                    tail=tail+f"-{out_dict['log']['E_serial']}"
                else:
                    tail=tail+'-E0000'
                tail=tail+f'-H0000_{t.year}-{t.month}-{t.day}--{t.hour}-{t.minute}-{t.second}'
            out_dict['log']['name']=tail

        if 'location' in out_dict['log']:
            head = out_dict['log']['location']
        else:
            head = f'/logs/{tail[:17]}/{tail[18:]}/logs/'
            out_dict['log']['location'] = head

        if os.path.isdir(head) is False:
            try:
                os.makedirs(head)
            except OSError:
                print("Creation of the directory %s failed" % head)
    else:
        head='/logs/'
        tail=f'A0000-E0000-H0000_{t.year}-{t.month}-{t.day}--{t.hour}-{t.minute}-{t.second}'

    # move file to new location
    yaml_name=head[:-5]+tail+'_results.yaml'
    with open(yaml_name, 'w', encoding='utf8') as outfile:
        yaml.dump(out_dict, outfile, default_flow_style=False, allow_unicode=True)
    os.remove(yaml_file)
    return yaml_name

def move_log(yaml_file, new_name='NULL'):
    '''Moves lastest CentAcESC_*_log.txt log file to new_name location, default is taken'''
    list_of_files = glob.glob('/tmp/CentAcESC_*_log.txt')
    tmp_file = max(list_of_files, key=os.path.getctime)
    if new_name == 'NULL':
        # read parameters from yaml file
        with open(yaml_file, 'r') as stream:
            out_dict = yaml.safe_load(stream)

        if not(('location' in out_dict['log']) and ('name' in out_dict['log'])):
            yaml_file = move_yaml(yaml_file)
            with open(yaml_file, 'r') as stream:
                out_dict = yaml.safe_load(stream)

        new_name = out_dict['log']['location']  \
                 + out_dict['log']['name']      \
                 + '_inertia-calib.log'

    cmd = 'cp ' + tmp_file + ' ' + new_name
    if os.system(cmd):
        sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error while copying logs' + plot_utils.bcolors.ENDC)
    print('log_file: ' + new_name)
