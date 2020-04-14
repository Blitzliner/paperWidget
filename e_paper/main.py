from read_image import create_snapshot, image_processing
from send_image import send_image
from Periodic import Periodic
import configparser
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s (%(name)s): %(message)s')
logger = logging.getLogger(__name__)


def update(general, parameter):
    image_path = "snapshot.png" # is used to temporary store a image
    base_address = general['AppBaseAddress']
    create_snapshot(base_address, parameter, 600, 800, image_path)
    
    image_processing(image_path)
    
    send_image(image_path)
    

def getActiveWidget():
    cfg = configparser.ConfigParser()
    cfg.read('../apps/config.cfg')
    active_app = cfg['general'].get('ActiveApp', None)
    if active_app is not None:
        logger.info(F'App "{active_app}" selected')
        cfg.read(F'../apps/{active_app}/config.cfg')
        return cfg
    else:
        logger.error("No app selected")
    return None

def main():
    cfg = getActiveWidget()
    
    if cfg is not None:
        refresh_cycle = int(cfg['general']['AppRefreshCycle'])
        
        logger.info(F'Run "{cfg["general"]["AppName"]}" every {refresh_cycle/3600}h')
        
        update(cfg['general'], cfg['parameter']) # call on start up
        
        Periodic(refresh_cycle, update, autostart=True)
    
    
if __name__ == '__main__':
    main()