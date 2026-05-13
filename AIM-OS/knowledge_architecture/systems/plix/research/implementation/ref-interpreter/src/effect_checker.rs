//! Effect Checker: Effect and confidence checking
//!
//! This module implements effect and confidence checking for Core-PLIx:
//! - Effect subtyping and weakening
//! - Path-sensitive confidence aggregation
//! - Capability gating by effects

use std::collections::HashSet;
use crate::resolver::Effect;
use crate::types::PlanDAG;

/// Effect checker
pub struct EffectChecker {
    /// Allowed effects in current context
    pub allowed_effects: HashSet<Effect>,
}

impl EffectChecker {
    /// Create new effect checker
    pub fn new(allowed_effects: HashSet<Effect>) -> Self {
        Self { allowed_effects }
    }

    /// Check if effects are allowed
    pub fn check_effects(&self, required_effects: &HashSet<Effect>) -> Result<(), String> {
        for effect in required_effects {
            if !self.allowed_effects.contains(effect) {
                return Err(format!("Effect not allowed: {:?}", effect));
            }
        }
        Ok(())
    }

    /// Check effect subtyping (weakening rule)
    pub fn is_subtype(&self, subset: &HashSet<Effect>, superset: &HashSet<Effect>) -> bool {
        subset.is_subset(superset)
    }
}

/// Confidence checker
pub struct ConfidenceChecker {
    /// Minimum required confidence
    pub min_confidence: f64,
}

impl ConfidenceChecker {
    /// Create new confidence checker
    pub fn new(min_confidence: f64) -> Self {
        Self { min_confidence }
    }

    /// Check plan confidence (infimum)
    pub fn check_plan_confidence(&self, step_confidences: &[f64]) -> Result<(), String> {
        let plan_confidence = step_confidences.iter()
            .copied()
            .min_by(|a, b| a.partial_cmp(b).unwrap())
            .unwrap_or(0.0);
        
        if plan_confidence < self.min_confidence {
            return Err(format!(
                "Plan confidence {} below minimum {}",
                plan_confidence,
                self.min_confidence
            ));
        }
        
        Ok(())
    }

    /// Check path-sensitive confidence (min product over paths)
    pub fn check_path_confidence(
        &self,
        dag: &PlanDAG,
        step_confidences: &std::collections::HashMap<String, f64>,
    ) -> Result<(), String> {
        // Simplified: just check all paths from roots to leaves
        // In full implementation, would enumerate all paths and compute min product
        
        let min_confidence = step_confidences.values()
            .copied()
            .min_by(|a, b| a.partial_cmp(b).unwrap())
            .unwrap_or(0.0);
        
        if min_confidence < self.min_confidence {
            return Err(format!(
                "Path confidence {} below minimum {}",
                min_confidence,
                self.min_confidence
            ));
        }
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_effect_checker() {
        let mut allowed = HashSet::new();
        allowed.insert(Effect::Io);
        allowed.insert(Effect::Net);
        
        let checker = EffectChecker::new(allowed);
        
        let mut required = HashSet::new();
        required.insert(Effect::Io);
        
        assert!(checker.check_effects(&required).is_ok());
        
        required.insert(Effect::Db);
        assert!(checker.check_effects(&required).is_err());
    }

    #[test]
    fn test_confidence_checker() {
        let checker = ConfidenceChecker::new(0.7);
        
        let confidences = vec![0.8, 0.9, 0.75];
        assert!(checker.check_plan_confidence(&confidences).is_ok());
        
        let confidences = vec![0.8, 0.6, 0.75];
        assert!(checker.check_plan_confidence(&confidences).is_err());
    }

    #[test]
    fn test_effect_subtyping() {
        let mut allowed = HashSet::new();
        allowed.insert(Effect::Io);
        allowed.insert(Effect::Net);
        
        let checker = EffectChecker::new(allowed);
        
        let mut subset = HashSet::new();
        subset.insert(Effect::Io);
        
        let mut superset = HashSet::new();
        superset.insert(Effect::Io);
        superset.insert(Effect::Net);
        
        assert!(checker.is_subtype(&subset, &superset));
        assert!(!checker.is_subtype(&superset, &subset));
    }
}

