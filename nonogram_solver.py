from ortools.sat.python import cp_model
from typing import List, Tuple, Set, Dict

Grid = List[List[int]]


def make_transition_matrix(
    clues: List[int],
) -> Tuple[List[Tuple[int, int, int]], int, int, List[int], List[int]]:
    """
    Build transition matrix from clues (e.g. [3, 2]) for AddAutomaton.
    Returns: transitions, initial_state, final_state, input_domain, final_states
    """
    # Build base transitions according to the clue pattern
    base: List[Tuple[int, int, int]] = []
    state = 0

    # Build transitions following the standard nonogram automaton
    for idx, run in enumerate(clues):
        # leading zeros or zeros between runs
        base.append((state, 0, state))
        for _ in range(run):
            base.append((state, 1, state + 1))
            state += 1
        if idx < len(clues) - 1:
            base.append((state, 0, state + 1))
            state += 1

    base.append((state, 0, state))  # trailing zeros
    final_state = state

    # Add a sink state to satisfy AddAutomaton's requirement that every
    # (state, label) pair has a transition.
    # Remove duplicates and ensure exactly one transition per (state, label)
    trans_map: Dict[Tuple[int, int], int] = {}
    for s, a, t in base:
        trans_map[(s, a)] = t

    sink = final_state + 1
    for s in range(sink):
        for a in (0, 1):
            if (s, a) not in trans_map:
                trans_map[(s, a)] = sink

    trans_map[(sink, 0)] = sink
    trans_map[(sink, 1)] = sink

    transitions = [(s, a, t) for (s, a), t in sorted(trans_map.items())]

    num_states = sink + 1
    input_domain = [0, 1]
    initial_state = 0
    final_states = [final_state]

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
