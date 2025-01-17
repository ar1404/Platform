import time
from loguru import logger
import run_syrringe_pump
import asyncio

def dim_load(gsioc_protocol_object, testing_active: bool = False):
    """Switches Direct Injection Module (DIM) to Load position. Queries the switching position for assuring success.

    :expects: Global variable TESTING_ACTIVE.
    :param gsioc_protocol_object: GSIOC Instance for commands to DIM.
    """
    gsioc_protocol_object.connect()
    time.sleep(5)
    gsioc_protocol_object.bCommand('VL')
    resp=gsioc_protocol_object.iCommand('X')
    while resp=='R':
        time.sleep(1)
        resp=gsioc_protocol_object.iCommand('X')
        pass
    if resp=='L':
        return True        
    else:
        if testing_active == True:
            return True
        else:
            error=gsioc_protocol_object.iCommand('e')
            logger.debug(f'the direct injection module returned the following error: {error}')
            return False


def dim_inject(gsioc_protocol_object, testing_active: bool = False):
    """Switches Direct Injection Module (DIM) to Inject position. Queries the switching position for assuring success.

    :expects: Global variable TESTING_ACTIVE.
    :param gsioc_protocol_object: GSIOC Instance for commands to DIM.
    """
    gsioc_protocol_object.connect()
    time.sleep(5)
    gsioc_protocol_object.bCommand('VI')
    resp=gsioc_protocol_object.iCommand('X')
    while resp=='R':
        time.sleep(1)
        resp=gsioc_protocol_object.iCommand('X')
        pass
    if resp=='I':
        return True
    else:
        if testing_active == True:
            return True
        else:
            error=gsioc_protocol_object.iCommand('e')
            logger.debug(f'the direct injection module returned the following error: {error}')
            return False
