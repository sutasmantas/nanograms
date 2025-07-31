"""Utilities to adapt puzzles until they have a unique solution."""

from typing import List, Tuple
from nonogram_clues import load_grid, extract_clues
from nonogram_solver import solve_nonogram

Grid = List[List[int]]


def grid_from_array(arr) -> Grid:
    return [[int(x) for x in row] for row in arr]


def adapt_grid_for_unique_solution(grid: Grid, max_attempts: int = 1000) -> Tuple[Grid, bool]:
    """Return a modified grid with a unique solution if possible."""
    import numpy as np
    import random

    grid = [row[:] for row in grid]
    attempt = 0
    while attempt < max_attempts:
        clues_row, clues_col = extract_clues(np.array(grid, dtype=np.uint8))
        solutions = solve_nonogram(clues_row, clues_col, max_solutions=2)
        if len(solutions) == 1:
            return grid, True
        if len(solutions) < 2:
            break

        sol_a, sol_b = solutions[0], solutions[1]

        # choose a solution that differs from the current grid so that a change
        # is actually made. if both differ, pick the one farther from the grid
        if sol_a == grid:
            target = sol_b
        elif sol_b == grid:
            target = sol_a
        else:
            diff_a = sum(sol_a[i][j] != grid[i][j] for i in range(len(grid)) for j in range(len(grid[0])))
            diff_b = sum(sol_b[i][j] != grid[i][j] for i in range(len(grid)) for j in range(len(grid[0])))
            target = sol_a if diff_a >= diff_b else sol_b

        diff_cells = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] != target[i][j]]
        if not diff_cells:
            break

        i, j = random.choice(diff_cells)
        grid[i][j] = target[i][j]
        attempt += 1
    return grid, False


if __name__ == "__main__":
    import argparse
    from PIL import Image
    import numpy as np

    parser = argparse.ArgumentParser(description="Adapt a puzzle for unique solubility")
    parser.add_argument("input", help="Path to preprocessed puzzle image")
    parser.add_argument("output", help="Path to save adapted image")
    parser.add_argument("--max-attempts", type=int, default=10)
    args = parser.parse_args()

    arr = load_grid(args.input)
    grid = grid_from_array(arr)
    grid, ok = adapt_grid_for_unique_solution(grid, max_attempts=args.max_attempts)
    out_arr = (1 - np.array(grid, dtype=np.uint8)) * 255
    Image.fromarray(out_arr).save(args.output)
    if ok:
        print("Puzzle adapted to unique solution")
    else:
        print("Failed to achieve unique solution")
