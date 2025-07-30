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

    attempt = 0
    while attempt < max_attempts:
        clues_row, clues_col = extract_clues(np.array(grid, dtype=np.uint8))
        solutions = solve_nonogram(clues_row, clues_col, max_solutions=2)
        if len(solutions) == 1:
            return grid, True
        if len(solutions) == 0:
            # no solution, revert last change by continuing with attempt++ to break
            break
        # more than one solution - find a differing cell between first two
        sol_a, sol_b = solutions[0], solutions[1]
        diff = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if sol_a[i][j] != sol_b[i][j]]
        if not diff:
            break
        i, j = diff[0]
        grid[i][j] = sol_a[i][j]
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
