from gilson import *
from hb_elite_pump.hb_elite import *
from platform_setup_new import *
import time
import serial

def pickup_from_vial(hbpump, g, vial, tvolume, wrate):
    #converting floats to strings 
    tvolume_str = str(tvolume)
    wrate_str = str(wrate)

    #setting withdrawal rate
    hbpump.set_wrate(f'{wrate_str} uL/min')

    #clearing syrpump vol and tvol
    hbpump.clear_volume()

    #connect to liquid handler
    g.connect()

    #if not a value and is instead 'solvent', will use go_to_solvent function
    if isinstance(vial,str) and vial.lower() == "solvent":
        g.go_to_solvent()

    else:
        g.go_to_vial(vial)

    #set tvolume
    hbpump.set_tvolume(f'{tvolume_str} uL')
    
    #withdrawal
    hbpump.withdraw()
    time.sleep(60 * (tvolume / wrate))
    hbpump.stop()
    
    #go up
    g.bCommand('Z125')

def dispense_in_dim(hbpump, g, g_dim, tvolume, irate):
    g_dim.connect()
    g_dim.bCommand('VL')
    tvolume_str = str(tvolume)
    irate_str = str(irate)
    hbpump.set_irate(f'{irate_str} uL/min')
    hbpump.clear_volume()
    g.connect()
    g.go_to_dim()
    hbpump.set_tvolume(f'{tvolume_str} uL')
    hbpump.infuse()
    time.sleep(60 * (tvolume / irate))
    hbpump.stop()
    g.go_to_home()
    g_dim.connect()
    g_dim.bCommand('VI')

def take_air_gap(hbpump, g, tvolume, wrate=None):
    if wrate is None:
        wrate = 500
    
    #converting floats to strings 
    tvolume_str = str(tvolume)
    wrate_str = str(wrate)

    #setting withdrawal rate
    hbpump.set_wrate(f'{wrate_str} uL/min')

    #clearing syrpump vol and tvol
    hbpump.clear_volume()

    #connect to liquid handler
    g.connect()

    #go up
    g.bCommand('Z125')

    #set tvolume
    hbpump.set_tvolume(f'{tvolume_str} uL')
    
    #withdrawal
    hbpump.withdraw()
    time.sleep(60 * (tvolume / wrate))
    hbpump.stop()
    