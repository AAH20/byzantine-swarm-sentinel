"""
Byzantine Swarm Sentinel:
Adversarial Swarm Traitor Isolation & Sensor-Spoofing Immunity Benchmark under Contested EW.
Zero external dependencies (pure Python standard library).
"""

from .models import (
    PeerTrustStatus,
    TraitorFaultType,
    PeerTargetClaim,
    QuarantineReceipt
)
from .detector.kinematic_physics_auditor import KinematicPhysicsAuditor
from .consensus.byzantine_fault_arbiter import ByzantineFaultArbiter
from .quarantine.mesh_quarantine_engine import MeshQuarantineEngine
from .sentinel import ByzantineSwarmSentinel

__all__ = [
    "PeerTrustStatus",
    "TraitorFaultType",
    "PeerTargetClaim",
    "QuarantineReceipt",
    "KinematicPhysicsAuditor",
    "ByzantineFaultArbiter",
    "MeshQuarantineEngine",
    "ByzantineSwarmSentinel"
]

__version__ = "1.0.0"
