from homeassistant.const import TEMP_CELCIUS
from homeassistant.helpers.entity import Entity
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.const import ATTR_ENTITY_ID

import socket
import threading
import json

#DEPENDENCIES = ["enocean"]
#
#cnt = 1

def setup_platform(hass, config, add_devices, discovery_info=None):
    #devid = config.get(ATTR_ENTITY_ID, None)
    add_devices([ExampleSensor()])


class ListenThread(threading.Thread):
    def __init__(self,dev):
            threading.Thread.__init__(self)
            self.dev = dev

    def run(self):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("192.168.1.78",8300)) 
            s.settimeout(1)
            while True:
                try:
                    rdata = s.recv()
                    js = json.load(rdata.decode('utf-8'))
                    print(js)
                    self.dev.alert()
                except socket.timeout:
                    ""
                except socket.error:
                    s.close()
                    break
                
        s.close()

class ExampleSensor(BinarySensorDevice):

    def __init__(self):
        print("\n\nSTARTED MYDOORBELL\n\n")
        th = ListenThread(self)
        th.start()
        #enocean.EnOceanDevice.__init__(self)

    @property
    def name(self):
        return 'Ringeklokke'

    #def value_changed(self,value,value2):
        #self.temp_temperature = value
        #self.update_ha_state()
    def alert(self):
        print("Door bell fired")
        self.hass.bus.fire('button_pressed', { ATTR_ENTITY_ID: "ringeklokke" })

    #@property
    #def state(self):
    #    return False # self.temp_temperature

    #@property
    #def unit_of_measurement(self):
    #    return TEMP_CELCIUS
