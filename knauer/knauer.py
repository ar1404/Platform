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
        ser.write(f'{code}\r'.encode())
        #accepting the response
        byteData = ser.readline().decode().strip()
        #give response
        return byteData

    #making functions with set commands to improve readability in the main code and to make logging easier
    def set_flow(self, flow_rate):
        byteData = pump.command(f"F{flow_rate}")
        return byteData
        print('Flow rate set to {flow_rate} ml/min')
        log_action('device_log.txt', "Knauer pump flow rate has been set to {flow_rate} ml/min.")

    def get_flow(self):
        byteData = pump.command(f"F?")
        return byteData
        print('Flow rate set to {byteData} ml/min')
        log_action('device_log.txt', "Knauer pump flow rate is set to {byteData} ml/min.")

    def start_flow(self):
        byteData = pump.command(f"M1")
        return byteData
        print('Pump to begin flow')
        log_action('device_log.txt', "Knauer pump has started flow.")

    def stop_flow(self):
        byteData = pump.command(f"M0")
        return byteData
        print('Pump to stop flow')
        log_action('device_log.txt', "Knauer pump has stopped flow.")