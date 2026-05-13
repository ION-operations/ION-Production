//! Retry/Fallback: Retry and fallback logic with precedence
//!
//! This module implements retry/fallback logic for Core-PLIx:
//! - Retry budget & idempotence
//! - Fallback precedence
//! - Exponential backoff

use std::time::Duration;

/// Retry configuration
#[derive(Debug, Clone)]
pub struct RetryConfig {
    /// Maximum number of retry attempts
    pub max_attempts: usize,
    /// Backoff strategy
    pub backoff: BackoffStrategy,
    /// Whether the action is idempotent
    pub idempotent: bool,
}

/// Backoff strategy
#[derive(Debug, Clone)]
pub enum BackoffStrategy {
    /// Fixed delay between retries
    Fixed(Duration),
    /// Linear backoff: initial + (attempt * increment)
    Linear { initial: Duration, increment: Duration },
    /// Exponential backoff: initial * base^attempt
    Exponential { initial: Duration, max: Duration, jitter: bool },
}

impl BackoffStrategy {
    /// Calculate delay for attempt number
    pub fn delay(&self, attempt: usize) -> Duration {
        match self {
            BackoffStrategy::Fixed(duration) => *duration,
            BackoffStrategy::Linear { initial, increment } => {
                *initial + *increment * (attempt as u32)
            }
            BackoffStrategy::Exponential { initial, max, jitter } => {
                let delay = *initial * 2_u32.pow(attempt as u32);
                let delay = delay.min(*max);
                
                if *jitter {
                    // Add random jitter (simplified: 0-50% of delay)
                    let jitter_factor = 0.5; // TODO: Use actual random
                    delay + delay.mul_f64(jitter_factor * 0.5)
                } else {
                    delay
                }
            }
        }
    }
}

/// Fallback configuration
#[derive(Debug, Clone)]
pub struct FallbackConfig {
    /// Fallback action ID
    pub fallback_action_id: String,
    /// Fallback parameters
    pub fallback_params: std::collections::HashMap<String, crate::types::Value>,
    /// Predicate for when to trigger fallback (e.g., HTTP 4xx)
    pub trigger_on: FallbackTrigger,
}

/// Fallback trigger condition
#[derive(Debug, Clone)]
pub enum FallbackTrigger {
    /// Always trigger fallback after retry exhaustion
    Always,
    /// Trigger on specific error patterns
    ErrorPattern(String),
    /// Custom predicate
    Custom(Box<dyn Fn(&str) -> bool>),
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fixed_backoff() {
        let strategy = BackoffStrategy::Fixed(Duration::from_millis(100));
        assert_eq!(strategy.delay(0), Duration::from_millis(100));
        assert_eq!(strategy.delay(5), Duration::from_millis(100));
    }

    #[test]
    fn test_linear_backoff() {
        let strategy = BackoffStrategy::Linear {
            initial: Duration::from_millis(100),
            increment: Duration::from_millis(50),
        };
        assert_eq!(strategy.delay(0), Duration::from_millis(100));
        assert_eq!(strategy.delay(1), Duration::from_millis(150));
        assert_eq!(strategy.delay(2), Duration::from_millis(200));
    }

    #[test]
    fn test_exponential_backoff() {
        let strategy = BackoffStrategy::Exponential {
            initial: Duration::from_millis(100),
            max: Duration::from_secs(1),
            jitter: false,
        };
        assert_eq!(strategy.delay(0), Duration::from_millis(100));
        assert_eq!(strategy.delay(1), Duration::from_millis(200));
        assert_eq!(strategy.delay(2), Duration::from_millis(400));
        // Should cap at max
        assert_eq!(strategy.delay(10), Duration::from_secs(1));
    }
}

