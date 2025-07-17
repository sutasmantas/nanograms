from dataclasses import dataclass
import numpy as np
from PIL import Image
import argparse

@dataclass
class NonogramPuzzle:
    clues_row: list
    clues_col: list
    grid_shape: tuple


def load_grid(path: str) -> np.ndarray:
    """Load a preprocessed nonogram image and return a binary array."""
    img = Image.open(path).convert('L')
    arr = np.array(img)
    # In preprocessed images, black cells are 0 and white cells are 255
    return (arr == 0).astype(np.uint8)


def rle_line(line: np.ndarray) -> list:
    """Run-length encode a 1D binary array of a row or column."""
    clues = []
    count = 0
    for val in line:
        if val:
            count += 1
        else:
            if count > 0:
                clues.append(int(count))
                count = 0
    if count > 0:
        clues.append(int(count))
    if not clues:
        clues = [0]
    return clues


def extract_clues(grid: np.ndarray) -> tuple:
    """Return row and column clues for the given binary grid."""
    clues_row = [rle_line(row) for row in grid]
    clues_col = [rle_line(col) for col in grid.T]
    return clues_row, clues_col


def puzzle_from_image(path: str) -> NonogramPuzzle:
    grid = load_grid(path)
    clues_row, clues_col = extract_clues(grid)
    return NonogramPuzzle(clues_row=clues_row, clues_col=clues_col, grid_shape=grid.shape)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate nonogram clues from a binary image")
    parser.add_argument('input', help='Path to preprocessed image')
    args = parser.parse_args()

    puzzle = puzzle_from_image(args.input)
    print('Grid shape:', puzzle.grid_shape)
    print('Row clues:', puzzle.clues_row)
    print('Column clues:', puzzle.clues_col)


if __name__ == '__main__':
    main()
