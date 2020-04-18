import snapshot
import sys
if not sys.platform.startswith('win'):
    import epaper
import configparser
import logging
import logging.config
import os
from datetime import datetime

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.ini'), disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def update(image_path=""):
    if len(image_path) > 0:
        logger.info("Update Display with image path")

        if not sys.platform.startswith('win'):
            epaper.send(image_path)
        else:
            logger.error("Sending to e-paper is yet not supported on Windows")
    else:
        logger.info("Update Display with snapshot of a website")
        cfg = _getActiveWidget()
        general, parameter = cfg['general'], cfg['parameter']
        image_path = os.path.join(os.path.dirname(__file__), "snapshot.png") # is used to temporary store a image
        base_address = general['app_base_address']

        snapshot.snap(base_address, parameter, 600, 800, image_path)
        if not sys.platform.startswith('win'):
            epaper.send(image_path)
        else:
            logger.error("Sending to e-paper is yet not supported on Windows")
        _update_timestamp()


def _update_timestamp():
    timestamp = datetime.timestamp(datetime.now())
    config_filepath = os.path.join(os.path.dirname(__file__), '../apps/config.cfg')
    cfg = configparser.ConfigParser()
    cfg.read(config_filepath)
    cfg['general']['last_execution'] = str(int(timestamp))
    with open(config_filepath, 'w') as file:
        cfg.write(file)


def _get_last_execution():
    config_filepath = os.path.join(os.path.dirname(__file__), '../apps/config.cfg')
    cfg = configparser.ConfigParser()
    cfg.read(config_filepath)
    timestamp = cfg['general'].get('last_execution', "")

    if len(timestamp) == 0:
        timestamp = int(0)
    else:
        timestamp = int(timestamp)

    return timestamp


def _getActiveWidget():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(os.path.dirname(__file__), '../apps/config.cfg'))
    active_app = cfg['general'].get('ActiveApp', None)
    if active_app is not None:
        logger.info(F'App "{active_app}" selected')
        cfg.read(os.path.join(os.path.dirname(__file__), F'../apps/{active_app}/config.cfg'))
        return cfg
    else:
        logger.error("No app selected")
    return None


def _get_refresh_cycle():
    refresh_cycle = int(1)
    cfg = _getActiveWidget()

    if cfg is not None:
        refresh_cycle = int(cfg['general']['app_refresh_cycle'])
        logger.info(F'Run "{cfg["general"]["app_name"]}" every {refresh_cycle}h')

    return refresh_cycle


def _main():
    cycle = _get_refresh_cycle()*3600
    last_run = _get_last_execution()
    current = int(datetime.timestamp(datetime.now()))
    logger.info(F"Run every {cycle}s, Last run was {current - last_run}s ago")

    if ((current - last_run + 100) > cycle):  # add 100s for stability reason
        update()
    else:
        logger.info("Skip update nothing to do")



if __name__ == '__main__':
    _main()
