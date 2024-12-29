from functools import wraps
from time import time
import logging
import socket
import os
import logging.config


#logging.basicConfig(
#    level=logging.INFO,
#    format="%(asctime)s [%(levelname)s] %(message)s",
#    handlers=[
#        logging.FileHandler("debug.log"),
#        logging.StreamHandler()
#    ]
#)
#logger = logging.getLogger()

__logger = None


def getLogger():
    global __logger
    if __logger:
        return __logger
    else:
        logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.ini'), disable_existing_loggers=False)
        __logger = logging.getLogger(__name__)
        return __logger


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        getLogger().info(f'<{f.__name__}> took: {te-ts:2.4f} sec')
        return result
    return wrap


def get_network_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 12345))  # 12345 is random port. 0 fails on Mac.
    return s.getsockname()[0]
