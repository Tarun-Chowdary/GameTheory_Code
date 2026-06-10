"""
stable_matching_gs_input.py
============================
Gale-Shapley (Men-Proposing Deferred Acceptance) Algorithm
with FILE-BASED input.

USAGE
-----
  python stable_matching_gs_input.py                        # prompts for filename
  python stable_matching_gs_input.py stable_matching_input.txt

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
  • n_men <= n_women  (required for a stable matching to always exist)
  • men == women  → perfect matching (all get matched)
  • men <  women  → all men matched, some women stay unmatched

Output
------
  result[i-1] = woman matched to man i  (1-indexed, length = n_men)
"""

import sys
import os


# ─────────────────────────────────────────────────────────────────────────────
# FILE PARSER
# ─────────────────────────────────────────────────────────────────────────────

def parse_input_file(filepath):
    """
    Parse the input file and return (n_men, n_women, men_prefs, women_prefs).

    men_prefs  : dict  {man_id (1-indexed): [woman_ids in preference order]}
    women_prefs: dict  {woman_id (1-indexed): [man_ids in preference order]}
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Input file not found: '{filepath}'")

    with open(filepath, "r") as f:
        raw_lines = f.readlines()

    # Strip comments and blank lines
    lines = []
    for line in raw_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(stripped)

    if not lines:
        raise ValueError("Input file is empty (no data lines found).")

    # ── Line 0: n_men n_women ────────────────────────────────────────────────
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

    # ── Men's preferences (lines 1 … n_men) ─────────────────────────────────
    men_prefs = {}
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
        men_prefs[m] = pref

    # ── Women's preferences (lines n_men+1 … n_men+n_women) ─────────────────
    women_prefs = {}
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
        women_prefs[w] = pref

    return n_men, n_women, men_prefs, women_prefs


# ─────────────────────────────────────────────────────────────────────────────
# GALE-SHAPLEY ALGORITHM
# ─────────────────────────────────────────────────────────────────────────────

def gale_shapley(men_prefs, women_prefs, verbose=True):
    """
    Men-proposing Gale-Shapley algorithm.
    Handles n_men <= n_women.

    Returns
    -------
    result      : list  result[i-1] = woman matched to man i  (1-indexed)
    man_matched : dict  man -> woman
    unmatched_w : list  women who remain unmatched
    """
    n_men   = len(men_prefs)
    n_women = len(women_prefs)

    # Build O(1) rank lookup: women_rank[w][m] = rank of m in w's preference list
    women_rank = {
        w: {m: rank for rank, m in enumerate(pref)}
        for w, pref in women_prefs.items()
    }

    free_men      = list(men_prefs.keys())
    next_proposal = {m: 0 for m in free_men}
    woman_holds   = {}   # woman -> currently held man
    man_matched   = {}   # man   -> woman (None if unmatched)
    round_num     = 0

    if verbose:
        print("\n" + "=" * 62)
        print("  RUNNING GALE-SHAPLEY (MEN PROPOSING)")
        print("=" * 62)

    while free_men:
        round_num += 1
        proposals  = {}
        next_free  = []

        # Every free man proposes to his next-best woman
        for man in list(free_men):
            woman = men_prefs[man][next_proposal[man]]
            next_proposal[man] += 1
            proposals[man] = woman

        if verbose:
            print(f"\n  Round {round_num}  {'─'*50}")
            for m, w in proposals.items():
                print(f"    Man {m:>3}  proposes to  Woman {w}")

        rejections = []
        for man, woman in proposals.items():
            if woman not in woman_holds:
                # Woman is free — tentatively accept
                woman_holds[woman] = man
                man_matched[man]   = woman
            else:
                current = woman_holds[woman]
                if women_rank[woman][man] < women_rank[woman][current]:
                    # New proposer preferred — upgrade
                    woman_holds[woman]   = man
                    man_matched[man]     = woman
                    man_matched[current] = None
                    next_free.append(current)
                    rejections.append((woman, current, man))
                else:
                    # Keep current — reject new proposer
                    next_free.append(man)
                    rejections.append((woman, man, None))

        free_men = next_free

        if verbose:
            if rejections:
                for w, rejected, winner in rejections:
                    if winner:
                        print(f"    Woman {w:>3}  drops  Man {rejected}  →  holds  Man {winner}")
                    else:
                        print(f"    Woman {w:>3}  rejects Man {rejected}  (keeps current)")
            else:
                print("    No rejections this round.")

            held_str = "  |  ".join(
                f"Man {m}↔W{w}" for w, m in sorted(woman_holds.items())
            )
            print(f"    Held pairs: {held_str}")

    # Build output list (length = n_men)
    result = [man_matched[i] for i in sorted(man_matched.keys())]

    # Women never matched
    all_women   = set(women_prefs.keys())
    matched_w   = set(man_matched.values())
    unmatched_w = sorted(all_women - matched_w)

    if verbose:
        print(f"\n  {'='*62}")
        print("  FINAL MATCHING")
        print(f"  {'─'*62}")
        for man in sorted(man_matched.keys()):
            woman = man_matched[man]
            mr = next_proposal[man]
            wr = women_rank[woman][man] + 1
            print(f"    Man {man:>3}  →  Woman {woman:<3}"
                  f"  | man proposed to {mr} woman(s) before match"
                  f"  | woman's rank of man: {wr}/{n_men}")

        if unmatched_w:
            print(f"\n  Unmatched women: {unmatched_w}")
        else:
            print("\n  All women are matched.")

        print(f"\n  Output list : {result}")
        print(f"  Length      : {len(result)}  (one entry per man)")
        print("  result[i-1] = woman number matched to man i")
        print(f"  {'='*62}\n")

        verify_stability(man_matched, men_prefs, women_rank)

    return result, man_matched, unmatched_w


# ─────────────────────────────────────────────────────────────────────────────
# STABILITY VERIFIER
# ─────────────────────────────────────────────────────────────────────────────

def verify_stability(matching, men_prefs, women_rank, verbose=True):
    """Scan all man–woman pairs for blocking pairs."""
    inv = {w: m for m, w in matching.items()}   # woman -> man

    men_rank = {
        m: {w: rank for rank, w in enumerate(pref)}
        for m, pref in men_prefs.items()
    }

    blocking = []
    for man, woman in matching.items():
        for other_w, other_m in inv.items():
            if other_w == woman:
                continue
            if men_rank[man][other_w] < men_rank[man][woman]:
                if women_rank[other_w][man] < women_rank[other_w][other_m]:
                    blocking.append((man, other_w))

    if verbose:
        print("  Stability Verification")
        print(f"  {'─'*54}")
        if blocking:
            print(f"  ✗  Blocking pairs found: {blocking}")
        else:
            print("  ✓  No blocking pairs — the matching is STABLE")
        print()

    return len(blocking) == 0


# MAIN

def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        STABLE MATCHING — GALE-SHAPLEY ALGORITHM          ║")
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
        n_men, n_women, men_prefs, women_prefs = parse_input_file(filepath)
    except (FileNotFoundError, ValueError) as e:
        print(f"\n  ✗  ERROR: {e}")
        sys.exit(1)

    print(f"  ✓  Parsed: {n_men} men, {n_women} women")
    if n_men == n_women:
        print("     Perfect matching: everyone will be matched.")
    else:
        print(f"     All {n_men} men will be matched; "
              f"{n_women - n_men} woman/women will remain unmatched.")

    # ── Echo preferences ─────────────────────────────────────────────────────
    print("\n" + "─" * 62)
    print("  MEN'S PREFERENCES (most preferred → least preferred)")
    print("─" * 62)
    for m in sorted(men_prefs):
        print(f"    Man {m:>3}: {men_prefs[m]}")

    print("\n" + "─" * 62)
    print("  WOMEN'S PREFERENCES (most preferred → least preferred)")
    print("─" * 62)
    for w in sorted(women_prefs):
        print(f"    Woman {w:>3}: {women_prefs[w]}")

    # ── Run algorithm ────────────────────────────────────────────────────────
    result, _, unmatched = gale_shapley(men_prefs, women_prefs, verbose=True)

    print("╔══════════════════════════════════════════════════════════╗")
    print("║                     FINAL RESULT                        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\n  Output list : {result}")
    print()
    for i, w in enumerate(result, start=1):
        print(f"    Man {i:>3}  →  Woman {w}")
    if unmatched:
        print(f"\n  Unmatched women : {unmatched}")
    print()


if __name__ == "__main__":
    main()
