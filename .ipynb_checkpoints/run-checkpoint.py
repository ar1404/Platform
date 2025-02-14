# Import hardware
from instruments.gilson import gsioc_protocol, direct_injection_module
# from instruments.knauer import TO DO

# Import settings
from platform_setup import gx241_com_port, gx241_ID, dim_ID, baudrate, rack1_commands, hplc_vial
from spka import spka


#######################################################################


# gx241 and DIM GSIOC protocols
ser = serial.Serial(gx241_com_port, baudrate, 8, "N", 1, 0.1)
gx241 = gsioc_protocol(ser, 'GX-241 II', 30)
dim = gsioc_protocol(ser, 'GX D Inject', 3)

# To Do - implement code to check the modules are communicating properly

