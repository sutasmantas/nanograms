#!/usr/bin/env python3
"""Test script for the nonogram solver."""

from nonogram_solver import solve_nonogram
from nonogram_clues import puzzle_from_image
import os


def print_grid(grid, title="Grid"):
    """Print a grid in a readable format."""
    print(f"\n{title}:")
    for row in grid:
        print(
            "".join(["█" if cell == 1 else "·" if cell == 0 else "?" for cell in row])
        )


def test_simple_puzzle():
    """Test with a simple hand-crafted puzzle."""
    print("=" * 50)
    print("Testing Simple 5x5 Puzzle")
    print("=" * 50)

    # Simple 5x5 puzzle - creates a cross pattern
    # Expected solution:
    # · · █ · ·
    # · · █ · ·
    # █ █ █ █ █
    # · · █ · ·
    # · · █ · ·

    clues_row = [
        [1],  # Row 0: single filled cell
        [1],  # Row 1: single filled cell
        [5],  # Row 2: five filled cells
        [1],  # Row 3: single filled cell
        [1],  # Row 4: single filled cell
    ]

    clues_col = [
        [1],  # Col 0: single filled cell
        [1],  # Col 1: single filled cell
        [5],  # Col 2: five filled cells
        [1],  # Col 3: single filled cell
        [1],  # Col 4: single filled cell
    ]

    print("Row clues:", clues_row)
    print("Column clues:", clues_col)

    solutions = solve_nonogram(clues_row, clues_col, max_solutions=2)

    print(f"\nFound {len(solutions)} solution(s)")
    for i, solution in enumerate(solutions):
        print_grid(solution, f"Solution {i + 1}")

    return len(solutions) == 1


def test_harder_puzzle():
    """Test with a more complex puzzle."""
    print("\n" + "=" * 50)
    print("Testing 10x10 Puzzle")
    print("=" * 50)

    # 10x10 puzzle that creates a simple pattern
    clues_row = [
        [3],
        [2, 1],
        [1, 1, 1],
        [1, 1],
        [1, 1],
        [1, 1],
        [1, 1, 1],
        [2, 1],
        [3],
        [1],
    ]

    clues_col = [[2], [4], [1, 1, 1], [1, 1], [1, 1], [1, 1], [1, 1, 1], [4], [2], [1]]

    print("Row clues:", clues_row)
    print("Column clues:", clues_col)

    solutions = solve_nonogram(clues_row, clues_col, max_solutions=2)

    print(f"\nFound {len(solutions)} solution(s)")
    for i, solution in enumerate(solutions):
        print_grid(solution, f"Solution {i + 1}")

    return len(solutions) >= 1


def test_from_image():
    """Test solver with a puzzle generated from an image."""
    print("\n" + "=" * 50)
    print("Testing Puzzle from Image")
    print("=" * 50)

    # Check if we have a preprocessed image
    if os.path.exists("output.png"):
        print("Loading puzzle from output.png...")
        puzzle = puzzle_from_image("output.png")

        print(f"Grid shape: {puzzle.grid_shape}")
        print(f"Number of rows: {len(puzzle.clues_row)}")
        print(f"Number of columns: {len(puzzle.clues_col)}")

        # Only try small puzzles to avoid long computation
        print("Attempting to solve...")
        solutions = solve_nonogram(
            puzzle.clues_row, puzzle.clues_col, max_solutions=2
        )

        print(f"\nFound {len(solutions)} solution(s)")
        for i, solution in enumerate(solutions):
            print_grid(solution, f"Solution {i + 1}")

        return len(solutions) >= 1
    else:
        print("No output.png found. Generate one first with:")
        print("python nonogram_preprocess.py input.jpg output.png --grid-size 10")
        return True


def test_unsolvable_puzzle():
    """Test with an unsolvable puzzle."""
    print("\n" + "=" * 50)
    print("Testing Unsolvable Puzzle")
    print("=" * 50)

    # Contradictory clues - impossible to satisfy
    clues_row = [
        [5],  # Row needs 5 filled cells
        [5],  # Row needs 5 filled cells
    ]

    clues_col = [
        [1],  # Col needs 1 filled cell
        [1],  # Col needs 1 filled cell
        [1],  # Col needs 1 filled cell
        [1],  # Col needs 1 filled cell
        [1],  # Col needs 1 filled cell
    ]

    print("Row clues:", clues_row)
    print("Column clues:", clues_col)
    print("(This puzzle should be unsolvable)")

    solutions = solve_nonogram(clues_row, clues_col, max_solutions=2)

    print(f"\nFound {len(solutions)} solution(s)")
    for i, solution in enumerate(solutions):
        print_grid(solution, f"Solution {i + 1}")

    return len(solutions) == 0

def test_multiple_solutions():
    """Test a puzzle with multiple valid solutions."""
    print("\n" + "=" * 50)
    print("Testing Puzzle with Multiple Solutions")
    print("=" * 50)

    # 2x2 grid, clue [1] for every row and column — many possible combinations
    clues_row = [
        [1],  # could be [1, 0] or [0, 1]
        [1],  # same
    ]
    clues_col = [
        [1],  # same
        [1],  # same
    ]

    print("Row clues:", clues_row)
    print("Column clues:", clues_col)
    print("(This puzzle should have multiple solutions)")

    solutions = solve_nonogram(clues_row, clues_col, max_solutions=3)

    print(f"\nFound {len(solutions)} solution(s)")
    for i, solution in enumerate(solutions):
        print_grid(solution, f"Solution {i + 1}")

    return len(solutions) > 1


if __name__ == "__main__":
    print("Nonogram Solver Test Suite")
    print("=" * 50)

    tests = [
        ("Simple 5x5 Cross", test_simple_puzzle),
        ("10x10 Pattern", test_harder_puzzle),
        ("From Image", test_from_image),
        ("Unsolvable", test_unsolvable_puzzle),
        ("Multiple Solutions", test_multiple_solutions),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"Error in {test_name}: {e}")
            results.append((test_name, "ERROR"))

    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    for test_name, result in results:
        print(f"{test_name:20} : {result}")
