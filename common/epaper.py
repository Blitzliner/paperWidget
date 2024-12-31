from waveshare.epaper import EPaper, Handshake, RefreshAndUpdate, SetPallet, FillRectangle, SetCurrentDisplayRotation, \
    SetEnFontSize
import time
import utils
from convert import get_shapes, SliceOptions, read_image

import struct

logger = utils.getLogger()


def send(path):
    img = read_image(path=path, bit_depth=1)
    rects = get_shapes(img=img, slicer=SliceOptions.SLICE_LINES_OPT, value=1)
    send_to_epaper(rects=rects)


@utils.timing
def send_to_epaper(rects):
    baudrate = 115200  # bits/s
    command_length = 17 * 8  # bits
    cost = (command_length * len(rects)) / baudrate
    logger.info(f'Image will take approx. {cost:.3f} s')

    with EPaper() as paper:
        paper.send(Handshake())
        time.sleep(0.1)
        paper.send(SetPallet(SetPallet.BLACK, SetPallet.WHITE))  # use of dark_gray for a more clear image, DARK_GRAY
        paper.send(SetCurrentDisplayRotation(SetCurrentDisplayRotation.FLIP))
        paper.read_responses(timeout=10)

        for idx, rect in enumerate(rects):
            _send_fast(paper.serial, rect)
            # paper.send(FillRectangle(x1=rect[0], y1=rect[1], x2=rect[2], y2=rect[3]))
            if idx % 1000 == 0:
                logger.info(f'Send {idx}/{len(rects)}')
        paper.send(RefreshAndUpdate())
        paper.read_responses()


def _send_fast(serial, rect):
    load = struct.pack(">HHHH", rect[0], rect[1], rect[2], rect[3])
    _verify = 0
    command = b'\xA5\x00\x11\x24' + load + b'\xA5\x00\x11\x24'
    for d in command:
        _verify ^= d
    command += _verify.to_bytes(1, byteorder='big')
    serial.write(command)
    serial.timeout = 3
    b = serial.read(2)
    logger.info(b)


if __name__ == '__main__':
    # send('snapshot.png')
    _send_fast((1, 1, 2, 2))
