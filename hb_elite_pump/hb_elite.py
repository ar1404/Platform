class HBElite :
    import time
    
    def __init__(self, serial):
        
        self.serial = serial

    def connect(self): 
        """"" Connection of the valve to the computer via serial port """
        COMPORT = 'COM4'
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

        else:
            print ('The Port is closed: ' + ser1.portstr)
        log_action('test_log.txt', "trying to connect")
    


    def command(self, code):
        # Send the command to the syringe pump
        ser.write(f'{code}\r'.encode())
        
        #Without this, the return does not match the executed code but the code previously executed
        time.sleep(0.1)
        
        # Initialize a list to hold the returned data
        response = []
        
        # Set a timeout for reading (1 seconds)
        timeout = time.time() + 1  # Timeout after 1 seconds (adjust as needed)
        
        # Read multiple lines of data from the syringe pump
        while time.time() < timeout:
            if ser.in_waiting > 0:  # If there is data available
                byte_data = ser.readline().decode().strip()  # Read one line of data
                response.append(byte_data)  # Add it to the response list
            else:
                break  # Exit if no more data is available


        if code == 'vers':
            log_action('test_log.txt', 'Syringe pump version information has been requested.')

        elif code == 'time':
            log_action('test_log.txt', 'Syringe pump time has been requested.')

        elif code.startswith('wrate'):
            # Use a regular expression to extract the rate 'x' value from the code string
            match = re.match(r'wrate (\d+(\.\d+)?) ml/min', code)
            if match:
                rate = match.group(1)  # Extract the rate (x) value
                log_action('test_log.txt', f'Syringe pump withdrawal rate has been set to {rate} ml/min.')
            else:
                log_action('test_log.txt', 'Syringe pump withdrawal rate has been requested.')

        elif code.startswith('irate'):
            # Use a regular expression to extract the rate 'x' value from the code string
            match = re.match(r'wrate (\d+(\.\d+)?) ml/min', code)
            if match:
                rate = match.group(1)  # Extract the rate (x) value
                log_action('test_log.txt', f'Syringe pump infusion rate has been set to {rate} ml/min.')
            else:
                log_action('test_log.txt', 'Syringe pump infusion rate has been requested.')

        elif code == 'time':
            log_action('test_log.txt', 'Syringe pump time has been requested.')

            
        # Join the list of responses into a single string with newlines
        formatted_response = '\n'.join(response)  # Combine lines into a single string
        
        # Print the formatted response
        print(formatted_response)