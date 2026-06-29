#!/usr/bin/env python3
"""
Main Entry Point

Usage:
    python main.py input.txt

Menu:
    1) Stable Matching
       a) Gale-Shapley
       b) LP Formulation
    2) Hospital-Resident Matching
       a) Gale-Shapley
       b) LP Formulation
    3) Course Allocation
       a) Gale-Shapley
       b) LP Formulation

"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from input_parser import (
    parse_input_file,
    get_stable_matching_data,
    get_hospital_resident_data,
    get_course_allocation_data
)
from stable_matching import (
    solve_stable_matching_gs,
    solve_stable_matching_lp,
    format_stable_matching_result
)
from hospital_resident import (
    solve_hospital_resident_gs,
    solve_hospital_resident_lp,
    format_hospital_resident_result
)
from course_allocation import (
    solve_course_allocation_gs,
    solve_course_allocation_lp,
    format_course_allocation_result
)


def print_menu():
    """Print the main menu."""
    print("\n" + "=" * 50)
    print("       MATCHING ALGORITHMS MENU")
    print("=" * 50)
    print("  1) Stable Matching")
    print("     a) Gale-Shapley Algorithm")
    print("     b) LP Formulation")
    print()
    print("  2) Hospital-Resident Matching")
    print("     a) Gale-Shapley Algorithm")
    print("     b) LP Formulation")
    print()
    print("  3) Course Allocation")
    print("     a) Gale-Shapley Algorithm")
    print("     b) LP Formulation")
    print("=" * 50)


def get_user_choice():
    """Get and validate user choice."""
    while True:
        print_menu()
        choice = input("\nEnter your choice (e.g., 1a, 2b, 3a): ").strip().lower()

        if len(choice) == 2 and choice[0] in '123' and choice[1] in 'ab':
            return choice
        print("Invalid choice. Please enter in format like '1a', '2b', or '3a'.")


def run_stable_matching(data: dict, algorithm: str):
    """Run stable matching with selected algorithm."""
    men, women, men_prefs, women_prefs = get_stable_matching_data(data)

    print(f"\nRunning Stable Matching with {'Gale-Shapley' if algorithm == 'a' else 'LP Formulation'}...")
    print(f"  Men: {men}")
    print(f"  Women: {women}")

    if algorithm == 'a':
        result = solve_stable_matching_gs(men, women, men_prefs, women_prefs)
    else:
        result = solve_stable_matching_lp(men, women, men_prefs, women_prefs)

    print(format_stable_matching_result(result))
    return result


def run_hospital_resident(data: dict, algorithm: str):
    """Run hospital-resident matching with selected algorithm."""
    residents, hospitals, res_prefs, hosp_prefs, capacities = get_hospital_resident_data(data)

    print(f"\nRunning Hospital-Resident Matching with {'Gale-Shapley' if algorithm == 'a' else 'LP Formulation'}...")
    print(f"  Residents: {residents}")
    print(f"  Hospitals: {hospitals}")
    print(f"  Capacities: {capacities}")

    if algorithm == 'a':
        result = solve_hospital_resident_gs(residents, hospitals, res_prefs, hosp_prefs, capacities)
    else:
        result = solve_hospital_resident_lp(residents, hospitals, res_prefs, hosp_prefs, capacities)

    print(format_hospital_resident_result(result, capacities))
    return result


def run_course_allocation(data: dict, algorithm: str):
    """Run course allocation with selected algorithm."""
    students, courses, stud_prefs, course_prefs, capacities = get_course_allocation_data(data)

    print(f"\nRunning Course Allocation with {'Gale-Shapley' if algorithm == 'a' else 'LP Formulation'}...")
    print(f"  Students: {students}")
    print(f"  Courses: {courses}")
    print(f"  Capacities: {capacities}")

    if algorithm == 'a':
        result = solve_course_allocation_gs(students, courses, stud_prefs, course_prefs, capacities)
    else:
        result = solve_course_allocation_lp(students, courses, stud_prefs, course_prefs, capacities)

    print(format_course_allocation_result(result, capacities))
    return result


def compare_algorithms(data: dict, problem_type: str):
    """Run both algorithms and compare their results."""
    print("\n" + "=" * 50)
    print("  COMPARING BOTH ALGORITHMS")
    print("=" * 50)

    if problem_type == 'stable_matching':
        gs_result = run_stable_matching(data, 'a')
        lp_result = run_stable_matching(data, 'b')
    elif problem_type == 'hospital_resident':
        gs_result = run_hospital_resident(data, 'a')
        lp_result = run_hospital_resident(data, 'b')
    elif problem_type == 'course_allocation':
        gs_result = run_course_allocation(data, 'a')
        lp_result = run_course_allocation(data, 'b')
    else:
        print(f"Unknown problem type: {problem_type}")
        return
"""
    # Compare results
    print("\n" + "=" * 50)
    print("  COMPARISON RESULT")
    print("=" * 50)

    if gs_result == lp_result:
        print("  Both algorithms produced the SAME solution!")
    else:
        print("  NOTE: Algorithms produced different solutions.")
        print("  (Both are stable; Gale-Shapley is proposer-optimal,")
        print("   LP may find a different stable matching)")
        print(f"\n  Gale-Shapley result: {gs_result}")
        print(f"  LP result:           {lp_result}")
    print("=" * 50)
"""

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python main.py input.txt")
        print("\nPlease provide an input file path.")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    # Parse input file
    print(f"Loading input from: {input_file}")
    problem_type, data = parse_input_file(input_file)

    print(f"Detected problem type: {problem_type}")

    # Get user choice
    choice = get_user_choice()
    problem_num = choice[0]
    algorithm = choice[1]

    # Validate that the chosen problem matches the input file type
    type_mapping = {
        '1': 'stable_matching',
        '2': 'hospital_resident',
        '3': 'course_allocation'
    }

    expected_type = type_mapping[problem_num]

    if expected_type != problem_type:
        print(f"\nWarning: Input file is for '{problem_type}', but you selected '{expected_type}'.")
        proceed = input("Do you want to proceed anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Exiting.")
            sys.exit(0)

    # Run the selected algorithm
    if problem_num == '1':
        run_stable_matching(data, algorithm)
    elif problem_num == '2':
        run_hospital_resident(data, algorithm)
    elif problem_num == '3':
        run_course_allocation(data, algorithm)
"""
    # Ask if user wants to compare with the other algorithm
    print("\n" + "-" * 50)
    compare = input("Compare with the other algorithm? (y/n): ").strip().lower()
    if compare == 'y':
        compare_algorithms(data, problem_type)

    print("\nDone!")
"""

if __name__ == '__main__':
    main()
