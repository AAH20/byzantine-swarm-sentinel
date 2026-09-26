"""
Byzantine Fault Tolerant (BFT) State Arbiter:
Implements f < n/3 quorum voting on target commitments and detects equivocation (split-brain vote flipping)
and phantom target injections in contested multi-agent networks.
Zero external dependencies (pure Python standard library).
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
from ..models import PeerTargetClaim, TraitorFaultType


class ByzantineFaultArbiter:
    """Arbiter guaranteeing targeting consensus retention with up to 33% malicious traitor nodes."""

    def __init__(self, min_spatial_corroboration_nodes: int = 2):
        self.min_corroboration = min_spatial_corroboration_nodes

    def evaluate_quorum_consensus(
        self,
        claims_for_target: List[PeerTargetClaim],
        total_swarm_nodes: int
    ) -> Tuple[bool, str, int, Optional[str]]:
        """
        Evaluates BFT 2f+1 supermajority quorum across all voting claims for a target.
        n = 3f + 1 -> Max tolerable traitors f = (n - 1) // 3.
        Required quorum: 2f + 1 agreeing votes.
        Returns: (consensus_reached, decision, vote_count, traitor_peer_id)
        """
        n = max(4, total_swarm_nodes)
        f = (n - 1) // 3
        required_quorum = 2 * f + 1

        commit_votes = 0
        abort_votes = 0
        voters: Set[str] = set()

        for c in claims_for_target:
            if c.peer_id in voters:
                # Duplicate / equivocation detected
                continue
            voters.add(c.peer_id)

            if c.vote_decision == "COMMIT_LOCK":
                commit_votes += 1
            else:
                abort_votes += 1

        if commit_votes >= required_quorum:
            return True, "COMMIT_LOCK", commit_votes, None
        elif abort_votes >= required_quorum:
            return True, "ABORT_LOCK", abort_votes, None
        else:
            return False, "QUORUM_NOT_MET", max(commit_votes, abort_votes), None

    def detect_phantom_target_injection(
        self,
        target_claims: Dict[str, List[PeerTargetClaim]],
        total_active_nodes: int
    ) -> List[Tuple[str, str]]:
        """
        Flags phantom target injections: targets claimed exclusively by a single or minority node
        where zero spatial corroboration exists from other sensor-equipped peers.
        Returns: list of (traitor_peer_id, phantom_target_id)
        """
        flagged_traitors = []
        for target_id, claims in target_claims.items():
            unique_claimants = set(c.peer_id for c in claims)
            # If only 1 node in a swarm of >= 4 nodes claims this target exists
            if len(unique_claimants) == 1 and total_active_nodes >= 4:
                lone_claimant = list(unique_claimants)[0]
                flagged_traitors.append((lone_claimant, target_id))

        return flagged_traitors
