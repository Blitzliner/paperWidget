from waveshare.epaper import EPaper, Handshake, RefreshAndUpdate, SetPallet, FillRectangle, SetCurrentDisplayRotation, SetEnFontSize
import time
import utils
from convert import get_shapes, SliceOptions, read_image

logger = utils.getLogger()


@utils.timing
def send(path):
    img = read_image(path=path, bit_depth=2)
    baudrate = 115200  # bits/s
    command_length = 17 * 8  # bits

    with EPaper() as paper:
        paper.send(Handshake())
        time.sleep(0.1)
        paper.send(SetCurrentDisplayRotation(SetCurrentDisplayRotation.FLIP))
        colors = {0: SetPallet.BLACK, 1: SetPallet.DARK_GRAY, 2: SetPallet.LIGHT_GRAY}  # , 3: SetPallet.WHITE}
        for value, color in colors.items():
            rects = get_shapes(img=img, slicer=SliceOptions.SLICE_RECTS_OPT_INLINE, value=value)
            logger.info(f'Image will take approx. {(command_length * len(rects)) / baudrate:.3f} s')
            # use of DARK_GRAY instead of BLACK for a more clear image
            paper.send(SetPallet(color, SetPallet.WHITE))
            # paper.read_responses(timeout=10)
            for idx, rect in enumerate(rects):
                paper.send(FillRectangle(x1=rect[0], y1=rect[1], x2=rect[2], y2=rect[3]))
                if idx % 1000 == 0:
                    logger.info(f'Send {idx}/{len(rects)}')
        paper.send(RefreshAndUpdate())  # does this take approx 8s?
        paper.read_responses()


if __name__ == '__main__':
    send('snapshot.png')
