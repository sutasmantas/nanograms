# Nanograms

Utilities for generating nonogram puzzles.

## Phase 1: Image Preprocessing

`nonogram_preprocess.py` converts an input image into a black-and-white grid suitable for generating clues.

### Usage

```bash
python3 nonogram_preprocess.py input.jpg output.png --grid-size 25 --method adaptive --block-size 100 --C 3
```

Key options:

- `--grid-size` / `--grid-height` control the resolution of the output grid.
- `--no-aspect` ignores aspect ratio; otherwise the image is padded.
- `--method` chooses the binarization technique: `threshold`, `adaptive`, `otsu`, or `canny`.
- `--threshold` fixed threshold value for the `threshold` method.
- `--block-size` and `--C` tune adaptive thresholding.
- `--erode` and `--dilate` apply morphological operations to clean up the result.
```

Install dependencies using:

```bash
pip install -r requirements.txt
```

## Phase 2: Clue Generation

`nonogram_clues.py` extracts the numerical clues for each row and column from a
preprocessed grid. It runs run-length encoding on the rows and columns where a
filled cell is represented by `1` (black) and blank cells are `0`.

Example:

```
[0, 1, 1, 0, 1, 1, 1] -> [2, 3]
```

### Usage

```bash
python3 nonogram_clues.py output.png
```

This prints the grid dimensions along with `Row clues` and `Column clues` lists.
The output can also be used programmatically via the `puzzle_from_image`
function which returns a `NonogramPuzzle` object containing:

- `clues_row`: list of row clue lists
- `clues_col`: list of column clue lists
- `grid_shape`: `(height, width)` tuple

