# packages/mcp_data_integration/mcp_data_bridge.py
"""
MCP Data Bridge - Bridge between MCP tools and file system data

This module provides a bridge between MCP tools and the AETHER_MEMORY directory,
enabling MCP tools to access 100% of consciousness data instead of the current 20%.

Features:
- MCP memory tool integration
- MCP timeline tool integration
- MCP goal tool integration
- MCP confidence tool integration
- Real-time data synchronization
- Search and retrieval capabilities
"""

import json
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from functools import lru_cache

from .data_indexer import DataIndexer, IndexedFile, SearchResult
from .file_system_monitor import FileSystemMonitor, FileChangeEvent, BatchFileProcessor

logger = logging.getLogger(__name__)

@dataclass
class MCPMemoryAtom:
    """Represents a memory atom in MCP format."""
    id: str
    content: str
    content_type: str
    content_hash: str
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]
    tags: List[str]
    categories: List[str]

@dataclass
class MCPTimelineEntry:
    """Represents a timeline entry in MCP format."""
    entry_id: str
    timestamp: str
    event_type: str
    description: str
    metadata: Dict[str, Any]
    file_path: str
    content_snippet: str

@dataclass
class MCPGoal:
    """Represents a goal in MCP format."""
    goal_id: str
    name: str
    description: str
    status: str
    priority: str
    progress: float
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]

@dataclass
class MCPConfidenceRecord:
    """Represents a confidence record in MCP format."""
    record_id: str
    confidence_score: float
    context: str
    reasoning: str
    timestamp: str
    file_path: str
    metadata: Dict[str, Any]

class MCPDataBridge:
    """
    Bridge between MCP tools and file system data.
    
    This class provides integration between MCP tools and the AETHER_MEMORY directory,
    enabling MCP tools to access all consciousness data through a unified interface.
    """
    
    def __init__(self, aether_memory_path: str, mcp_db_path: str = "mcp_integrated.db"):
        """
        Initialize the MCP Data Bridge.
        
        Args:
            aether_memory_path: Path to AETHER_MEMORY directory
            mcp_db_path: Path to MCP database
        """
        self.aether_memory_path = aether_memory_path
        self.mcp_db_path = mcp_db_path
        
        # Initialize components
        self.data_indexer = DataIndexer(aether_memory_path, f"{mcp_db_path}.index")
        self.file_monitor = FileSystemMonitor(aether_memory_path, self._handle_file_change)
        self.batch_processor = BatchFileProcessor()
        
        # Caching
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_ttl: float = 300.0  # 5 minutes cache TTL
        
        # Set up batch processing
        self.batch_processor.set_callback(self._process_batch_events)
        
        # Initialize MCP database
        self._init_mcp_database()
        
        # Start monitoring
        self.file_monitor.start_monitoring()
        
        logger.info("MCP Data Bridge initialized")
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache and key in self._cache_timestamps:
            if time.time() - self._cache_timestamps[key] < self._cache_ttl:
                return self._cache[key]
            else:
                # Remove expired cache entry
                del self._cache[key]
                del self._cache_timestamps[key]
        return None
    
    def _set_cache(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp."""
        self._cache[key] = value
        self._cache_timestamps[key] = time.time()
    
    def _clear_cache(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    def _init_mcp_database(self):
        """Initialize the MCP database."""
        import sqlite3
        
        self.mcp_db = sqlite3.connect(self.mcp_db_path)
        cursor = self.mcp_db.cursor()
        
        # Create MCP tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcp_memory_atoms (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                content_type TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT NOT NULL,
                tags TEXT,
                categories TEXT,
                file_path TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcp_timeline_entries (
                entry_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                metadata TEXT NOT NULL,
                file_path TEXT,
                content_snippet TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcp_goals (
                goal_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                progress REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcp_confidence_records (
                record_id TEXT PRIMARY KEY,
                confidence_score REAL NOT NULL,
                context TEXT NOT NULL,
                reasoning TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                file_path TEXT,
                metadata TEXT NOT NULL
            )
        """)
        
        self.mcp_db.commit()
        logger.info("MCP database initialized")
    
    def _handle_file_change(self, event: FileChangeEvent):
        """Handle file change events."""
        self.batch_processor.add_event(event)
    
    def _process_batch_events(self, events: List[FileChangeEvent]):
        """Process a batch of file change events."""
        for event in events:
            try:
                if event.event_type in ['created', 'modified']:
                    self._index_file(event.file_path)
                elif event.event_type == 'deleted':
                    self._remove_file(event.file_path)
                elif event.event_type == 'moved':
                    self._move_file(event.old_path, event.file_path)
            except Exception as e:
                logger.error(f"Error processing file change event: {e}")
    
    def _index_file(self, file_path: str):
        """Index a file and create MCP records."""
        try:
            # Index the file
            self.data_indexer._index_file(Path(file_path))
            
            # Get the indexed file
            indexed_file = self.data_indexer.get_file_by_path(file_path)
            if not indexed_file:
                return
            
            # Create MCP memory atom
            self._create_memory_atom(indexed_file)
            
            # Create timeline entry if applicable
            if indexed_file.file_type == 'timeline_entry':
                self._create_timeline_entry(indexed_file)
            
            # Extract confidence data if present
            self._extract_confidence_data(indexed_file)
            
            logger.debug(f"Indexed and created MCP records for {file_path}")
            
        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e}")
    
    def _remove_file(self, file_path: str):
        """Remove file from MCP database."""
        cursor = self.mcp_db.cursor()
        
        # Remove from all MCP tables
        cursor.execute("DELETE FROM mcp_memory_atoms WHERE file_path = ?", (file_path,))
        cursor.execute("DELETE FROM mcp_timeline_entries WHERE file_path = ?", (file_path,))
        cursor.execute("DELETE FROM mcp_confidence_records WHERE file_path = ?", (file_path,))
        
        self.mcp_db.commit()
        logger.debug(f"Removed MCP records for {file_path}")
    
    def _move_file(self, old_path: str, new_path: str):
        """Handle file move events."""
        cursor = self.mcp_db.cursor()
        
        # Update file paths in all MCP tables
        cursor.execute("UPDATE mcp_memory_atoms SET file_path = ? WHERE file_path = ?", (new_path, old_path))
        cursor.execute("UPDATE mcp_timeline_entries SET file_path = ? WHERE file_path = ?", (new_path, old_path))
        cursor.execute("UPDATE mcp_confidence_records SET file_path = ? WHERE file_path = ?", (new_path, old_path))
        
        self.mcp_db.commit()
        logger.debug(f"Moved MCP records from {old_path} to {new_path}")
    
    def _create_memory_atom(self, indexed_file: IndexedFile):
        """Create MCP memory atom from indexed file."""
        atom_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat()
        
        # Create MCP memory atom
        atom = MCPMemoryAtom(
            id=atom_id,
            content=indexed_file.content,
            content_type="text/markdown",
            content_hash=indexed_file.file_hash,
            created_at=current_time,
            updated_at=current_time,
            metadata=indexed_file.metadata,
            tags=indexed_file.tags,
            categories=indexed_file.categories
        )
        
        # Store in database
        cursor = self.mcp_db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO mcp_memory_atoms
            (id, content, content_type, content_hash, created_at, updated_at, 
             metadata, tags, categories, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            atom.id,
            atom.content,
            atom.content_type,
            atom.content_hash,
            atom.created_at,
            atom.updated_at,
            json.dumps(atom.metadata),
            json.dumps(atom.tags),
            json.dumps(atom.categories),
            indexed_file.file_path
        ))
        
        self.mcp_db.commit()
    
    def _create_timeline_entry(self, indexed_file: IndexedFile):
        """Create MCP timeline entry from indexed file."""
        entry_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat()
        
        # Extract timeline information from metadata
        title = indexed_file.metadata.get('title', indexed_file.file_name)
        description = title
        
        # Create timeline entry
        entry = MCPTimelineEntry(
            entry_id=entry_id,
            timestamp=current_time,
            event_type=indexed_file.file_type,
            description=description,
            metadata=indexed_file.metadata,
            file_path=indexed_file.file_path,
            content_snippet=indexed_file.content[:200] + "..." if len(indexed_file.content) > 200 else indexed_file.content
        )
        
        # Store in database
        cursor = self.mcp_db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO mcp_timeline_entries
            (entry_id, timestamp, event_type, description, metadata, file_path, content_snippet)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.entry_id,
            entry.timestamp,
            entry.event_type,
            entry.description,
            json.dumps(entry.metadata),
            entry.file_path,
            entry.content_snippet
        ))
        
        self.mcp_db.commit()
    
    def _extract_confidence_data(self, indexed_file: IndexedFile):
        """Extract confidence data from indexed file."""
        content_lower = indexed_file.content.lower()
        
        # Look for confidence-related content
        confidence_keywords = ['confidence', 'confident', 'certainty', 'uncertain', 'doubt']
        if any(keyword in content_lower for keyword in confidence_keywords):
            # Extract confidence score (simple implementation)
            confidence_score = self._extract_confidence_score(indexed_file.content)
            
            if confidence_score is not None:
                record_id = str(uuid.uuid4())
                current_time = datetime.utcnow().isoformat()
                
                # Create confidence record
                record = MCPConfidenceRecord(
                    record_id=record_id,
                    confidence_score=confidence_score,
                    context=indexed_file.content[:500],
                    reasoning="Extracted from file content",
                    timestamp=current_time,
                    file_path=indexed_file.file_path,
                    metadata=indexed_file.metadata
                )
                
                # Store in database
                cursor = self.mcp_db.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO mcp_confidence_records
                    (record_id, confidence_score, context, reasoning, timestamp, file_path, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.record_id,
                    record.confidence_score,
                    record.context,
                    record.reasoning,
                    record.timestamp,
                    record.file_path,
                    json.dumps(record.metadata)
                ))
                
                self.mcp_db.commit()
    
    def _extract_confidence_score(self, content: str) -> Optional[float]:
        """Extract confidence score from content."""
        import re
        
        # Look for confidence patterns
        patterns = [
            r'confidence[:\s]+(\d+\.?\d*)',
            r'confident[:\s]+(\d+\.?\d*)',
            r'certainty[:\s]+(\d+\.?\d*)',
            r'(\d+\.?\d*)[:\s]+confidence',
            r'(\d+\.?\d*)[:\s]+confident'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    # Normalize to 0-1 range if needed
                    if score > 1.0:
                        score = score / 100.0
                    return min(max(score, 0.0), 1.0)
                except ValueError:
                    continue
        
        return None
    
    # MCP Tool Integration Methods
    
    def get_memory_atoms(self, limit: int = 50, offset: int = 0) -> List[MCPMemoryAtom]:
        """Get memory atoms from MCP database."""
        cursor = self.mcp_db.cursor()
        cursor.execute("""
            SELECT id, content, content_type, content_hash, created_at, updated_at,
                   metadata, tags, categories, file_path
            FROM mcp_memory_atoms
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        atoms = []
        for row in cursor.fetchall():
            atom = MCPMemoryAtom(
                id=row[0],
                content=row[1],
                content_type=row[2],
                content_hash=row[3],
                created_at=row[4],
                updated_at=row[5],
                metadata=json.loads(row[6]),
                tags=json.loads(row[7]) if row[7] else [],
                categories=json.loads(row[8]) if row[8] else []
            )
            atoms.append(atom)
        
        return atoms
    
    def get_timeline_entries(self, limit: int = 50, offset: int = 0) -> List[MCPTimelineEntry]:
        """Get timeline entries from MCP database."""
        cursor = self.mcp_db.cursor()
        cursor.execute("""
            SELECT entry_id, timestamp, event_type, description, metadata,
                   file_path, content_snippet
            FROM mcp_timeline_entries
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        entries = []
        for row in cursor.fetchall():
            entry = MCPTimelineEntry(
                entry_id=row[0],
                timestamp=row[1],
                event_type=row[2],
                description=row[3],
                metadata=json.loads(row[4]),
                file_path=row[5],
                content_snippet=row[6]
            )
            entries.append(entry)
        
        return entries
    
    def get_confidence_records(self, limit: int = 50, offset: int = 0) -> List[MCPConfidenceRecord]:
        """Get confidence records from MCP database."""
        cursor = self.mcp_db.cursor()
        cursor.execute("""
            SELECT record_id, confidence_score, context, reasoning, timestamp,
                   file_path, metadata
            FROM mcp_confidence_records
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        records = []
        for row in cursor.fetchall():
            record = MCPConfidenceRecord(
                record_id=row[0],
                confidence_score=row[1],
                context=row[2],
                reasoning=row[3],
                timestamp=row[4],
                file_path=row[5],
                metadata=json.loads(row[6])
            )
            records.append(record)
        
        return records
    
    def search_memory(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search memory using the data indexer."""
        return self.data_indexer.search(query, limit)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        cursor = self.mcp_db.cursor()
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM mcp_memory_atoms")
        memory_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM mcp_timeline_entries")
        timeline_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM mcp_confidence_records")
        confidence_count = cursor.fetchone()[0]
        
        # Get index stats
        index_stats = self.data_indexer.get_index_stats()
        
        # Get monitoring status
        monitoring_status = self.file_monitor.get_monitoring_status()
        
        return {
            "memory_atoms": memory_count,
            "timeline_entries": timeline_count,
            "confidence_records": confidence_count,
            "index_stats": index_stats,
            "monitoring_status": monitoring_status,
            "total_consciousness_data": index_stats.get("total_files", 0)
        }
    
    def sync_all_data(self) -> Dict[str, Any]:
        """Sync all data from file system to MCP database."""
        logger.info("Starting full data sync")
        
        # Index all files
        indexed_count = self.data_indexer.index_all_files()
        
        # Create MCP records for all indexed files
        mcp_count = 0
        for file_path, indexed_file in self.data_indexer.indexed_files.items():
            try:
                self._create_memory_atom(indexed_file)
                if indexed_file.file_type == 'timeline_entry':
                    self._create_timeline_entry(indexed_file)
                self._extract_confidence_data(indexed_file)
                mcp_count += 1
            except Exception as e:
                logger.error(f"Error creating MCP record for {file_path}: {e}")
        
        logger.info(f"Data sync complete: {indexed_count} files indexed, {mcp_count} MCP records created")
        
        return {
            "files_indexed": indexed_count,
            "mcp_records_created": mcp_count,
            "sync_timestamp": datetime.utcnow().isoformat()
        }
    
    def close(self):
        """Close the MCP Data Bridge."""
        self.file_monitor.stop_monitoring()
        self.data_indexer.close()
        if hasattr(self, 'mcp_db'):
            self.mcp_db.close()
        logger.info("MCP Data Bridge closed")
