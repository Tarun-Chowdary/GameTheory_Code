"""
Stable Matching Module
"""

from typing import Dict, List
from gale_shapley import gale_shapley, is_stable
from lp_solver import lp_stable_matching


def solve_stable_matching_gs(
    men: List[str],
    women: List[str],
    men_preferences: Dict[str, List[str]],
    women_preferences: Dict[str, List[str]]
) -> Dict[str, str]:
    
    #Solve stable matching using Gale-Shapley algorithm.

    matches = gale_shapley(
        proposers=men,
        proposee_preferences=women_preferences,
        proposer_preferences=men_preferences,
        capacities=None  # One-to-one matching
    )

    # Convert from {woman: [man]} to {woman: man} for one-to-one
    result = {}
    for woman, matched_men in matches.items():
        if matched_men:
            result[woman] = matched_men[0]

    # Verify stability
    assert is_stable(matches, women_preferences, men_preferences), "GS result is not stable!"

    return result


def solve_stable_matching_lp(
    men: List[str],
    women: List[str],
    men_preferences: Dict[str, List[str]],
    women_preferences: Dict[str, List[str]]
) -> Dict[str, str]:
    #Solve stable matching using LP formulation.
    matches = lp_stable_matching(
        proposers=men,
        proposee_preferences=women_preferences,
        proposer_preferences=men_preferences,
        capacities=None
    )

    # Convert from {woman: [man]} to {woman: man} for one-to-one
    result = {}
    for woman, matched_men in matches.items():
        if matched_men:
            result[woman] = matched_men[0]

    return result


def format_stable_matching_result(matches: Dict[str, str]) -> str:
    """Format the stable matching result for display."""
    lines = ["=" * 50]
    lines.append("STABLE MATCHING RESULT")
    lines.append("=" * 50)

    if not matches:
        lines.append("No matches found.")
        return "\n".join(lines)

    for woman, man in sorted(matches.items()):
        lines.append(f"  {woman} <-> {man}")

    lines.append("=" * 50)
    return "\n".join(lines)
