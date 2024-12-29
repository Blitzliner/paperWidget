from waveshare.epaper import EPaper, Handshake, RefreshAndUpdate, SetPallet, FillRectangle, SetCurrentDisplayRotation, SetEnFontSize
import time
import utils
from convert import get_shapes, SliceOptions

logger = utils.getLogger()


@utils.timing
def send(path):
    rects = get_shapes(path=path, slicer=SliceOptions.SLICE_RECTS_OPT, bit_depth=1)
    baudrate = 115200  # bits/s
    command_length = 17 * 8  # bits
    cost = (command_length * len(rects)) / baudrate
    logger.info(f'Image will take approx. {cost:.3f} s')

    with EPaper() as paper:
        paper.send(Handshake())
        time.sleep(2)
        paper.send(SetPallet(SetPallet.DARK_GRAY, SetPallet.WHITE))  # use of dark_gray for a more clear image
        paper.send(SetCurrentDisplayRotation(SetCurrentDisplayRotation.FLIP))
        paper.send(SetEnFontSize(SetEnFontSize.THIRTYTWO))
        paper.read_responses(timeout=10)

        for idx, rect in enumerate(rects):
            paper.send(FillRectangle(*rect))
            if idx % 1000 == 0:
                logger.info(f'Send {idx}/{len(rects)}')
        paper.send(RefreshAndUpdate())
        paper.read_responses()


if __name__ == '__main__':
    send('snapshot.png')
