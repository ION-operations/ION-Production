# packages/mcp_data_integration/file_system_monitor.py
"""
File System Monitor - Real-time monitoring of AETHER_MEMORY directory

This module provides real-time monitoring of the AETHER_MEMORY directory,
automatically detecting file changes and updating the index accordingly.

Features:
- Real-time file change detection
- Automatic index updates
- File creation, modification, and deletion handling
- Batch processing for efficiency
- Error handling and recovery
"""

import os
import sys
import time
import threading
import yaml
import re
from pathlib import Path
from typing import Callable, Optional, Set, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import logging

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Try to import dependency tracker and cross-reference generator
try:
    from scripts.track_doc_dependencies import parse_frontmatter, build_dependency_graph
    from scripts.generate_cross_references import CrossReferenceGenerator
    DOC_UPDATE_AVAILABLE = True
except ImportError:
    DOC_UPDATE_AVAILABLE = False
    logger.warning("Doc update functionality not available (scripts not found)")

# Try to import watchdog, fall back to polling if not available
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    FileSystemEventHandler = object

logger = logging.getLogger(__name__)

@dataclass
class FileChangeEvent:
    """Represents a file change event."""
    event_type: str  # 'created', 'modified', 'deleted', 'moved'
    file_path: str
    timestamp: float
    old_path: Optional[str] = None  # For moved events

class FileSystemMonitor:
    """
    Real-time file system monitor for AETHER_MEMORY directory.
    
    This class monitors the AETHER_MEMORY directory for changes and
    automatically updates the index when files are created, modified, or deleted.
    """
    
    def __init__(self, aether_memory_path: str, callback: Optional[Callable[[FileChangeEvent], None]] = None, 
                 doc_update_callback: Optional[Callable[[FileChangeEvent], None]] = None,
                 monitor_source_files: bool = False):
        """
        Initialize the FileSystemMonitor.
        
        Args:
            aether_memory_path: Path to AETHER_MEMORY directory
            callback: Callback function to handle file change events
            doc_update_callback: Callback function to trigger doc updates when sources change
            monitor_source_files: If True, also monitor source files (SOURCE_OF_TRUTH.yaml, etc.)
        """
        self.aether_memory_path = Path(aether_memory_path)
        self.callback = callback
        self.doc_update_callback = doc_update_callback
        self.monitor_source_files = monitor_source_files
        self.observer = None
        self.is_monitoring = False
        self.monitor_thread = None
        self.polling_interval = 1.0  # seconds
        self.last_check_time = 0
        self.file_timestamps: Dict[str, float] = {}
        
        # Source files to monitor (if enabled)
        self.source_files: Set[Path] = set()
        if monitor_source_files:
            self._initialize_source_files()
        
        # Initialize file timestamps
        self._initialize_file_timestamps()
        
        logger.info(f"FileSystemMonitor initialized for {aether_memory_path}")
        if monitor_source_files:
            logger.info(f"Monitoring {len(self.source_files)} source files for doc updates")
    
    def start_monitoring(self):
        """Start monitoring the file system."""
        if self.is_monitoring:
            logger.warning("File system monitoring is already running")
            return
        
        if WATCHDOG_AVAILABLE:
            self._start_watchdog_monitoring()
        else:
            self._start_polling_monitoring()
        
        self.is_monitoring = True
        logger.info("File system monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring the file system."""
        if not self.is_monitoring:
            logger.warning("File system monitoring is not running")
            return
        
        if WATCHDOG_AVAILABLE and self.observer:
            self.observer.stop()
            self.observer.join()
        elif self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        self.is_monitoring = False
        logger.info("File system monitoring stopped")
    
    def _initialize_source_files(self):
        """Initialize list of source files to monitor from dependency graph."""
        if not DOC_UPDATE_AVAILABLE:
            logger.warning("Doc update functionality not available, skipping source file initialization")
            return
        
        try:
            # Load dependency graph to find source files
            _, doc_deps = build_dependency_graph()
            
            # Extract source files from doc dependencies
            for doc_path, dep_info in doc_deps.items():
                source_of_truth = dep_info.get("source_of_truth")
                if source_of_truth:
                    source_path = project_root / source_of_truth
                    if source_path.exists():
                        self.source_files.add(source_path)
            
            # Also add known leading source files
            known_sources = [
                project_root / "SOURCE_OF_TRUTH.yaml",
                project_root / "goals" / "GOAL_TREE.yaml",
                project_root / "lucid_mcp_server.py",
            ]
            
            for source_path in known_sources:
                if source_path.exists():
                    self.source_files.add(source_path)
            
            logger.info(f"Initialized {len(self.source_files)} source files for monitoring")
        
        except Exception as e:
            logger.error(f"Error initializing source files: {e}")
    
    def _is_source_file(self, file_path: Path) -> bool:
        """Check if a file is a source file (source_of_truth)."""
        # Normalize path
        try:
            file_path = file_path.resolve()
        except Exception:
            pass
        
        # Check if in source_files set
        if file_path in self.source_files:
            return True
        
        # Check by name/pattern
        source_patterns = [
            "SOURCE_OF_TRUTH.yaml",
            "GOAL_TREE.yaml",
            "lucid_mcp_server.py",
        ]
        
        for pattern in source_patterns:
            if pattern in str(file_path):
                return True
        
        return False
    
    def on_source_file_changed(self, event: FileChangeEvent):
        """
        Handle source file change - trigger doc updates.
        
        When a source file changes, find all dependent docs and update them.
        """
        if not DOC_UPDATE_AVAILABLE:
            logger.warning("Doc update functionality not available")
            return
        
        file_path = Path(event.file_path)
        logger.info(f"Source file changed: {file_path} - triggering doc updates")
        
        # Use custom callback if provided
        if self.doc_update_callback:
            try:
                self.doc_update_callback(event)
            except Exception as e:
                logger.error(f"Error in doc update callback: {e}")
        else:
            # Default: trigger doc updates via cross-reference generator
            self._trigger_doc_updates(file_path)
    
    def _trigger_doc_updates(self, source_path: Path):
        """Trigger doc updates for dependents of source file."""
        try:
            # Use cross-reference generator to update dependents
            # We need a system name, but this is a generic update
            # So we'll use a dummy system or find the system from the source path
            
            # Try to determine system from source path
            system_name = None
            if "cmc" in str(source_path):
                system_name = "cmc"
            elif "hhni" in str(source_path):
                system_name = "hhni"
            else:
                # Use first available system as fallback
                systems_path = project_root / "knowledge_architecture" / "systems"
                if systems_path.exists():
                    systems = [d.name for d in systems_path.iterdir() if d.is_dir()]
                    if systems:
                        system_name = systems[0]
            
            if system_name:
                generator = CrossReferenceGenerator(system_name, dry_run=False)
                success, files_updated, errors = generator.auto_update_dependent_docs(source_path)
                
                if success:
                    logger.info(f"Updated {len(files_updated)} dependent docs for {source_path}")
                    if errors:
                        logger.warning(f"Some errors during doc update: {errors}")
                else:
                    logger.error(f"Failed to update dependent docs: {errors}")
            else:
                logger.warning(f"Could not determine system for source file: {source_path}")
        
        except Exception as e:
            logger.error(f"Error triggering doc updates for {source_path}: {e}")
    
    def _start_polling_monitoring(self):
        """Start monitoring using polling (fallback method)."""
        self.monitor_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Started polling-based file system monitoring")
    
    def _polling_loop(self):
        """Polling loop for file system monitoring."""
        while self.is_monitoring:
            try:
                self._check_for_changes()
                time.sleep(self.polling_interval)
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(self.polling_interval)
    
    def _check_for_changes(self):
        """Check for file changes using polling."""
        current_time = time.time()
        
        # Get current file timestamps (AETHER_MEMORY + source files if enabled)
        current_timestamps = {}
        
        # Check AETHER_MEMORY directory
        for file_path in self.aether_memory_path.rglob("*.md"):
            try:
                current_timestamps[str(file_path)] = file_path.stat().st_mtime
            except (OSError, FileNotFoundError):
                continue
        
        # Check source files if monitoring enabled
        if self.monitor_source_files:
            for source_path in self.source_files:
                if source_path.exists():
                    try:
                        current_timestamps[str(source_path)] = source_path.stat().st_mtime
                    except (OSError, FileNotFoundError):
                        continue
        
        # Check for new or modified files
        for file_path, mtime in current_timestamps.items():
            if file_path not in self.file_timestamps:
                # New file
                event = FileChangeEvent(
                    event_type='created',
                    file_path=file_path,
                    timestamp=current_time
                )
                self._handle_event(event)
            elif self.file_timestamps[file_path] != mtime:
                # Modified file
                event = FileChangeEvent(
                    event_type='modified',
                    file_path=file_path,
                    timestamp=current_time
                )
                self._handle_event(event)
        
        # Check for deleted files
        for file_path in list(self.file_timestamps.keys()):
            if file_path not in current_timestamps:
                # Deleted file
                event = FileChangeEvent(
                    event_type='deleted',
                    file_path=file_path,
                    timestamp=current_time
                )
                self._handle_event(event)
                del self.file_timestamps[file_path]
        
        # Update timestamps
        self.file_timestamps.update(current_timestamps)
        self.last_check_time = current_time
    
    def _initialize_file_timestamps(self):
        """Initialize file timestamps for change detection."""
        # Initialize AETHER_MEMORY files
        for file_path in self.aether_memory_path.rglob("*.md"):
            try:
                self.file_timestamps[str(file_path)] = file_path.stat().st_mtime
            except (OSError, FileNotFoundError):
                continue
        
        # Initialize source files if monitoring enabled
        if self.monitor_source_files:
            for source_path in self.source_files:
                if source_path.exists():
                    try:
                        self.file_timestamps[str(source_path)] = source_path.stat().st_mtime
                    except (OSError, FileNotFoundError):
                        continue
        
        logger.info(f"Initialized timestamps for {len(self.file_timestamps)} files")
    
    def _handle_event(self, event: FileChangeEvent):
        """Handle a file change event."""
        logger.debug(f"File change event: {event.event_type} - {event.file_path}")
        
        # Check if this is a source file change (for doc updates)
        file_path = Path(event.file_path)
        if self.monitor_source_files and event.event_type in ['modified', 'created']:
            if self._is_source_file(file_path):
                self.on_source_file_changed(event)
        
        # Call regular callback
        if self.callback:
            try:
                self.callback(event)
            except Exception as e:
                logger.error(f"Error in file change callback: {e}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get the current monitoring status.
        
        Returns:
            Dictionary with monitoring status information
        """
        return {
            "is_monitoring": self.is_monitoring,
            "monitoring_method": "watchdog" if WATCHDOG_AVAILABLE and self.observer else "polling",
            "polling_interval": self.polling_interval,
            "last_check_time": self.last_check_time,
            "files_being_monitored": len(self.file_timestamps),
            "aether_memory_path": str(self.aether_memory_path),
            "monitor_source_files": self.monitor_source_files,
            "source_files_count": len(self.source_files)
        }
    
    def _initialize_source_files(self):
        """Initialize list of source files to monitor from dependency graph."""
        if not DOC_UPDATE_AVAILABLE:
            logger.warning("Doc update functionality not available, skipping source file initialization")
            return
        
        try:
            # Load dependency graph to find source files
            _, doc_deps = build_dependency_graph()
            
            # Extract source files from doc dependencies
            for doc_path, dep_info in doc_deps.items():
                source_of_truth = dep_info.get("source_of_truth")
                if source_of_truth:
                    source_path = project_root / source_of_truth
                    if source_path.exists():
                        self.source_files.add(source_path)
            
            # Also add known leading source files
            known_sources = [
                project_root / "SOURCE_OF_TRUTH.yaml",
                project_root / "goals" / "GOAL_TREE.yaml",
                project_root / "lucid_mcp_server.py",
            ]
            
            for source_path in known_sources:
                if source_path.exists():
                    self.source_files.add(source_path)
            
            logger.info(f"Initialized {len(self.source_files)} source files for monitoring")
        
        except Exception as e:
            logger.error(f"Error initializing source files: {e}")
    
    def _is_source_file(self, file_path: Path) -> bool:
        """Check if a file is a source file (source_of_truth)."""
        # Normalize path
        try:
            file_path = file_path.resolve()
        except Exception:
            pass
        
        # Check if in source_files set
        if file_path in self.source_files:
            return True
        
        # Check by name/pattern
        source_patterns = [
            "SOURCE_OF_TRUTH.yaml",
            "GOAL_TREE.yaml",
            "lucid_mcp_server.py",
        ]
        
        for pattern in source_patterns:
            if pattern in str(file_path):
                return True
        
        return False
    
    def on_source_file_changed(self, event: FileChangeEvent):
        """
        Handle source file change - trigger doc updates.
        
        When a source file changes, find all dependent docs and update them.
        """
        if not DOC_UPDATE_AVAILABLE:
            logger.warning("Doc update functionality not available")
            return
        
        file_path = Path(event.file_path)
        logger.info(f"Source file changed: {file_path} - triggering doc updates")
        
        # Use custom callback if provided
        if self.doc_update_callback:
            try:
                self.doc_update_callback(event)
            except Exception as e:
                logger.error(f"Error in doc update callback: {e}")
        else:
            # Default: trigger doc updates via cross-reference generator
            self._trigger_doc_updates(file_path)
    
    def _trigger_doc_updates(self, source_path: Path):
        """Trigger doc updates for dependents of source file."""
        try:
            # Use cross-reference generator to update dependents
            # We need a system name, but this is a generic update
            # So we'll use a dummy system or find the system from the source path
            
            # Try to determine system from source path
            system_name = None
            if "cmc" in str(source_path):
                system_name = "cmc"
            elif "hhni" in str(source_path):
                system_name = "hhni"
            else:
                # Use first available system as fallback
                systems_path = project_root / "knowledge_architecture" / "systems"
                if systems_path.exists():
                    systems = [d.name for d in systems_path.iterdir() if d.is_dir()]
                    if systems:
                        system_name = systems[0]
            
            if system_name:
                generator = CrossReferenceGenerator(system_name, dry_run=False)
                success, files_updated, errors = generator.auto_update_dependent_docs(source_path)
                
                if success:
                    logger.info(f"Updated {len(files_updated)} dependent docs for {source_path}")
                    if errors:
                        logger.warning(f"Some errors during doc update: {errors}")
                else:
                    logger.error(f"Failed to update dependent docs: {errors}")
            else:
                logger.warning(f"Could not determine system for source file: {source_path}")
        
        except Exception as e:
            logger.error(f"Error triggering doc updates for {source_path}: {e}")

class AetherMemoryEventHandler(FileSystemEventHandler):
    """
    Event handler for AETHER_MEMORY directory changes.
    
    This class handles file system events from the watchdog library
    and converts them to FileChangeEvent objects.
    """
    
    def __init__(self, callback: Optional[Callable[[FileChangeEvent], None]] = None,
                 monitor_source_files: bool = False, source_files: Optional[Set[Path]] = None):
        """
        Initialize the event handler.
        
        Args:
            callback: Callback function to handle events
            monitor_source_files: Whether to monitor source files
            source_files: Set of source files to check
        """
        super().__init__()
        self.callback = callback
        self.monitor_source_files = monitor_source_files
        self.source_files = source_files or set()
    
    def _is_source_file(self, file_path: Path) -> bool:
        """Check if a file is a source file."""
        if file_path in self.source_files:
            return True
        
        source_patterns = [
            "SOURCE_OF_TRUTH.yaml",
            "GOAL_TREE.yaml",
            "lucid_mcp_server.py",
        ]
        
        for pattern in source_patterns:
            if pattern in str(file_path):
                return True
        
        return False
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            # Check markdown files or source files
            if file_path.suffix == '.md' or (self.monitor_source_files and self._is_source_file(file_path)):
                file_event = FileChangeEvent(
                    event_type='created',
                    file_path=event.src_path,
                    timestamp=time.time()
                )
                self._handle_event(file_event)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            # Check markdown files or source files
            if file_path.suffix == '.md' or (self.monitor_source_files and self._is_source_file(file_path)):
                file_event = FileChangeEvent(
                    event_type='modified',
                    file_path=event.src_path,
                    timestamp=time.time()
                )
                self._handle_event(file_event)
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix == '.md' or (self.monitor_source_files and self._is_source_file(file_path)):
                file_event = FileChangeEvent(
                    event_type='deleted',
                    file_path=event.src_path,
                    timestamp=time.time()
                )
                self._handle_event(file_event)
    
    def on_moved(self, event):
        """Handle file move events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix == '.md' or (self.monitor_source_files and self._is_source_file(file_path)):
                file_event = FileChangeEvent(
                    event_type='moved',
                    file_path=event.dest_path,
                    old_path=event.src_path,
                    timestamp=time.time()
                )
                self._handle_event(file_event)
    
    def _handle_event(self, event: FileChangeEvent):
        """Handle a file change event."""
        logger.debug(f"File system event: {event.event_type} - {event.file_path}")
        
        if self.callback:
            try:
                self.callback(event)
            except Exception as e:
                logger.error(f"Error in file system event callback: {e}")

class BatchFileProcessor:
    """
    Batch processor for handling multiple file changes efficiently.
    
    This class collects file change events and processes them in batches
    to improve performance and reduce database load.
    """
    
    def __init__(self, batch_size: int = 10, batch_timeout: float = 5.0):
        """
        Initialize the batch processor.
        
        Args:
            batch_size: Maximum number of events per batch
            batch_timeout: Maximum time to wait before processing batch (seconds)
        """
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_events: List[FileChangeEvent] = []
        self.last_batch_time = time.time()
        self.lock = threading.Lock()
        self.callback: Optional[Callable[[List[FileChangeEvent]], None]] = None
    
    def set_callback(self, callback: Callable[[List[FileChangeEvent]], None]):
        """Set the callback function for batch processing."""
        self.callback = callback
    
    def add_event(self, event: FileChangeEvent):
        """Add an event to the batch processor."""
        with self.lock:
            self.pending_events.append(event)
            
            # Process batch if size limit reached
            if len(self.pending_events) >= self.batch_size:
                self._process_batch()
            else:
                # Check if timeout reached
                current_time = time.time()
                if current_time - self.last_batch_time >= self.batch_timeout:
                    self._process_batch()
    
    def _process_batch(self):
        """Process the current batch of events."""
        if not self.pending_events:
            return
        
        events_to_process = self.pending_events.copy()
        self.pending_events.clear()
        self.last_batch_time = time.time()
        
        logger.info(f"Processing batch of {len(events_to_process)} file change events")
        
        if self.callback:
            try:
                self.callback(events_to_process)
            except Exception as e:
                logger.error(f"Error processing batch: {e}")
    
    def force_process(self):
        """Force processing of all pending events."""
        with self.lock:
            if self.pending_events:
                self._process_batch()
    
    def get_pending_count(self) -> int:
        """Get the number of pending events."""
        with self.lock:
            return len(self.pending_events)
