from homeassistant.const import TEMP_CELCIUS
from homeassistant.helpers.entity import Entity
from homeassistant.components import enocean
from homeassistant.const import ATTR_ENTITY_ID

DEPENDENCIES = ["enocean"]

def setup_platform(hass, config, add_devices, discovery_info=None):
    devid = config.get(ATTR_ENTITY_ID, None)
    add_devices([ExampleSensor(devid)])


class ExampleSensor(enocean.EnOceanDevice,Entity):

    def __init__(self,devid):
        enocean.EnOceanDevice.__init__(self)
        self.stype = "listener"
        self.temp_temperature = 0
        self.__devid = devid
        self.sensorid = devid

    @property
    def name(self):
        return 'Temperature'

    def value_changed(self,value):
        self.temp_temperature = value
        self.update_ha_state()
        print("ID: %s" % str(ATTR_ENTITY_ID))
        print("devID: %s" % str(self.__devid))
        self.hass.bus.fire('button_pressed', { ATTR_ENTITY_ID: self.sensorid , 'state' : value})

    @property
    def state(self):
        return self.temp_temperature

    @property
    def unit_of_measurement(self):
        return TEMP_CELCIUS
