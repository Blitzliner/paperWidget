import os.path
import numpy as np
from PIL import Image
import logging.config
import os
from utils import timing

logger = logging.getLogger()


class SliceOptions:
    SLICE_LINES = 'SLICE_LINES'
    SLICE_RECTS = 'SLICE_RECTS'
    SLICE_RECTS_OPT = 'SLICE_RECTS_OPT'


@timing
def get_shapes(path: str, slicer: str, bit_depth=1):
    img = _read_image(path=path, bit_depth=bit_depth)
    if slicer == SliceOptions.SLICE_LINES:
        rects = _slice_image_to_lines(img)
    elif slicer == SliceOptions.SLICE_RECTS:
        rects = _slice_image_to_rect(img, value=1)
    elif slicer == SliceOptions.SLICE_RECTS_OPT:
        rects = _slice_image_to_rect_opt(img, value=1)
    else:
        raise Exception(f'Slicer {slicer} not supported.')

    logger.info(f'Sliced Image into {len(rects)} rects')
    return rects


@timing
def _slice_image_to_rect(matrix: np.ndarray, value: int):
    rows, cols = matrix.shape
    visited = np.zeros((rows, cols), dtype=bool)  # Tracks visited cells
    rectangles = []

    def explore_rectangle(row, col) -> Rect:
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

        return (row, col, row_e, col_e)

    # Iterate over the matrix
    for r in range(rows):
        for c in range(cols):
            if not visited[r, c] and matrix[r, c] == value:
                rectangles.append(explore_rectangle(r, c))

    if len(rectangles) > 40000:
        logger.warning(F"Image is too detailed. Detected ({len(rectangles)}) lines. Limit to 40000.")
        rectangles = rectangles[:40000]

    return rectangles


@timing
def _read_image(path: str, max_width: int = 800, max_height: int = 600, bit_depth: int = 2,
                to_file: bool = True) -> np.array:
    if bit_depth not in [1, 2]:
        raise ValueError(f'Bit depth must be 1 or 2 but values is {bit_depth}')
    if not os.path.isfile(path):
        raise ValueError(f'Path does not exist <{path}>')
    img = np.array(Image.open(path).convert('L').resize((max_width, max_height)))

    max_value = 2 ** bit_depth - 1
    img_scaled = (img / 255) * max_value
    img_quantized = np.round(img_scaled).astype(np.uint8)
    if to_file:
        img_rescaled = (img_quantized / max_value) * 255  # Scale back to [0, 255]
        Image.fromarray(img_rescaled.astype(np.uint8)).save('grayscale.png')
    return img_quantized


@timing
def _slice_image_to_lines(img: np.array):  # , max_width=800, max_height=600):
    logger.info("Slice image")
    lines = []
    start_row_px = 0
    logger.info(F"Slice Image with size {img.shape}")
    max_height, max_width = img.shape
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


@timing
def _slice_image_to_rect_opt(grid: list, value: int) -> list:
    if isinstance(grid, np.ndarray):
        grid = grid.tolist()
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

        rectangles.append((row, col, row_e, col_e))

    # Iterate over the matrix
    for r in range(rows):
        for c in range(cols):
            if not visited[r][c] and grid[r][c] == value:
                explore_rectangle(r, c)

    return rectangles


if __name__ == '__main__':
    import cProfile

    get_shapes('example.jpg', slicer=SliceOptions.SLICE_LINES)
    get_shapes('example.jpg', slicer=SliceOptions.SLICE_RECTS)
    get_shapes('example.jpg', slicer=SliceOptions.SLICE_RECTS_OPT)
    get_shapes('example.jpg', slicer=SliceOptions.SLICE_RECTS_OPT, bit_depth=2)
    #cProfile.run("send('example.jpg')")  # 0.15 s
    # cProfile.run("send('example.jpg', func=_slice_image_to_rect)")  # 1.08 s
    # cProfile.run("send('example.jpg', func=_slice_image_to_rect_opt, bit_depth=2)")  # 0.43
