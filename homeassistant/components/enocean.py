
import serial
import threading
import time
from homeassistant.components import crc8

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
    def __init__(self,ser,lock,callback,kwargs=None):
        threading.Thread.__init__(self,kwargs=kwargs)
        self.__lock = lock
        self.__ser = ser
        self.__running = True
        self.__count = 0
        self.__callback = callback
    def run(self):
        print("\n\nRunning thread\n\n")
        while self.__running:
            print("Running: %d" % (self.__running))
            with self.__lock:
                data = self.__ser.read()
            print("\nData recived: "+str(data)+"\n")
            self.__callback(self.__count)
            self.__count = self.__count + 1
            time.sleep(1)
    def stop_this_one(self):
        self.__running = False

class EnOceanDongle:
    def __init__(self,hass,ser):
        self.__ser = serial.Serial(ser, 57600, timeout=0.1)
        self.__thread = EnOceanThread(self.__ser,ENOCEAN_LOCK,self.callback)
        self.__thread.start()
        self.__devices = []

    def __del__(self):
        self.__thread.stop_this_one()
        self.__thread.join()

    def register_device(self,dev):
        self.__devices.append(dev)

    def send_command(self,command):
        with(ENOCEAN_LOCK):
            self.__ser.write(command)

    def callback(self,temp):
        print("\n\nCalling back %d\n\n",temp)
        for d in self.__devices:
            if d.stype == "listener":
                print("Found one listener")
                d.value_changed(temp)

class EnOceanDevice():
    def __init__(self):
        print("\n\nStarted device\n\n\n")
        ENOCEAN_DONGLE.register_device(self)
        self.stype = ""

    def send_command(self,data,optional,packet_type):
        command = self.build_packet(data,optional,packet_type)
        command = bytearray(command)
        print("Got: "+str(command))
        ENOCEAN_DONGLE.send_command(command)

    def build_packet(self,data,optional,packet_type):
        data_length = len(data)
        ords = [0x55, (data_length >> 8) & 0xFF, data_length & 0xFF, len(optional), int(packet_type)]
        ords.append(crc8.calc(ords[1:5]))
        ords.extend(data)
        ords.extend(optional)
        ords.append(crc8.calc(ords[6:]))
        return ords
        
