import os.path
import numpy as np
from PIL import Image
import logging.config
import os
from utils import timing

logger = logging.getLogger()


class SliceOptions:
    SLICE_LINES = 'SLICE_LINES'
    SLICE_LINES_OPT = 'SLICE_LINES_OPT'
    SLICE_RECTS = 'SLICE_RECTS'
    SLICE_RECTS_OPT = 'SLICE_RECTS_OPT'
    SLICE_RECTS_OPT_INLINE = 'SLICE_RECTS_OPT_INLINE'


@timing
def read_image(path: str, target_width: int = 800, target_height: int = 600, bit_depth: int = 2, to_file: bool = False) -> np.ndarray:
    if bit_depth not in [1, 2]:
        raise ValueError(f'Bit depth must be 1 or 2 but values is {bit_depth}')
    if not os.path.isfile(path):
        raise ValueError(f'Path does not exist <{path}>')
    with Image.open(path) as img:
        # Calculate aspect ratios
        target_aspect = target_width / target_height
        original_aspect = img.width / img.height

        # Crop the image to match the target aspect ratio
        if original_aspect > target_aspect:  # Wider than target
            new_width = int(target_aspect * img.height)
            left = (img.width - new_width) // 2
            right = left + new_width
            img = img.crop((left, 0, right, img.height))
        elif original_aspect < target_aspect:  # Taller than target
            new_height = int(img.width / target_aspect)
            top = (img.height - new_height) // 2
            bottom = top + new_height
            img = img.crop((0, top, img.width, bottom))

        # Use an efficient filter (e.g., Image.Resampling.BOX or HAMMING)
        if not hasattr(Image, 'Resampling'):  # Pillow<9.0
            Image.Resampling = Image
        img = np.array(img.convert('L').resize((target_width, target_height), Image.Resampling.BOX))

    max_value = 2 ** bit_depth - 1
    img_scaled = (img / 255) * max_value
    img_quantized = np.round(img_scaled).astype(np.uint8)
    if to_file:
        img_rescaled = (img_quantized / max_value) * 255  # Scale back to [0, 255]
        Image.fromarray(img_rescaled.astype(np.uint8)).save('grayscale.png')
    return img_quantized


@timing
def get_shapes(img: np.ndarray, slicer: str, value: int = 1):
    logger.info(f'Slice Image with size {img.shape}')
    if slicer in [SliceOptions.SLICE_LINES_OPT, SliceOptions.SLICE_RECTS_OPT, SliceOptions.SLICE_RECTS_OPT_INLINE]:
        if isinstance(img, np.ndarray):
            img = img.tolist()
    if slicer == SliceOptions.SLICE_LINES:
        rects = _slice_image_to_lines(img)
    elif slicer == SliceOptions.SLICE_LINES_OPT:
        rects = _slice_image_to_lines_opt(img)
    elif slicer == SliceOptions.SLICE_RECTS:
        rects = _slice_image_to_rect(img, value=value)
    elif slicer == SliceOptions.SLICE_RECTS_OPT:
        rects = _slice_image_to_rect_opt(img, value=value)
    elif slicer == SliceOptions.SLICE_RECTS_OPT_INLINE:
        rects = _slice_image_to_rect_opt_inline(img, value=value)
    else:
        raise Exception(f'Slicer {slicer} not supported.')

    logger.info(f'Sliced Image into {len(rects)} rects')

    if len(rects) > 40000:
        logger.warning(F'Image is too detailed. Detected ({len(rects)}) lines. Limit to 40000.')
        rects = rects[:40000]
    return rects


@timing
def _slice_image_to_rect(matrix: np.ndarray, value: int):
    rows, cols = matrix.shape
    visited = np.zeros((rows, cols), dtype=np.bool_)  # Tracks visited cells; use bool_ from numpy for numba
    rectangles = []

    def explore_rectangle(row, col) -> tuple:
        # Expand downward
        row_e = row
        while row_e < rows and matrix[row_e, col] == value and not visited[row_e, col]:
            row_e += 1
        row_e -= 1

        # Expand rightward for all rows in the range
        col_e = col
        # do not check for visited in order to reduce rectangles
        while col_e < cols and np.all(
                matrix[row:row_e + 1, col_e] == value):  # and not np.any(visited[row:row_e + 1, col_e]):
            col_e += 1
        col_e -= 1

        # Mark all cells in the rectangle as visited
        visited[row:row_e + 1, col:col_e + 1] = True
        return row, col, row_e, col_e

    # Iterate over the matrix
    for r in range(rows):
        for c in range(cols):
            if not visited[r, c] and matrix[r, c] == value:
                rectangles.append(explore_rectangle(r, c))
    return rectangles


@timing
def _slice_image_to_lines(img: np.array):  # , max_width=800, max_height=600):
    lines = []
    max_height, max_width = img.shape
    end_of_line = max_height - 1

    for col_idx in range(max_width):
        start_row_px = None
        for row_idx in range(max_height):
            val = img[row_idx, col_idx]
            if start_row_px is not None and not val:  # start of line detected
                start_row_px = row_idx
            elif start_row_px is not None and (val or (row_idx == end_of_line)):  # end of line detected
                lines.append([col_idx, start_row_px, col_idx, row_idx])
                start_row_px = None
    return lines


@timing
def _slice_image_to_lines_opt(img: np.array):
    lines = []
    max_height, max_width = len(img), len(img[0])
    end_of_line = max_height - 1

    for col_idx in range(max_width):
        start_row_px = None
        for row_idx in range(max_height):
            val = img[row_idx][col_idx]
            if start_row_px is None and not val:  # start of line detected
                start_row_px = row_idx
            elif start_row_px is not None and (val or (row_idx == end_of_line)):  # end of line detected
                lines.append([col_idx, start_row_px, col_idx, row_idx])
                start_row_px = None
    return lines


@timing
def _slice_image_to_rect_opt(grid: list, value: int) -> list:
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    rectangles = []

    def explore_rectangle(row, col):
        # Expand downward
        row_e = row
        while row_e < rows and grid[row_e][col] == value and not visited[row_e][col]:
            visited[row_e][col] = True
            row_e += 1
        row_e -= 1

        # Expand rightward for all rows in the range
        col_e = col
        # do not check for visited in order to reduce rectangles
        while col_e < cols and all(grid[row_][col_e] == value for row_ in range(row, row_e + 1)):
            for row_ in range(row, row_e + 1):
                visited[row_][col_e] = True
            col_e += 1
        col_e -= 1

        rectangles.append((col, row, col_e, row_e))

    # Iterate over the matrix
    for r in range(rows):
        for c in range(cols):
            if not visited[r][c] and grid[r][c] == value:
                explore_rectangle(r, c)

    return rectangles


@timing
def _slice_image_to_rect_opt_inline(grid: list, value: int) -> list:
    rows, cols = len(grid), len(grid[0])
    rectangles = []

    def explore_rectangle(row, col):
        # Expand downward
        row_e = row
        while row_e < rows and grid[row_e][col] == value:
            grid[row_e][col] = 0  # reset pixel
            row_e += 1
        row_e -= 1

        # Expand rightward for all rows in the range
        col_e = col + 1
        # do not check for visited in order to reduce rectangles
        while col_e < cols and all(grid[row_][col_e] == value for row_ in range(row, row_e + 1)):
            for row_ in range(row, row_e + 1):
                grid[row_][col_e] = 0
            col_e += 1
        col_e -= 1

        rectangles.append((col, row, col_e, row_e))

    # Iterate over the matrix
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == value:
                explore_rectangle(r, c)

    return rectangles


if __name__ == '__main__':
    img = read_image(path='example.jpg', bit_depth=1)
    get_shapes(img=img, slicer=SliceOptions.SLICE_LINES)
    get_shapes(img=img, slicer=SliceOptions.SLICE_LINES_OPT)
    get_shapes(img=img, slicer=SliceOptions.SLICE_RECTS)
    get_shapes(img=img, slicer=SliceOptions.SLICE_RECTS_OPT)
    get_shapes(img=img, slicer=SliceOptions.SLICE_RECTS_OPT_INLINE)

    # import cProfile
    # cProfile.run("send('example.jpg')")  # 0.15 s
    # cProfile.run("send('example.jpg', func=_slice_image_to_rect)")  # 1.08 s
    # cProfile.run("send('example.jpg', func=_slice_image_to_rect_opt, bit_depth=2)")  # 0.43
