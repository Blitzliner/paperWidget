import time
import RPi.GPIO as GPIO
from waveshare.epaper import EPaper
from waveshare.epaper import Handshake
from waveshare.epaper import RefreshAndUpdate
from waveshare.epaper import SetPallet
from waveshare.epaper import FillRectangle
from waveshare.epaper import DisplayText
from waveshare.epaper import SetCurrentDisplayRotation
from waveshare.epaper import SetEnFontSize
from waveshare.epaper import ClearScreen
import os.path
import numpy as np
from PIL import Image
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s (%(name)s): %(message)s')
logger = logging.getLogger(__name__)

def _read_image(path):
    logger.info("Slice image")
    lines = []
    if os.path.isfile(path):
        start_row_px = 0
        img = np.array(Image.open(path).convert('L').resize((800, 600))).astype(np.uint8)
        bitmask = img>128
        img[bitmask] = 1
        img[~bitmask] = 0

        #if len(img[0,0]) == 3:
        #    logger.error("wrong image format it has to be grayscale")
        # iterate over all columns
        for col_idx in range(img.shape[1]):
            #col = img[:,col_idx]
            for row_idx in range(img.shape[0]):
                val = img[row_idx, col_idx]
                if not start_row_px and not val: # start of line detected
                    start_row_px = row_idx + 1
                if start_row_px and val: # end of line detected
                    x1 = col_idx+1
                    y1 = start_row_px
                    x2 = x1
                    y2 = row_idx+1
                    lines.append([x1,y1,x2,y2])
                    start_row_px = 0
    return lines
                                     

def send(path):
    logger.info("Send Image to E-Paper..")
    start = time.time()
    
    lines = _read_image(path)
        
    with EPaper() as paper:
        paper.send(Handshake())
        time.sleep(2)
        paper.send(SetPallet(SetPallet.DARK_GRAY, SetPallet.WHITE)) #use of dark_gray for a more clear image
        paper.send(SetCurrentDisplayRotation(SetCurrentDisplayRotation.FLIP))
        paper.send(SetEnFontSize(SetEnFontSize.THIRTYTWO))
        paper.read_responses(timeout=10)
    
        for line in lines:
            paper.send(FillRectangle(*line))
            
        paper.send(RefreshAndUpdate())
        paper.read_responses()

        logger.info(F"Refreshing took {time.time() - start:.3} s")


if __name__ == '__main__':
    send("snapshot.png")
