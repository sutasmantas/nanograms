# Nanograms

Utilities for generating nonogram puzzles.

## Phase 1: Image Preprocessing

`nonogram_preprocess.py` converts an input image into a black-and-white grid suitable for generating clues.

### Usage

```bash
python3 nonogram_preprocess.py input.jpg output.png --grid-size 25 \
    --method adaptive --block-size 15 --C 3
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
