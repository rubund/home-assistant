from homeassistant.const import TEMP_CELCIUS
from homeassistant.helpers.entity import Entity
from homeassistant.components import enocean
from homeassistant.const import ATTR_ENTITY_ID

DEPENDENCIES = ["enocean"]

def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([ExampleSensor()])


class ExampleSensor(enocean.EnOceanDevice,Entity):

    def __init__(self):
        enocean.EnOceanDevice.__init__(self)
        self.stype = "listener"
        self.temp_temperature = 0

    @property
    def name(self):
        return 'Temperature'

    def value_changed(self,value):
        self.temp_temperature = value
        self.update_ha_state()
        self.hass.bus.fire('button_pressed', { ATTR_ENTITY_ID: "Mine" , 'state' : value})

    @property
    def state(self):
        return self.temp_temperature

    @property
    def unit_of_measurement(self):
        return TEMP_CELCIUS
