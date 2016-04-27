from homeassistant.const import TEMP_CELCIUS
from homeassistant.helpers.entity import Entity
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.components import enocean
from homeassistant.const import ATTR_ENTITY_ID

DEPENDENCIES = ["enocean"]

cnt = 1

def setup_platform(hass, config, add_devices, discovery_info=None):
    global cnt
    devid = config.get(ATTR_ENTITY_ID, None)
    add_devices([ExampleSensor(devid,cnt)])
    cnt = cnt + 1


class ExampleSensor(enocean.EnOceanDevice,BinarySensorDevice):

    def __init__(self,devid,cnt):
        enocean.EnOceanDevice.__init__(self)
        self.stype = "listener"
        self.temp_temperature = 0
        self.__devid = devid
        self.sensorid = devid
        self.which = -1
        self.onoff = -1
        self._cnt = cnt

    @property
    def name(self):
        return 'Trykknapp %d' % self._cnt

    def value_changed(self,value,value2):
        self.temp_temperature = value
        self.update_ha_state()
        print("ID: %s" % str(ATTR_ENTITY_ID))
        print("devID: %s" % str(self.__devid))
        if value2 == 0x70:
            self.which = 0
            self.onoff = 0
        elif value2 == 0x50:
            self.which = 0
            self.onoff = 1
        elif value2 == 0x30:
            self.which = 1
            self.onoff = 0
        elif value2 == 0x10:
            self.which = 1
            self.onoff = 1
        self.hass.bus.fire('button_pressed', { ATTR_ENTITY_ID: self.sensorid , 'pushed' : value, 'which' : self.which, 'onoff' : self.onoff})

    #@property
    #def state(self):
    #    return False # self.temp_temperature

    #@property
    #def unit_of_measurement(self):
    #    return TEMP_CELCIUS
