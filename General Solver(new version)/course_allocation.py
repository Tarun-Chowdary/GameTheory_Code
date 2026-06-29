"""
Course Allocation Module
"""

from typing import Dict, List
from gale_shapley import gale_shapley, is_stable
from lp_solver import lp_course_allocation


def solve_course_allocation_gs(
    students: List[str],
    courses: List[str],
    student_preferences: Dict[str, List[str]],
    course_preferences: Dict[str, List[str]],
    course_capacities: Dict[str, int]
) -> Dict[str, List[str]]:
    
    #Solve Course Allocation problem using Gale-Shapley algorithm.
    
    matches = gale_shapley(
        proposers=students,
        proposee_preferences=course_preferences,
        proposer_preferences=student_preferences,
        capacities=course_capacities
    )

    # Verify stability
    assert is_stable(matches, course_preferences, student_preferences, course_capacities),         "GS result is not stable!"

    return matches


def solve_course_allocation_lp(
    students: List[str],
    courses: List[str],
    student_preferences: Dict[str, List[str]],
    course_preferences: Dict[str, List[str]],
    course_capacities: Dict[str, int]
) -> Dict[str, List[str]]:
    # Solve Course Allocation problem using LP formulation.
    matches = lp_course_allocation(
        students=students,
        courses=courses,
        student_preferences=student_preferences,
        course_preferences=course_preferences,
        course_capacities=course_capacities
    )

    return matches


def format_course_allocation_result(matches: Dict[str, List[str]], course_capacities: Dict[str, int]) -> str:
    """Format the course allocation result for display."""
    lines = ["=" * 50]
    lines.append("COURSE ALLOCATION RESULT")

    if not matches:
        lines.append("No matches found.")
        return "\n".join(lines)

    for course in sorted(matches.keys()):
        students = matches[course]
        capacity = course_capacities.get(course, 1)
        lines.append(f"\n  {course} (capacity: {capacity}):")
        if students:
            for student in students:
                lines.append(f"    -> {student}")
        else:
            lines.append("    (no students assigned)")

    return "\n".join(lines)
