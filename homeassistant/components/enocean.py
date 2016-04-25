
import serial
import threading
import time
from homeassistant.util import crc8

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
        self.packet = []
        self.pcounter = 0
        self.datalength = 0
        self.optionallength = 0
        self.packettype = 0
        self.receiving = False
    def run(self):
        print("\n\nRunning thread\n\n")
        while self.__running:
            with self.__lock:
                data = bytearray([1])
                while len(data) != 0:
                    data = self.__ser.read()#,timeout=None)
                    #print("data: "+str(data))
                    #print("done")
                    #self.rbuffer.extend(data)
                    for b in data:
                        if self.optionallength != 0 and self.pcounter == (self.datalength + self.optionallength + 6):
                            self.packet.append(b)
                            for p in self.packet:
                                print("%02x, " % p, end="")
                            print("")
                            self.receiving = False
                            self.__callback(self.packet)
                        elif b == 0x55 and (not self.receiving or self.optionallength == 0):
                            print("\nNew packet: ")
                            self.packet = [0x55]
                            self.pcounter = 0
                            self.datalength = 0
                            self.optionallength = 0
                            self.receiving = True
                        else:
                            self.packet.append(b)
                        if self.pcounter == 2:
                            self.datalength = b
                        if self.pcounter == 3:
                            self.optionallength = b
                        if self.pcounter == 4:
                            self.packettype = b
                        # 5: CRC;  dataLength + optionallength +1 CRC
                        self.pcounter = self.pcounter + 1

            self.__count = self.__count + 1
            time.sleep(0.1)
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
        print("\n\nCalling back %s\n\n",str(temp))
        for d in self.__devices:
            if d.stype == "listener":
                print("Found one listener")
                if temp[7] == 0x50:
                    d.value_changed(1)
                elif temp[7] == 0x00:
                    d.value_changed(0)

class EnOceanDevice():
    def __init__(self):
        print("\n\nStarted device\n\n\n")
        ENOCEAN_DONGLE.register_device(self)
        self.stype = ""

    def send_command(self,data,optional,packet_type):
        command = self.build_packet([0xf6, 0x30, 0xfe, 0xfb, 0x71, 0xe1, 0x30 ],[0x01, 0xff, 0xff,  0xff, 0xff, 0x47, 0x00 ],0x01)  # <-- Button pushed (left-top-push)
        command = self.build_packet([0xf6, 0x00, 0xfe, 0xfb, 0x71, 0xe1, 0x20 ],[0x01, 0xff, 0xff,  0xff, 0xff, 0x44, 0x00 ],0x01)  # <-- Button pushed (left-top-release)
        command = self.build_packet([0xf6, 0x10, 0xfe, 0xfb, 0x71, 0xe1, 0x30 ],[0x01, 0xff, 0xff,  0xff, 0xff, 0x46, 0x00 ],0x01)  # <-- Button pushed (left-bottom-push)
        command = self.build_packet([0xf6, 0x00, 0xfe, 0xfb, 0x71, 0xe1, 0x20 ],[0x01, 0xff, 0xff,  0xff, 0xff, 0x47, 0x00 ],0x01)  # <-- Button pushed (left-bottom-release)

        command = self.build_packet([0xf6, 0x70, 0xfe, 0xfb, 0x71, 0xe1, 0x30 ],[0x01, 0xff, 0xff,  0xff, 0xff, 0x4f, 0x00 ],0x01)  # <-- Button pushed (right-top-push)


        command = self.build_packet([0xf6, 0x37, 0xfe, 0xfb, 0x71, 0xe1, 0x30 ],[0x01, 0xff, 0xff,  0xff, 0xff, 0x4a, 0x00 ],0x01)  # <-- Button pushed
        print("GotTmp: ")
        for i in command:
            print("0x%02x, " % i,end="")
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
        
