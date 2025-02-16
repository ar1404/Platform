def log_action(filename, data):
    timestamp = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    with open('test_log.txt', 'a') as file:
        file.write(f'[{timestamp}] {data}\n')

class K100Pump :
    def __init__(self, serial, device_name, ID):
        
        self.serial = serial
        self.device_name = device_name
        self.ID = ID
        self.connection_repeats = 5 # was 100...

    def connect(self): 
        """"" Connection of the valve to the computer via serial port """
        COMPORT = 'COM7'
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
            log_action('test_log.txt', "Knauer pump is connected.")
            
        else:
            print ('The Port is closed: ' + ser1.portstr)
            log_action('test_log.txt', "Not connected to Knauer pump.")
        
    def command(self, code):
        ser.write(f'{code}\r'.encode())
        byteData = ser.readline().decode().strip()
        return byteData

    def set_flow(self, flow_rate):
        byteData = pump.command(f"F{flow_rate}")
        return byteData
        print('Flow rate set to {flow_rate} ml/min')
        log_action('test_log.txt', "Knauer pump flow rate has been set to {flow_rate} ml/min.")

    def get_flow(self):
        byteData = pump.command(f"F?")
        return byteData
        print('Flow rate set to {byteData} ml/min')
        log_action('test_log.txt', "Knauer pump flow rate is set to {byteData} ml/min.")

    def start_flow(self):
        byteData = pump.command(f"M1")
        return byteData
        print('Pump to begin flow')
        log_action('test_log.txt', "Knauer pump has started flow.")

    def stop_flow(self):
        byteData = pump.command(f"M0")
        return byteData
        print('Pump to stop flow')
        log_action('test_log.txt', "Knauer pump has stopped flow.")