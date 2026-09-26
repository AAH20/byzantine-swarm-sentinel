"""
Kinematic Physics & Trajectory Consistency Auditor:
Audits peer sensor claims against physical aerodynamics and momentum conservation.
Detects physics-defying phantom trajectories, instant velocity jumps, and spoofed sensor claims.
Zero external dependencies (pure Python standard library).
"""

from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple
from ..models import PeerTargetClaim, TraitorFaultType


def euclidean_distance_3d(p1: Tuple[float, float, float], p2: Tuple[float, float, float]) -> float:
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)


class KinematicPhysicsAuditor:
    """Audits claimed target maneuvers against rigid-body physical boundaries."""

    def __init__(
        self,
        max_aerodynamic_speed_mps: float = 1200.0,    # Max Mach 3.5 atmospheric flight
        max_sustained_accel_g: float = 30.0,           # Max 30G missile turn limit
        max_teleport_jump_mps: float = 1500.0
    ):
        self.max_speed = max_aerodynamic_speed_mps
        self.max_accel_mps2 = max_sustained_accel_g * 9.81
        self.max_jump = max_teleport_jump_mps
        self._history: Dict[str, Dict[str, Tuple[Tuple[float, float, float], float]]] = {}

    def audit_claim_physics(
        self,
        claim: PeerTargetClaim
    ) -> Tuple[bool, Optional[TraitorFaultType], str]:
        """
        Evaluates physical consistency of peer's target claim.
        Returns: (is_physically_valid, fault_type, diagnostic_reason)
        """
        vx, vy, vz = claim.claimed_velocity_mps
        speed = math.sqrt(vx * vx + vy * vy + vz * vz)

        # 1. Absolute velocity ceiling check
        if speed > self.max_speed:
            return (
                False,
                TraitorFaultType.KINEMATIC_VIOLATION,
                f"Physically impossible velocity: {speed:.1f} m/s exceeds max aerodynamic bound ({self.max_speed:.1f} m/s)."
            )

        # 2. Acceleration limit check
        if claim.claimed_accel_mps2 > self.max_accel_mps2:
            return (
                False,
                TraitorFaultType.KINEMATIC_VIOLATION,
                f"Physically impossible turn acceleration: {claim.claimed_accel_mps2:.1f} m/s² exceeds max airframe tolerance ({self.max_accel_mps2:.1f} m/s²)."
            )

        # 3. Trajectory continuity / teleportation check across consecutive claims
        peer_id = claim.peer_id
        target_id = claim.target_id

        if peer_id in self._history and target_id in self._history[peer_id]:
            last_pos, last_time = self._history[peer_id][target_id]
            dt = max(0.001, (claim.timestamp_epoch_ms - last_time) / 1000.0)
            displacement = euclidean_distance_3d(claim.claimed_position_m, last_pos)
            implied_speed = displacement / dt

            if implied_speed > self.max_jump:
                return (
                    False,
                    TraitorFaultType.KINEMATIC_VIOLATION,
                    f"Kinematic teleport jump detected: displacement {displacement:.1f}m in {dt:.3f}s implies {implied_speed:.1f} m/s (> {self.max_jump:.1f} m/s)."
                )

        # Update history
        if peer_id not in self._history:
            self._history[peer_id] = {}
        self._history[peer_id][target_id] = (claim.claimed_position_m, claim.timestamp_epoch_ms)

        return True, None, "Claim conforms to rigid-body physical bounds."
