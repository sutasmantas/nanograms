from typing import List
from PIL import Image, ImageDraw, ImageFont


def render_clue_grid(row_clues: List[List[int]], col_clues: List[List[int]], cell_size: int = 20) -> Image.Image:
    """Return an image visualizing the puzzle clues."""
    rows, cols = len(row_clues), len(col_clues)
    row_pad = max(len(c) for c in row_clues)
    col_pad = max(len(c) for c in col_clues)

    width = (row_pad + cols) * cell_size
    height = (col_pad + rows) * cell_size
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # Draw grid lines
    for i in range(rows + 1):
        y = (col_pad + i) * cell_size
        draw.line([(row_pad * cell_size, y), (width, y)], fill="gray")
    for j in range(cols + 1):
        x = (row_pad + j) * cell_size
        draw.line([(x, col_pad * cell_size), (x, height)], fill="gray")

    # Draw row clues
    for i, clues in enumerate(row_clues):
        for k, num in enumerate(reversed(clues)):
            x = (row_pad - 1 - k) * cell_size + 4
            y = (col_pad + i) * cell_size + 4
            draw.text((x, y), str(num), fill="black", font=font)

    # Draw column clues
    for j, clues in enumerate(col_clues):
        for k, num in enumerate(reversed(clues)):
            x = (row_pad + j) * cell_size + 4
            y = (col_pad - 1 - k) * cell_size + 4
            draw.text((x, y), str(num), fill="black", font=font)

    return img
