//! Resolver: Namespace resolution (Σ)
//!
//! This module implements the resolver `Σ = (Tags, Actions)` for:
//! - Tag resolution: `resolve_tag : Σ × Tag → Value`
//! - Action resolution: `resolve_action : Σ × Id → PrimAction`

use std::collections::HashMap;
use crate::types::Value;

/// Resolver: Σ = (Tags, Actions)
#[derive(Debug, Clone)]
pub struct Resolver {
    /// Tag map: Tag → Value
    pub tags: HashMap<String, Value>,
    /// Action map: Id → PrimAction
    pub actions: HashMap<String, PrimAction>,
}

impl Resolver {
    /// Create new resolver
    pub fn new() -> Self {
        Self {
            tags: HashMap::new(),
            actions: HashMap::new(),
        }
    }

    /// Resolve tag: `resolve_tag(Σ, tag) → Value`
    pub fn resolve_tag(&self, tag: &str) -> Option<Value> {
        self.tags.get(tag).cloned()
    }

    /// Resolve action: `resolve_action(Σ, id) → PrimAction`
    pub fn resolve_action(&self, id: &str) -> Option<PrimAction> {
        self.actions.get(id).cloned()
    }

    /// Register tag
    pub fn register_tag(&mut self, tag: String, value: Value) {
        self.tags.insert(tag, value);
    }

    /// Register action
    pub fn register_action(&mut self, id: String, action: PrimAction) {
        self.actions.insert(id, action);
    }
}

impl Default for Resolver {
    fn default() -> Self {
        Self::new()
    }
}

/// Primitive action
#[derive(Debug, Clone)]
pub struct PrimAction {
    /// Action identifier
    pub id: String,
    /// Action name
    pub name: String,
    /// Required parameters
    pub params: Vec<String>,
    /// Effects
    pub effects: Vec<Effect>,
    /// Confidence function (returns confidence for given params and state)
    pub confidence_fn: Box<dyn Fn(&HashMap<String, Value>, &HashMap<String, Value>) -> f64>,
}

/// Effect type
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Effect {
    Io,
    Net,
    Db,
    Compensable,
    Idempotent,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resolver_new() {
        let resolver = Resolver::new();
        assert_eq!(resolver.tags.len(), 0);
        assert_eq!(resolver.actions.len(), 0);
    }

    #[test]
    fn test_resolve_tag() {
        let mut resolver = Resolver::new();
        resolver.register_tag("test:tag".to_string(), Value::String("test_value".to_string()));
        
        let value = resolver.resolve_tag("test:tag");
        assert_eq!(value, Some(Value::String("test_value".to_string())));
    }

    #[test]
    fn test_resolve_action() {
        let mut resolver = Resolver::new();
        let action = PrimAction {
            id: "test_action".to_string(),
            name: "test_action".to_string(),
            params: vec!["param1".to_string()],
            effects: vec![Effect::Io],
            confidence_fn: Box::new(|_, _| 0.9),
        };
        resolver.register_action("test_action".to_string(), action.clone());
        
        let resolved = resolver.resolve_action("test_action");
        assert!(resolved.is_some());
    }
}

