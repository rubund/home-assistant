"""
Support for the NetAtmo Weather Service.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.netatmo/
"""
import logging
from datetime import timedelta

from homeassistant.components.sensor import DOMAIN
from homeassistant.const import (
    CONF_API_KEY, CONF_PASSWORD, CONF_USERNAME, TEMP_CELSIUS, CONF_STATION)
from homeassistant.helpers import validate_config
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

REQUIREMENTS = [
    'https://github.com/HydrelioxGitHub/netatmo-api-python/archive/'
    '43ff238a0122b0939a0dc4e8836b6782913fb6e2.zip'
    '#lnetatmo==0.4.0']

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    'temperature': ['Temperature', TEMP_CELSIUS, 'mdi:thermometer'],
    'co2':         ['CO2', 'ppm', 'mdi:cloud'],
    'pressure':    ['Pressure', 'mbar', 'mdi:gauge'],
    'noise':       ['Noise', 'dB', 'mdi:volume-high'],
    'humidity':    ['Humidity', '%', 'mdi:water-percent'],
    'rain':        ['Rain', 'mm', 'mdi:weather-rainy'],
    'sum_rain_1':  ['sum_rain_1', 'mm', 'mdi:weather-rainy'],
    'sum_rain_24': ['sum_rain_24', 'mm', 'mdi:weather-rainy'],
}

CONF_SECRET_KEY = 'secret_key'
ATTR_MODULE = 'modules'

# Return cached results if last scan was less then this time ago
# NetAtmo Data is uploaded to server every 10mn
# so this time should not be under
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=600)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the NetAtmo sensor."""
    if not validate_config({DOMAIN: config},
                           {DOMAIN: [CONF_API_KEY,
                                     CONF_USERNAME,
                                     CONF_PASSWORD,
                                     CONF_SECRET_KEY]},
                           _LOGGER):
        return None

    import lnetatmo

    authorization = lnetatmo.ClientAuth(config.get(CONF_API_KEY, None),
                                        config.get(CONF_SECRET_KEY, None),
                                        config.get(CONF_USERNAME, None),
                                        config.get(CONF_PASSWORD, None))

    if not authorization:
        _LOGGER.error(
            "Connection error "
            "Please check your settings for NatAtmo API.")
        return False

    data = NetAtmoData(authorization,config.get(CONF_STATION,None))

    dev = []
    try:
        # Iterate each module
        for module_name, monitored_conditions in config[ATTR_MODULE].items():
            module_not_found = False
            # Test if module exist """
            if module_name not in data.get_module_names():
                _LOGGER.error('Module name: "%s" not found', module_name)
                module_not_found = True
            # Only create sensor for monitored """
            for variable in monitored_conditions:
                sensor_not_found = False
                if variable not in SENSOR_TYPES:
                    _LOGGER.error('Sensor type: "%s" does not exist', variable)
                    sensor_not_found = True

                dev.append(
                    NetAtmoSensor(data, module_name, variable,module_not_found, sensor_not_found))
    except KeyError:
        pass

    add_devices(dev)


# pylint: disable=too-few-public-methods
class NetAtmoSensor(Entity):
    """Implementation of a NetAtmo sensor."""

    def __init__(self, netatmo_data, module_name, sensor_type, module_not_found, sensor_not_found):
        """Initialize the sensor."""
        self._name = "NetAtmo {} {}".format(module_name,
                                            SENSOR_TYPES[sensor_type][0])
        self.netatmo_data = netatmo_data
        self.module_name = module_name
        self.type = sensor_type
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self.module_not_found = module_not_found
        self.sensor_not_found = sensor_not_found
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return SENSOR_TYPES[self.type][2]

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    # pylint: disable=too-many-branches
    def update(self):
        """Get the latest data from NetAtmo API and updates the states."""
        if self.sensor_not_found or self.module_not_found:
            self.netatmo_data.update(no_throttle=True)
        else:
            self.netatmo_data.update()
        if not self.module_name in self.netatmo_data.data:
            print("Did not find module %s" % self.module_name)
            return
        self.module_not_found = False
        data = self.netatmo_data.data[self.module_name]


        if self.type == 'temperature':
            key = 'Temperature'
        elif self.type == 'humidity':
            key = 'Humidity'
        elif self.type == 'rain':
            key = 'Rain'
        elif self.type == 'sum_rain_1':
            key = 'sum_rain_1'
        elif self.type == 'sum_rain_24':
            key = 'sum_rain_24'
        elif self.type == 'noise':
            key = 'Noise'
        elif self.type == 'co2':
            key = 'CO2'
        elif self.type == 'pressure':
            key = 'Pressure'
        else:
            key = ''

        if not key in data:
            print("Did not find sensor %s" % key)
            return
        self.sensor_not_found = False

        if key == '':
            self._state = 0
        elif self.type == 'temperature':
            self._state = round(data[key], 1)
        elif self.type == 'pressure':
            self._state = round(data[key], 1)
        else:
            self._state = data[key]


class NetAtmoData(object):
    """Get the latest data from NetAtmo."""

    def __init__(self, auth, station):
        """Initialize the data object."""
        self.auth = auth
        self.data = None
        self.station = station

    def get_module_names(self):
        """Return all module available on the API as a list."""
        self.update()
        return self.data.keys()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Call the NetAtmo API to update the data."""
        import lnetatmo
        dev_list = lnetatmo.DeviceList(self.auth)
        
        self.data = dev_list.lastData(station=self.station,exclude=3600)
