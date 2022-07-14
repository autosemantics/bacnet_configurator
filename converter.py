import json
import argparse
import pandas as pd
from collections.abc import Iterable

parser = argparse.ArgumentParser(description = 'Convert Thingsboard IOT Gateway BACnet config file based on mapping file')
parser.add_argument('--mapping_table', type=str, help='mapping table path')
parser.add_argument('--config', type=str, help = 'Thingsboard IOT Gateway BACnet config file path')

args = parser.parse_args()
with open(args.config, 'r') as f :
    bacnet_cfg = json.load(f)

devices = bacnet_cfg['devices']
mapping_table_path = args.mapping_table

try : 
    mapping_table = pd.read_csv(mapping_table_path, encoding='cp949')
except : 
    mapping_table = pd.read_csv(mapping_table_path)

print(mapping_table)

def table_to_dict(df) : 
    ret = dict()

    ips = list(set(df['ip']))

    for ip in ips: 
        ret[ip] = dict()
        subset = df[df['ip']==ip]
        for row in subset.itertuples() : 
            ret[ip][row.key] = row.description
    return ret

mapping_table = table_to_dict(mapping_table)

#with open('verify.json', 'w', encoding='UTF-8-sig') as f : 
#    f.write(json.dumps(mapping_table, indent=4, ensure_ascii=False))
#exit(1)

print(json.dumps(mapping_table, indent = 2))

def convert(cfg, mt) : 
    targets = set(['attributes', 'attributeUpdates', 'timeseries'])
    #drop_fields = ['attributes', 'attributesUpdates']
    devices = cfg['devices']
    mapping_keys =set(mt.keys())
    for i in range(len(devices)) :
        device = devices[i]
        ip_addr = device['address'].split(':')[0]
        
        for field in targets:
            #print('field : ' , field)
            #print(f'devices[{ip_addr}][{field}] : ' , devices[i][field])
            #print(f'devices[{i}][{field}] : ', devices[i][field])
            for j in range(len(devices[i][field])) :
                data_point_id = devices[i][field][j]['key']
                if data_point_id in mt[ip_addr].keys() : 
                    value = mt[ip_addr][data_point_id]
                    devices[i][field][j]['key'] = value
        if 'attributes' in devices[i].keys() : 
            del devices[i]['attributes']
        if 'attributeUpdates' in devices[i].keys():
            del devices[i]['attributeUpdates']
        #if 'serverSideRpc' in devices[i].keys() : 
        #    del devices[i]['serverSideRpc']
    #cfg['devices'] = [devices[0], devices[1], devices[2], devices[3], devices[4], devices[5], devices[6], devices[7]]
    cfg['devices'] = devices
    return cfg

bacnet_cfg = convert(bacnet_cfg, mapping_table)

with open('converted.json', 'w') as f :
    f.write(json.dumps(bacnet_cfg, indent = 4))
