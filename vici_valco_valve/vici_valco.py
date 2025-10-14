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
        COMPORT = 'COM9'
        self.ser = serial.Serial(
            port=COMPORT,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=5
        )
        self.ser = serial.Serial()
        self.ser.baudrate = 9600
        self.ser.port = COMPORT #counter for port name starts at 0
        parity=serial.PARITY_NONE
        stopbits=serial.STOPBITS_ONE
        bytesize=serial.EIGHTBITS
  
        if (self.ser.isOpen() == False):
            self.ser.timeout = 1
            self.ser.open()
            print("Device is connected")
            log_action('device_log.txt', "ViciValco device is connected.")

        else:
            print ('The Port is closed: ' + ser1.portstr)
            log_action('device_log.txt', "Connection has failed.")


    #go_to_pos, read_pos and change_pos have been written for the sampling valve EUHA and are only usable for a 2 position valve

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

    #the command function has been written for the vici solvent selection valve, though can be used with the sampling valve. for the solvent selection valve, 'GOx' sends the valve to position x of 6. command 'VR' should be used to ensure connection - the expected output is: I-PD-EMHX88RN\r06-01-2001


    def command(self, code):
        """ Sends command to device in ASCII and retrieves the response """
        if not self.ser or not self.ser.is_open:
            raise Exception("Serial port is not open")
    
        # send command + carriage return
        cmd = f"{code}\r".encode("ascii")
        self.ser.write(cmd)
    
        # read response (increase timeout if needed)
        response = self.ser.readline().decode(errors="ignore")
    
        return response.strip()
