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


class ExampleSensor(enocean.EnOceanDevice,Entity):

    def __init__(self,devid,cnt):
        enocean.EnOceanDevice.__init__(self)
        self.stype = "powersensor"
        self.power = 0
        self.__devid = devid
        self.sensorid = devid
        self.which = -1
        self.onoff = -1
        self._cnt = cnt

    @property
    def name(self):
        return 'Power sensor %d' % self._cnt

    def value_changed(self,value):
        self.power = value
        self.update_ha_state()

    @property
    def state(self):
        return self.power

    @property
    def unit_of_measurement(self):
        return "W"
