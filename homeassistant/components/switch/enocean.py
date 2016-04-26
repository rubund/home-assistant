import logging

# Import the device class from the component that you want to support
#from homeassistant.components.light import Light
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
from homeassistant.components import enocean
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.const import ATTR_ENTITY_ID

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
    devid = config.get(ATTR_ENTITY_ID, None)

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
    #add_devices(AwesomeLight(light) for light in [0,1])
    add_devices([AwesomeLight(devid)])

class AwesomeLight(enocean.EnOceanDevice,ToggleEntity):
    """Represents an AwesomeLight in Home Assistant."""

    def __init__(self, devid):
        """Initialize an AwesomeLight."""
        enocean.EnOceanDevice.__init__(self)
        self._devid = devid
        self._light = None
        self._on_state = False
        self._on_state2 = False
        print("\n\n\nHER ER JEG\n")

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assitant.
        """
        #self._light.update()

    #@property
    #def brightness(self):
    #    """Brightness of the light.

    #    This method is optional. Removing it indicates to Home Assistant
    #    that brightness is not supported for this light.
    #    """
    #    return 50

    @property
    def is_on(self):
        """If light is on."""
        return self._on_state

    @property
    def name(self):
        return "Enocean actuator"


    def turn_on(self, **kwargs):
        print("TUrning on")
        #a = bytearray(b'\x55\x00\x0A\x00\x01\x80\xA5\x02\x64\x01\x09\xFF\xC6\xEA\x01\x00\x6E/')
        # nattbord
        #self.send_command(data=[0xD2,0x01,0x00,0x64,0x00,0x00,0x00,0x00,0x00],optional=[0x03,0x01,0x91,0x3d,0xe7,0xff,0x00],packet_type=0x01)
        # ovn_stue
        #self.send_command(data=[0xD2,0x01,0x00,0x64,0x00,0x00,0x00,0x00,0x00],optional=[0x03,0x01,0x94,0x9e,0xca,0xff,0x00],packet_type=0x01)
        # tvbenk
        optional = [0x03,]
        optional.extend(self._devid)
        optional.extend([0xff, 0x00])
        self.send_command(data=[0xD2,0x01,0x00,0x64,0x00,0x00,0x00,0x00,0x00],optional=optional,packet_type=0x01)
        self._on_state = True

    def turn_off(self, **kwargs):
        print("TUrning off")
        #a = bytearray(b'\x55\x00\x0A\x00\x01\x80\xA5\x02\x00\x01\x08\xFF\xC6\xEA\x01\x00\xB9/')
        # nattbord
        #self.send_command(data=[0xD2,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00],optional=[0x03,0x01,0x91,0x3d,0xe7,0xff,0x00],packet_type=0x01)
        # ovn_stue
        #self.send_command(data=[0xD2,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00],optional=[0x03,0x01,0x94,0x9e,0xca,0xff,0x00],packet_type=0x01)
        # tvbenk
        optional = [0x03,]
        optional.extend(self._devid)
        optional.extend([0xff, 0x00])
        self.send_command(data=[0xD2,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00],optional=optional,packet_type=0x01)
        #self.send_command(data=[0xD2,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00],optional=[0x03,0x01,0x90,0x84,0x3c,0xff,0x00],packet_type=0x01)
        self._on_state = False

