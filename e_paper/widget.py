import snapshot
import epaper
import periodic
import configparser
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s (%(name)s): %(message)s')
logger = logging.getLogger(__name__)

def update():
    cfg = _getActiveWidget()
    general, parameter = cfg['general'], cfg['parameter']
    image_path = "snapshot.png" # is used to temporary store a image
    base_address = general['app_base_address']
    
    snapshot.snap(base_address, parameter, 600, 800, image_path)
    epaper.send(image_path)
    
def _getActiveWidget():
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

def _get_refresh_cycle():
    refresh_cycle = 3600
    cfg = _getActiveWidget()
    
    if cfg is not None:
        refresh_cycle = int(cfg['general']['app_refresh_cycle'])
        logger.info(F'Run "{cfg["general"]["app_name"]}" every {refresh_cycle/3600}h')
        
    return refresh_cycle
    
def _main():
    refresh_cycle = _get_refresh_cycle()
    
    # call on start up
    update() 
    
    # todo: refresh cycle is only considered after a restart of the pi
    periodic.Periodic(refresh_cycle, update, autostart=True)
    
    
if __name__ == '__main__':
    #_main()
    update() 