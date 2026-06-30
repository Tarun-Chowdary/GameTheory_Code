#!/usr/bin/env python3
"""
Input File Generator for Matching Problems

Generates random but valid input files for:
  1) Stable Matching
  2) Hospital-Resident Matching
  3) Course Allocation

Usage:
    python input_generator.py

Interactive prompts will ask for problem type and parameters.
"""

import random


def generate_stable_matching_input(num_men, num_women, filename="stable_matching_input.txt"):
    """Generate a stable matching input file."""
    men = [f"m{i+1}" for i in range(num_men)]
    women = [f"w{i+1}" for i in range(num_women)]
    
    men_preferences = {man: random.sample(women, len(women)) for man in men}
    women_preferences = {woman: random.sample(men, len(men)) for woman in women}
    
    lines = []
    lines.append("---")
    lines.append("TYPE: stable_matching")
    lines.append(f"MEN: {', '.join(men)}")
    lines.append(f"WOMEN: {', '.join(women)}")
    lines.append("MEN_PREFERENCES:")
    for m in men:
        lines.append(f"{m}: {', '.join(men_preferences[m])}")
    lines.append("WOMEN_PREFERENCES:")
    for w in women:
        lines.append(f"{w}: {', '.join(women_preferences[w])}")
    lines.append("---")
    
    with open(filename, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    
    print(f"\nGenerated: {filename} (Men: {num_men}, Women: {num_women})")
    return filename


def generate_hospital_resident_input(num_residents, num_hospitals, capacity, filename="hospital_resident_input.txt"):
    """Generate a hospital-resident matching input file. All hospitals get the same capacity."""
    residents = [f"r{i+1}" for i in range(num_residents)]
    hospitals = [f"h{i+1}" for i in range(num_hospitals)]
    
    resident_preferences = {r: random.sample(hospitals, len(hospitals)) for r in residents}
    hospital_preferences = {h: random.sample(residents, len(residents)) for h in hospitals}
    
    lines = []
    lines.append("---")
    lines.append("TYPE: hospital_resident")
    lines.append(f"RESIDENTS: {', '.join(residents)}")
    lines.append(f"HOSPITALS: {', '.join(hospitals)}")
    lines.append("HOSPITAL_CAPACITIES:")
    for h in hospitals:
        lines.append(f"{h}: {capacity}")
    lines.append("RESIDENT_PREFERENCES:")
    for r in residents:
        lines.append(f"{r}: {', '.join(resident_preferences[r])}")
    lines.append("HOSPITAL_PREFERENCES:")
    for h in hospitals:
        lines.append(f"{h}: {', '.join(hospital_preferences[h])}")
    lines.append("---")
    
    with open(filename, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    
    print(f"\nGenerated: {filename} (Residents: {num_residents}, Hospitals: {num_hospitals}, Cap: {capacity})")
    return filename


def generate_course_allocation_input(num_students, num_courses, capacity, filename="course_allocation_input.txt"):
    """Generate a course allocation input file. All courses get the same capacity."""
    students = [f"s{i+1}" for i in range(num_students)]
    courses = [f"c{i+1}" for i in range(num_courses)]
    
    student_preferences = {s: random.sample(courses, len(courses)) for s in students}
    course_preferences = {c: random.sample(students, len(students)) for c in courses}
    
    lines = []
    lines.append("---")
    lines.append("TYPE: course_allocation")
    lines.append(f"STUDENTS: {', '.join(students)}")
    lines.append(f"COURSES: {', '.join(courses)}")
    lines.append("COURSE_CAPACITIES:")
    for c in courses:
        lines.append(f"{c}: {capacity}")
    lines.append("STUDENT_PREFERENCES:")
    for s in students:
        lines.append(f"{s}: {', '.join(student_preferences[s])}")
    lines.append("COURSE_PREFERENCES:")
    for c in courses:
        lines.append(f"{c}: {', '.join(course_preferences[c])}")
    lines.append("---")
    
    with open(filename, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    
    print(f"\nGenerated: {filename} (Students: {num_students}, Courses: {num_courses}, Cap: {capacity})")
    return filename


def get_int(prompt, min_val=1, max_val=1000):
    """Get an integer input from user with validation."""
    while True:
        try:
            val = int(input(prompt).strip())
            if min_val <= val <= max_val:
                return val
            print(f"Enter a value between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Enter a valid integer.")


def main():
    print("=" * 55)
    print("     MATCHING PROBLEM INPUT GENERATOR")
    print("=" * 55)
    print("\nSelect problem type:")
    print("  1) Stable Matching")
    print("  2) Hospital-Resident Matching")
    print("  3) Course Allocation")
    
    choice = get_int("\nEnter choice (1-3): ", 1, 3)
    
    if choice == 1:
        print("\n--- Stable Matching ---")
        n_men = get_int("Enter number of men: ", 1, 500)
        n_women = get_int("Enter number of women: ", 1, 500)
        fn = input("Output filename [stable_matching_input.txt]: ").strip() or "stable_matching_input.txt"
        generate_stable_matching_input(n_men, n_women, fn)
    
    elif choice == 2:
        print("\n--- Hospital-Resident Matching ---")
        n_res = get_int("Enter number of residents: ", 1, 500)
        n_hosp = get_int("Enter number of hospitals: ", 1, 500)
        cap = get_int("Enter capacity per hospital (same for all): ", 1, 500)
        fn = input("Output filename [hospital_resident_input.txt]: ").strip() or "hospital_resident_input.txt"
        generate_hospital_resident_input(n_res, n_hosp, cap, fn)
    
    elif choice == 3:
        print("\n--- Course Allocation ---")
        n_stud = get_int("Enter number of students: ", 1, 500)
        n_cour = get_int("Enter number of courses: ", 1, 500)
        cap = get_int("Enter capacity per course (same for all): ", 1, 500)
        fn = input("Output filename [course_allocation_input.txt]: ").strip() or "course_allocation_input.txt"
        generate_course_allocation_input(n_stud, n_cour, cap, fn)
    
    print(f"\nDone! Run: python main.py {fn}")


if __name__ == '__main__':
    main()