import time
import RPi.GPIO as GPIO
from waveshare.epaper import EPaper
from waveshare.epaper import Handshake
from waveshare.epaper import RefreshAndUpdate
from waveshare.epaper import SetPallet
from waveshare.epaper import FillRectangle
from waveshare.epaper import SetCurrentDisplayRotation
from waveshare.epaper import SetEnFontSize
from waveshare.epaper import ClearScreen
import os.path
import numpy as np
from PIL import Image
import time
import logging.config
import os

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.ini'), disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def _read_image(path, max_width=800, max_height=600):
    logger.info("Slice image")
    lines = []
    if os.path.isfile(path):
        start_row_px = 0
        img = np.array(Image.open(path).convert('L').resize((max_width, max_height))).astype(np.uint8)
        bitmask = img > 128
        img[bitmask] = 1
        img[~bitmask] = 0
        logger.info(F"Slice Image with size {img.shape}")

        # iterate over all columns
        for col_idx in range(max_width):
            for row_idx in range(max_height):
                val = img[row_idx, col_idx]
                if not start_row_px and not val:  # start of line detected
                    start_row_px = row_idx
                if start_row_px and (val or (row_idx == (max_height - 1))):  # end of line detected
                    x1 = col_idx
                    y1 = start_row_px
                    x2 = x1
                    y2 = row_idx
                    lines.append([x1, y1, x2, y2])
                    start_row_px = 0
    if len(lines) > 40000:
        logger.warning(F"Image is too detailed. Detected ({len(lines)}) lines. Limit to 40000.")
        lines = lines[:40000]

    return lines


def send(path):
    start = time.time()
    lines = _read_image(path)
    logger.info(F"Send Image.. Split Image to {len(lines)} lines")

    with EPaper() as paper:
        paper.send(Handshake())
        time.sleep(2)
        paper.send(SetPallet(SetPallet.DARK_GRAY, SetPallet.WHITE))  # use of dark_gray for a more clear image
        paper.send(SetCurrentDisplayRotation(SetCurrentDisplayRotation.FLIP))
        paper.send(SetEnFontSize(SetEnFontSize.THIRTYTWO))
        paper.read_responses(timeout=10)

        for idx, line in enumerate(lines):
            paper.send(FillRectangle(*line))

        paper.send(RefreshAndUpdate())
        paper.read_responses()

        logger.info(F"Refreshing took {time.time() - start:.3} s")


if __name__ == '__main__':
    send("snapshot.png")
