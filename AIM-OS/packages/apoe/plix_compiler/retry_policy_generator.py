"""
Retry Policy Generator

Generates retry policies from PLIx retry syntax.
Implements subdistribution monad semantics.
"""

from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum


class BackoffStrategy(Enum):
    """Backoff strategies"""
    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass
class PLIxRetry:
    """PLIx retry policy definition"""
    strategy: BackoffStrategy
    max_attempts: int
    backoff_base: float  # seconds
    max_backoff: Optional[float] = None


class RetryPolicyGenerator:
    """
    Generates ACL retry policies from PLIx retry syntax.
    
    PLIx Syntax:
        retry: exponential(max: 3, backoff: 2s)
        retry: linear(max: 5, backoff: 1s)
        retry: constant(max: 3, backoff: 5s)
    
    ACL Output:
        {
            "max_attempts": int,
            "backoff_strategy": str,
            "backoff_base": float,
            "max_backoff": float,
            "jitter": bool
        }
    """
    
    def generate(self, plix_retry: PLIxRetry) -> Dict[str, Any]:
        """
        Generate ACL retry policy from PLIx retry.
        
        Args:
            plix_retry: PLIx retry definition
            
        Returns:
            ACL retry policy structure
        """
        return {
            "max_attempts": plix_retry.max_attempts,
            "backoff_strategy": plix_retry.strategy.value,
            "backoff_base": plix_retry.backoff_base,
            "max_backoff": plix_retry.max_backoff or 60.0,
            "jitter": True  # Always add jitter to prevent thundering herd
        }
    
    def validate_policy(self, policy: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate retry policy configuration.
        
        Args:
            policy: Retry policy to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        max_attempts = policy.get("max_attempts", 0)
        backoff_base = policy.get("backoff_base", 0)
        max_backoff = policy.get("max_backoff", 0)
        
        # Validate max_attempts
        if max_attempts < 1:
            return False, "max_attempts must be >= 1"
        if max_attempts > 10:
            return False, "max_attempts must be <= 10 (excessive retries)"
        
        # Validate backoff_base
        if backoff_base <= 0:
            return False, "backoff_base must be positive"
        
        # Validate max_backoff
        if max_backoff < backoff_base:
            return False, "max_backoff must be >= backoff_base"
        
        # Validate strategy
        strategy = policy.get("backoff_strategy", "")
        if strategy not in ["constant", "linear", "exponential"]:
            return False, f"Invalid backoff_strategy: {strategy}"
        
        return True, None

