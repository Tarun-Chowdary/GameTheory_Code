"""
Input Parser Module
Parses input text files for stable matching, hospital-resident, and course allocation problems.
"""

from typing import Dict, List, Tuple


# Section headers that contain list values (e.g., MEN: m1, m2, m3)
LIST_SECTIONS = {'MEN', 'WOMEN', 'RESIDENTS', 'HOSPITALS', 'STUDENTS', 'COURSES'}

# Section headers that contain capacity key-value pairs
CAPACITY_SECTIONS = {'HOSPITAL_CAPACITIES', 'COURSE_CAPACITIES'}

# Section headers that contain preference key-value pairs
PREFERENCE_SECTIONS = {
    'MEN_PREFERENCES', 'WOMEN_PREFERENCES',
    'RESIDENT_PREFERENCES', 'HOSPITAL_PREFERENCES',
    'STUDENT_PREFERENCES', 'COURSE_PREFERENCES'
}

ALL_SECTIONS = LIST_SECTIONS | CAPACITY_SECTIONS | PREFERENCE_SECTIONS


def parse_input_file(filepath: str) -> Tuple[str, dict]:
    """
    Parse the input file and return the problem type and data.

    Expected format:

    For Stable Matching:
    ---
    TYPE: stable_matching
    MEN: m1, m2, m3
    WOMEN: w1, w2, w3
    MEN_PREFERENCES:
    m1: w1, w2, w3
    m2: w2, w1, w3
    m3: w1, w3, w2
    WOMEN_PREFERENCES:
    w1: m1, m2, m3
    w2: m2, m1, m3
    w3: m1, m3, m2
    ---

    For Hospital-Resident:
    ---
    TYPE: hospital_resident
    RESIDENTS: r1, r2, r3, r4
    HOSPITALS: h1, h2
    HOSPITAL_CAPACITIES:
    h1: 2
    h2: 2
    RESIDENT_PREFERENCES:
    r1: h1, h2
    r2: h1, h2
    r3: h2, h1
    r4: h2, h1
    HOSPITAL_PREFERENCES:
    h1: r1, r2, r3, r4
    h2: r3, r4, r1, r2
    ---

    For Course Allocation:
    ---
    TYPE: course_allocation
    STUDENTS: s1, s2, s3, s4
    COURSES: c1, c2, c3
    COURSE_CAPACITIES:
    c1: 2
    c2: 1
    c3: 2
    STUDENT_PREFERENCES:
    s1: c1, c2, c3
    s2: c1, c3, c2
    s3: c2, c1, c3
    s4: c3, c1, c2
    COURSE_PREFERENCES:
    c1: s1, s2, s3, s4
    c2: s3, s1, s2, s4
    c3: s4, s1, s2, s3
    ---

    Returns:
        Tuple of (problem_type, data_dict)
    """
    with open(filepath, 'r') as f:
        content = f.read()

    lines = [line.strip() for line in content.split('\n') if line.strip()]

    problem_type = None
    data = {}
    current_section = None

    for line in lines:
        if line.startswith('---'):
            continue

        if line.startswith('TYPE:'):
            problem_type = line.split(':', 1)[1].strip().lower()
            data['type'] = problem_type
            current_section = None
            continue

        # Check if this line defines a section header
        # A section header is a line where the part before ':' is a known section name
        if ':' in line:
            potential_header = line.split(':', 1)[0].strip().upper()

            if potential_header in ALL_SECTIONS:
                # This is a section header line
                current_section = potential_header

                # Initialize the data structure for this section
                if current_section in (CAPACITY_SECTIONS | PREFERENCE_SECTIONS):
                    data[current_section] = {}

                # For LIST_SECTIONS, the value is on the same line, so parse it now
                if current_section in LIST_SECTIONS:
                    value = line.split(':', 1)[1].strip()
                    data[current_section] = [v.strip() for v in value.split(',')]

                continue

        # If we get here, this is a data line within a section
        if ':' in line and current_section:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if current_section in CAPACITY_SECTIONS:
                data[current_section][key] = int(value)
            elif current_section in PREFERENCE_SECTIONS:
                data[current_section][key] = [v.strip() for v in value.split(',')]

    return problem_type, data


def get_stable_matching_data(data: dict) -> Tuple[List[str], List[str], Dict[str, List[str]], Dict[str, List[str]]]:
    """Extract stable matching data from parsed input."""
    return (
        data['MEN'],
        data['WOMEN'],
        data['MEN_PREFERENCES'],
        data['WOMEN_PREFERENCES']
    )


def get_hospital_resident_data(data: dict) -> Tuple[List[str], List[str], Dict[str, List[str]], Dict[str, List[str]], Dict[str, int]]:
    """Extract hospital-resident data from parsed input."""
    return (
        data['RESIDENTS'],
        data['HOSPITALS'],
        data['RESIDENT_PREFERENCES'],
        data['HOSPITAL_PREFERENCES'],
        data['HOSPITAL_CAPACITIES']
    )


def get_course_allocation_data(data: dict) -> Tuple[List[str], List[str], Dict[str, List[str]], Dict[str, List[str]], Dict[str, int]]:
    """Extract course allocation data from parsed input."""
    return (
        data['STUDENTS'],
        data['COURSES'],
        data['STUDENT_PREFERENCES'],
        data['COURSE_PREFERENCES'],
        data['COURSE_CAPACITIES']
    )
