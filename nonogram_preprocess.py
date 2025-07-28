import argparse
import numpy as np
from PIL import Image, ImageOps
import cv2


def load_and_resize(path, grid_width, grid_height, maintain_aspect=True, fill_color=255):
    """Load image and resize to grid dimensions."""
    img = Image.open(path)
    if maintain_aspect:
        img.thumbnail((grid_width, grid_height), Image.LANCZOS)
        background = Image.new('RGB', (grid_width, grid_height), (fill_color, fill_color, fill_color))
        offset = ((grid_width - img.width) // 2, (grid_height - img.height) // 2)
        background.paste(img, offset)
        img = background
    else:
        img = img.resize((grid_width, grid_height), Image.LANCZOS)
    return img


def binarize_image(img, method='threshold', threshold=128, block_size=11, C=2):
    """Binarize using different methods."""
    gray = ImageOps.grayscale(img)
    arr = np.array(gray)
    if method == 'threshold':
        _, binary = cv2.threshold(arr, threshold, 255, cv2.THRESH_BINARY)
    elif method == 'adaptive':
        binary = cv2.adaptiveThreshold(arr, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, block_size, C)
    elif method == 'otsu':
        _, binary = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method == 'canny':
        binary = cv2.Canny(arr, 100, 200)
    else:
        raise ValueError(f"Unknown method: {method}")
    return Image.fromarray(binary)


def post_process(img, erode_iters=0, dilate_iters=0):
    """Apply optional morphological operations."""
    arr = np.array(img)
    if erode_iters > 0:
        arr = cv2.erode(arr, None, iterations=erode_iters)
    if dilate_iters > 0:
        arr = cv2.dilate(arr, None, iterations=dilate_iters)
    return Image.fromarray(arr)


def parse_args():
    p = argparse.ArgumentParser(description="Preprocess image for nonogram generation")
    p.add_argument('input', help="Input image path")
    p.add_argument('output', help="Output image path")
    p.add_argument('--grid-size', type=int, default=25, help="Grid size, e.g. 25 for 25x25")
    p.add_argument('--grid-height', type=int, default=None, help="Grid height if not square")
    p.add_argument('--no-aspect', action='store_true', help="Ignore aspect ratio")
    p.add_argument('--method', choices=['threshold', 'adaptive', 'otsu', 'canny'], default='threshold')
    p.add_argument('--threshold', type=int, default=128, help="Fixed threshold value")
    p.add_argument('--block-size', type=int, default=11, help="Block size for adaptive threshold")
    p.add_argument('--C', type=int, default=2, help="Constant C for adaptive threshold")
    p.add_argument('--erode', type=int, default=0, help="Erosion iterations")
    p.add_argument('--dilate', type=int, default=0, help="Dilation iterations")
    return p.parse_args()


def main():
    args = parse_args()
    gh = args.grid_height or args.grid_size
    img = load_and_resize(args.input, args.grid_size, gh, maintain_aspect=not args.no_aspect)
    bin_img = binarize_image(img, method=args.method, threshold=args.threshold,
                             block_size=args.block_size, C=args.C)
    proc_img = post_process(bin_img, erode_iters=args.erode, dilate_iters=args.dilate)
    proc_img.save(args.output)


if __name__ == '__main__':
    main()
