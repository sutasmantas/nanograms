"""Rendering utilities for nonogram clue grids.

`render_clue_grid` can optionally embed a preview of the puzzle image
in the top-left corner beneath the dimensions label.
"""

from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling


def render_clue_grid(
    row_clues: List[List[int]],
    col_clues: List[List[int]],
    cell_size: int = 20,
    image_path: Optional[str] = None,
) -> Image.Image:
    """Return an image visualizing the puzzle clues with nicer styling."""
    rows, cols = len(row_clues), len(col_clues)
    row_pad = max(len(c) for c in row_clues)
    col_pad = max(len(c) for c in col_clues)

    grid_width = (row_pad + cols) * cell_size
    grid_height = (col_pad + rows) * cell_size
    pad = cell_size // 2  # extra space on bottom/right

    img = Image.new("RGB", (grid_width + pad, grid_height + pad), "lavenderblush")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # Dimensions label in the top-left corner
    draw.text((4, 4), f"{rows}x{cols}", fill="darkblue", font=font)

    bbox = draw.textbbox((0, 0), "A", font=font)
    preview_y = bbox[3] + 6
    if image_path:
        try:
            preview = Image.open(image_path).convert("RGB")
            max_w = row_pad * cell_size
            max_h = col_pad * cell_size - preview_y - 4
            if max_w > 5 and max_h > 5:
                preview.thumbnail((max_w, max_h), Resampling.NEAREST)
                img.paste(preview, (4, preview_y))
        except Exception as e:
            print(f"Failed to load image preview from {image_path}: {e}")

    def choose_color(idx: int, max_idx: int) -> str:
        if idx == max_idx // 2:
            return "mediumorchid"
        if idx % 5 == 0:
            return "darkviolet"
        if idx % 2 == 0:
            return "pink"
        return "gray"

    # Draw grid lines with alternating colors
    for i in range(rows + 1):
        y = (col_pad + i) * cell_size
        draw.line(
            [(row_pad * cell_size, y), (grid_width, y)],
            fill=choose_color(i, rows),
        )
    for j in range(cols + 1):
        x = (row_pad + j) * cell_size
        draw.line(
            [(x, col_pad * cell_size), (x, grid_height)],
            fill=choose_color(j, cols),
        )

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
