"""
stable_matching_lp_input.py
============================
Stable Matching via Integer Linear Program (ILP)
with FILE-BASED input.

USAGE
-----
  python stable_matching_lp_input.py                        # prompts for filename
  python stable_matching_lp_input.py stable_matching_input.txt

INPUT FILE FORMAT
-----------------
  • Lines starting with '#' and blank lines are ignored.
  • Line 1 (data)        : n_men  n_women
  • Next n_men lines     : each man's preference list (space-separated woman IDs,
                           most preferred FIRST, 1-indexed)
  • Next n_women lines   : each woman's preference list (space-separated man IDs,
                           most preferred FIRST, 1-indexed)

  Example (3 men, 3 women):
    3 3
    2 1 3
    1 3 2
    3 2 1
    1 3 2
    2 1 3
    3 2 1

NOTE
----
  • n_men <= n_women  (required for stable matching to exist)
  • men == women  → perfect matching
  • men <  women  → all men matched, some women unmatched

LP Formulation
--------------
Variables:   x[i][j] ∈ {0,1}   (1 iff man i matched to woman j)
Constraints:
  (1a) Each man matched to exactly one woman:   ∑_j x[i][j] = 1
  (1b) Each woman matched to at most one man:   ∑_i x[i][j] <= 1
  (2)  Stability — no blocking pair (i,j):
       ∑_{j': man i weakly prefers j'} x[i][j']
     + ∑_{i': woman j weakly prefers i'} x[i'][j]  >= 1
Objective:   Maximise ∑_i ∑_j x[i][j]  (= n_men)

Output:
  result[i-1] = woman matched to man i  (1-indexed, length = n_men)
"""

import sys
import os
import pulp


# FILE PARSER  (shared format with the GS script)

def parse_input_file(filepath):
    """
    Parse the input file and return
    (n_men, n_women, men_prefs_1, women_prefs_1)
    where keys and values are all 1-indexed.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Input file not found: '{filepath}'")

    with open(filepath, "r") as f:
        raw_lines = f.readlines()

    # Drop comments and blanks
    lines = []
    for line in raw_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(stripped)

    if not lines:
        raise ValueError("Input file is empty (no data lines found).")

    # Line 0: n_men n_women
    parts = lines[0].split()
    if len(parts) != 2:
        raise ValueError(
            f"First data line must be 'n_men n_women', got: '{lines[0]}'"
        )
    n_men, n_women = int(parts[0]), int(parts[1])

    if n_men < 1 or n_women < 1:
        raise ValueError("n_men and n_women must both be >= 1.")
    if n_men > n_women:
        raise ValueError(
            f"n_men ({n_men}) > n_women ({n_women}) — not allowed.\n"
            "  A stable matching requires n_men <= n_women."
        )

    expected_lines = 1 + n_men + n_women
    if len(lines) < expected_lines:
        raise ValueError(
            f"Expected {expected_lines} data lines "
            f"(1 header + {n_men} men + {n_women} women), "
            f"found only {len(lines)}."
        )

    men_ids   = list(range(1, n_men   + 1))
    women_ids = list(range(1, n_women + 1))

    # Men's preferences
    men_prefs_1 = {}
    for idx, m in enumerate(men_ids, start=1):
        tokens = lines[idx].split()
        if len(tokens) != n_women:
            raise ValueError(
                f"Man {m}'s preference list has {len(tokens)} entries; "
                f"expected {n_women}."
            )
        pref = [int(t) for t in tokens]
        if sorted(pref) != women_ids:
            raise ValueError(
                f"Man {m}'s preference list must be a permutation of "
                f"{women_ids}; got {pref}."
            )
        men_prefs_1[m] = pref

    # Women's preferences
    women_prefs_1 = {}
    for idx, w in enumerate(women_ids, start=1 + n_men):
        tokens = lines[idx].split()
        if len(tokens) != n_men:
            raise ValueError(
                f"Woman {w}'s preference list has {len(tokens)} entries; "
                f"expected {n_men}."
            )
        pref = [int(t) for t in tokens]
        if sorted(pref) != men_ids:
            raise ValueError(
                f"Woman {w}'s preference list must be a permutation of "
                f"{men_ids}; got {pref}."
            )
        women_prefs_1[w] = pref

    return n_men, n_women, men_prefs_1, women_prefs_1


# RANK BUILDER

def build_rank(preferences):
    """rank[person][other] = position in person's list (0 = most preferred)."""
    return {
        person: {other: rank for rank, other in enumerate(pref_list)}
        for person, pref_list in preferences.items()
    }


# ILP SOLVER

def solve_stable_matching_lp(men_prefs_1, women_prefs_1, verbose=True):
    """
    Solve the stable matching ILP using 1-indexed preferences.

    Returns
    -------
    result     : list  result[i-1] = woman (1-indexed) matched to man i
    matching_1 : dict  man (1-indexed) -> woman (1-indexed)
    """
    n_men   = len(men_prefs_1)
    n_women = len(women_prefs_1)
    perfect = (n_men == n_women)

    # Convert to 0-based for LP variable naming
    men_prefs_0   = {m-1: [w-1 for w in pref] for m, pref in men_prefs_1.items()}
    women_prefs_0 = {w-1: [m-1 for m in pref] for w, pref in women_prefs_1.items()}

    men_range   = range(n_men)
    women_range = range(n_women)

    men_rank   = build_rank(men_prefs_0)
    women_rank = build_rank(women_prefs_0)

    # ── Create problem ───────────────────────────────────────────────────────
    prob = pulp.LpProblem("Stable_Matching", pulp.LpMaximize)

    # ── Variables x[i][j] ∈ {0,1} ───────────────────────────────────────────
    x = {
        (i, j): pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
        for i in men_range
        for j in women_range
    }

    # ── Objective ────────────────────────────────────────────────────────────
    prob += pulp.lpSum(x[i, j] for i in men_range for j in women_range), "Total_Matches"

    # ── Constraint 1a: each man matched to exactly one woman ─────────────────
    for i in men_range:
        prob += (
            pulp.lpSum(x[i, j] for j in women_range) == 1,
            f"Man_{i}_assigned"
        )

    # ── Constraint 1b: each woman matched to at most (or exactly) one man ────
    for j in women_range:
        if perfect:
            prob += (
                pulp.lpSum(x[i, j] for i in men_range) == 1,
                f"Woman_{j}_assigned"
            )
        else:
            prob += (
                pulp.lpSum(x[i, j] for i in men_range) <= 1,
                f"Woman_{j}_at_most_one"
            )

    # ── Constraint 2: stability — no blocking pair ───────────────────────────
    for i in men_range:
        for j in women_range:
            rank_j_for_i = men_rank[i][j]
            rank_i_for_j = women_rank[j][i]

            weakly_better_for_man   = [jj for jj in women_range
                                        if men_rank[i][jj]   <= rank_j_for_i]
            weakly_better_for_woman = [ii for ii in men_range
                                        if women_rank[j][ii] <= rank_i_for_j]

            prob += (
                pulp.lpSum(x[i, jj] for jj in weakly_better_for_man)
              + pulp.lpSum(x[ii, j] for ii in weakly_better_for_woman)
              >= 1,
                f"Stability_{i}_{j}"
            )

    # ── Solve ────────────────────────────────────────────────────────────────
    solver = pulp.PULP_CBC_CMD(msg=0)
    prob.solve(solver)

    # ── Print summary ─────────────────────────────────────────────────────────
    if verbose:
        print("\n" + "=" * 62)
        print("  STABLE MATCHING — LP FORMULATION")
        print("=" * 62)
        print(f"\n  Solver status : {pulp.LpStatus[prob.status]}")
        print(f"  Objective     : {pulp.value(prob.objective):.0f}  (= n_men = {n_men})")
        print(f"  Variables     : {n_men * n_women}  binary  (x_i_j)")
        con_assign = n_men + n_women
        con_stab   = n_men * n_women
        print(f"  Constraints   : {con_assign} assignment  +  {con_stab} stability"
              f"  =  {con_assign + con_stab} total")
        print()

    # ── Extract matching (0-based → 1-based) ─────────────────────────────────
    matching_1 = {}
    for i in men_range:
        for j in women_range:
            val = pulp.value(x[i, j])
            if val is not None and round(val) == 1:
                matching_1[i + 1] = j + 1

    if verbose:
        women_rank_1 = build_rank(women_prefs_1)
        men_rank_1   = build_rank(men_prefs_1)

        print("  Matching:  man → woman")
        for man_1, woman_1 in sorted(matching_1.items()):
            mr = men_rank_1[man_1][woman_1] + 1
            wr = women_rank_1[woman_1][man_1] + 1
            print(f"    Man {man_1:>3}  →  Woman {woman_1:<3}"
                  f"  | man's rank of woman: {mr}/{n_women}"
                  f"  | woman's rank of man: {wr}/{n_men}")

        unmatched_w = sorted(set(range(1, n_women+1)) - set(matching_1.values()))
        if unmatched_w:
            print(f"\n  Unmatched women: {unmatched_w}")
        else:
            print("\n  All women are matched.")

        result_display = [matching_1[i] for i in range(1, n_men+1)]
        print(f"\n  Output list (1-indexed): {result_display}")
        print("  result[k-1] = woman matched to man k")
        print()

        # Stability check
        print("  Stability check:")
        inv_1    = {w: m for m, w in matching_1.items()}
        blocking = []
        for man, woman in matching_1.items():
            for other_w, other_m in inv_1.items():
                if other_w == woman:
                    continue
                if (men_rank_1[man][other_w] < men_rank_1[man][woman] and
                        women_rank_1[other_w][man] < women_rank_1[other_w][other_m]):
                    blocking.append((man, other_w))

        if blocking:
            print(f"    ✗  Blocking pairs: {blocking}")
        else:
            print("    ✓  No blocking pairs — matching is STABLE")
        print("=" * 62)

    result = [matching_1[i] for i in range(1, n_men+1)]
    return result, matching_1


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║      STABLE MATCHING — INTEGER LINEAR PROGRAM (ILP)     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # ── Resolve input file ───────────────────────────────────────────────────
    if len(sys.argv) >= 2:
        filepath = sys.argv[1]
    else:
        filepath = input("  Enter path to input file: ").strip()

    print(f"\n  Reading from: {filepath}")

    # ── Parse ────────────────────────────────────────────────────────────────
    try:
        n_men, n_women, men_prefs_1, women_prefs_1 = parse_input_file(filepath)
    except (FileNotFoundError, ValueError) as e:
        print(f"\n  ✗  ERROR: {e}")
        sys.exit(1)

    print(f"  ✓  Parsed: {n_men} men, {n_women} women")
    if n_men == n_women:
        print("     Perfect matching: everyone will be matched.")
    else:
        print(f"     All {n_men} men matched; "
              f"{n_women - n_men} woman/women may be unmatched.")

    if n_men > 50:
        print("\n  ⚠  Warning: ILP may be slow for n > 50. Consider")
        print("     using stable_matching_gs_input.py instead.")

    # ── Echo preferences ─────────────────────────────────────────────────────
    print("\n" + "─" * 62)
    print("  MEN'S PREFERENCES (most preferred → least preferred)")
    print("─" * 62)
    for m in sorted(men_prefs_1):
        print(f"    Man {m:>3}: {men_prefs_1[m]}")

    print("\n" + "─" * 62)
    print("  WOMEN'S PREFERENCES (most preferred → least preferred)")
    print("─" * 62)
    for w in sorted(women_prefs_1):
        print(f"    Woman {w:>3}: {women_prefs_1[w]}")

    # ── Solve ────────────────────────────────────────────────────────────────
    result, matching = solve_stable_matching_lp(men_prefs_1, women_prefs_1, verbose=True)

    # ── Final clean output ───────────────────────────────────────────────────
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                     FINAL RESULT                        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\n  Output list : {result}")
    print()
    for i, w in enumerate(result, start=1):
        print(f"    Man {i:>3}  →  Woman {w}")
    print()


if __name__ == "__main__":
    main()
