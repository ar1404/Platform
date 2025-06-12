import serial
import datetime

def log_action(filename, data):
    timestamp = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    with open('device_log.txt', 'a') as file:
        file.write(f'[{timestamp}] {data}\n')

class ViciValco:
    def __init__(self, serial):
        
        self.serial = serial
    
    def connect(self): 
        """"" Connection of the valve to the computer via serial port """
        COMPORT = 'COM14'
        global ser
        ser = serial.Serial()
        ser.baudrate = 9600
        ser.port = COMPORT #counter for port name starts at 0
        parity=serial.PARITY_NONE
        stopbits=serial.STOPBITS_ONE
        bytesize=serial.EIGHTBITS
  
        if (ser.isOpen() == False):
            ser.timeout = 1
            ser.open()
            print("Device is connected")
            log_action('device_log.txt', "ViciValco device is connected.")

        else:
            print ('The Port is closed: ' + ser1.portstr)
            log_action('device_log.txt', "Connection has failed.")

    def go_to_pos(self, pos):
        """ Sends command to change positions to device in bytes, retrieves the response and adds to the activity log the relevant command """
        ser.write(b'CP\r')
        byteData = ser.readline().decode()
        position = byteData[-2]

        if position != pos:
            if pos == 'A':
                ser.write(b'CW\r')
                print('Valve moved to position A')
                log_action('device_log.txt', "ViciValco moved to position A.")
            elif pos == 'B':
                ser.write(b'CC\r')
                print('Valve moved to position B')
                log_action('device_log.txt', "ViciValco moved to position B.")
        else:
                print('Valve already at that position')
                log_action('device_log.txt', "ViciValco already at the desired position.")


    def read_pos(self):
        """ Sends command to read position to device in bytes, retrieves the response and adds to the activity log the relevant command """
        ser.write(b'CP\r')
        byteData = ser.readline().decode()
        return byteData[-2]
        log_action('device_log.txt', "ViciValco at the position {byteData[-2]}.")


    def change_pos(self):
        """ Toggles the valve position between A and B """
        ser.write(b'CP\r')
        byteData = ser.readline().decode()
        position = byteData[-2]  # Assuming this gives 'A' or 'B'
    
        if position == 'A':
            self.go_to_pos('B')
        elif position == 'B':
            self.go_to_pos('A')
        else:
            print(f"Unknown current position: {position}")
            log_action('device_log.txt', f"Failed to toggle position. Unknown current position: {position}")