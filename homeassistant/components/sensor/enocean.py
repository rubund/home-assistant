from homeassistant.const import TEMP_CELCIUS
from homeassistant.helpers.entity import Entity
from homeassistant.components import enocean

DEPENDENCIES = ["enocean"]

def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([ExampleSensor()])


class ExampleSensor(enocean.EnOceanDevice,Entity):
    @property
    def name(self):
        return 'Temperature'

    @property
    def state(self):
        return 23

    @property
    def unit_of_measurement(self):
        return TEMP_CELCIUS
