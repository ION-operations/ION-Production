"""
Retry/Fallback Engine

Implements retry with exponential backoff and fallback execution.
Preserves subdistribution monad semantics.
"""

import time
import random
from typing import Optional, Callable, Any, List
from dataclasses import dataclass
from enum import Enum
from datetime import UTC, datetime


class BackoffStrategy(Enum):
    """Backoff strategies for retries"""
    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass
class RetryAttempt:
    """Record of single retry attempt"""
    attempt_number: int
    timestamp: datetime
    success: bool
    result: Optional[Any]
    error: Optional[str]
    duration_ms: float
    backoff_delay: Optional[float]  # Delay before this attempt


@dataclass
class RetryResult:
    """Result of retry execution"""
    success: bool
    attempts: List[RetryAttempt]
    final_result: Optional[Any]
    fallback_used: bool
    total_time_ms: float


class RetryEngine:
    """
    Executes steps with retry and fallback logic.
    
    Retry Logic:
    - Attempt 1: Execute immediately
    - Attempt 2: Wait backoff_base seconds
    - Attempt 3: Wait backoff_base * 2 seconds (exponential)
    - etc.
    
    Fallback Logic:
    - If all retries exhausted, try fallback step
    - Fallback is separate execution path
    
    Subdistribution Semantics:
    - Each attempt has probability
    - Total mass ≤ 1.0
    - Failures reduce mass
    """
    
    def execute_with_retry(
        self,
        step_fn: Callable,
        max_attempts: int = 3,
        backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
        backoff_base: float = 2.0,
        max_backoff: float = 60.0,
        jitter: bool = True,
        fallback_fn: Optional[Callable] = None
    ) -> RetryResult:
        """
        Execute function with retry and optional fallback.
        
        Args:
            step_fn: Function to execute
            max_attempts: Maximum retry attempts
            backoff_strategy: Backoff strategy
            backoff_base: Base backoff delay (seconds)
            max_backoff: Maximum backoff delay (seconds)
            jitter: Whether to add random jitter
            fallback_fn: Optional fallback function
            
        Returns:
            RetryResult with execution details
        """
        start_time = time.time()
        attempts = []
        
        for attempt in range(max_attempts):
            attempt_start = time.time()
            
            # Calculate delay for this attempt (0 for first attempt)
            if attempt > 0:
                delay = self._calculate_backoff(
                    attempt - 1,  # 0-indexed for calculation
                    backoff_strategy,
                    backoff_base,
                    max_backoff,
                    jitter
                )
                time.sleep(delay)
            else:
                delay = None
            
            try:
                # Execute step
                result = step_fn()
                
                # Success!
                attempt_duration = (time.time() - attempt_start) * 1000
                attempts.append(RetryAttempt(
                    attempt_number=attempt + 1,
                    timestamp=datetime.now(UTC),
                    success=True,
                    result=result,
                    error=None,
                    duration_ms=attempt_duration,
                    backoff_delay=delay
                ))
                
                end_time = time.time()
                return RetryResult(
                    success=True,
                    attempts=attempts,
                    final_result=result,
                    fallback_used=False,
                    total_time_ms=(end_time - start_time) * 1000
                )
            
            except Exception as e:
                # Failure: record attempt
                attempt_duration = (time.time() - attempt_start) * 1000
                attempts.append(RetryAttempt(
                    attempt_number=attempt + 1,
                    timestamp=datetime.now(UTC),
                    success=False,
                    result=None,
                    error=str(e),
                    duration_ms=attempt_duration,
                    backoff_delay=delay
                ))
                
                # Check if should retry
                if attempt < max_attempts - 1:
                    # Not last attempt: continue to next iteration
                    continue
                else:
                    # Last attempt failed: try fallback
                    if fallback_fn:
                        try:
                            fallback_start = time.time()
                            fallback_result = fallback_fn()
                            fallback_duration = (time.time() - fallback_start) * 1000
                            
                            attempts.append(RetryAttempt(
                                attempt_number=attempt + 2,  # After retries
                                timestamp=datetime.now(UTC),
                                success=True,
                                result=fallback_result,
                                error=None,
                                duration_ms=fallback_duration,
                                backoff_delay=None
                            ))
                            
                            end_time = time.time()
                            return RetryResult(
                                success=True,
                                attempts=attempts,
                                final_result=fallback_result,
                                fallback_used=True,
                                total_time_ms=(end_time - start_time) * 1000
                            )
                        except Exception as fallback_error:
                            # Fallback also failed
                            pass
                    
                    # Everything failed
                    end_time = time.time()
                    return RetryResult(
                        success=False,
                        attempts=attempts,
                        final_result=None,
                        fallback_used=fallback_fn is not None,
                        total_time_ms=(end_time - start_time) * 1000
                    )
    
    def _calculate_backoff(
        self,
        attempt: int,
        strategy: BackoffStrategy,
        base: float,
        max_backoff: float,
        jitter: bool
    ) -> float:
        """
        Calculate backoff delay for retry attempt.
        
        Args:
            attempt: Attempt number (0-indexed)
            strategy: Backoff strategy
            base: Base delay
            max_backoff: Maximum delay
            jitter: Whether to add jitter
            
        Returns:
            Delay in seconds
        """
        if strategy == BackoffStrategy.CONSTANT:
            delay = base
        elif strategy == BackoffStrategy.LINEAR:
            delay = base * (attempt + 1)
        elif strategy == BackoffStrategy.EXPONENTIAL:
            delay = base * (2 ** attempt)
        else:
            delay = base
        
        # Cap at max_backoff
        delay = min(delay, max_backoff)
        
        # Add jitter to prevent thundering herd
        if jitter:
            jitter_amount = random.uniform(-delay * 0.1, delay * 0.1)
            delay = max(0, delay + jitter_amount)
        
        return delay
    
    def compute_probability_mass(self, retry_result: RetryResult) -> float:
        """
        Compute total probability mass consumed.
        
        For subdistribution monad validation.
        Each attempt consumes probability mass based on success/failure.
        
        Args:
            retry_result: Result from retry execution
            
        Returns:
            Total probability mass (should be ≤ 1.0)
        """
        # Simple model: success = 1.0, failure reduces by attempt
        if retry_result.success:
            return 1.0 - (0.1 * (len(retry_result.attempts) - 1))
        else:
            return 0.0

