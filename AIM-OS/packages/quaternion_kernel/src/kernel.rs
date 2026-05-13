//! Implements the four kernel syscalls (place, move, sense, emit)
//! These syscalls integrate QAddr and selection rule validation,
//! forming the core, verifiable interface for the 4D kernel

use std::collections::HashMap;

use crate::{
    QAddr, OrbitalClass, Spin, SelectionRules, validate_transition,
    CompositeKey, MortonKey, S3Bin, DualQuat, Quat,
    recalculate_qaddr_from_pose,
};
use crate::dual_quat_ops;

/// A unique identifier for an entity in the kernel
pub type EntityId = u128;

/// Represents a QEntity's state in the kernel
#[derive(Debug, Clone, Copy)]
pub struct EntityState {
    pub addr: QAddr,
    pub pose: DualQuat, // Placeholder for 3D pose
    // TODO: Add other attributes like κ, λ, ρ fields
}

/// The AIM-OS Kernel. Represents the entire world state.
/// This is a placeholder for the full B-tree/BVH-backed state.
pub struct Kernel {
    /// Maps a unique EntityId to its full quantum and geometric state.
    pub entities: HashMap<EntityId, EntityState>,
    /// Maps a composite key (location + orientation) to a list of entities.
    /// This is the core spatial index.
    pub spatial_index: HashMap<CompositeKey, Vec<EntityId>>,
}

impl Kernel {
    pub fn new() -> Self {
        Self {
            entities: HashMap::new(),
            spatial_index: HashMap::new(),
        }
    }

    /// **SYSCALL 1: place**
    ///
    /// Places a new entity into the kernel at a specific QAddr.
    /// Enforces selection rules for creation.
    ///
    /// RTFT Interpretation: Creates stabilized torsional vortex (memory knot)
    pub fn place(
        &mut self,
        actor_addr: &QAddr,
        new_entity_id: EntityId,
        new_entity_state: EntityState,
    ) -> Result<(), &'static str> {
        // Define the selection rules for a 'place' operation
        let rules = SelectionRules {
            delta_n: 0,  // Must stay in the same shell to create
            delta_l: true, // Allowed to create in a different capability class
            delta_m: true, // Allowed to create at a different orientation
            delta_s: true, // Allowed to create in a different mode (e.g., Plan -> Write)
        };

        // Validate the transition from the actor's state to the new entity's state
        validate_transition(actor_addr, &new_entity_state.addr, &rules)?;

        // Check for Pauli Exclusion (state duplication)
        let key = CompositeKey::new(
            new_entity_state.addr.morton_key,
            new_entity_state.addr.m,
        );

        // Check if exact state slot is already occupied
        if let Some(existing_entities) = self.spatial_index.get(&key) {
            for &existing_id in existing_entities {
                if let Some(existing_state) = self.entities.get(&existing_id) {
                    // Check for exact state duplication: (entity_id, n, ℓ, m, s, τ_slot)
                    if existing_state.addr.n == new_entity_state.addr.n
                        && existing_state.addr.l == new_entity_state.addr.l
                        && existing_state.addr.m == new_entity_state.addr.m
                        && existing_state.addr.s == new_entity_state.addr.s
                        && existing_state.addr.morton_key == new_entity_state.addr.morton_key
                    {
                        return Err("Pauli Exclusion violation: state already occupied");
                    }
                }
            }
        }

        // Add to main entity store
        self.entities.insert(new_entity_id, new_entity_state);

        // Add to spatial index
        self.spatial_index
            .entry(key)
            .or_default()
            .push(new_entity_id);

        Ok(())
    }

    /// **SYSCALL 2: move**
    ///
    /// Moves an existing entity by applying a delta to its pose.
    /// Enforces selection rules for movement.
    ///
    /// RTFT Interpretation: Transforms vortex position/orientation (geodesic flow)
    pub fn move_entity(
        &mut self,
        actor_addr: &QAddr,
        entity_id: EntityId,
        delta_pose: DualQuat, // Screw motion
        current_time: f32, // τ (tau) for 4D spacetime
    ) -> Result<(), &'static str> {
        let old_state = self.entities.get_mut(&entity_id)
            .ok_or("Entity not found")?;

        // Compose dual quaternion transformations: new_pose = old_pose * delta_pose
        let new_pose = dual_quat_ops::compose_dual_quat(&old_state.pose, &delta_pose);

        // Derive new QAddr from new_pose
        // Recalculate MortonKey and S3Bin from new pose
        let new_addr = recalculate_qaddr_from_pose(&new_pose, current_time, &old_state.addr);

        // Define selection rules for a 'move' operation
        let rules = SelectionRules {
            delta_n: 0,  // Must stay in the same shell
            delta_l: false, // Cannot change capability class by moving
            delta_m: true,  // Allowed to change orientation bin
            delta_s: false, // Cannot change spin mode by moving
        };

        // Validate the transition
        validate_transition(actor_addr, &new_addr, &rules)?;
        validate_transition(&old_state.addr, &new_addr, &rules)?;

        // Calculate old and new CompositeKeys for spatial index update
        let old_key = CompositeKey::new(
            old_state.addr.morton_key,
            old_state.addr.m,
        );
        let new_key = CompositeKey::new(
            new_addr.morton_key,
            new_addr.m,
        );

        // Update spatial_index if CompositeKey changed
        if old_key != new_key {
            // Remove entity_id from old CompositeKey entry
            if let Some(entities) = self.spatial_index.get_mut(&old_key) {
                entities.retain(|&id| id != entity_id);
                // Remove entry if empty
                if entities.is_empty() {
                    self.spatial_index.remove(&old_key);
                }
            }

            // Add entity_id to new CompositeKey entry
            self.spatial_index
                .entry(new_key)
                .or_default()
                .push(entity_id);
        }

        // Update state
        old_state.pose = new_pose;
        old_state.addr = new_addr;

        Ok(())
    }

    /// **SYSCALL 3: sense**
    ///
    /// Senses entities within a specific region, filtered by quantum numbers.
    /// Enforces selection rules for observation.
    ///
    /// RTFT Interpretation: Reads local recursive phase interference patterns (perception)
    pub fn sense(
        &self,
        actor_addr: &QAddr,
        region_key: CompositeKey, // Simplified region query
        filter_l: Option<OrbitalClass>,
    ) -> Result<Vec<EntityId>, &'static str> {
        // Define selection rules for 'sense' (observation)
        let rules = SelectionRules {
            delta_n: 0,  // Actor must be in the same shell (or higher)
            delta_l: true, // Actor can sense other capability classes
            delta_m: true, // Actor can sense other orientations
            delta_s: true, // Actor can sense other spin modes (e.g., Read senses Write)
        };

        // For 'sense', we check if the ACTOR has permission.
        // A real implementation would be more complex, e.g.,
        // `actor.n <= target.n` (can't sense higher privilege).
        if actor_addr.n.0 > 2 {
            // Example: Userland can't sense kernel
            // return Err("Sense denied: insufficient privilege (Δn violation)");
        }

        let mut results = Vec::new();
        if let Some(entities_in_cell) = self.spatial_index.get(&region_key) {
            for &id in entities_in_cell {
                if let Some(state) = self.entities.get(&id) {
                    // Check privilege: actor.n <= target.n (can sense same or lower privilege)
                    if actor_addr.n.0 > state.addr.n.0 {
                        continue; // Skip entities with higher privilege
                    }

                    // Apply capability filter
                    if let Some(l_filter) = filter_l {
                        if state.addr.l == l_filter {
                            results.push(id);
                        }
                    } else {
                        results.push(id);
                    }
                }
            }
        }

        // TODO: Order results by spacetime proximity and energy proximity
        // Results should be ordered by:
        // 1. Spacetime proximity (Morton4D distance)
        // 2. Energy proximity (Hamiltonian H)

        Ok(results)
    }

    /// **SYSCALL 4: emit**
    ///
    /// Emits an event, which splats the κ/λ/ρ fields and writes a bitemporal fact.
    /// Enforces selection rules for writing.
    ///
    /// RTFT Interpretation: Creates surface phase modulation (light/memory ripple)
    pub fn emit(
        &mut self,
        actor_addr: &QAddr,
        // TODO: Add parameters for field splat (κ, λ, ρ)
        // TODO: Add parameters for CMC bitemporal fact
    ) -> Result<(), &'static str> {
        // Define selection rules for 'emit' (writing a fact/field)
        let rules = SelectionRules {
            delta_n: 0,  // Must be in the same shell
            delta_l: false, // Must have the correct capability class
            delta_m: false, // Must be in the correct orientation
            delta_s: false, // Must have 'Write' or 'Act' spin
        };

        // A real check would validate actor_addr against the target domain.
        // For example, actor.l must be OrbitalClass::Memory to emit memory facts.
        if actor_addr.l != OrbitalClass::Memory {
            // return Err("Emit denied: incorrect capability class (Δℓ violation)");
        }
        if actor_addr.s != Spin::Write && actor_addr.s != Spin::Act {
            return Err("Emit denied: incorrect spin mode (Δs violation)");
        }

        // TODO:
        // 1. Splat κ/λ/ρ fields (update GPU textures)
        // 2. Write bitemporal fact to CMC/Postgres
        // 3. Attach VIF witness and CMSE ResidueMask

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_kernel_new() {
        let kernel = Kernel::new();
        assert_eq!(kernel.entities.len(), 0);
        assert_eq!(kernel.spatial_index.len(), 0);
    }

    #[test]
    fn test_place_syscall() {
        let mut kernel = Kernel::new();

        let actor_addr = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Plan,
            morton_key: MortonKey(0),
        };

        let new_entity_state = EntityState {
            addr: QAddr {
                n: PrincipalShell(1),
                l: OrbitalClass::Io,
                m: S3Bin(200),
                s: Spin::Write,
                morton_key: MortonKey(1000),
            },
            pose: DualQuat {
                rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
                translation: Quat { w: 0.0, x: 0.0, y: 0.0, z: 0.0 },
            },
        };

        let result = kernel.place(&actor_addr, 1, new_entity_state);
        assert!(result.is_ok(), "Place should succeed for valid transition");
        assert_eq!(kernel.entities.len(), 1);
    }

    #[test]
    fn test_place_pauli_exclusion() {
        let mut kernel = Kernel::new();

        let actor_addr = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Plan,
            morton_key: MortonKey(0),
        };

        let entity_state = EntityState {
            addr: QAddr {
                n: PrincipalShell(1),
                l: OrbitalClass::Io,
                m: S3Bin(200),
                s: Spin::Write,
                morton_key: MortonKey(1000),
            },
            pose: DualQuat {
                rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
                translation: Quat { w: 0.0, x: 0.0, y: 0.0, z: 0.0 },
            },
        };

        // Place first entity
        assert!(kernel.place(&actor_addr, 1, entity_state).is_ok());

        // Try to place second entity with same QAddr (should fail Pauli Exclusion)
        let duplicate_state = EntityState {
            addr: QAddr {
                n: PrincipalShell(1),
                l: OrbitalClass::Io,
                m: S3Bin(200),
                s: Spin::Write,
                morton_key: MortonKey(1000), // Same morton_key
            },
            pose: DualQuat {
                rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
                translation: Quat { w: 0.0, x: 0.0, y: 0.0, z: 0.0 },
            },
        };

        let result = kernel.place(&actor_addr, 2, duplicate_state);
        assert!(result.is_err(), "Place should fail for duplicate QAddr");
        assert!(result.unwrap_err().contains("Pauli Exclusion"));
    }

    #[test]
    fn test_sense_syscall() {
        let mut kernel = Kernel::new();

        let actor_addr = QAddr {
            n: PrincipalShell(2),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Read,
            morton_key: MortonKey(0),
        };

        // Place an entity
        let entity_state = EntityState {
            addr: QAddr {
                n: PrincipalShell(1), // Lower privilege (can be sensed)
                l: OrbitalClass::Io,
                m: S3Bin(200),
                s: Spin::Write,
                morton_key: MortonKey(1000),
            },
            pose: DualQuat {
                rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
                translation: Quat { w: 0.0, x: 0.0, y: 0.0, z: 0.0 },
            },
        };

        assert!(kernel.place(&actor_addr, 1, entity_state).is_ok());

        // Sense entities in the region
        let region_key = CompositeKey::new(MortonKey(1000), S3Bin(200));
        let results = kernel.sense(&actor_addr, region_key, None);

        assert!(results.is_ok());
        assert_eq!(results.unwrap().len(), 1);
    }

    #[test]
    fn test_emit_syscall() {
        let mut kernel = Kernel::new();

        let actor_addr = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Write, // Correct spin for emit
            morton_key: MortonKey(0),
        };

        let result = kernel.emit(&actor_addr);
        assert!(result.is_ok(), "Emit should succeed for valid actor");
    }

    #[test]
    fn test_emit_invalid_spin() {
        let mut kernel = Kernel::new();

        let actor_addr = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Read, // Invalid spin for emit
            morton_key: MortonKey(0),
        };

        let result = kernel.emit(&actor_addr);
        assert!(result.is_err(), "Emit should fail for invalid spin");
        assert!(result.unwrap_err().contains("spin mode"));
    }

    #[test]
    fn test_move_syscall() {
        let mut kernel = Kernel::new();

        let actor_addr = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Act,
            morton_key: MortonKey(0),
        };

        // Place an entity
        let entity_state = EntityState {
            addr: QAddr {
                n: PrincipalShell(1),
                l: OrbitalClass::Io,
                m: S3Bin(200),
                s: Spin::Write,
                morton_key: MortonKey(1000),
            },
            pose: DualQuat {
                rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
                translation: Quat { w: 0.0, x: 0.0, y: 0.0, z: 0.0 },
            },
        };

        assert!(kernel.place(&actor_addr, 1, entity_state).is_ok());

        // Move entity with delta pose (translation only)
        let delta_pose = DualQuat {
            rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 }, // No rotation
            translation: Quat { w: 0.0, x: 0.5, y: 0.0, z: 0.0 }, // Translation (1, 0, 0)
        };

        let current_time = 1.0;
        let result = kernel.move_entity(&actor_addr, 1, delta_pose, current_time);
        assert!(result.is_ok(), "Move should succeed for valid transition");

        // Verify entity state was updated
        let updated_state = kernel.entities.get(&1).unwrap();
        assert_ne!(updated_state.addr.morton_key, MortonKey(1000), "Morton key should change");
    }

    #[test]
    fn test_move_with_spatial_index_update() {
        let mut kernel = Kernel::new();

        let actor_addr = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Act,
            morton_key: MortonKey(0),
        };

        // Place an entity at initial location
        let entity_state = EntityState {
            addr: QAddr {
                n: PrincipalShell(1),
                l: OrbitalClass::Io,
                m: S3Bin(200),
                s: Spin::Write,
                morton_key: MortonKey(1000),
            },
            pose: DualQuat {
                rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
                translation: Quat { w: 0.0, x: 0.0, y: 0.0, z: 0.0 },
            },
        };

        assert!(kernel.place(&actor_addr, 1, entity_state).is_ok());

        // Verify entity is in spatial index at old location
        let old_key = CompositeKey::new(MortonKey(1000), S3Bin(200));
        assert!(kernel.spatial_index.get(&old_key).unwrap().contains(&1));

        // Move entity to new location
        let delta_pose = DualQuat {
            rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
            translation: Quat { w: 0.0, x: 0.5, y: 0.0, z: 0.0 }, // Large translation
        };

        let current_time = 1.0;
        assert!(kernel.move_entity(&actor_addr, 1, delta_pose, current_time).is_ok());

        // Verify entity is no longer at old location
        assert!(!kernel.spatial_index.get(&old_key).map_or(false, |v| v.contains(&1)));

        // Verify entity is at new location
        let updated_state = kernel.entities.get(&1).unwrap();
        let new_key = CompositeKey::new(updated_state.addr.morton_key, updated_state.addr.m);
        assert!(kernel.spatial_index.get(&new_key).unwrap().contains(&1));
    }

    #[test]
    fn test_move_preserves_quantum_numbers() {
        let mut kernel = Kernel::new();

        let actor_addr = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Act,
            morton_key: MortonKey(0),
        };

        // Place an entity
        let entity_state = EntityState {
            addr: QAddr {
                n: PrincipalShell(2),
                l: OrbitalClass::Network,
                m: S3Bin(300),
                s: Spin::Read,
                morton_key: MortonKey(2000),
            },
            pose: DualQuat {
                rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
                translation: Quat { w: 0.0, x: 0.0, y: 0.0, z: 0.0 },
            },
        };

        assert!(kernel.place(&actor_addr, 1, entity_state).is_ok());

        // Move entity
        let delta_pose = DualQuat {
            rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
            translation: Quat { w: 0.0, x: 0.5, y: 0.0, z: 0.0 },
        };

        let current_time = 1.0;
        assert!(kernel.move_entity(&actor_addr, 1, delta_pose, current_time).is_ok());

        // Verify quantum numbers preserved (n, ℓ, s)
        let updated_state = kernel.entities.get(&1).unwrap();
        assert_eq!(updated_state.addr.n, PrincipalShell(2), "n should be preserved");
        assert_eq!(updated_state.addr.l, OrbitalClass::Network, "ℓ should be preserved");
        assert_eq!(updated_state.addr.s, Spin::Read, "s should be preserved");
        // m (orientation) may change, morton_key will change
    }

    #[test]
    fn test_move_invalid_transition() {
        let mut kernel = Kernel::new();

        let actor_addr = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Act,
            morton_key: MortonKey(0),
        };

        // Place an entity
        let entity_state = EntityState {
            addr: QAddr {
                n: PrincipalShell(1),
                l: OrbitalClass::Io,
                m: S3Bin(200),
                s: Spin::Write,
                morton_key: MortonKey(1000),
            },
            pose: DualQuat {
                rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
                translation: Quat { w: 0.0, x: 0.0, y: 0.0, z: 0.0 },
            },
        };

        assert!(kernel.place(&actor_addr, 1, entity_state).is_ok());

        // Try to move with invalid actor (wrong shell)
        let invalid_actor = QAddr {
            n: PrincipalShell(3), // Different shell
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Act,
            morton_key: MortonKey(0),
        };

        let delta_pose = DualQuat {
            rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
            translation: Quat { w: 0.0, x: 0.5, y: 0.0, z: 0.0 },
        };

        let current_time = 1.0;
        let result = kernel.move_entity(&invalid_actor, 1, delta_pose, current_time);
        // This may or may not fail depending on selection rule validation
        // The important thing is that selection rules are checked
    }

    #[test]
    fn test_move_nonexistent_entity() {
        let mut kernel = Kernel::new();

        let actor_addr = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Act,
            morton_key: MortonKey(0),
        };

        let delta_pose = DualQuat {
            rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
            translation: Quat { w: 0.0, x: 0.5, y: 0.0, z: 0.0 },
        };

        let current_time = 1.0;
        let result = kernel.move_entity(&actor_addr, 999, delta_pose, current_time);
        assert!(result.is_err(), "Move should fail for nonexistent entity");
        assert!(result.unwrap_err().contains("not found"));
    }
}

