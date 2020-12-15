#!/usr/bin/python3

import os
import yaml

def move(yaml_file):
    # read parameters from yaml file
    with open(yaml_file, 'r') as stream:
        out_dict = yaml.safe_load(stream)
        tail=out_dict['log']['name']

    old_head, old_tail = os.path.split(yaml_file)
    new_head = f'{old_head}{tail[:17]}/{tail[-14:-10]}-{tail[-10:-8]}-{tail[-8:-6]}--{tail[-6:-4]}-{tail[-4:-2]}-{tail[-2:]}/'

    # update yaml
    out_dict['log']['location'] = new_head

    # move file to new location
    yaml_name=new_head+old_tail
    with open(yaml_name, 'w', encoding='utf8') as outfile:
        yaml.dump(out_dict, outfile, default_flow_style=False, allow_unicode=True)
    os.remove(yaml_file)
    return yaml_name