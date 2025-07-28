#!/usr/bin/env python3
"""Interactive nonogram solver demo."""

from nonogram_solver import solve_nonogram


def print_grid(grid, title="Grid"):
    """Print a grid in a readable format."""
    print(f"\n{title}:")
    for row in grid:
        print(
            "".join(["█" if cell == 1 else "·" if cell == 0 else "?" for cell in row])
        )


def input_clues(dimension_name):
    """Get clues input from user."""
    print(f"\nEnter {dimension_name} clues:")
    print("Format: For each line, enter numbers separated by spaces")
    print("Example: '2 1' means two consecutive filled cells, then one filled cell")
    print("Enter '0' for a line with no filled cells")
    print("Enter empty line when done")

    clues = []
    i = 0
    while True:
        try:
            line = input(f"{dimension_name} {i}: ").strip()
            if not line:
                break
            if line == "0":
                clues.append([0])
            else:
                numbers = [int(x) for x in line.split()]
                clues.append(numbers)
            i += 1
        except ValueError:
            print("Invalid input. Please enter numbers separated by spaces.")

    return clues


def main():
    """Interactive nonogram solver."""
    print("Interactive Nonogram Solver")
    print("=" * 40)

    print("\nChoose an option:")
    print("1. Enter custom puzzle")
    print("2. Try example puzzles")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        # Custom puzzle input
        print("\nCustom Puzzle Input")
        print("-" * 20)

        row_clues = input_clues("Row")
        if not row_clues:
            print("No row clues entered. Exiting.")
            return

        col_clues = input_clues("Column")
        if not col_clues:
            print("No column clues entered. Exiting.")
            return

        print(f"\nPuzzle: {len(row_clues)}x{len(col_clues)}")
        print("Row clues:", row_clues)
        print("Column clues:", col_clues)

    elif choice == "2":
        # Example puzzles
        examples = {
            "1": {
                "name": "Simple 3x3 Cross",
                "row_clues": [[1], [3], [1]],
                "col_clues": [[1], [3], [1]],
            },
            "2": {
                "name": "5x5 Cross",
                "row_clues": [[1], [1], [5], [1], [1]],
                "col_clues": [[1], [1], [5], [1], [1]],
            },
            "3": {
                "name": "4x4 Diagonal",
                "row_clues": [[1], [1], [1], [1]],
                "col_clues": [[1], [1], [1], [1]],
            },
            "4": {
                "name": "20x20 Pattern",
                "row_clues": [[2], *[[1, 1] for x in range(36)], [2]],
                "col_clues": [[2], *[[1, 1] for x in range(36)], [2]],
            },
        }

        print("\nExample Puzzles:")
        for key, example in examples.items():
            print(f"{key}. {example['name']}")

        ex_choice = input("Choose example (1-4): ").strip()
        if ex_choice in examples:
            example = examples[ex_choice]
            row_clues = example["row_clues"]
            col_clues = example["col_clues"]
            print(f"\nSelected: {example['name']}")
            print("Row clues:", row_clues)
            print("Column clues:", col_clues)
        else:
            print("Invalid choice. Exiting.")
            return
    else:
        print("Invalid choice. Exiting.")
        return

    # Solve the puzzle
    print("\nSolving...")
    try:
        solutions = solve_nonogram(row_clues, col_clues, max_solutions=2)

        if not solutions:
            print("No solution found. The puzzle may be unsolvable.")
        elif len(solutions) == 1:
            print("Found unique solution!")
            print_grid(solutions[0], "Solution")
        else:
            print(f"Found {len(solutions)} solutions (showing first 2):")
            for i, solution in enumerate(solutions[:2]):
                print_grid(solution, f"Solution {i + 1}")

    except Exception as e:
        print(f"Error solving puzzle: {e}")


if __name__ == "__main__":
    main()
