
import serial
import threading
import time
from homeassistant.util import crc8
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import Packet

DOMAIN = "enocean"

REQUIREMENTS = ['enocean']

ENOCEAN_LOCK = threading.Lock()

ENOCEAN_DONGLE = None

def setup(hass,config):
    global ENOCEAN_DONGLE
    ""
    #hass.states.set('enocean.runstatus', 'It\' ok you know')
    #print("First setting up")

    ENOCEAN_DONGLE = EnOceanDongle(hass,"/dev/ttyUSB0")
    return True


class EnOceanDongle:
    def __init__(self,hass,ser):
        ""
        #self.__ser = serial.Serial(ser, 57600, timeout=0.1)
        #self.__thread = EnOceanThread(self.__ser,ENOCEAN_LOCK,self.callback)
        #self.__thread.start()
        self.__communicator = SerialCommunicator(port=ser,callback=self.callback)
        self.__communicator.start()
        self.__devices = []

    def __del__(self):
        self.__thread.stop_this_one()
        self.__thread.join()

    def register_device(self,dev):
        self.__devices.append(dev)

    def send_command(self,command):
        print("Sending command: %s" % str(command))
        self.__communicator.send(command)
        #with(ENOCEAN_LOCK):
        #    self.__ser.write(command)

    def callback(self,temp):
        print("Callback %s" % str(temp))
        return
        #print("\n\nCalling back %s\n\n",str(temp))
        for d in self.__devices:
            if d.stype == "listener":
                #print("Found one listener")
                equal = True
                for i in range(0,4):
                    if temp[8+i] != d.sensorid[i]:
                        equal = False
                if equal:
                    if temp[12] == 0x30:
                        d.value_changed(1,temp[7])
                    elif temp[12] == 0x20:
                        d.value_changed(0,temp[7])
            elif d.stype == "powersensor":
                #print("Found one listener")
                equal = True
                for i in range(0,4):
                    if temp[11+i] != d.sensorid[i]:
                        equal = False
                if equal:
                    print("FOUND!!!")
                    if temp[10] == 0x0C: # power
                        val = temp[9] + (temp[8] << 8)
                        d.value_changed(val)
                    #elif temp[10] == 0x09: # energy
                    #    val = temp[9] + (temp[8] << 8)
                    #    d.value_changed(val)
            elif d.stype == "switch":
                equal = True
                for i in range(0,4):
                    if temp[10+i] != d.sensorid[i]:
                        equal = False
                if equal:
                    print("FOUND!!!")
                    if temp[8] == 0x60:
                        if temp[9] == 0xe4:
                            d.value_changed(1)
                        elif temp[9] == 0x80:
                            d.value_changed(0)

class EnOceanDevice():
    def __init__(self):
        print("\n\nStarted device\n\n\n")
        ENOCEAN_DONGLE.register_device(self)
        self.stype = ""
        self.sensorid = [0x00,0x00,0x00,0x00]

    def send_command(self,data,optional,packet_type):
        p = Packet(packet_type,data=data,optional=optional)
        ENOCEAN_DONGLE.send_command(p)

        


# Teach for Permundo:
#1
#New packet: 
#55, 00, 0a, 07, 01, eb, a5, 48, 08, 33, 80, 01, 94, 9e, ca, 00, 03, ff, ff, ff, ff, 4c, 00, 7b, 
#
#New packet: 
#55, 00, 09, 07, 01, 56, d2, 04, 60, 80, 01, 94, 9e, ca, 00, 02, ff, ff, ff, ff, 4c, 00, a7, 
#
#New packet: 
#55, 00, 0a, 07, 01, eb, a5, 00, 00, 00, 0c, 01, 94, 9e, ca, 00, 03, ff, ff, ff, ff, 4c, 00, ed,

#2
#New packet: 
#55, 00, 0d, 07, 01, fd, d4, a0, ff, 33, 00, 09, 01, d2, 01, 94, 9e, ca, 00, 03, ff, ff, ff, ff, 55, 00, 99, 
#
#New packet: 
#55, 00, 0a, 07, 01, eb, a5, 48, 08, 33, 80, 01, 94, 9e, ca, 00, 03, ff, ff, ff, ff, 55, 00, 91, 
#
#New packet: 
#55, 00, 09, 07, 01, 56, d2, 04, 60, 80, 01, 94, 9e, ca, 00, 03, ff, ff, ff, ff, 55, 00, 92, 
#
#New packet: 
#55, 00, 0a, 07, 01, eb, a5, 00, 00, 00, 0c, 01, 94, 9e, ca, 00, 03, ff, ff, ff, ff, 55, 00, 07, 

#3:
#New packet: 
#55, 00, 0d, 07, 01, fd, d4, a0, ff, 33, 00, 09, 01, d2, 01, 94, 9e, ca, 00, 03, ff, ff, ff, ff, 52, 00, f2, 
#
#New packet: 
#55, 00, 0a, 07, 01, eb, a5, 48, 08, 33, 80, 01, 94, 9e, ca, 00, 03, ff, ff, ff, ff, 52, 00, fa, 
#




#with button:

#
#New packet: 
#55, 00, 07, 07, 01, 7a, f6, 70, fe, fb, 71, e1, 30, 03, ff, ff, ff, ff, 46, 00, 84, 
#INFO:homeassistant.core:Bus:Handling <Event state_changed[L]: entity_id=sensor.temperature_4, new_state=<state sensor.temperature_4=1; unit_of_measurement=°C, friendly_name=Temperature @ 2016-04-26T08:15:01.814665+02:00>, old_state=<state sensor.temperature_4=0; unit_of_measurement=°C, friendly_name=Temperature @ 2016-04-26T08:14:50.306600+02:00>>
#ID: entity_id
#devID: [254, 251, 113, 225]
#INFO:homeassistant.core:Bus:Handling <Event button_pressed[L]: entity_id=[254, 251, 113, 225], onoff=0, which=0, pushed=1>
#INFO:homeassistant.components.automation:Executing When pushing button
#INFO:homeassistant.core:Bus:Handling <Event logbook_entry[L]: name=When pushing button, message=has been triggered, domain=automation>
#INFO:homeassistant.helpers.script:Script When pushing button: Running script
#INFO:homeassistant.helpers.script:Script When pushing button: Executing step %s
#INFO:homeassistant.core:Bus:Handling <Event call_service[L]: service_call_id=140605427085664-26, service=turn_on, domain=light, service_data=>
#TUrning on
#Wanted: bytearray(b'U\x00\n\x00\x01\x80\xa5\x02d\x01\t\xff\xc6\xea\x01\x00n/')
#GotTmp: 
#0x55, 0x00, 0x07, 0x07, 0x01, 0x7a, 0xf6, 0x37, 0xfe, 0xfb, 0x71, 0xe1, 0x30, 0x01, 0xff, 0xff, 0xff, 0xff, 0x4a, 0x00, 0xdf, Got: bytearray(b'U\x00\n\x00\x01\x80\xa5\x02\x13\x01\t\xff\xc6\xea\x01\x00\x92')
#
#New packet: 
#55, 00, 09, 07, 01, 56, d2, 04, 60, 80, 01, 94, 9e, ca, 00, 03, ff, ff, ff, ff, 47, 00, ef, 
#
#New packet: 
#55, 00, 0a, 07, 01, eb, a5, 00, 00, 00, 0c, 01, 94, 9e, ca, 00, 03, ff, ff, ff, ff, 47, 00, 7a, 
#TUrning on
#Wanted: bytearray(b'U\x00\n\x00\x01\x80\xa5\x02d\x01\t\xff\xc6\xea\x01\x00n/')
#GotTmp: 
#0x55, 0x00, 0x07, 0x07, 0x01, 0x7a, 0xf6, 0x37, 0xfe, 0xfb, 0x71, 0xe1, 0x30, 0x01, 0xff, 0xff, 0xff, 0xff, 0x4a, 0x00, 0xdf, Got: bytearray(b'U\x00\n\x00\x01\x80\xa5\x02\x13\x01\t\xff\xc6\xea\x01\x00\x92')
#INFO:homeassistant.core:Bus:Handling <Event service_executed[L]: service_call_id=140605427085664-26>
#
#New packet: 
#
#New packet: 
#
#New packet: 
#55, 00, 07, 07, 01, 7a, f6, 00, fe, fb, 71, e1, 20, 03, ff, ff, ff, ff, 43, 00, 88, 
#INFO:homeassistant.core:Bus:Handling <Event state_changed[L]: entity_id=sensor.temperature_4, new_state=<state sensor.temperature_4=0; unit_of_measurement=°C, friendly_name=Temperature @ 2016-04-26T08:15:02.098163+02:00>, old_state=<state sensor.temperature_4=1; unit_of_measurement=°C, friendly_name=Temperature @ 2016-04-26T08:15:01.814665+02:00>>
#ID: entity_id
#devID: [254, 251, 113, 225]
#INFO:homeassistant.core:Bus:Handling <Event button_pressed[L]: entity_id=[254, 251, 113, 225], onoff=0, which=0, pushed=0>
#INFO:homeassistant.components.automation:Executing When pushing button
#INFO:homeassistant.core:Bus:Handling <Event logbook_entry[L]: name=When pushing button, message=has been triggered, domain=automation>
#INFO:homeassistant.helpers.script:Script When pushing button: Running script
#INFO:homeassistant.helpers.script:Script When pushing button: Executing step %s
#INFO:homeassistant.core:Bus:Handling <Event call_service[L]: service_call_id=140605427085664-27, service=turn_on, domain=light, service_data=>
#TUrning on
#Wanted: bytearray(b'U\x00\n\x00\x01\x80\xa5\x02d\x01\t\xff\xc6\xea\x01\x00n/')
#GotTmp: 
#0x55, 0x00, 0x07, 0x07, 0x01, 0x7a, 0xf6, 0x37, 0xfe, 0xfb, 0x71, 0xe1, 0x30, 0x01, 0xff, 0xff, 0xff, 0xff, 0x4a, 0x00, 0xdf, Got: bytearray(b'U\x00\n\x00\x01\x80\xa5\x02\x13\x01\t\xff\xc6\xea\x01\x00\x92')
#TUrning on
#Wanted: bytearray(b'U\x00\n\x00\x01\x80\xa5\x02d\x01\t\xff\xc6\xea\x01\x00n/')
#GotTmp: 
#0x55, 0x00, 0x07, 0x07, 0x01, 0x7a, 0xf6, 0x37, 0xfe, 0xfb, 0x71, 0xe1, 0x30, 0x01, 0xff, 0xff, 0xff, 0xff, 0x4a, 0x00, 0xdf, Got: bytearray(b'U\x00\n\x00\x01\x80\xa5\x02\x13\x01\t\xff\xc6\xea\x01\x00\x92')
#INFO:homeassistant.core:Bus:Handling <Event service_executed[L]: service_call_id=140605427085664-27>
#
#New packet: 
#
#New packet: 
#
#




# Teaching from FHEM

#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 55000D0701
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 55000D0701FDD4A0FF3300
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 55000D0701FDD4A0FF33000901D20194
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 55000D0701FDD4A0FF33000901D201949ECA0001FFFF
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 55000D0701FDD4A0FF33000901D201949ECA0001FFFFFFFF500061
#2016.04.26 18:06:11 5: TCM_ESP3_0 dispatch EnOcean:1:D4:A0FF33000901D2:01949ECA:00:01FFFFFFFF5000
#2016.04.26 18:06:11 4: EnOcean received via TCM_ESP3_0: EnOcean:1:D4:A0FF33000901D2:01949ECA:00:01FFFFFFFF5000
#2016.04.26 18:06:11 4: EnOcean ovn_stue received PacketType: 1 RORG: D4 DATA: A0FF33000901D2 SenderID: 01949ECA STATUS: 00
#2016.04.26 18:06:11 5: EnOcean ovn_stue UTE teach-in received from 01949ECA
#2016.04.26 18:06:11 4: EnOcean ovn_stue sent PacketType: 1 RORG: D4 DATA: 91FF33000901D2 SenderID: 00000000 STATUS: 00 ODATA: 0301949ECAFF00
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 sending ESP3: 55000D0701FDD491FF33000901D200000000000301949ECAFF00A1
#2016.04.26 18:06:11 5: SW: 55000D0701FDD491FF33000901D200000000000301949ECAFF00A1
#2016.04.26 18:06:11 2: EnOcean ovn_stue UTE teach-in response send to 01949ECA
#2016.04.26 18:06:11 2: EnOcean ovn_stue UTE teach-in accepted EEP D2-01-09 Manufacturer: Permundo GmbH
#2016.04.26 18:06:11 5: Triggering global (1 changes)
#2016.04.26 18:06:11 5: Notify loop for global SAVE
#2016.04.26 18:06:11 5: Triggering ovn_stue (1 changes)
#2016.04.26 18:06:11 5: Notify loop for ovn_stue teach: UTE teach-in accepted EEP D2-01-09 Manufacturer: Permundo GmbH
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 550001
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 5500010002650000
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RESPONSE: OK
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 550009
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 550009070156D20460
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 550009070156D204608001949ECA00
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 550009070156D204608001949ECA0001FFFFFFFF50
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 550009070156D204608001949ECA0001FFFFFFFF50006A
#2016.04.26 18:06:11 5: TCM_ESP3_0 dispatch EnOcean:1:D2:046080:01949ECA:00:01FFFFFFFF5000
#2016.04.26 18:06:11 4: EnOcean received via TCM_ESP3_0: EnOcean:1:D2:046080:01949ECA:00:01FFFFFFFF5000
#2016.04.26 18:06:11 4: EnOcean ovn_stue received PacketType: 1 RORG: D2 DATA: 046080 SenderID: 01949ECA STATUS: 00
#2016.04.26 18:06:11 5: Triggering ovn_stue (9 changes)
#2016.04.26 18:06:11 5: Notify loop for ovn_stue powerFailure0: disabled
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 55000A0701
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 55000A0701EBA50000000C
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 55000A0701EBA50000000C01949ECA0001
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 55000A0701EBA50000000C01949ECA0001FFFFFFFF5000
#2016.04.26 18:06:11 5: TCM TCM_ESP3_0 RAW: 55000A0701EBA50000000C01949ECA0001FFFFFFFF5000FF
#2016.04.26 18:06:11 5: TCM_ESP3_0 dispatch EnOcean:1:A5:0000000C:01949ECA:00:01FFFFFFFF5000
#2016.04.26 18:06:11 4: EnOcean received via TCM_ESP3_0: EnOcean:1:A5:0000000C:01949ECA:00:01FFFFFFFF5000
#2016.04.26 18:06:11 4: EnOcean ovn_stue received PacketType: 1 RORG: A5 DATA: 0000000C SenderID: 01949ECA STATUS: 00
#2016.04.26 18:06:11 5: Triggering ovn_stue (1 changes)
#2016.04.26 18:06:11 5: Notify loop for ovn_stue power: 0






# Again
#
#2016.04.26 18:08:09 5: TCM TCM_ESP3_0 RAW: 5500
#2016.04.26 18:08:09 5: TCM TCM_ESP3_0 RAW: 55000D0701FD
#2016.04.26 18:08:09 5: TCM TCM_ESP3_0 RAW: 55000D0701FDD4A0FF
#2016.04.26 18:08:09 5: TCM TCM_ESP3_0 RAW: 55000D0701FDD4A0FF33000901D201
#2016.04.26 18:08:09 5: TCM TCM_ESP3_0 RAW: 55000D0701FDD4A0FF33000901D201949ECA0001FF
#2016.04.26 18:08:09 5: TCM TCM_ESP3_0 RAW: 55000D0701FDD4A0FF33000901D201949ECA0001FFFFFFFF4F00F5
#2016.04.26 18:08:09 5: TCM_ESP3_0 dispatch EnOcean:1:D4:A0FF33000901D2:01949ECA:00:01FFFFFFFF4F00
#2016.04.26 18:08:09 4: EnOcean received via TCM_ESP3_0: EnOcean:1:D4:A0FF33000901D2:01949ECA:00:01FFFFFFFF4F00
#2016.04.26 18:08:09 4: EnOcean ovn_stue received PacketType: 1 RORG: D4 DATA: A0FF33000901D2 SenderID: 01949ECA STATUS: 00
#2016.04.26 18:08:09 5: EnOcean ovn_stue UTE teach-in received from 01949ECA
#2016.04.26 18:08:09 4: EnOcean ovn_stue sent PacketType: 1 RORG: D4 DATA: 91FF33000901D2 SenderID: 00000000 STATUS: 00 ODATA: 0301949ECAFF00
#2016.04.26 18:08:09 5: TCM TCM_ESP3_0 sending ESP3: 55000D0701FDD491FF33000901D200000000000301949ECAFF00A1
#2016.04.26 18:08:09 5: SW: 55000D0701FDD491FF33000901D200000000000301949ECAFF00A1
#2016.04.26 18:08:09 2: EnOcean ovn_stue UTE teach-in response send to 01949ECA
#2016.04.26 18:08:09 2: EnOcean ovn_stue UTE teach-in accepted EEP D2-01-09 Manufacturer: Permundo GmbH
#2016.04.26 18:08:09 5: Triggering global (1 changes)
#2016.04.26 18:08:09 5: Notify loop for global SAVE
#2016.04.26 18:08:09 5: Triggering ovn_stue (1 changes)
#2016.04.26 18:08:09 5: Notify loop for ovn_stue teach: UTE teach-in accepted EEP D2-01-09 Manufacturer: Permundo GmbH
#2016.04.26 18:08:09 5: TCM TCM_ESP3_0 RAW: 5500
#2016.04.26 18:08:09 5: TCM TCM_ESP3_0 RAW: 5500010002650000
#2016.04.26 18:08:09 5: TCM TCM_ESP3_0 RESPONSE: OK
#2016.04.26 18:08:13 5: TCM TCM_ESP3_0 RAW: 55000A07
#2016.04.26 18:08:13 5: TCM TCM_ESP3_0 RAW: 55000A0701EBA5000EEE
#2016.04.26 18:08:13 5: TCM TCM_ESP3_0 RAW: 55000A0701EBA5000EEE0901949ECA00
#2016.04.26 18:08:13 5: TCM TCM_ESP3_0 RAW: 55000A0701EBA5000EEE0901949ECA0001FFFFFFFF5B
#2016.04.26 18:08:13 5: TCM TCM_ESP3_0 RAW: 55000A0701EBA5000EEE0901949ECA0001FFFFFFFF5B0009
#2016.04.26 18:08:13 5: TCM_ESP3_0 dispatch EnOcean:1:A5:000EEE09:01949ECA:00:01FFFFFFFF5B00
#2016.04.26 18:08:13 4: EnOcean received via TCM_ESP3_0: EnOcean:1:A5:000EEE09:01949ECA:00:01FFFFFFFF5B00
#2016.04.26 18:08:13 4: EnOcean ovn_stue received PacketType: 1 RORG: A5 DATA: 000EEE09 SenderID: 01949ECA STATUS: 00
#2016.04.26 18:08:13 5: Triggering ovn_stue (2 changes)
#2016.04.26 18:08:13 5: Notify loop for ovn_stue energy0: 382.2


