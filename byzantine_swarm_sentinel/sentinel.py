"""
Master Byzantine Swarm Sentinel Orchestrator:
Unifies kinematic physics auditing, BFT 2f+1 state consensus, and peer mesh quarantine.
Zero external dependencies (pure Python standard library).
"""

from __future__ import annotations
import time
from typing import Dict, List, Optional, Tuple
from .models import (
    PeerTargetClaim,
    TraitorFaultType,
    QuarantineReceipt,
    PeerTrustStatus
)
from .detector.kinematic_physics_auditor import KinematicPhysicsAuditor
from .consensus.byzantine_fault_arbiter import ByzantineFaultArbiter
from .quarantine.mesh_quarantine_engine import MeshQuarantineEngine


class ByzantineSwarmSentinel:
    """Master guardian isolating Byzantine traitors and spoofed sensors in combat swarms."""

    def __init__(self, node_id: str, total_swarm_nodes: int = 10):
        self.node_id = node_id
        self.total_nodes = total_swarm_nodes
        self.physics_auditor = KinematicPhysicsAuditor()
        self.bft_arbiter = ByzantineFaultArbiter()
        self.quarantine_engine = MeshQuarantineEngine()

    def process_incoming_claims(
        self,
        claims: List[PeerTargetClaim]
    ) -> Tuple[Dict[str, str], List[QuarantineReceipt]]:
        """
        Processes a batch of peer claims:
        1. Audits kinematic physics of each claim.
        2. Quarantines nodes that submit impossible physics.
        3. Identifies phantom target injections.
        4. Reaches BFT 2f+1 consensus on genuine targets among non-quarantined peers.
        Returns: (target_consensus_decisions {target_id: decision}, new_quarantine_receipts)
        """
        receipts: List[QuarantineReceipt] = []
        valid_claims_by_target: Dict[str, List[PeerTargetClaim]] = {}

        # 1. Physics Audit
        for claim in claims:
            self.quarantine_engine.register_peer(claim.peer_id)

            # Skip already quarantined traitors
            if self.quarantine_engine.is_peer_quarantined(claim.peer_id):
                continue

            is_valid, fault, reason = self.physics_auditor.audit_claim_physics(claim)
            if not is_valid and fault is not None:
                rcpt = self.quarantine_engine.penalize_peer(
                    peer_id=claim.peer_id,
                    fault=fault,
                    telemetry={"claimed_accel": claim.claimed_accel_mps2, "speed": claim.claimed_velocity_mps[0]}
                )
                if rcpt:
                    receipts.append(rcpt)
                continue

            if claim.target_id not in valid_claims_by_target:
                valid_claims_by_target[claim.target_id] = []
            valid_claims_by_target[claim.target_id].append(claim)

        # 2. Phantom Target Injection Check
        phantoms = self.bft_arbiter.detect_phantom_target_injection(
            valid_claims_by_target,
            self.total_nodes
        )
        for traitor_id, phantom_tid in phantoms:
            rcpt = self.quarantine_engine.penalize_peer(
                peer_id=traitor_id,
                fault=TraitorFaultType.PHANTOM_TARGET_INJECTION,
                telemetry={"target_id_hash": float(hash(phantom_tid) % 10000)}
            )
            if rcpt:
                receipts.append(rcpt)
            # Remove phantom target from consideration
            if phantom_tid in valid_claims_by_target:
                del valid_claims_by_target[phantom_tid]

        # 3. BFT Quorum Consensus on Remaining Targets
        consensus_decisions: Dict[str, str] = {}
        for target_id, t_claims in valid_claims_by_target.items():
            consensus, decision, votes, _ = self.bft_arbiter.evaluate_quorum_consensus(
                claims_for_target=t_claims,
                total_swarm_nodes=self.total_nodes
            )
            if consensus:
                consensus_decisions[target_id] = decision
            else:
                consensus_decisions[target_id] = "QUORUM_NOT_MET"

        return consensus_decisions, receipts
