"""
Windower - create rolling time windows from log records.
"""

from typing import List, Optional
import time
import uuid

from ..types import LogRecord, Window


class Windower:
    """
    Creates rolling time windows from log records.
    
    Windows are created based on:
    - Time window (roll_seconds)
    - Minimum records (min_records)
    - Burst threshold (burst_threshold)
    """
    
    def __init__(
        self,
        roll_seconds: int = 60,
        min_records: int = 12,
        burst_threshold: float = 2.5
    ):
        self.roll_seconds = roll_seconds
        self.min_records = min_records
        self.burst_threshold = burst_threshold
        
        # Track baseline for burst detection
        self.baseline_rate = 0.0
    
    async def create_window(
        self,
        records: List[LogRecord]
    ) -> Optional[Window]:
        """
        Create rolling window from log records.
        
        Args:
            records: List of log records
            
        Returns:
            Window if sufficient records, None otherwise
        """
        if len(records) < self.min_records:
            return None
        
        now = int(time.time())
        window_start = now - self.roll_seconds
        
        # Filter records in time window
        window_records = [
            r for r in records
            if window_start <= int(r.ts) <= now
        ]
        
        if len(window_records) < self.min_records:
            return None
        
        # Check burst threshold
        current_rate = len(window_records) / self.roll_seconds
        if self.baseline_rate > 0:
            burst_ratio = current_rate / self.baseline_rate
            if burst_ratio < self.burst_threshold:
                # Not a burst, skip window
                return None
        
        # Update baseline
        if self.baseline_rate == 0:
            self.baseline_rate = current_rate
        else:
            # Exponential moving average
            self.baseline_rate = 0.7 * self.baseline_rate + 0.3 * current_rate
        
        # Create window
        window = Window(
            id=str(uuid.uuid4()),
            source=window_records[0].source if window_records else "unknown",
            from_time=window_start,
            to_time=now,
            size=len(window_records),
            templates={},  # Will be filled by template miner
            sample=[r.raw[:100] for r in window_records[:10]]  # Sample for Scout
        )
        
        return window

