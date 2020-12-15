#!/usr/bin/python3

import os
import glob
import yaml

def move_yaml(yaml_file):
    # read parameters from yaml file
    with open(yaml_file, 'r') as stream:
        out_dict = yaml.safe_load(stream)
        tail=out_dict['log']['name']

    #define new path and create folders
    old_head, old_tail = os.path.split(yaml_file)
    new_head = f'{old_head}/{tail[:17]}/{tail[-14:-10]}-{tail[-10:-8]}-{tail[-8:-6]}--{tail[-6:-4]}-{tail[-4:-2]}-{tail[-2:]}/'
    try:
        os.makedirs(new_head)
    except OSError:
        print("Creation of the directory %s failed" % new_head)
    else:
        print("Successfully created the directory %s" % new_head)

    # update yaml
    out_dict['log']['location'] = new_head

    # move file to new location
    yaml_name=new_head+old_tail
    with open(yaml_name, 'w', encoding='utf8') as outfile:
        yaml.dump(out_dict, outfile, default_flow_style=False, allow_unicode=True)
    os.remove(yaml_file)
    return yaml_name

def move_log(yaml_file, new_name='NULL'):
    '''Moves lastest CentAcESC_*_log.txt log file to new_name location, default is taken'''
    list_of_files = glob.glob('/tmp/CentAcESC_*_log.txt')
    tmp_file = max(list_of_files, key=os.path.getctime)
    if new_name == 'NULL':
        new_name = yaml_file[:-len('-results.yaml')] + '-inertia_calib.log'
    cmd = 'cp ' + tmp_file + ' ' + new_name
    if os.system(cmd):
        sys.exit(plot_utils.bcolors.FAIL + u'[\u2717] Error while copying logs' + plot_utils.bcolors.ENDC)
    print('log_file: ' + new_name)
