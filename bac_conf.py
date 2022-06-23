import BAC0
import random
import json
import argparse

poll_period = 10000

class ConfigGenerator :
    def __init__(self, 
            identifier=1476, 
            ip_addr='0.0.0.0', 
            port=47808,
            max_apdu=1476, 
            segmentation = 'segmentedBoth', 
            vendor =15) :
        self._addr = f'{ip_addr}:{port}'
        self._apdu = max_apdu
        self._vid = vendor
        self._id = identifier
        self._seg= segmentation

    def get_config(self, devices) :
        cfg = {}
        cfg['general'] = {
            'objectName' : 'TB_gateway',
            'address' : self._addr,
            'objectIdentifier' : self._id,
            "maxApduLengthAccepted": self._apdu,
            "segmentationSupported": self._seg,
            "vendorIdentifier": self._vid
        }
        cfg['devices'] = devices
        return cfg

class DeviceConfig :
    def __init__(self, ip_address, port=47808, poll_period=10000) :
        self._ip = ip_address
        self._port = port
        self._type = 'default'
        self._name = 'BACnet Device ${objectName}'

    def get_config(self, attrs, ts, updates, rpc= None)  : 
        cfg = {}
        cfg['deviceName'] = self._name
        cfg['deviceType'] = self._type
        cfg['address'] = f"{self._ip}:{self._port}"
        cfg['pollPeriod'] = poll_period
        cfg['attributes'] = attrs
        cfg['attributeUpdates'] = updates
        cfg['timeseries'] = ts
        if rpc != None:
            cfg['serverSideRpc'] = rpc

        return cfg

class ObjectConfig : 
    def __init__(self, name, object_type, object_id) : 
        self._name = name
        self._type = object_type
        self._id = object_id
        self._object_id = f'{self._type}:{self._id}'
        self._dtype = self.find_type()
        self._controllable = True if 'Output' in object_type else False

    def find_type(self) : 
        if 'analog' in self._type : 
            return 'double'
        elif 'binary' in self._type : 
            return 'bool'
        return 'string'

    def attributes(self) : 
        return {
            'key' : self._name,
            'type' : 'string',
            'objectId' : self._object_id,
            'propertyId' : 'description'
        }

    def timeseries(self) : 
        return {
            'key' : self._name,
            'type' : self._dtype,
            'objectId' : self._object_id,
            'propertyId' : 'presentValue'
        }
    
    def attribute_updates(self) : 
        return {
            'key' : self._name,
            'requestType' : 'writeProperty',
            'objectId' : self._object_id,
            'propertyId' : 'presentValue'
        }

    def rpc_setter(self) : 
        return {
            'method' : 'set_state',
            'requestType' : 'writeProperty',
            'requestTimeout' : 10000,
            'objectId' : self._object_id,
            'propertyId' : 'presentValue'
        }

    def rpc_getter(self) :
        return {
            'method' : 'get_state',
            'requestType' : 'readProperty',
            'requestTimeout' : 10000,
            'objectId' : self._object_id,
            'propertyId' : 'presentValue'
        }

    def get_config(self) : 
        ret = {}
        ret['attributes'] = self.attributes()
        ret['timeseries'] = self.timeseries()
        ret['attributeUpdates'] = self.attribute_updates()
        if self._controllable :
            ret['serverSideRpc'] = [
                self.rpc_setter(),
                self.rpc_getter()
            ]

        return ret
        

class BACnetManager : 
    def __init__(self, ip_addr, subnet_mask=24) :
        self.conn = BAC0.connect(f'{ip_addr}/{subnet_mask}')
        self.conn.whois()
    
    def scan(self) : 
        devices = self.conn.devices
        return devices

    def destroy(self) : 
        self.conn.disconnect()

    def request(self, ip_addr, request_type, instance_id, command, **kwargs) : 
        return self.conn.readMultiple(f'{ip_addr} {request_type} {instance_id} {command}', **kwargs)

    def get_object_detail(self,obj, ip_addr, **kwargs) :
        return self.request(ip_addr, obj[0], obj[1], 'objectName')

    def get_objects_in_device(self, device, **kwargs) : 
        ip_addr = device[2]
        device_id = device[3]
        return self.request(ip_addr, 'device', device_id, 'objectList', **kwargs)

    def get_object_property(self, instance_id, prop_id) : 
        prop = read_property(())
        return None

    def create_table(self, cfg_gen, polling_rate = 10000) : 
        devices = self.scan()
        print('devices : ' , devices)
        blacklist =  set(['program', 'trendLog', 'calender', 'schedule', 'file', 'notificationClass'])

        device_configs = []
        for device in devices : 
            print('## Objects in device : ', device)
            
            [attributes,timeseries, attribute_updates, rpc] = [[] for i in range(4)]
            objs = self.get_objects_in_device(device)
            for i in range(1, len(objs[0])) :
                obj_type = objs[0][i][0]
                if obj_type in blacklist : 
                    continue;
                detail = self.get_object_detail(
                            objs[0][i], 
                            device[2]
                )
                obj = detail
                obj_name = obj[0]
                obj_id = objs[0][i][1]
                config = ObjectConfig(obj_name, obj_type, obj_id).get_config()
                attributes.append(config['attributes'])
                timeseries.append(config['timeseries'])
                attribute_updates.append(config['attributeUpdates'])
                if 'serverSideRpc' in config.keys() : 
                    for r in config['serverSideRpc'] : 
                        rpc.append(r)

                print('#### objects detail',detail)
            device_config = DeviceConfig(device[2]).get_config(
                    attributes, 
                    timeseries, 
                    attribute_updates, 
                    rpc = rpc)

            device_configs.append(device_config)
        
        global_config = cfg_gen.get_config(device_configs)
        
        with open('bacnet.json', 'w') as f :
            f.write(json.dumps(global_config, indent=4, ensure_ascii=True))

if __name__ == '__main__' : 
    ip_addr = ''
    subnet_mask = 24
    manager = BACnetManager(ip_addr, subnet_mask = subnet_mask)
    config_generator = ConfigGenerator()
    manager.create_table(config_generator)
    manager.destroy()



