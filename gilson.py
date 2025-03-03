# -*- coding: utf-8 -*-

import datetime, time
import serial
import binascii
import logging
import regex as re
from math import isclose
import numpy as np

from loguru import logger

def log_action(filename, data):
    timestamp = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    with open('test_log.txt', 'a') as file:
        file.write(f'[{timestamp}] {data}\n')


class gsioc_Protocol:

    """
    Base class implementing various common functions shared across GSIOC devices. This class implements:
    - verify_open : Checks if the port is open; If not opens it
    - verify_device : Checks that the device is correct
    - connect : Connects to device specified through ID, verifies device is correct
    - iCommand : Immediate Command
    - bCommand : Buffered Command

    A seperate class passes a serial port object to this class to allow connecting multiple GSIOC devices through
    a single serial port. The devices are identified through their ID.
    """

    def __init__(self, serial, device_name, ID):
        
        self.serial = serial
        self.device_name = device_name
        self.ID = ID
        self.connection_repeats = 5 # was 100...

        #Logging off by default
        self.logging_enabled = False
        self.create_logger()
        
    def create_logger(self):
        logger.remove()  # ✅ Prevent duplicate handlers
        logger.add("autosampler_log.txt", level="DEBUG", format="[{time:DD/MM/YY HH:mm:ss}] - {level} - {message}")
        logger.disable(__name__)  # ✅ Logging is OFF by default

    def enable_logging(self):
        self.logging_enabled = True
        logger.enable(__name__)  # ✅ Turn logging ON
        print("Logging enabled.")

    def disable_logging(self):
        self.logging_enabled = False
        logger.disable(__name__)  # ✅ Turn logging OFF

    def log_info(self, message):
        """Wrapper to log messages only when enabled"""
        if self.logging_enabled:
            logger.info(message)
        
    # Checks if SerialPort is open; If not opens it
    def verify_open(self):
        logger.debug('Check if port is open.')
        if self.serial.isOpen() == False:
            try:
                self.serial.open()
            except Exception as e:
                logger.exception('Port is not opening.')
                raise e

        return True

    # Check that we are connected to the right device
    def verify_device(self):
        
        # Verify that it is connected to the correct device (device_name)
        time.sleep(0.2)
        device_version_string = self.iCommand('%')
        time.sleep(0.2)
        device_string = device_version_string.split(' v')[0]
        # Return True if correct device, False otherwise
        return device_string == self.device_name

    # Connect to Device using UnitID (see manual + back of device)
    # Verify that it's the right device
    def connect(self):
        # Verify port is opened
        self.verify_open()

        # Connect to unit ID
        if( int(self.ID) not in range(64) ):
            raise Exception("ID out of range [0,63]")

        byte_ID = self.ID +  128

        self.serial.flushInput()
        self.serial.write(bytes.fromhex('ff'))
        time.sleep(0.2)   # Passively wait for all devices to disconnect
        self.serial.write(byte_ID.to_bytes(1,byteorder='big'))

        resp = self.serial.read(10)    # Will return empty array after timeout
        if(len(resp) == 0) or resp == b'':
            logger.critical('No response from device')
            if self.connection_repeats > 0:
                self.connection_repeats = (self.connection_repeats - 1)
                logger.error(f'Attempt {100-self.connection_repeats}/100: {str(datetime.datetime.now())} No response from device {byte_ID-128}')
                log_action('test_log.txt', "Unable to connect to Gilson autosampler.")
                self.connect()
            else:
                raise Exception(str(datetime.datetime.now()) + "No response from device")

        # Verifies that the correct device is connected
        if self.verify_device():
            
            logger.debug(f"Connected to device {byte_ID-128}")
            log_action('test_log.txt', "Connected to autosampler.")
            
        # Wrong Device ID
        else:
            logger.error(f'Connected to wrong device: connecting to device {byte_ID-128} failed.')
            if self.connection_repeats > 0:
                self.connection_repeats = (self.connection_repeats - 1)
                logger.error(f'Attempt {100-self.connection_repeats}/100: Tried connecting to device: {byte_ID-128}')
                self.connect()
            else:
                logger.error('Connected to wrong device: {}'.format(self.iCommand('%')))
                raise Exception('Connected to wrong device: {}'.format(self.iCommand('%')))

    # Send immediate Command; One Character at most
    def iCommand(self,commandstring):
        
        # Convert to binary
        command = binascii.a2b_qp(commandstring)

        # Write command
        self.serial.flushInput()
        self.serial.write(command)

        # Retrieve Response - looks like this returns one byte at a time...
        resp = bytearray(0)
        while(True):
            resp_raw = self.serial.read(10)    # Will return empty array after timeout

            if(len(resp_raw) == 0) or resp_raw == b'':
                if self.connection_repeats > 0:
                    self.connection_repeats = (self.connection_repeats - 1)
                    logger.error(f'Attempt {100-self.connection_repeats}/100: sent Immediate Command {commandstring}, in binascii: {command}')
                    self.iCommand(commandstring)
                else:
                    logger.critical('No response from device')
                    raise Exception(str(datetime.datetime.now()) + "No response from device")

            resp.append(resp_raw[0])

            # Extended ASCII represents end of message
            if(resp[len(resp)-1] > 127):
                resp[len(resp)-1] -= 128

                logger.debug(f'Sending immediate command complete.')
                
                break

            # Write Acknowledge to Device to signal next byte can be retrieved
            else:
                self.serial.flushInput()
                self.serial.write(bytes.fromhex("06"))
                
        # logger.debug('Received {} as response'.format(resp.decode("ascii")))
        logger.debug(f'received {resp} as response.')

        return resp.decode("ascii")

    # Buffered Command; More then one character
    def bCommand(self, commandstring):

        # Convert to byte, \n signifies start of command, \r signals end of command
        data = binascii.a2b_qp("\n" + commandstring + "\r")
        logger.info(f'GSIOC <<< {commandstring}')
        self.serial.flushInput()
        resp = bytearray(0)

        # begin buffered command by sending \n until the device echos \n or times out
        firstErrorPrinted = False # This is used to prevent repetitive printing

        while(True):
            self.serial.write(data[0:1])    # send \n
            resp_raw = self.serial.read(10)    # Will return empty array after timeout J.F.W.>>> changed to 2 bytes. If no timeout is defined in serial, it will simply wait forever!
            
            if(len(resp_raw) == 0) or resp_raw == b'':
                if self.connection_repeats > 0:
                    self.connection_repeats = (self.connection_repeats - 1)
                    logger.error(f'Attempt {100-self.connection_repeats}/100: sent buffered Command {commandstring}, in binascii: {data}')
                    self.bCommand(commandstring)
                else:
                    logger.critical('No response from device')
                    raise Exception(str(datetime.datetime.now()) + "No response from device")
            logger.debug(f'ready signal: {resp_raw}')
            ################################################################################################################
            # TODO CHECK IF THE FOLLOWING CONIDTION RAISES MORE PROBLEMS!!! IT IS MEANT TO FIX THE INDEX OUT OF RANGE ERROR!
            if not resp_raw:
                return
            ################################################################################################################
            readySig = resp_raw[0]
            # If devices answers \n signifies device is ready
            if(readySig == 10): #J.F.W.>>> 10 is ascii code for Line Feed LF
                logger.debug('Starting to send buffered command.')
                break

            # Device is busy
            elif(readySig == 35): #J.F.W>>> 35 is ascii code for "#"-symbol
                if(not firstErrorPrinted):
                    logger.debug('Device busy. Waiting....')
                    firstErrorPrinted = True
            else:
                logger.error("Did not recieve \\n (0x0A) or # as response")
                # raise Exception("Did not recieve \\n (0x0A) or # as response")
        logger.debug(readySig)#.decode("ascii")) #JFW>>>
        resp.append(readySig)
        self.serial.flushInput()
        # Send buffered data, one byte at a time, Device echo's byte send
        for i in range(1,len(data)):
            logger.debug(f'Writes buffered Command character {data[i:i+1]} to the device {self.device_name}.')
            self.serial.write(data[i:i+1])
            logger.debug(f'Starts reading character from the device {self.device_name}.')
            resp_raw = self.serial.read(3)    # Will return empty array after timeout
            logger.debug(f'got back {resp_raw} from the device {self.device_name}.')
        # for i in range(len(data)):
        #     self.serial.write(data[i:i+1])
        #     resp_raw = self.serial.read(3) 
            logger.debug("resp_raw: "+str(resp_raw)) #JFW>>>

            # self.serial.flushInput()
            if(len(resp_raw) == 0) or resp_raw == b'':
                if self.connection_repeats > 0:
                    self.connection_repeats = (self.connection_repeats - 1)
                    logger.error(f'Attempt {100-self.connection_repeats}/100: sent buffered Command {commandstring}, in binascii: {data}')
                    self.bCommand(commandstring)
                else:
                    logger.critical('No response from device')
                    raise Exception(str(datetime.datetime.now()) + "No response from device")
                # logger.debug(resp_raw) #JFW>>>

            # logger.debug("resp_raw: "+str(resp_raw))
            
            if len(resp_raw)==3:
                resp.append(resp_raw[1])
            else:
                logger.debug(f'resp_raw 2: {resp_raw[0]}')
                resp.append(resp_raw[0])

            # resp=binascii.a2b_qp(resp)
            # if(resp[len(resp)-1] > 127):
            #     resp[len(resp)-1] -= 128
           

            if( resp[i] != data[i] ):
                logger.debug("Response:" + str(resp[:])) #JFW>>>
                logger.debug("Data:" + str(data[:])) #JFW>>>
                logger.error('Received ' + str(resp) + " instead of " + str(data[i:i+1]))
                # raise Exception("Received " + str(resp) + " instead of " + str(data[i:i+1]))
            
            if( resp[i] == 13 ):
                logger.debug('Buffered command complete.')
                logger.debug(f'Received {resp} from device.')    
                logger.info(f'GSIOC >>> {resp}')
                return resp
            
            if commandstring == 'H':
                log_action('test_log.txt', "Autosampler sent to home position.")           

            elif commandstring == 'e[n]':
                log_action('test_log.txt', "Autosampler has cleared errors.")  

        # This will happen if sending the data failed
        logger.error("Buffered command FAILED")
        resp_no_whitespace = resp[1:len(resp)-2]
        return resp_no_whitespace.decode("ascii")


                    

    ## General Commands ##
    def closeSerial(self):
        self.serial.close()
        
    def get_error(self):
        return self.iCommand('e')

    def get_device_name(self):
        return self.iCommand('%')
    
    def status(self):
        return self.iCommand('M')

    def reset(self):
        self.iCommand('$')
        time.sleep(0.1)
        self.connect()

    def go_to_vial(self, vial):
        thing = rack1_commands.get_xy_command(vial)
        self.bCommand(thing[0])
        log_action('test_log.txt', f"Autosampler sent to {vial} position.")


class rack1:
    rack_position_offset_x=92       #distance in mm between rack_position=1 and =2 on x-axis
    rack_position_offset_y=0        #distance in mm between rack_position=1 and =2 on y-axis
    
    ############################# RACK 1 DEFINITION #################################
    
    # From platform_setup.py 
    rack1 = Rack([4,16], 7.5, 39.5, 18.5, 13.75, 65) # groundlevel_height assumed the minimum Z
    
    #  array_dimensions, offset_x, offset_y=offset_y, vial2vial_x, vial2vial_y, groundlevel_height
    
    # Previous vial2vialx = (2.11+15.6)
    # Previous vial2vial7 = (2.72+15.6+0.35)
    
    array_order1 = np.array([      #user is obliged to define a integer number i>=1 for each vial in the rack in ascending order 
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10,11,12],
        [13,14,15,16],
        [17,18,19,20],
        [21,22,23,24],     
        [25,26,27,28],     
        [29,30,31,32],
        [33,34,35,36],
        [37,38,39,40],
        [41,42,43,44],
        [45,46,47,48],
        [49,50,51,52],
        [53,54,55,56],
        [57,58,59,60],
        [61,62,63,64]        
        ])
        
    rack_pos1=1
    
    global rack1_commands
    
    # Not sure what rack_position_offset_x/y are for x=92 and y=0
    
    rack1_commands = Rackcommands(rack1, array_order1, rack_pos1, rack_position_offset_x, rack_position_offset_y)
    
    global vial_selfmade
    
    vial_selfmade = Vial(1.5, 1, 33, 31.08)


class DeviceController:
    def __init__(self, serial_connection, max_repeats=100):
        self.serial = serial_connection
        self.max_repeats = max_repeats
        self.connection_repeats = max_repeats

    # 3. Method Definition
    def iCommand(self, commandstring):
        logger.debug(f'Sending immediate command {commandstring} to device.')
        
        # Convert to binary
        command = binascii.a2b_qp(commandstring)
        logger.debug(f'Converted command to binary: {command}')

        # Write command
        self.serial.flushInput()
        self.serial.write(command)
        logger.debug('Command written to serial port.')

        # Retrieve Response
        resp = bytearray()
        while True:
            resp_raw = self.serial.read(10)    # Will return empty array after timeout
            logger.debug(f'Received raw response: {resp_raw}')

            if len(resp_raw) == 0:
                logger.debug(f'No response received. Connection repeats left: {self.connection_repeats}')
                if self.connection_repeats > 0:
                    self.connection_repeats -= 1
                    logger.error(f'Attempt {self.max_repeats - self.connection_repeats}/{self.max_repeats}: sent Immediate Command {commandstring}, in binascii: {command}')
                    return self.iCommand(commandstring)  # Safe recursion
                else:
                    logger.critical('No response from device after maximum retries.')
                    raise Exception(str(datetime.datetime.now()) + " No response from device")

            resp.extend(resp_raw)
            logger.debug(f'Current response buffer: {resp}')

            # Extended ASCII represents end of message
            if resp[-1] > 127:
                resp[-1] -= 128
                logger.debug(f'End of message detected, adjusted last byte: {resp[-1]}')
                logger.debug('Sending immediate command complete.')
                break

            # Write Acknowledge to Device to signal next byte can be retrieved
            else:
                self.serial.flushInput()
                self.serial.write(bytes.fromhex("06"))
                logger.debug('Acknowledgement sent to device.')

        logger.debug(f'Received full response: {resp}')
        return resp.decode("ascii")

def check_xy_position_change(gsioc_lh, logging_entity, destination_command, TESTING_ACTIVE=False):
    """Checks if current x/y-position is close to the expected destination. 
    Returns True if position is the expected one, False if not."""
    
    logging_entity.info(f'The following command is checked: {destination_command}')
    match =  re.search('^X(\d+\.?(\d+)?)/(\d+\.?(\d+)?)$',destination_command)
    if match:
        gsioc_lh.connect()
        current_xy_position = str(gsioc_lh.iCommand('X'))
        # Reformat destination and current position (expected gsioc command "X###.######/###.######")
        dest_posx, dest_posy = str(destination_command).replace('X','').split('/')
        current_posx, current_posy = str(current_xy_position).replace('X','').split('/')
        if TESTING_ACTIVE == True:
            current_posx = dest_posx
            current_posy = dest_posy
        coords = [dest_posx,dest_posy,current_posx,current_posy]
        for i in range(len(coords)):
            coords[i]=float(coords[i])
        cond_x = isclose(coords[0],coords[2],abs_tol=0.6)
        cond_y = isclose(coords[1],coords[3],abs_tol=0.6)
        if cond_x and cond_y:
            return True
        else:
            logging_entity.critical(f'X/Y-POSITION {current_xy_position} UNEXPECTED. Expected: {destination_command}, equality up to a difference of 0.6 mm.')
            return False
    else:
        logging_entity.critical(f'INVALID USE OF FUNCTION. Expected X/Y-command, not {destination_command}')
        return True

def ensure_xy_position_will_be_reached(gsioc_liqhan,attempts,logging_entity,xy_positioning_command, TESTING_ACTIVE = False):
    logging_entity.info(f'The following command is ensured to get reached: {xy_positioning_command}')
    gsioc_liqhan.connect()
    time.sleep(5)
    # gsioc_liqhan.bCommand('H')
    gsioc_liqhan.bCommand('Z125')
    for i in range(attempts):
        gsioc_liqhan.bCommand(xy_positioning_command)
        approval = check_xy_position_change(gsioc_liqhan,logging_entity,xy_positioning_command, TESTING_ACTIVE)
        if i > 0:
            logging_entity.critical(f'X/Y-POSITION UNEXPECTED')
            if i == attempts-1:
                g.bCommand('H')
                time.sleep(15)
                raise TimeoutError(f'This Error was raised after {attempts} attemps of repositioning to {xy_positioning_command}.')
        if approval:
            break
        else:
            continue


if __name__ == '__main__':
    PORT1   = 'COM1'
    ser=serial.Serial(PORT1,19200,8,"N",1,0.1) 
    g = gsioc_Protocol(ser,'GX-241 II',33)
    #g1 = gsioc_Protocol(ser,'GX D Inject',3)

    g.connect()
    ###### COMMANDS TO THE LIQUID HANDLER ######
    g.iCommand("%")
    g.bCommand('H')
    time.sleep(5)

    #g1.connect()
    ##### COMMANDS TO THE VALVE ######
    #g1.iCommand("%")
    #g1.bCommand('VL')

class Rack():
    """Representation for a Rack within the flow setup."""
    def __init__(self, array_dimensions, offset_x, offset_y, vial2vial_x, vial2vial_y, groundlevel_height):
        self.array_dimensions=array_dimensions
        self.offset_x=offset_x
        self.offset_y=offset_y
        self.vial2vial_x=vial2vial_x
        self.vial2vial_y=vial2vial_y
        self.groundlevel_height=groundlevel_height    
    
    def get_vial_indices(self, vial_position, array_order, tolerance):
        """get indices of a specific vial in a rack with a certain order of the vials
        :returns: a tuple of (i,j) with i=vial-position along x-axis, and j=vial-position along y-axis
        TODO: verify that input is valid type, array dimensions and validation of the inputted values
        """
        indices=np.where(array_order==vial_position)
        # print(str(f'indices are: {indices}'))
        if len(indices)==2 and len(indices[0])==1:
            
            return indices
        elif len(indices)==2 and len(indices[0])==0 and tolerance.lower()=='no':                #tolerance settings
            #REMOVE THIS STATEMENT!!!
            sys.exit(f'fatal error: zero vials with position number {vial_position}')                        #REMOVE THIS STATEMENT!!!
        else:
            logger.warning(f'warning: multiple vials with position number {vial_position}')
            return indices


class Rackcommands(): 
    """Representation for Commands connected to the Rack of the flow setup."""

    def __init__(self,rack,rack_order,rack_position,rack_position_offset_x,rack_position_offset_y):
        self.rack=rack
        self.rack_order=rack_order
        self.rack_position=rack_position
        self.rack_position_offset_x=rack_position_offset_x
        self.rack_position_offset_y=rack_position_offset_y
        
    def get_xy_command(self, vial_pos: int, tolerance: str = 'no') -> str: #speed 125mm/s, force 100%
        """returns a str object command suitable for the liquid handler gx-241"""
        
        index_y, index_x = self.rack.get_vial_indices(vial_pos, self.rack_order, tolerance)
        
        if len(index_x)==len(index_y):
            command=[]
            for i in range(len(index_x)):
                i_x=index_x[i]
                i_y=index_y[i]
                distance_x=self.rack.offset_x + self.rack.vial2vial_x * i_x + (self.rack_position-1)*self.rack_position_offset_x    
                distance_y=self.rack.offset_y + self.rack.vial2vial_y * i_y + (self.rack_position-1)*self.rack_position_offset_y    
                command.append(str(f'X{distance_x}/{distance_y}'))
            return command
        else:
            logger.error("error: len(index_x) != len(index_y) ")



class Vial():
    """Representation for a Vial within the flow setup."""
    def __init__(self,vial_volume_max,vial_usedvolume_max,vial_height,vial_free_depth):
        self.vial_volume_max=vial_volume_max                #volume in mL
        self.vial_usedvolume_max=vial_usedvolume_max        #volume in mL
        self.vial_height=vial_height                        #height in mm
        self.vial_free_depth=vial_free_depth                #depth in mm
        self.sum_liquid_level = 0