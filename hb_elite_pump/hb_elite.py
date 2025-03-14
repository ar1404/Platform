import serial
import datetime
import re
import time

def log_action(filename, data):
    """ Logging activity of equipment in an ongoing .txt file to allow for easier identification of errors that may occur """
    #Adding a timestamp in the format DD/MM/YYYY hh:mm:ss
    timestamp = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    #filename and 'a' for append mode(add not make new)
    with open('device_log.txt', 'a') as file:
        #added in the format [timestamp] + log information
        file.write(f'[{timestamp}] {data}\n')

class HBElite :
    
    def __init__(self, serial):
        self.ser = serial

    def connect(self): 
        """"" Connection of the valve to the computer via serial port """
        if self.ser.isOpen():
            self.ser.timeout = 1
            print("Device is connected")
            log_action('device_log.txt', "Connection to HB pump successful.")

        else:
            print ('The Port is closed: ' + self.ser.portstr)
            log_action('device_log.txt', "Connection to HB pump failed.")
    


    def command(self, code):
        """ Sends command to device in bytes, retrieves the response and adds to the activity log the relevant command """
        # Send the command to the syringe pump
        self.ser.write(f'{code}\r'.encode())
        
        #Without this, the return does not match the executed code but the code previously executed
        time.sleep(0.1)
        
        # Initialize a list to hold the returned data
        response = []
        
        # Set a timeout for reading (1 seconds)
        timeout = time.time() + 1  # Timeout after 1 seconds (adjust as needed)
        
        # Read multiple lines of data from the syringe pump
        while time.time() < timeout:
            if self.ser.in_waiting > 0:  # If there is data available
                byte_data = self.ser.readline().decode().strip()  # Read one line of data

                if byte_data == '<':
                    print('Pump withdrawing')

                elif byte_data == '>':
                    print('Pump infusing')

                elif byte_data == 'T*':
                    print('Target volume reached')
                    
                response.append(byte_data)  # Add it to the response list
            else:
                break  # Exit if no more data is available

        return response


        if code == 'vers':
            log_action('device_log.txt', 'Syringe pump version information has been requested.')

        elif code == 'time':
            log_action('device_log.txt', 'Syringe pump time has been requested.')

        elif code.startswith('wrate'):
            # Use a regular expression to extract the rate 'x' value from the code string
            match = re.match(r'wrate (\d+(\.\d+)?) ml/min', code)
            if match:
                rate = match.group(1)  # Extract the rate (x) value
                log_action('device_log.txt', f'Syringe pump withdrawal rate has been set to {rate} ml/min.')
            else:
                log_action('device_log.txt', 'Syringe pump withdrawal rate has been requested.')

        elif code.startswith('irate'):
            # Use a regular expression to extract the rate 'x' value from the code string
            match = re.match(r'wrate (\d+(\.\d+)?) ml/min', code)
            if match:
                rate = match.group(1)  # Extract the rate (x) value
                log_action('device_log.txt', f'Syringe pump infusion rate has been set to {rate} ml/min.')
            else:
                log_action('device_log.txt', 'Syringe pump infusion rate has been requested.')

        elif code == 'time':
            log_action('device_log.txt', 'Syringe pump time has been requested.')

            
        # Join the list of responses into a single string with newlines
        formatted_response = '\n'.join(response)  # Combine lines into a single string
        
        # Print the formatted response
        print(formatted_response)


    def set_flow(self, flow_rate):
        self.command(f'irate {flow_rate}')
        self.command(f'wrate {flow_rate}')
        print(f'Flow rate set to {flow_rate}')

    def get_flow(self):
        flow_rate = self.command('irate')
        print(f'Flow rate is {flow_rate}.')

    def withdraw(self):
        self.command('wrun')
        print('Pump withdrawing.')

    def infuse(self):
        self.command('irun')
        print('Pump infusing.')

    def set_tvolume(self, tvolume):
        self.command(f'tvolume {tvolume}')
        print(f'Target volume set to {tvolume}.')

    def clear_volume(self):
        self.command('cvolume')
        self.command('ctvolume')
        print('Volumes reset to zero.')

    def stop(self):
        self.command('stop')
        print('Pump action halted.')
        