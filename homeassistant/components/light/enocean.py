import logging
import math

# Import the device class from the component that you want to support
from homeassistant.components.light import Light, ATTR_BRIGHTNESS
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
from homeassistant.components import enocean

# Home Assistant depends on 3rd party packages for API specific code.
#REQUIREMENTS = ['awesome_lights==1.2.3']

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ["enocean"]

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Initialize Awesome Light platform."""
    #import awesomelights

    # Validate passed in config
    host = config.get(CONF_HOST)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    #if host is None or username is None or password is None:
    #    _LOGGER.error('Invalid config. Expected %s, %s and %s',
    #                  CONF_HOST, CONF_USERNAME, CONF_PASSWORD)
    #    return False
    print("\n\n\nHUHUHUH345\n\n")

    ## Setup connection with devices/cloud
    #hub = awesomelights.Hub(host, username, password)

    ## Verify that passed in config works
    #if not hub.is_valid_login():
    #    _LOGGER.error('Could not connect to AwesomeLight hub')
    #    return False

    # Add devices
    add_devices([AwesomeLight(0)])

class AwesomeLight(enocean.EnOceanDevice,Light):
    """Represents an AwesomeLight in Home Assistant."""

    def __init__(self, light):
        """Initialize an AwesomeLight."""
        enocean.EnOceanDevice.__init__(self)
        self._light = None
        self._on_state = False
        self._on_state2 = False
        self._brightness = 50
        print("\n\n\nHER ER JEG\n")

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assitant.
        """
        #self._light.update()

    @property
    def brightness(self):
        """Brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self):
        """If light is on."""
        return self._on_state

    @property
    def name(self):
        return "Dimmelys"

    def turn_on(self, **kwargs):
        print("TUrning on")
        a = bytearray(b'\x55\x00\x0A\x00\x01\x80\xA5\x02\x64\x01\x09\xFF\xC6\xEA\x01\x00\x6E/')
        print("Wanted: "+str(a))
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness is not None:
            self._brightness = brightness
            print("Brightness: %d" % brightness)

        bval = math.floor(self._brightness / 256.0 * 100.0)
        #self.send_command(a)
        #self.send_command(data=[0x01,0x80,0xa5,0x02,0x64,0x09,0xff,0xc6,0xea,0x01],optional=[],packet_type=0x00)
        #self.send_command([0xa5,0x02,bval,0x01,0x09,0xff,0xc6,0xea,0x01,0x00],[],0x01)
        self.send_command([0xa5,0x02,bval,0x01,0x09,0xff,0xc6,0xea,0x03,0x00],[],0x01)
        #55 000A00 01 80 A5 02 64 01 09FFC6EA030044
        self._on_state = True

    def turn_off(self, **kwargs):
        print("TUrning off")
        a = bytearray(b'\x55\x00\x0A\x00\x01\x80\xA5\x02\x00\x01\x08\xFF\xC6\xEA\x01\x00\xB9/')
        #self.send_command(a)
        self.send_command([0xa5,0x02,0x00,0x01,0x09,0xff,0xc6,0xea,0x03,0x00],[],0x01)
        self._on_state = False

