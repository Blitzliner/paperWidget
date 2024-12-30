from waveshare.epaper import EPaper, Handshake, RefreshAndUpdate, SetPallet, FillRectangle, SetCurrentDisplayRotation, SetEnFontSize
import time
import utils
from convert import get_shapes, SliceOptions, read_image

import struct

logger = utils.getLogger()

_cmd_buff = [0]*16
_cmd_buff[0] = 0xA5
_cmd_buff[1] = 0x00
_cmd_buff[2] = 0x11
_cmd_buff[3] = 0x24

_cmd_buff[12] = 0xCC
_cmd_buff[13] = 0x33
_cmd_buff[14] = 0xC3
_cmd_buff[15] = 0x3C

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
            bytes = struct.pack(">HHHH", rect[0], rect[1], rect[2], rect[3])
            for i, b in enumerate(bytes):
                _cmd_buff[4 + i] = b
            _verify = 0
            for d in _cmd_buff:
                _verify ^= d
                paper.serial.write(d)
            paper.serial.write(_verify)
            # paper.send(FillRectangle(x1=rect[0], y1=rect[1], x2=rect[2], y2=rect[3]))
            if idx % 1000 == 0:
                logger.info(f'Send {idx}/{len(rects)}')
        paper.send(RefreshAndUpdate())
        paper.read_responses()


if __name__ == '__main__':
    send('snapshot.png')
