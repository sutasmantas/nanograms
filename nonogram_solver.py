"""Nonogram solver using constraint propagation and backtracking."""

from typing import List, Optional


Grid = List[List[int]]  # 0/1 values


def line_possibilities(length: int, clues: List[int]) -> List[List[int]]:
    """Generate all binary lines of given length that satisfy clues."""
    if clues == [0]:
        return [[0] * length]
    results: List[List[int]] = []

    def helper(idx: int, clue_idx: int, line: List[int]):
        if clue_idx == len(clues):
            # fill rest with zeros
            results.append(line + [0] * (length - idx))
            return
        run = clues[clue_idx]
        max_start = length - run
        while idx <= max_start:
            new_line = line + [0] * (idx - len(line)) + [1] * run
            next_idx = idx + run
            if next_idx < length:
                new_line.append(0)
                helper(next_idx + 1, clue_idx + 1, new_line)
            else:
                helper(next_idx, clue_idx + 1, new_line)
            idx += 1

    helper(0, 0, [])
    return results


def propagate(grid: Grid, row_poss: List[List[List[int]]], col_poss: List[List[List[int]]]) -> bool:
    changed = True
    h, w = len(grid), len(grid[0])
    while changed:
        changed = False
        # filter row possibilities based on current grid
        for i in range(h):
            new_poss = [p for p in row_poss[i] if all(grid[i][j] == -1 or grid[i][j] == p[j] for j in range(w))]
            if not new_poss:
                return False
            row_poss[i] = new_poss
            for j in range(w):
                vals = {p[j] for p in new_poss}
                if len(vals) == 1 and grid[i][j] == -1:
                    grid[i][j] = vals.pop()
                    changed = True
        # filter column possibilities
        for j in range(w):
            new_poss = [p for p in col_poss[j] if all(grid[i][j] == -1 or grid[i][j] == p[i] for i in range(h))]
            if not new_poss:
                return False
            col_poss[j] = new_poss
            for i in range(h):
                vals = {p[i] for p in new_poss}
                if len(vals) == 1 and grid[i][j] == -1:
                    grid[i][j] = vals.pop()
                    changed = True
    return True


def solve_nonogram(clues_row: List[List[int]], clues_col: List[List[int]], max_solutions: int = 2) -> List[Grid]:
    """Return up to max_solutions solutions for the puzzle."""
    h, w = len(clues_row), len(clues_col)
    row_poss = [line_possibilities(w, clue) for clue in clues_row]
    col_poss = [line_possibilities(h, clue) for clue in clues_col]
    grid: Grid = [[-1 for _ in range(w)] for _ in range(h)]  # -1 unknown
    solutions: List[Grid] = []

    def backtrack() -> None:
        if len(solutions) >= max_solutions:
            return
        if not propagate(grid, row_poss, col_poss):
            return
        # check if solved
        if all(all(cell != -1 for cell in row) for row in grid):
            solutions.append([row[:] for row in grid])
            return
        # choose row with minimal possibilities >1
        candidate_rows = [(i, len(row_poss[i])) for i in range(h) if len(row_poss[i]) > 1]
        candidate_cols = [(j, len(col_poss[j])) for j in range(w) if len(col_poss[j]) > 1]
        if candidate_rows:
            i = min(candidate_rows, key=lambda x: x[1])[0]
            poss = row_poss[i][:]
            for pattern in poss:
                backup_grid = [r[:] for r in grid]
                backup_row = row_poss[i][:]
                row_poss[i] = [pattern]
                grid[i] = pattern[:]
                backtrack()
                row_poss[i] = backup_row
                grid[i] = backup_grid[i]
                if len(solutions) >= max_solutions:
                    return
        elif candidate_cols:
            j = min(candidate_cols, key=lambda x: x[1])[0]
            poss = col_poss[j][:]
            for pattern in poss:
                backup_grid = [r[:] for r in grid]
                backup_col = col_poss[j][:]
                for k in range(h):
                    grid[k][j] = pattern[k]
                col_poss[j] = [pattern]
                backtrack()
                for k in range(h):
                    grid[k][j] = backup_grid[k][j]
                col_poss[j] = backup_col
                if len(solutions) >= max_solutions:
                    return

    backtrack()
    return solutions
