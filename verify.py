import json
import pandas as pd

with open('converted.json' ,'r') as f :
    cfg = json.load(f)

devices = cfg['devices']
key_mapper = {
    "binaryInput" : "BI",
    "binaryOutput" : "BO",
    "analogInput" : "AI",
    "analogOutput" : "AO"
}

data= [] 

def pad_num(value : int,length=4) : 
    value = str(value)
    pad_size = length - len(value)
    
    return '0'*pad_size+value
        

for device in devices :
    ip_addr = device['address'].split(':')[0]
    endpoints = device['timeseries']
    
    tmp = []
    for ep in endpoints : 
        sp = ep['objectId'].split(':') 
        type = sp[0]
        id = sp[1]

        if type in key_mapper : 
            type = key_mapper[type]

        tmp.append({
            "ip_addr" : ip_addr,
            "key" : type+":"+pad_num(id),
            "description" : ep['key']
        })
    print("tmp size : ", len(tmp))
    data.extend(tmp)

df = pd.DataFrame(data)
print(df)
df.to_csv('verify.csv', encoding='cp949')
    
