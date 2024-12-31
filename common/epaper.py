from waveshare.epaper import EPaper, Handshake, RefreshAndUpdate, SetPallet, FillRectangle, SetCurrentDisplayRotation
import time
import utils
from convert import get_shapes, SliceOptions, read_image
from functools import reduce
import struct

logger = utils.getLogger()


def send(path):
    img = read_image(path=path, bit_depth=1)
    rects = get_shapes(img=img, slicer=SliceOptions.SLICE_LINES_OPT, value=1)
    send_to_epaper(rects=rects)


@utils.timing
def send_to_epaper(rects):
    baudrate = 460800  #460800, 230400 115200  # bits/s
    command_length = 17 * 8  # bits
    cost = (command_length * len(rects)) / baudrate
    logger.info(f'Image will take approx. {cost:.3f} s')
    # change baudrate
    from waveshare.epaper import SetBaudrate, ReadBaudrate
    default_braudrate = 115200
    with EPaper(baudrate=default_braudrate) as paper:
        paper.send(Handshake())
        time.sleep(0.1)
        paper.send(ReadBaudrate())
        logger.info(f'Current baudrate: {paper.read(6)}')
        paper.send(SetBaudrate(baudrate))
        time.sleep(10)
    with EPaper(baudrate=baudrate) as paper:
        paper.send(Handshake())
        time.sleep(0.1)
        paper.send(ReadBaudrate())
        logger.info(f'Current baudrate: {paper.read(6)}')
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
    # 0: frame header: b'\xa5'
    # 1-2: length: 1 + 2 + 1 + len(load) + 4 + 1 = 17 = b'\x11
    # 3: command: b'\x24'
    # 4-12: load:
    # 13-16: frame footer: b'\xcc\x33\xc3\x3c'
    load = struct.pack(">HHHH", rect[0], rect[1], rect[2], rect[3])
    command = bytearray(b'\xA5\x00\x11\x24' + load + b'\xcc\x33\xc3\x3c')
    verify = reduce(lambda x, y: x ^ y, command)
    command.append(verify)
    serial.write(command)
    serial.timeout = 1  # reduce timeout
    serial.read(2)
    #b = serial.read(2)
    #if b != b'OK':
    #    logger.info(b)


if __name__ == '__main__':
    # send('snapshot.png')
    _send_fast(None, (1, 1, 2, 2))
