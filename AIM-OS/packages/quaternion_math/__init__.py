"""
PLIx Quaternion Extension: Quaternion Math Library

Phase 1, Weeks 1-2: Foundation - Quaternion Math Library

This module provides quaternion operations with determinism guarantees:
- QQuat: Basic quaternion operations
- DualQuat: Dual quaternions for 3D screw motions
- DoubleQuat: Double quaternions for 4D rotations
- Sign canonicalization for deterministic operations

RTFT Interpretation:
- Quaternionic rotational state = torsional vortex
- Hamilton product = recursive phase memory fusion
- Sign canonicalization = deterministic breath alignment
"""

from typing import Tuple, Optional
import math
import numpy as np
from dataclasses import dataclass


@dataclass
class QQuat:
    """
    Quaternion: q = q0 + q1*i + q2*j + q3*k
    
    RTFT: Quaternionic rotational state = torsional vortex
    """
    q0: float  # Scalar part (w)
    q1: float  # i component (x)
    q2: float  # j component (y)
    q3: float  # k component (z)
    
    def __post_init__(self):
        """Ensure quaternion is normalized (only if non-zero)"""
        # Don't normalize if this is being used as a dual part (will be handled by DualQuat)
        # Only normalize if it's a standalone quaternion
        norm = self.norm()
        if norm > 1e-10:
            # Check if this looks like it might be a dual part (very small q0, but not too small norm)
            # Dual parts have q0=0 and should preserve their scale
            if abs(self.q0) < 1e-10:
                # This is a pure quaternion - could be a dual part
                # Don't normalize if norm is reasonable (preserve scale for dual quaternions)
                if norm > 0.01:  # Reasonable scale for dual part
                    return
            self.normalize()
    
    def normalize(self) -> 'QQuat':
        """Normalize quaternion to unit quaternion"""
        norm = self.norm()
        if norm > 1e-10:
            self.q0 /= norm
            self.q1 /= norm
            self.q2 /= norm
            self.q3 /= norm
        else:
            # If norm is too small, set to identity
            self.q0 = 1.0
            self.q1 = 0.0
            self.q2 = 0.0
            self.q3 = 0.0
        return self
    
    def norm(self) -> float:
        """Compute quaternion norm: ||q|| = sqrt(q0² + q1² + q2² + q3²)"""
        return math.sqrt(self.q0**2 + self.q1**2 + self.q2**2 + self.q3**2)
    
    def conjugate(self) -> 'QQuat':
        """Compute quaternion conjugate: q* = q0 - q1*i - q2*j - q3*k"""
        return QQuat(self.q0, -self.q1, -self.q2, -self.q3)
    
    def inverse(self) -> 'QQuat':
        """Compute quaternion inverse: q⁻¹ = q* / ||q||²"""
        norm_sq = self.norm() ** 2
        if norm_sq < 1e-10:
            raise ValueError("Cannot invert zero quaternion")
        conj = self.conjugate()
        return QQuat(
            conj.q0 / norm_sq,
            conj.q1 / norm_sq,
            conj.q2 / norm_sq,
            conj.q3 / norm_sq
        )
    
    def __add__(self, other: 'QQuat') -> 'QQuat':
        """Quaternion addition"""
        return QQuat(
            self.q0 + other.q0,
            self.q1 + other.q1,
            self.q2 + other.q2,
            self.q3 + other.q3
        )
    
    def __mul__(self, other: 'QQuat') -> 'QQuat':
        """
        Hamilton product (non-commutative): q₁ * q₂
        
        RTFT: Non-commutative fusion = recursive phase memory
        
        Formula:
        q₁ * q₂ = (q₁₀q₂₀ - q₁₁q₂₁ - q₁₂q₂₂ - q₁₃q₂₃) +
                   (q₁₀q₂₁ + q₁₁q₂₀ + q₁₂q₂₃ - q₁₃q₂₂)*i +
                   (q₁₀q₂₂ - q₁₁q₂₃ + q₁₂q₂₀ + q₁₃q₂₁)*j +
                   (q₁₀q₂₃ + q₁₁q₂₂ - q₁₂q₂₁ + q₁₃q₂₀)*k
        """
        return QQuat(
            self.q0 * other.q0 - self.q1 * other.q1 - self.q2 * other.q2 - self.q3 * other.q3,
            self.q0 * other.q1 + self.q1 * other.q0 + self.q2 * other.q3 - self.q3 * other.q2,
            self.q0 * other.q2 - self.q1 * other.q3 + self.q2 * other.q0 + self.q3 * other.q1,
            self.q0 * other.q3 + self.q1 * other.q2 - self.q2 * other.q1 + self.q3 * other.q0
        )
    
    def canonicalize(self) -> 'QQuat':
        """
        Sign canonicalization for determinism.
        
        Always choose q or -q consistently (prefer positive q0, or if q0=0, prefer positive q1, etc.)
        RTFT: Deterministic breath alignment
        """
        if self.q0 < 0 or (abs(self.q0) < 1e-10 and self.q1 < 0) or \
           (abs(self.q0) < 1e-10 and abs(self.q1) < 1e-10 and self.q2 < 0) or \
           (abs(self.q0) < 1e-10 and abs(self.q1) < 1e-10 and abs(self.q2) < 1e-10 and self.q3 < 0):
            return QQuat(-self.q0, -self.q1, -self.q2, -self.q3)
        return QQuat(self.q0, self.q1, self.q2, self.q3)
    
    def slerp(self, other: 'QQuat', t: float) -> 'QQuat':
        """
        Spherical Linear Interpolation (SLERP)
        
        Smooth interpolation between two quaternions on S³
        """
        # Ensure both are normalized
        q1 = self.normalize()
        q2 = other.normalize()
        
        # Compute dot product
        dot = q1.q0 * q2.q0 + q1.q1 * q2.q1 + q1.q2 * q2.q2 + q1.q3 * q2.q3
        
        # If dot < 0, negate q2 for shorter path
        if dot < 0:
            q2 = QQuat(-q2.q0, -q2.q1, -q2.q2, -q2.q3)
            dot = -dot
        
        # If quaternions are very close, use linear interpolation
        if dot > 0.9995:
            result = QQuat(
                q1.q0 + t * (q2.q0 - q1.q0),
                q1.q1 + t * (q2.q1 - q1.q1),
                q1.q2 + t * (q2.q2 - q1.q2),
                q1.q3 + t * (q2.q3 - q1.q3)
            )
            return result.normalize()
        
        # Compute angle
        theta = math.acos(dot)
        sin_theta = math.sin(theta)
        
        # SLERP formula
        w1 = math.sin((1 - t) * theta) / sin_theta
        w2 = math.sin(t * theta) / sin_theta
        
        result = QQuat(
            w1 * q1.q0 + w2 * q2.q0,
            w1 * q1.q1 + w2 * q2.q1,
            w1 * q1.q2 + w2 * q2.q2,
            w1 * q1.q3 + w2 * q2.q3
        )
        return result.normalize()
    
    def rotate_vector(self, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Rotate 3D vector by quaternion: v' = q * v * q⁻¹
        
        RTFT: Geometric transformation of vortex orientation
        """
        # Convert vector to pure quaternion
        v_quat = QQuat(0.0, v[0], v[1], v[2])
        
        # Rotate: q * v * q⁻¹
        rotated = self * v_quat * self.inverse()
        
        return (rotated.q1, rotated.q2, rotated.q3)
    
    def to_rotation_matrix(self) -> np.ndarray:
        """Convert quaternion to 3x3 rotation matrix"""
        w, x, y, z = self.q0, self.q1, self.q2, self.q3
        
        return np.array([
            [1 - 2*(y**2 + z**2), 2*(x*y - w*z), 2*(x*z + w*y)],
            [2*(x*y + w*z), 1 - 2*(x**2 + z**2), 2*(y*z - w*x)],
            [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x**2 + y**2)]
        ])
    
    @classmethod
    def from_axis_angle(cls, axis: Tuple[float, float, float], angle: float) -> 'QQuat':
        """Create quaternion from axis-angle representation"""
        axis_norm = math.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
        if axis_norm < 1e-10:
            return cls(1.0, 0.0, 0.0, 0.0)  # Identity
        
        axis_normalized = (axis[0]/axis_norm, axis[1]/axis_norm, axis[2]/axis_norm)
        half_angle = angle / 2.0
        sin_half = math.sin(half_angle)
        
        return cls(
            math.cos(half_angle),
            axis_normalized[0] * sin_half,
            axis_normalized[1] * sin_half,
            axis_normalized[2] * sin_half
        )
    
    @classmethod
    def identity(cls) -> 'QQuat':
        """Create identity quaternion (no rotation)"""
        return cls(1.0, 0.0, 0.0, 0.0)
    
    def __repr__(self) -> str:
        return f"QQuat({self.q0:.6f}, {self.q1:.6f}, {self.q2:.6f}, {self.q3:.6f})"


@dataclass
class DualQuat:
    """
    Dual Quaternion: dq = q_r + ε * q_d
    
    Where:
    - q_r: rotation quaternion (unit quaternion)
    - q_d: translation quaternion (pure quaternion)
    - ε: dual unit (ε² = 0)
    
    Represents screw motion (rotation + translation) in 3D space.
    RTFT: Dual quaternion pose = stabilized torsional vortex position
    """
    rotation: QQuat  # q_r: rotation
    translation: QQuat  # q_d: translation (pure quaternion, q0=0)
    
    def __post_init__(self):
        """Ensure rotation is normalized"""
        self.rotation = self.rotation.normalize()
        # Ensure translation is pure (q0 = 0)
        self.translation = QQuat(0.0, self.translation.q1, self.translation.q2, self.translation.q3)
    
    def __mul__(self, other: 'DualQuat') -> 'DualQuat':
        """
        Dual quaternion multiplication (screw motion composition)
        
        dq₁ * dq₂ = (q_r₁ * q_r₂) + ε * (q_r₁ * q_d₂ + q_d₁ * q_r₂)
        
        Note: The dual part addition preserves scale (no normalization)
        """
        new_rotation = self.rotation * other.rotation
        
        # Dual part: q_r₁ * q_d₂ + q_d₁ * q_r₂
        # Compute each term separately to avoid normalization issues
        term1_raw = self.rotation * other.translation
        term2_raw = self.translation * other.rotation
        
        # Extract vector parts directly (avoid creating QQuat that might normalize)
        # Since both terms are pure quaternions (q0=0), we can add component-wise
        new_translation = QQuat(
            0.0,
            term1_raw.q1 + term2_raw.q1,
            term1_raw.q2 + term2_raw.q2,
            term1_raw.q3 + term2_raw.q3
        )
        
        return DualQuat(new_rotation, new_translation)
    
    def transform_point(self, point: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Transform 3D point by dual quaternion (screw motion)
        
        RTFT: Geometric transformation of vortex position
        
        For dual quaternion dq = q_r + ε * q_d where q_d = 0.5 * q_r * t:
        - Rotate: p_rot = q_r * p * q_r⁻¹
        - Extract translation: Since q_d = 0.5 * q_r * t, we have q_r⁻¹ * q_d = 0.5 * t
        - So: t = 2 * q_r⁻¹ * q_d
        - Result: p' = p_rot + t
        """
        # Rotate point: q_r * p * q_r⁻¹
        rotated = self.rotation.rotate_vector(point)
        
        # Extract translation: t = 2 * q_r⁻¹ * q_d
        # Since q_d = 0.5 * q_r * t, we have: q_r⁻¹ * q_d = q_r⁻¹ * (0.5 * q_r * t) = 0.5 * t
        # So: t = 2 * q_r⁻¹ * q_d
        rot_inv = self.rotation.inverse()
        t_extracted = rot_inv * self.translation
        # Extract vector part and scale by 2
        translation = (2.0 * t_extracted.q1, 2.0 * t_extracted.q2, 2.0 * t_extracted.q3)
        
        # Apply translation
        return (
            rotated[0] + translation[0],
            rotated[1] + translation[1],
            rotated[2] + translation[2]
        )
    
    def inverse(self) -> 'DualQuat':
        """
        Compute dual quaternion inverse
        
        For dual quaternion dq = q_r + ε * q_d:
        dq⁻¹ = q_r⁻¹ - ε * q_r⁻¹ * q_d * q_r⁻¹
        
        This ensures dq * dq⁻¹ = 1 + ε * 0 (identity dual quaternion)
        
        Note: The dual part of the inverse is computed as -q_r⁻¹ * q_d * q_r⁻¹
        """
        rot_inv = self.rotation.inverse()
        
        # Compute dual part inverse: -q_r⁻¹ * q_d * q_r⁻¹
        # First compute q_r⁻¹ * q_d
        temp = rot_inv * self.translation
        # Then multiply by q_r⁻¹ again
        trans_inv_quat = temp * rot_inv
        
        # Negate and ensure pure quaternion (q0 should be ~0 due to quaternion algebra)
        # Extract only vector part
        trans_inv = QQuat(0.0, -trans_inv_quat.q1, -trans_inv_quat.q2, -trans_inv_quat.q3)
        
        return DualQuat(rot_inv, trans_inv)
    
    @classmethod
    def from_rotation_translation(
        cls,
        rotation: QQuat,
        translation: Tuple[float, float, float]
    ) -> 'DualQuat':
        """
        Create dual quaternion from rotation and translation
        
        For dual quaternion dq = q_r + ε * q_d representing screw motion:
        - q_r: rotation quaternion
        - q_d: dual part encoding translation
        - Formula: q_d = 0.5 * q_r * t (where t is pure quaternion representing translation)
        """
        # Normalize rotation first
        rot_normalized = rotation.normalize()
        
        # Convert translation to pure quaternion
        t_quat = QQuat(0.0, translation[0], translation[1], translation[2])
        
        # Compute dual part: q_d = 0.5 * q_r * t
        # Create QQuat without normalization (we'll handle it manually)
        dual_part_raw = rot_normalized * t_quat
        # Extract dual part (pure quaternion, don't normalize)
        dual_part = QQuat(0.0, 0.5 * dual_part_raw.q1, 0.5 * dual_part_raw.q2, 0.5 * dual_part_raw.q3)
        
        # Create DualQuat - translation won't be normalized due to our __post_init__ logic
        return cls(rot_normalized, dual_part)
    
    def __repr__(self) -> str:
        return f"DualQuat(rotation={self.rotation}, translation={self.translation})"


@dataclass
class DoubleQuat:
    """
    Double Quaternion: (q_L, q_R) ∈ SU(2) × SU(2) ≅ SO(4)
    
    Represents 4D rotations.
    RTFT: Left/right rotors = chirality lanes, policy paths
    """
    left: QQuat   # q_L: left rotor
    right: QQuat  # q_R: right rotor
    
    def __post_init__(self):
        """Ensure both rotors are normalized"""
        self.left = self.left.normalize()
        self.right = self.right.normalize()
    
    def __mul__(self, other: 'DoubleQuat') -> 'DoubleQuat':
        """Double quaternion multiplication"""
        return DoubleQuat(self.left * other.left, self.right * other.right)
    
    def rotate_4d_vector(self, v: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        """
        Rotate 4D vector by double quaternion
        
        For 4D rotation, we use the isomorphism SO(4) ≅ SU(2) × SU(2)
        """
        # Convert to quaternion pair
        v_left = QQuat(v[0], v[1], v[2], v[3])
        v_right = QQuat(v[0], -v[1], -v[2], -v[3])
        
        # Rotate: q_L * v_left * q_L⁻¹, q_R * v_right * q_R⁻¹
        rotated_left = self.left * v_left * self.left.inverse()
        rotated_right = self.right * v_right * self.right.inverse()
        
        # Extract 4D vector
        return (
            (rotated_left.q0 + rotated_right.q0) / 2.0,
            (rotated_left.q1 - rotated_right.q1) / 2.0,
            (rotated_left.q2 - rotated_right.q2) / 2.0,
            (rotated_left.q3 - rotated_right.q3) / 2.0
        )
    
    def __repr__(self) -> str:
        return f"DoubleQuat(left={self.left}, right={self.right})"


# Module-level convenience functions

def canonicalize_quaternion(q: QQuat) -> QQuat:
    """Canonicalize quaternion for determinism"""
    return q.canonicalize()


def quaternion_distance(q1: QQuat, q2: QQuat) -> float:
    """Compute distance between two quaternions on S³"""
    dot = q1.q0 * q2.q0 + q1.q1 * q2.q1 + q1.q2 * q2.q2 + q1.q3 * q2.q3
    dot = max(-1.0, min(1.0, dot))  # Clamp to [-1, 1]
    return math.acos(abs(dot))


__all__ = ['QQuat', 'DualQuat', 'DoubleQuat', 'canonicalize_quaternion', 'quaternion_distance']

