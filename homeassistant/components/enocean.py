
import serial
import threading
import time

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


class EnOceanThread(threading.Thread):
    def __init__(self,ser,lock,kwargs=None):
        threading.Thread.__init__(self,kwargs=kwargs)
        self.__lock = lock
        self.__ser = ser
        self.__running = True
    def run(self):
        print("\n\nRunning thread\n\n")
        while self.__running:
            print("Running: %d" % (self.__running))
            with self.__lock:
                data = self.__ser.read()
            print("\nData recived: "+str(data)+"\n")
            time.sleep(1)
    def stop_this_one(self):
        self.__running = False

class EnOceanDongle:
    def __init__(self,hass,ser):
        self.__ser = serial.Serial(ser, 57600, timeout=0.1)
        self.__thread = EnOceanThread(self.__ser,ENOCEAN_LOCK)
        self.__thread.start()

    def __del__(self):
        self.__thread.stop_this_one()
        self.__thread.join()

    def send_command(self,command):
        with(ENOCEAN_LOCK):
            self.__ser.write(command)

class EnOceanDevice():
    def __init__(self):
        print("\n\nStarted device\n\n\n")

    def send_command(self,command):
        ENOCEAN_DONGLE.send_command(command)
