import os
import glob
import shutil
import subprocess
from pathlib import Path
from typing import List

import numpy as np
from PIL import Image

from nonogram_clues import load_grid, extract_clues, puzzle_from_image
from nonogram_solver import solve_nonogram
from adapt_puzzle import grid_from_array, adapt_grid_for_unique_solution
from clue_grid import render_clue_grid


def validate_or_adapt(puzzle_path: str) -> bool:
    """Return True if the puzzle has a unique solution, adapting if necessary."""
    arr = load_grid(puzzle_path)
    clues_row, clues_col = extract_clues(arr)
    solutions = solve_nonogram(clues_row, clues_col, max_solutions=2)
    if len(solutions) == 1:
        return True
    else:
        print(f"Puzzle at {puzzle_path} has {len(solutions)} solutions, adapting...")

    grid = grid_from_array(arr)
    grid, ok = adapt_grid_for_unique_solution(grid)
    if ok:
        Image.fromarray((1 - np.array(grid, dtype=np.uint8)) * 255).save(puzzle_path)
    return ok


def batch_process_images() -> None:
    """Process all images in the 'potential' folder."""
    potential_folder = "potential"
    output_root = Path("output")
    output_root.mkdir(exist_ok=True)
    bad_log = open("bad_logging.txt", "a")

    if not os.path.exists(potential_folder):
        print(f"Folder '{potential_folder}' not found!")
        return

    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
    image_files: List[str] = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(potential_folder, ext)))
        image_files.extend(glob.glob(os.path.join(potential_folder, ext.upper())))

    if not image_files:
        print(f"No image files found in '{potential_folder}' folder!")
        return

    methods = [
        # {"name": "threshold", "args": ["--method", "threshold", "--threshold", "128"]}, # TODO MAYBE ADD LATER
        {"name": "adaptive", "args": ["--method", "adaptive", "--block-size", "15", "--C", "3"]},
    ]
    grid_sizes = [50]

    print(f"Found {len(image_files)} images to process")

    for idx, image_path in enumerate(image_files):
        print(f"\nProcessing image {idx + 1}/{len(image_files)}: {os.path.basename(image_path)}")

        base_name = Path(image_path).stem
        output_folder = output_root / base_name
        output_folder.mkdir(exist_ok=True)
        shutil.copy(image_path, output_folder / Path(image_path).name)

        for grid_size in grid_sizes:
            for method in methods:
                method_name = method["name"]
                method_args = method["args"]

                output_file = output_folder / f"{method_name}_grid{grid_size}.png"

                cmd = [
                    "python",
                    "nonogram_preprocess.py",
                    image_path,
                    str(output_file),
                    "--grid-size",
                    str(grid_size),
                ] + method_args

                try:
                    print(f"  Creating {method_name} (grid {grid_size})...")
                    subprocess.run(cmd, check=True, capture_output=True)
                    if validate_or_adapt(str(output_file)):
                        print(f"    Valid puzzle created: {output_file}")
                        puzzle = puzzle_from_image(str(output_file))
                        print("   Puzzle made")
                        clue_img = render_clue_grid(
                            puzzle.clues_row,
                            puzzle.clues_col,
                            image_path=str(image_path),
                        )
                        clue_path = output_folder / f"{method_name}_grid{grid_size}_clues.png"
                        clue_img.save(clue_path)
                    else:
                        output_file.unlink(missing_ok=True)
                        bad_log.write(f"{image_path} - {method_name} grid{grid_size} invalid\n")
                        print("    Invalid puzzle, logged.")
                except subprocess.CalledProcessError as e:
                    print(f"    Error processing {method_name}: {e}")
                except Exception as e:
                    print(f"    Unexpected error: {e}")

        print(f"  Completed image {idx + 1} -> folder '{output_folder}'")

    print("\nBatch processing complete! Check the 'output' folder.")
    bad_log.close()


if __name__ == "__main__":

    batch_process_images()

