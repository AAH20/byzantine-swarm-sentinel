"""
Data Models for Byzantine Swarm Sentinel:
Defines peer trust states, claimed target telemetry, Byzantine fault types,
and cryptographic mesh quarantine receipts for adversarial combat swarms.
Zero external dependencies (pure Python standard library).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class PeerTrustStatus(str, Enum):
    TRUSTED = "TRUSTED"
    SUSPECT = "SUSPECT"
    BYZANTINE_QUARANTINED = "BYZANTINE_QUARANTINED"


class TraitorFaultType(str, Enum):
    KINEMATIC_VIOLATION = "KINEMATIC_VIOLATION"          # Physics-breaking acceleration or teleports
    PHANTOM_TARGET_INJECTION = "PHANTOM_TARGET_INJECTION"  # Fabricated targets with zero multi-sensor corroboration
    SPLIT_BRAIN_VOTE_FLIP = "SPLIT_BRAIN_VOTE_FLIP"        # Equivocation (sending different votes to different peers)
    REPLAY_SPOOF = "REPLAY_SPOOF"                          # Replaying stale timestamped target messages


@dataclass
class PeerTargetClaim:
    peer_id: str
    target_id: str
    claimed_position_m: Tuple[float, float, float]
    claimed_velocity_mps: Tuple[float, float, float]
    claimed_accel_mps2: float
    timestamp_epoch_ms: float
    vote_decision: str  # "COMMIT_LOCK" or "ABORT_LOCK"
    evidence_signature: str = ""


@dataclass
class QuarantineReceipt:
    receipt_id: str
    traitor_peer_id: str
    fault_type: TraitorFaultType
    telemetry_evidence: Dict[str, float]
    detection_latency_ms: float
    byzantine_quorum_votes: int
    collective_quarantine_root: str
    timestamp_epoch_ms: int
