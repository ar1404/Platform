import datetime
import serial
import re
import time


def log_action(filename, data):
    """ Logging activity of equipment in an ongoing .txt file to allow for easier identification of errors that may occur """
    timestamp = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    with open('device_log.txt', 'a') as file:
        file.write(f'[{timestamp}] {data}\n')

class K100Pump :
    def __init__(self, serial):
        self.ser = serial

    def connect(self): 
        """"" Connection of the valve to the computer via serial port """
        if self.ser.isOpen():
            self.ser.timeout = 1
            print("Device is connected")
            log_action('device_log.txt', "Connection to Knauer pump successful.")

        else:
            print ('The Port is closed: ' + self.ser.portstr)
            log_action('device_log.txt', "Connection to Knauer pump failed.")
        
    def command(self, code):
        """ Sends command to device in bytes and retrieves the response """
        #sending the command to device
        self.ser.write(f'{code}\r'.encode())
        #accepting the response
        byteData = self.ser.readline().decode().strip()
        #give response
        return byteData

    def get_sernum(self):
        byteData = self.command("SERNUM?")
        return byteData
        log_action('device_log.txt', "Knauer pump's serial number has been requested.")
    
    #making functions with set commands to improve readability in the main code and to make logging easier
    def set_flow_rate(self, flow_rate):
        byteData = self.command(f"FLOW:{flow_rate}")
        return byteData
        print('Flow rate set to {flow_rate} ul/min')
        log_action('device_log.txt', "Knauer pump flow rate has been set to {flow_rate} ul/min.")

    def get_flow_rate(self):
        byteData = self.command("FLOW?")
        return byteData
        print('Flow rate set to {byteData} ml/min.')
        log_action('device_log.txt', "Knauer pump's flow rate has been requested.")

    def start_flow(self):
        byteData = self.command('ON')
        return byteData
        print('Pump to begin flow.')
        log_action('device_log.txt', "Knauer pump has started flow.")

    def stop_flow(self):
        byteData = self.command('OFF')
        return byteData
        print('Pump to stop flow.')
        log_action('device_log.txt', "Knauer pump has stopped flow.")