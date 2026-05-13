"""
Log collectors - collect logs from various sources.
"""

from typing import List
from abc import ABC, abstractmethod

from ..types import LogRecord


class LogCollector(ABC):
    """Base class for log collectors."""
    
    @abstractmethod
    async def collect(self) -> List[LogRecord]:
        """Collect logs from source."""
        pass


class BrowserConsoleCollector(LogCollector):
    """Collect logs from browser console via WebSocket."""
    
    def __init__(self, ws_url: str = "ws://localhost:7001/console"):
        self.ws_url = ws_url
        self.ws = None
    
    async def collect(self) -> List[LogRecord]:
        """Collect logs from browser console."""
        # In production, would:
        # 1. Connect to WebSocket
        # 2. Listen for console messages
        # 3. Convert to LogRecord objects
        # 4. Return list
        
        # Stub implementation
        return []


class TerminalCollector(LogCollector):
    """Collect logs from terminal output."""
    
    def __init__(self, log_path: str = "./logs/dev-terminal.log"):
        self.log_path = log_path
    
    async def collect(self) -> List[LogRecord]:
        """Collect logs from terminal log file."""
        # In production, would:
        # 1. Tail log file
        # 2. Parse log lines
        # 3. Convert to LogRecord objects
        # 4. Return list
        
        # Stub implementation
        return []


class BackendAPICollector(LogCollector):
    """Collect logs from backend API via OpenTelemetry."""
    
    def __init__(self, endpoint: str = "http://localhost:4318/v1/logs"):
        self.endpoint = endpoint
    
    async def collect(self) -> List[LogRecord]:
        """Collect logs from backend API."""
        # In production, would:
        # 1. Connect to OpenTelemetry endpoint
        # 2. Query logs
        # 3. Convert to LogRecord objects
        # 4. Return list
        
        # Stub implementation
        return []

