"""
Gale-Shapley Algorithm Module
"""

from typing import Dict, List, Set, Tuple, Optional
from collections import deque


def gale_shapley(
    proposers: List[str],
    proposee_preferences: Dict[str, List[str]],
    proposer_preferences: Dict[str, List[str]],
    capacities: Optional[Dict[str, int]] = None
) -> Dict[str, List[str]]:
    
#Gale-Shapley deferred acceptance algorithm.

    if capacities is None:
        capacities = {p: 1 for p in proposee_preferences}

    # Initialize: all proposers are free
    free_proposers = deque(proposers)

    # Current matches: proposee -> list of matched proposers
    matches = {p: [] for p in proposee_preferences}

    # Track proposals made by each proposer to avoid re-proposing
    proposals_made = {p: set() for p in proposers}

    # Create rank dictionaries for O(1) preference comparison
    # proposee_rank[proposee][proposer] = rank (lower is better)
    proposee_rank = {}
    for proposee, prefs in proposee_preferences.items():
        proposee_rank[proposee] = {proposer: idx for idx, proposer in enumerate(prefs)}

    while free_proposers:
        proposer = free_proposers.popleft()

        # Get proposer's preference list
        prefs = proposer_preferences.get(proposer, [])

        # Find the next proposee to propose to
        found_match = False
        for proposee in prefs:
            if proposee in proposals_made[proposer]:
                continue

            proposals_made[proposer].add(proposee)

            # Check if proposee has capacity
            if len(matches[proposee]) < capacities[proposee]:
                # Proposee accepts
                matches[proposee].append(proposer)
                found_match = True
                break
            else:
                # Proposee is full, check if proposer is preferred over current worst match
                current_matches = matches[proposee]
                worst_match = max(current_matches, key=lambda m: proposee_rank[proposee].get(m, float('inf')))

                if proposee_rank[proposee].get(proposer, float('inf')) < proposee_rank[proposee].get(worst_match, float('inf')):
                    # Replace worst match with new proposer
                    matches[proposee].remove(worst_match)
                    matches[proposee].append(proposer)
                    # Worst match becomes free
                    free_proposers.append(worst_match)
                    found_match = True
                    break
                # Else: rejected, continue to next preference

        if not found_match:
            # Proposer exhausted all options, remains unmatched
            pass

    return matches


def is_stable(
    matches: Dict[str, List[str]],
    proposee_preferences: Dict[str, List[str]],
    proposer_preferences: Dict[str, List[str]],
    capacities: Optional[Dict[str, int]] = None
) -> bool:
    
    # Verify if a matching is stable (no blocking pairs exist).

    if capacities is None:
        capacities = {p: 1 for p in proposee_preferences}

    # Build proposee rank and proposer rank dictionaries
    proposee_rank = {}
    for proposee, prefs in proposee_preferences.items():
        proposee_rank[proposee] = {proposer: idx for idx, proposer in enumerate(prefs)}

    proposer_rank = {}
    for proposer, prefs in proposer_preferences.items():
        proposer_rank[proposer] = {proposee: idx for idx, proposee in enumerate(prefs)}

    # Build inverse matching: proposer -> matched proposee
    proposer_match = {}
    for proposee, matched in matches.items():
        for proposer in matched:
            proposer_match[proposer] = proposee

    # Check for blocking pairs
    for proposer in proposer_preferences:
        current_match = proposer_match.get(proposer, None)

        for proposee in proposer_preferences[proposer]:
            # If proposer prefers current match over proposee, no blocking pair here
            if current_match is not None and proposer_rank[proposer].get(current_match, float('inf')) <= proposer_rank[proposer].get(proposee, float('inf')):
                break

            # Check if proposee would prefer proposer over some current match
            matched_to_proposee = matches.get(proposee, [])

            if len(matched_to_proposee) < capacities[proposee]:
                # Proposee has capacity and prefers proposer over being unmatched
                if proposer in proposee_rank[proposee]:
                    return False  # Blocking pair found
            else:
                for matched_proposer in matched_to_proposee:
                    if proposee_rank[proposee].get(proposer, float('inf')) < proposee_rank[proposee].get(matched_proposer, float('inf')):
                        return False  # Blocking pair found

    return True
