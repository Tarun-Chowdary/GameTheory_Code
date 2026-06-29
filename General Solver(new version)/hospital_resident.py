"""
Hospital-Resident Module
"""

from typing import Dict, List
from gale_shapley import gale_shapley, is_stable
from lp_solver import lp_hospital_resident


def solve_hospital_resident_gs(
    residents: List[str],
    hospitals: List[str],
    resident_preferences: Dict[str, List[str]],
    hospital_preferences: Dict[str, List[str]],
    hospital_capacities: Dict[str, int]
) -> Dict[str, List[str]]:
   
   #Solve Hospital-Resident problem using Gale-Shapley algorithm.
   
    matches = gale_shapley(
        proposers=residents,
        proposee_preferences=hospital_preferences,
        proposer_preferences=resident_preferences,
        capacities=hospital_capacities
    )

    # Verify stability
    assert is_stable(matches, hospital_preferences, resident_preferences, hospital_capacities),         "GS result is not stable!"

    return matches


def solve_hospital_resident_lp(
    residents: List[str],
    hospitals: List[str],
    resident_preferences: Dict[str, List[str]],
    hospital_preferences: Dict[str, List[str]],
    hospital_capacities: Dict[str, int]
) -> Dict[str, List[str]]:
    
#Solve Hospital-Resident problem using LP formulation.


    matches = lp_hospital_resident(
        residents=residents,
        hospitals=hospitals,
        resident_preferences=resident_preferences,
        hospital_preferences=hospital_preferences,
        hospital_capacities=hospital_capacities
    )

    return matches


def format_hospital_resident_result(matches: Dict[str, List[str]], hospital_capacities: Dict[str, int]) -> str:
    """Format the hospital-resident matching result for display."""
    lines = ["=" * 50]
    lines.append("HOSPITAL-RESIDENT MATCHING RESULT")

    if not matches:
        lines.append("No matches found.")
        return "\n".join(lines)

    for hospital in sorted(matches.keys()):
        residents = matches[hospital]
        capacity = hospital_capacities.get(hospital, 1)
        lines.append(f"\n  {hospital} (capacity: {capacity}):")
        if residents:
            for resident in residents:
                lines.append(f"    -> {resident}")
        else:
            lines.append("    (no residents assigned)")
            
    return "\n".join(lines)
