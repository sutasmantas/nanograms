"""Improved Nonogram solver with lazy pattern generation, uniqueness verification,
and debug logging to help trace unsolvable cases.
"""

from typing import List, Optional, Generator
from itertools import tee

Grid = List[List[int]]  # 0/1 values

DEBUG = False  # Set to True to enable step-wise logging

def debug_print(*args):
    if DEBUG:
        print("[DEBUG]", *args)

def line_possibilities_lazy(length: int, clues: List[int]) -> Generator[List[int], None, None]:
    """Lazily generate all binary lines of given length that satisfy clues."""
    if clues == [0]:
        yield [0] * length
        return

    def helper(pos: int, clue_idx: int, line: List[int]):
        if clue_idx == len(clues):
            if len(line) < length:
                line += [0] * (length - len(line))
            if len(line) == length:
                yield line
            return

        run = clues[clue_idx]
        max_start = length - sum(clues[clue_idx:]) - (len(clues) - clue_idx - 1)
        for start in range(pos, max_start + 1):
            new_line = line + [0] * (start - len(line)) + [1] * run
            if len(new_line) < length:
                new_line.append(0)
            yield from helper(start + run + 1, clue_idx + 1, new_line)

    yield from helper(0, 0, [])


def intersect_patterns(patterns: Generator[List[int], None, None], length: int) -> Optional[List[int]]:
    found = False
    for pattern in patterns:
        if not found:
            mask = pattern[:]
            found = True
        else:
            for i in range(length):
                if mask[i] != pattern[i]:
                    mask[i] = -1  # unknown
    return mask if found else None


def propagate(grid: Grid, row_clues: List[List[int]], col_clues: List[List[int]]) -> bool:
    h, w = len(grid), len(grid[0])
    changed = True
    while changed:
        changed = False
        for i in range(h):
            if -1 not in grid[i]:
                continue
            gen = (p for p in line_possibilities_lazy(w, row_clues[i]) if all(grid[i][j] in (-1, p[j]) for j in range(w)))
            gen, gen_copy = tee(gen)
            intersection = intersect_patterns(gen, w)
            has_any = next(gen_copy, None) is not None
            debug_print(f"Row {i} patterns exist: {has_any}, intersection: {intersection}")
            if intersection is None or not has_any:
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
            gen = (p for p in line_possibilities_lazy(h, col_clues[j]) if all(col[i] in (-1, p[i]) for i in range(h)))
            gen, gen_copy = tee(gen)
            intersection = intersect_patterns(gen, h)
            has_any = next(gen_copy, None) is not None
            debug_print(f"Col {j} patterns exist: {has_any}, intersection: {intersection}")
            if intersection is None or not has_any:
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

        for i in range(h):
            if -1 in grid[i]:
                line_gen = [p for p in line_possibilities_lazy(w, clues_row[i]) if all(grid[i][j] in (-1, p[j]) for j in range(w))]
                if not line_gen:
                    debug_print(f"No valid row patterns to backtrack row {i}")
                    return
                for pattern in line_gen:
                    backup = [r[:] for r in grid]
                    grid[i] = pattern[:]
                    backtrack()
                    if len(solutions) >= max_solutions:
                        return
                    grid[:] = backup
                return

    backtrack()
    return solutions
