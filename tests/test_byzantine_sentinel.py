"""
Unit Tests for Byzantine Swarm Sentinel:
Validates kinematic physics auditing, BFT 2f+1 quorum consensus under 30% traitors,
phantom target isolation, and cryptographic quarantine receipts.
Zero external dependencies (pure Python standard library).
"""

import time
import unittest
from byzantine_swarm_sentinel import (
    PeerTrustStatus,
    TraitorFaultType,
    PeerTargetClaim,
    KinematicPhysicsAuditor,
    ByzantineFaultArbiter,
    MeshQuarantineEngine,
    ByzantineSwarmSentinel
)


class TestByzantineSwarmSentinel(unittest.TestCase):

    def setUp(self):
        self.sentinel = ByzantineSwarmSentinel(node_id="LOCAL-SENTINEL-01", total_swarm_nodes=10)

    def test_kinematic_physics_auditor(self):
        auditor = KinematicPhysicsAuditor()

        # Claim with impossible 65G acceleration (> 30G limit)
        impossible_claim = PeerTargetClaim(
            peer_id="TRAITOR-DRONE-09",
            target_id="TGT-TEST-01",
            claimed_position_m=(1000.0, 500.0, 100.0),
            claimed_velocity_mps=(400.0, 0.0, 0.0),
            claimed_accel_mps2=650.0,  # 650 m/s^2 ≈ 66G
            timestamp_epoch_ms=time.time() * 1000,
            vote_decision="COMMIT_LOCK"
        )

        is_valid, fault, reason = auditor.audit_claim_physics(impossible_claim)
        self.assertFalse(is_valid)
        self.assertEqual(fault, TraitorFaultType.KINEMATIC_VIOLATION)

    def test_phantom_target_injection_detection(self):
        claims = []
        now = time.time() * 1000

        # Traitor injects a lone phantom target with 0 corroboration from 9 other nodes
        phantom_claim = PeerTargetClaim(
            peer_id="COMPROMISED-NODE-03",
            target_id="PHANTOM-GHOST-99",
            claimed_position_m=(5000.0, 5000.0, 200.0),
            claimed_velocity_mps=(200.0, 0.0, 0.0),
            claimed_accel_mps2=15.0,
            timestamp_epoch_ms=now,
            vote_decision="COMMIT_LOCK"
        )
        claims.append(phantom_claim)

        # 9 honest nodes all claim genuine target
        for i in range(1, 10):
            c = PeerTargetClaim(
                peer_id=f"HONEST-NODE-{i:02d}",
                target_id="GENUINE-CRUISE-MISSILE",
                claimed_position_m=(12000.0, 4000.0, 50.0),
                claimed_velocity_mps=(-800.0, 0.0, 0.0),
                claimed_accel_mps2=20.0,
                timestamp_epoch_ms=now,
                vote_decision="COMMIT_LOCK"
            )
            claims.append(c)

        consensus_decisions, receipts = self.sentinel.process_incoming_claims(claims)

        # Phantom target must be rejected!
        self.assertNotIn("PHANTOM-GHOST-99", consensus_decisions)
        # Genuine target must achieve consensus!
        self.assertEqual(consensus_decisions.get("GENUINE-CRUISE-MISSILE"), "COMMIT_LOCK")
        # Traitor must be quarantined
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0].traitor_peer_id, "COMPROMISED-NODE-03")
        self.assertEqual(receipts[0].fault_type, TraitorFaultType.PHANTOM_TARGET_INJECTION)

    def test_bft_quorum_consensus_under_30_percent_traitors(self):
        # 10 total nodes: 7 honest voting COMMIT_LOCK, 3 traitors voting ABORT_LOCK
        now = time.time() * 1000
        claims = []

        # 7 honest
        for i in range(1, 8):
            c = PeerTargetClaim(
                peer_id=f"HONEST-NODE-{i:02d}",
                target_id="HOSTILE-TARGET-01",
                claimed_position_m=(8000.0, 2000.0, 100.0),
                claimed_velocity_mps=(-500.0, 0.0, 0.0),
                claimed_accel_mps2=10.0,
                timestamp_epoch_ms=now,
                vote_decision="COMMIT_LOCK"
            )
            claims.append(c)

        # 3 traitors
        for j in range(8, 11):
            c = PeerTargetClaim(
                peer_id=f"TRAITOR-NODE-{j:02d}",
                target_id="HOSTILE-TARGET-01",
                claimed_position_m=(8000.0, 2000.0, 100.0),
                claimed_velocity_mps=(-500.0, 0.0, 0.0),
                claimed_accel_mps2=10.0,
                timestamp_epoch_ms=now,
                vote_decision="ABORT_LOCK"  # Maliciously opposing lock
            )
            claims.append(c)

        consensus_decisions, _ = self.sentinel.process_incoming_claims(claims)

        # 7 >= 2f + 1 (for n=10, f=3, required=7) -> COMMIT_LOCK achieved!
        self.assertEqual(consensus_decisions.get("HOSTILE-TARGET-01"), "COMMIT_LOCK")


if __name__ == "__main__":
    unittest.main()
