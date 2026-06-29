"""
LP Formulation Module
"""

from typing import Dict, List, Optional
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds


def lp_stable_matching(
    proposers: List[str],
    proposee_preferences: Dict[str, List[str]],
    proposer_preferences: Dict[str, List[str]],
    capacities: Optional[Dict[str, int]] = None
) -> Dict[str, List[str]]:
    #    Solve stable matching using Integer Linear Programming (ILP).
    if capacities is None:
        capacities = {p: 1 for p in proposee_preferences}

    # Build index mappings
    all_proposers = list(proposers)
    all_proposees = list(proposee_preferences.keys())

    n_proposers = len(all_proposers)
    n_proposees = len(all_proposees)

    proposer_idx = {p: i for i, p in enumerate(all_proposers)}
    proposee_idx = {p: i for i, p in enumerate(all_proposees)}

    # Build rank matrices
    # rank_proposer[i][j] = rank of proposee j in proposer i's preferences (0-indexed, -1 if not listed)
    rank_proposer = np.full((n_proposers, n_proposees), -1, dtype=int)
    for proposer, prefs in proposer_preferences.items():
        if proposer in proposer_idx:
            for rank, proposee in enumerate(prefs):
                if proposee in proposee_idx:
                    rank_proposer[proposer_idx[proposer]][proposee_idx[proposee]] = rank

    # rank_proposee[j][i] = rank of proposer i in proposee j's preferences (0-indexed, -1 if not listed)
    rank_proposee = np.full((n_proposees, n_proposers), -1, dtype=int)
    for proposee, prefs in proposee_preferences.items():
        if proposee in proposee_idx:
            for rank, proposer in enumerate(prefs):
                if proposer in proposer_idx:
                    rank_proposee[proposee_idx[proposee]][proposer_idx[proposer]] = rank

    # Variables: x_{i,j} for each valid pair (proposer i, proposee j)
    # We create a flat list of all possible pairs
    pairs = []
    for i, proposer in enumerate(all_proposers):
        for j, proposee in enumerate(all_proposees):
            if rank_proposer[i][j] >= 0 and rank_proposee[j][i] >= 0:
                pairs.append((i, j))

    n_pairs = len(pairs)
    pair_idx = {pair: idx for idx, pair in enumerate(pairs)}

    # Objective: Maximize total matches (all weights = 1)
    c = -np.ones(n_pairs)  # Negative because milp minimizes

    # Constraints matrices
    A_eq = []
    b_eq = []
    A_ub = []
    b_ub = []

    # Constraint 1: Each proposer matched to at most 1 proposee
    for i in range(n_proposers):
        row = np.zeros(n_pairs)
        for j in range(n_proposees):
            if (i, j) in pair_idx:
                row[pair_idx[(i, j)]] = 1
        A_ub.append(row)
        b_ub.append(1.0)

    # Constraint 2: Each proposee matched to at most capacity proposees
    for j in range(n_proposees):
        row = np.zeros(n_pairs)
        for i in range(n_proposers):
            if (i, j) in pair_idx:
                row[pair_idx[(i, j)]] = 1
        A_ub.append(row)
        b_ub.append(float(capacities.get(all_proposees[j], 1)))

    for i, j in pairs:
        row = np.zeros(n_pairs)

        # Sum of i's better or equal matches
        for j_prime in range(n_proposees):
            if rank_proposer[i][j_prime] >= 0 and rank_proposer[i][j_prime] <= rank_proposer[i][j]:
                if (i, j_prime) in pair_idx:
                    row[pair_idx[(i, j_prime)]] = 1

        # Sum of j's better or equal matches
        for i_prime in range(n_proposers):
            if rank_proposee[j][i_prime] >= 0 and rank_proposee[j][i_prime] <= rank_proposee[j][i]:
                if (i_prime, j) in pair_idx:
                    row[pair_idx[(i_prime, j)]] = 1

        # The constraint: sum >= 1 + x_{i,j} (when x_{i,j}=0, sum>=1; when x_{i,j}=1, sum>=2 which is always true if valid)
        # Actually, we need: sum >= 1 for all pairs, but if x_{i,j}=1, it's automatically satisfied
        # Better formulation: sum - x_{i,j} >= 1  =>  sum >= 1 + x_{i,j}
        # But this is nonlinear. Instead:
        # For each pair (i,j): if not matched, then sum of better matches >= 1
        # Using big-M: sum_{better} + M * x_{i,j} >= 1
        # With M = 1: sum_{better} + x_{i,j} >= 1

        row[pair_idx[(i, j)]] += 1  # Add x_{i,j} to left side
        A_ub.append(-row)  # -row <= -1  =>  row >= 1
        b_ub.append(-1.0)

    # Convert to scipy format
    A_ub_matrix = np.array(A_ub)
    b_ub_vector = np.array(b_ub)

    # Variable bounds: 0 <= x <= 1 (binary)
    bounds = Bounds(lb=np.zeros(n_pairs), ub=np.ones(n_pairs))

    # Integer constraints: all variables are binary
    integrality = np.ones(n_pairs, dtype=int)

    # Solve
    constraints = LinearConstraint(A_ub_matrix, lb=-np.inf, ub=b_ub_vector)

    result = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=integrality
    )

    if not result.success:
        raise RuntimeError(f"LP solver failed: {result.message}")

    # Extract solution
    x = result.x

    # Build matches
    matches = {proposee: [] for proposee in all_proposees}
    for (i, j), idx in pair_idx.items():
        if x[idx] > 0.5:  # Binary variable is 1
            matches[all_proposees[j]].append(all_proposers[i])

    return matches


def lp_hospital_resident(
    residents: List[str],
    hospitals: List[str],
    resident_preferences: Dict[str, List[str]],
    hospital_preferences: Dict[str, List[str]],
    hospital_capacities: Dict[str, int]
) -> Dict[str, List[str]]:
    """
    Solve Hospital-Resident problem using LP formulation.
    """
    return lp_stable_matching(
        proposers=residents,
        proposee_preferences=hospital_preferences,
        proposer_preferences=resident_preferences,
        capacities=hospital_capacities
    )


def lp_course_allocation(
    students: List[str],
    courses: List[str],
    student_preferences: Dict[str, List[str]],
    course_preferences: Dict[str, List[str]],
    course_capacities: Dict[str, int]
) -> Dict[str, List[str]]:
    """
    Solve Course Allocation problem using LP formulation.
    """
    return lp_stable_matching(
        proposers=students,
        proposee_preferences=course_preferences,
        proposer_preferences=student_preferences,
        capacities=course_capacities
    )
