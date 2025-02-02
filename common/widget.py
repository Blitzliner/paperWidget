import snapshot
import sys
if not sys.platform.startswith('win'):
    import epaper
from config import config
import logging.config
import os
from datetime import datetime

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.ini'), disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def update(image_path=""):
    if len(image_path) > 0:
        logger.info("Update Display with image path")

        if not sys.platform.startswith('win'):
            epaper.send(image_path, bit_depth=2)
        else:
            logger.error("Sending to e-paper is yet not supported on Windows")
    else:
        logger.info("Update Display with snapshot of a website")
        app = config.get_app(config.active_app)
        if app:
            image_path = os.path.join(os.path.dirname(__file__), "snapshot.png") # is used to temporary store a image
            snapshot.snap(app.address, app.parameter, 600, 800, image_path)
            if not sys.platform.startswith('win'):
                epaper.send(image_path, bit_depth=1)
            else:
                logger.error("Sending to e-paper is yet not supported on Windows")

            timestamp = datetime.timestamp(datetime.now())
            config.last_execution = str(int(timestamp))
        else:
            logger.error("No valid App selected")


def _main():
    app = config.get_app(config.active_app)
    cycle = int(app.frequency)*3600
    last_run = int(config.last_execution + " ")  # for safety convert empty string to int
    current = int(datetime.timestamp(datetime.now()))
    logger.info(F"Run every {cycle}s, Last run was {current - last_run}s ago")

    if (current - last_run + 100) > cycle:  # add 100s for stability reason
        update()
    else:
        logger.info("Skip update nothing to do")


if __name__ == '__main__':
    _main()
