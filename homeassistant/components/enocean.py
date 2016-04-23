
import serial
import threading

DOMAIN = "enocean"

ENOCEAN_LOCK = threading.Lock()

ENOCEAN_DONGLE = None

def setup(hass,config):
    global ENOCEAN_DONGLE
    ""
    hass.states.set('enocean.runstatus', 'It\' ok you know')
    print("First setting up")

    ENOCEAN_DONGLE = EnOceanDongle(hass,"/dev/ttyUSB0")
    return True

class EnOceanDongle:
    def __init__(self,hass,ser):
        self.__ser = serial.Serial(ser, 57600, timeout=0.1)

    def send_command(self,command):
        with(ENOCEAN_LOCK):
            self.__ser.write(command)

class EnOceanDevice():
    def __init__(self):
        print("\n\nStarted device\n\n\n")

    def send_command(self,command):
        ENOCEAN_DONGLE.send_command(command)
