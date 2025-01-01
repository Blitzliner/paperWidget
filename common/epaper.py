from waveshare.epaper import EPaper, Handshake, RefreshAndUpdate, SetPallet, FillRectangle, SetCurrentDisplayRotation, SetEnFontSize
import time
import utils
from convert import get_shapes, SliceOptions, read_image

logger = utils.getLogger()


@utils.timing
def send(path):
    img = read_image(path=path, bit_depth=1)
    rects = get_shapes(img=img, slicer=SliceOptions.SLICE_RECTS_OPT, value=1)  # _INLINE, value=1)
    baudrate = 115200  # bits/s
    command_length = 17 * 8  # bits
    cost = (command_length * len(rects)) / baudrate
    logger.info(f'Image will take approx. {cost:.3f} s')

    with EPaper() as paper:
        paper.send(Handshake())
        time.sleep(0.1)
        # use of DARK_GRAY instead of BLACK for a more clear image
        paper.send(SetPallet(SetPallet.DARK_GRAY, SetPallet.WHITE))
        paper.send(SetCurrentDisplayRotation(SetCurrentDisplayRotation.FLIP))
        paper.read_responses(timeout=10)

        for idx, rect in enumerate(rects):
            paper.send(FillRectangle(x1=rect[0], y1=rect[1], x2=rect[2], y2=rect[3]))
            if idx % 1000 == 0:
                logger.info(f'Send {idx}/{len(rects)}')
        paper.send(RefreshAndUpdate())  # does this take approx 8s?
        paper.read_responses()


if __name__ == '__main__':
    send('snapshot.png')
