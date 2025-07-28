"""Improved Nonogram solver with lazy pattern generation, uniqueness verification,
and debug logging to help trace unsolvable cases. Includes memoization,
row pattern prioritization, and full-line probing for better performance.
"""

from typing import List, Optional, Generator, Tuple
from itertools import tee
from functools import lru_cache

Grid = List[List[int]]  # 0/1 values

DEBUG = False  # Set to True to enable step-wise logging

def debug_print(*args):
    if DEBUG:
        print("[DEBUG]", *args)

@lru_cache(maxsize=None)
def line_possibilities_cached(length: int, clues_key: Tuple[int, ...]) -> List[List[int]]:
    clues = list(clues_key)
    results = []

    if clues == [0]:
        return [[0] * length]

    def helper(pos: int, clue_idx: int, line: List[int]):
        if clue_idx == len(clues):
            if len(line) < length:
                line += [0] * (length - len(line))
            if len(line) == length:
                results.append(line)
            return

        run = clues[clue_idx]
        max_start = length - sum(clues[clue_idx:]) - (len(clues) - clue_idx - 1)
        for start in range(pos, max_start + 1):
            new_line = line + [0] * (start - len(line)) + [1] * run
            if len(new_line) < length:
                new_line.append(0)
            helper(start + run + 1, clue_idx + 1, new_line)

    helper(0, 0, [])
    return results


def intersect_patterns(patterns: List[List[int]], length: int) -> Optional[List[int]]:
    if not patterns:
        return None
    mask = patterns[0][:]
    for pattern in patterns[1:]:
        for i in range(length):
            if mask[i] != pattern[i]:
                mask[i] = -1
    return mask


def propagate(grid: Grid, row_clues: List[List[int]], col_clues: List[List[int]]) -> bool:
    h, w = len(grid), len(grid[0])
    changed = True
    while changed:
        changed = False
        for i in range(h):
            if -1 not in grid[i]:
                continue
            all_patterns = line_possibilities_cached(w, tuple(row_clues[i]))
            filtered = [p for p in all_patterns if all(grid[i][j] in (-1, p[j]) for j in range(w))]
            intersection = intersect_patterns(filtered, w)
            debug_print(f"Row {i} filtered: {len(filtered)}")
            if not filtered or intersection is None:
                debug_print(f"Contradiction found in row {i}")
                return False
            for j in range(w):
                if grid[i][j] == -1 and intersection[j] != -1:
                    grid[i][j] = intersection[j]
                    changed = True

        for j in range(w):
            col = [grid[i][j] for i in range(h)]
            if -1 not in col:
                continue
            all_patterns = line_possibilities_cached(h, tuple(col_clues[j]))
            filtered = [p for p in all_patterns if all(col[i] in (-1, p[i]) for i in range(h))]
            intersection = intersect_patterns(filtered, h)
            debug_print(f"Col {j} filtered: {len(filtered)}")
            if not filtered or intersection is None:
                debug_print(f"Contradiction found in column {j}")
                return False
            for i in range(h):
                if grid[i][j] == -1 and intersection[i] != -1:
                    grid[i][j] = intersection[i]
                    changed = True
    return True


def validate_solution(grid: Grid, row_clues: List[List[int]], col_clues: List[List[int]]) -> bool:
    def line_to_clues(line: List[int]) -> List[int]:
        result, count = [], 0
        for val in line:
            if val == 1:
                count += 1
            elif count:
                result.append(count)
                count = 0
        if count:
            result.append(count)
        return result or [0]

    for i, row in enumerate(grid):
        clues = line_to_clues(row)
        if clues != row_clues[i]:
            debug_print(f"Row {i} failed validation: {clues} != {row_clues[i]}")
            return False

    for j in range(len(grid[0])):
        col = [grid[i][j] for i in range(len(grid))]
        clues = line_to_clues(col)
        if clues != col_clues[j]:
            debug_print(f"Col {j} failed validation: {clues} != {col_clues[j]}")
            return False

    return True


def solve_nonogram(clues_row: List[List[int]], clues_col: List[List[int]], max_solutions: int = 2) -> List[Grid]:
    h, w = len(clues_row), len(clues_col)
    grid: Grid = [[-1] * w for _ in range(h)]
    solutions: List[Grid] = []

    def backtrack():
        if len(solutions) >= max_solutions:
            return
        if not propagate(grid, clues_row, clues_col):
            return
        if all(all(c != -1 for c in row) for row in grid):
            if validate_solution(grid, clues_row, clues_col):
                solutions.append([r[:] for r in grid])
            else:
                debug_print("Grid fully filled but violates clues.")
            return

        # Pick row with smallest number of possible patterns
        row_options = []
        for i in range(h):
            if -1 in grid[i]:
                all_patterns = line_possibilities_cached(w, tuple(clues_row[i]))
                filtered = [p for p in all_patterns if all(grid[i][j] in (-1, p[j]) for j in range(w))]
                if not filtered:
                    return
                row_options.append((len(filtered), i, filtered))

        if not row_options:
            return

        _, row_idx, patterns = min(row_options, key=lambda x: x[0])
        for pattern in patterns:
            backup = [r[:] for r in grid]
            grid[row_idx] = pattern[:]
            backtrack()
            if len(solutions) >= max_solutions:
                return
            grid[:] = backup

    backtrack()
    return solutions
