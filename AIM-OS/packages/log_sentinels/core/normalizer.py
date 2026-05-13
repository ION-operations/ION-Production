"""
Log normalizer - redact PII/secrets before cloud calls.
"""

import re
import hashlib
from typing import Dict, Any

from ..types import LogRecord, RedactionPattern, RedactionConfig


class LogNormalizer:
    """
    Normalizes log records by redacting PII/secrets.
    
    Critical: Redaction happens BEFORE any cloud calls.
    Raw logs stay local, only redacted versions sent to cloud.
    """
    
    def __init__(self, config: RedactionConfig):
        self.config = config
        self.patterns = [
            self._compile_pattern(p) for p in config.patterns
        ]
    
    def normalize(self, record: LogRecord) -> LogRecord:
        """
        Normalize log record by redacting PII.
        
        Args:
            record: Original log record
            
        Returns:
            Normalized log record with redacted raw text
        """
        redacted = record.raw
        
        # Apply all redaction patterns
        for pattern in self.patterns:
            redacted = pattern["regex"].sub(pattern["replacement"], redacted)
        
        # Compute hash of original (for local storage reference)
        raw_hash = hashlib.sha256(record.raw.encode()).hexdigest()
        
        return LogRecord(
            ts=record.ts,
            source=record.source,
            level=record.level,
            template=record.template,
            vars=record.vars,
            raw_hash=raw_hash,
            raw=redacted  # Redacted version
        )
    
    def _compile_pattern(self, pattern: RedactionPattern) -> Dict[str, Any]:
        """Compile redaction pattern into regex."""
        return {
            "name": pattern.name,
            "regex": re.compile(pattern.regex, re.IGNORECASE),
            "replacement": pattern.replacement
        }

