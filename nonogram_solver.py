from ortools.sat.python import cp_model
from typing import List, Tuple

Grid = List[List[int]]


def make_transition_matrix(
    clues: List[int],
) -> Tuple[List[Tuple[int, int, int]], int, int, List[int], List[int]]:
    """
    Build transition matrix from clues (e.g. [3, 2]) for AddAutomaton.
    Returns: transitions, initial_state, final_state, input_domain, final_states
    """
    transitions = []
    state = 0
    for idx, run in enumerate(clues):
        transitions.append((state, 0, state))  # loop on 0s (optional)
        for _ in range(run):
            transitions.append((state, 1, state + 1))
            state += 1
        if idx < len(clues) - 1:
            transitions.append((state, 0, state + 1))  # mandatory 0 between blocks
            state += 1
    transitions.append((state, 0, state))  # trailing 0s
    num_states = state + 1
    input_domain = [0, 1]
    initial_state = 0
    final_states = [state]
    return transitions, initial_state, num_states, input_domain, final_states


def solve_nonogram(
    row_clues: List[List[int]], col_clues: List[List[int]], max_solutions: int = 2
) -> List[Grid]:
    model = cp_model.CpModel()
    h, w = len(row_clues), len(col_clues)

    grid = [
        [model.NewIntVar(0, 1, f"cell_{r}_{c}") for c in range(w)] for r in range(h)
    ]

    for r, clues in enumerate(row_clues):
        row = grid[r]
        transitions, q0, n, sigma, final = make_transition_matrix(
            clues if clues else [0]
        )
        model.AddAutomaton(row, q0, final, transitions)

    for c, clues in enumerate(col_clues):
        col = [grid[r][c] for r in range(h)]
        transitions, q0, n, sigma, final = make_transition_matrix(
            clues if clues else [0]
        )
        model.AddAutomaton(col, q0, final, transitions)

    solver = cp_model.CpSolver()
    # Fix: Use enumerate_all_solutions instead of max_number_of_solutions
    solver.parameters.enumerate_all_solutions = True

    class SolutionCollector(cp_model.CpSolverSolutionCallback):
        def __init__(self, max_sols: int):
            super().__init__()
            self.solutions = []
            self.max_solutions = max_sols

        def on_solution_callback(self):
            if len(self.solutions) >= self.max_solutions:
                self.StopSearch()
                return

            solution = [[self.Value(grid[r][c]) for c in range(w)] for r in range(h)]
            self.solutions.append(solution)

    collector = SolutionCollector(max_solutions)
    solver.SearchForAllSolutions(model, collector)
    return collector.solutions
