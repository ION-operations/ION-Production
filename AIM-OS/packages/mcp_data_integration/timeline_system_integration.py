# packages/mcp_data_integration/timeline_system_integration.py
"""
Timeline System Integration - Connect MCP timeline tools with file system timeline

This module provides integration between MCP timeline tools and the file system
timeline, enabling comprehensive timeline tracking and management.

Features:
- Timeline entry extraction from file system
- MCP timeline format conversion
- Timeline event correlation
- Timeline analytics and insights
- Timeline search and filtering
"""

import json
import re
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from .data_indexer import DataIndexer, IndexedFile

logger = logging.getLogger(__name__)

@dataclass
class MCPTimelineEntry:
    """Represents a timeline entry in MCP format."""
    entry_id: str
    timestamp: str
    event_type: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: str = ""
    content_snippet: str = ""
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    importance_score: float = 0.0

@dataclass
class TimelineEvent:
    """Represents a timeline event with additional context."""
    event_id: str
    timestamp: datetime
    event_type: str
    description: str
    source_file: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_events: List[str] = field(default_factory=list)

class TimelineSystemIntegration:
    """
    Timeline system integration for MCP tools.
    
    This class provides integration between MCP timeline tools and the file system
    timeline, enabling comprehensive timeline tracking and management.
    """
    
    def __init__(self, data_indexer: DataIndexer, db_path: str = "timeline_integration.db"):
        """
        Initialize the Timeline System Integration.
        
        Args:
            data_indexer: DataIndexer instance for accessing indexed data
            db_path: Path to timeline integration database
        """
        self.data_indexer = data_indexer
        self.db_path = db_path
        self.timeline_entries: Dict[str, MCPTimelineEntry] = {}
        self.timeline_events: Dict[str, TimelineEvent] = {}
        
        # Initialize database
        self._init_database()
        
        # Load existing timeline entries
        self._load_timeline_entries()
        
        logger.info("Timeline System Integration initialized")
    
    def _init_database(self):
        """Initialize the timeline integration database."""
        import sqlite3
        
        self.db = sqlite3.connect(self.db_path)
        cursor = self.db.cursor()
        
        # Create timeline entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcp_timeline_entries (
                entry_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                metadata TEXT NOT NULL,
                file_path TEXT,
                content_snippet TEXT,
                tags TEXT,
                categories TEXT,
                confidence_score REAL,
                importance_score REAL
            )
        """)
        
        # Create timeline events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                source_file TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                related_events TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_timestamp ON mcp_timeline_entries (timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_event_type ON mcp_timeline_entries (event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_file_path ON mcp_timeline_entries (file_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON timeline_events (timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_event_type ON timeline_events (event_type)")
        
        self.db.commit()
        logger.info("Timeline integration database initialized")
    
    def _load_timeline_entries(self):
        """Load existing timeline entries from database."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM mcp_timeline_entries")
        
        for row in cursor.fetchall():
            entry = MCPTimelineEntry(
                entry_id=row[0],
                timestamp=row[1],
                event_type=row[2],
                description=row[3],
                metadata=json.loads(row[4]),
                file_path=row[5] or "",
                content_snippet=row[6] or "",
                tags=json.loads(row[7]) if row[7] else [],
                categories=json.loads(row[8]) if row[8] else [],
                confidence_score=row[9] or 0.0,
                importance_score=row[10] or 0.0
            )
            self.timeline_entries[entry.entry_id] = entry
        
        # Load timeline events
        cursor.execute("SELECT * FROM timeline_events")
        for row in cursor.fetchall():
            event = TimelineEvent(
                event_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                event_type=row[2],
                description=row[3],
                source_file=row[4],
                content=row[5],
                metadata=json.loads(row[6]),
                related_events=json.loads(row[7]) if row[7] else []
            )
            self.timeline_events[event.event_id] = event
        
        logger.info(f"Loaded {len(self.timeline_entries)} timeline entries and {len(self.timeline_events)} events")
    
    def extract_timeline_from_files(self) -> List[MCPTimelineEntry]:
        """
        Extract timeline entries from all indexed files.
        
        Returns:
            List of extracted timeline entries
        """
        logger.info("Extracting timeline entries from indexed files")
        
        extracted_entries = []
        
        for file_path, indexed_file in self.data_indexer.indexed_files.items():
            # Extract timeline entries from different file types
            if indexed_file.file_type == "timeline_entry":
                entries = self._extract_timeline_from_timeline_file(indexed_file)
                extracted_entries.extend(entries)
            elif indexed_file.file_type == "thought_journal":
                entries = self._extract_timeline_from_thought_journal(indexed_file)
                extracted_entries.extend(entries)
            elif indexed_file.file_type == "decision_log":
                entries = self._extract_timeline_from_decision_log(indexed_file)
                extracted_entries.extend(entries)
            elif indexed_file.file_type == "historic_achievement":
                entries = self._extract_timeline_from_historic_achievement(indexed_file)
                extracted_entries.extend(entries)
            else:
                # Try to extract timeline information from any file
                entries = self._extract_timeline_from_general_file(indexed_file)
                extracted_entries.extend(entries)
        
        # Process and store timeline entries
        for entry in extracted_entries:
            self._store_timeline_entry(entry)
        
        logger.info(f"Extracted {len(extracted_entries)} timeline entries from files")
        return extracted_entries
    
    def _extract_timeline_from_timeline_file(self, indexed_file: IndexedFile) -> List[MCPTimelineEntry]:
        """Extract timeline entries from dedicated timeline files."""
        entries = []
        content = indexed_file.content
        
        # Look for timeline patterns
        timeline_patterns = [
            r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}):\s*(.+?)(?:\n|$)",
            r"(\d{4}-\d{2}-\d{2}):\s*(.+?)(?:\n|$)",
            r"(\d{2}:\d{2}):\s*(.+?)(?:\n|$)",
            r"##\s*(.+?)(?:\n|$)",
            r"###\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in timeline_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                timestamp_str = match.group(1)
                description = match.group(2).strip()
                
                if len(description) > 10:
                    entry = self._create_timeline_entry(
                        timestamp_str,
                        description,
                        indexed_file,
                        "timeline_entry",
                        "high"
                    )
                    entries.append(entry)
        
        return entries
    
    def _extract_timeline_from_thought_journal(self, indexed_file: IndexedFile) -> List[MCPTimelineEntry]:
        """Extract timeline entries from thought journal files."""
        entries = []
        content = indexed_file.content
        
        # Look for timestamp patterns in thought journals
        timestamp_patterns = [
            r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}):\s*(.+?)(?:\n|$)",
            r"(\d{4}-\d{2}-\d{2}):\s*(.+?)(?:\n|$)",
            r"(\d{2}:\d{2}):\s*(.+?)(?:\n|$)",
            r"Timestamp:\s*(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}):\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in timestamp_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                timestamp_str = match.group(1)
                description = match.group(2).strip()
                
                if len(description) > 10:
                    entry = self._create_timeline_entry(
                        timestamp_str,
                        description,
                        indexed_file,
                        "thought_journal",
                        "medium"
                    )
                    entries.append(entry)
        
        return entries
    
    def _extract_timeline_from_decision_log(self, indexed_file: IndexedFile) -> List[MCPTimelineEntry]:
        """Extract timeline entries from decision log files."""
        entries = []
        content = indexed_file.content
        
        # Look for decision patterns
        decision_patterns = [
            r"Decision:\s*(.+?)(?:\n|$)",
            r"Choice:\s*(.+?)(?:\n|$)",
            r"Outcome:\s*(.+?)(?:\n|$)",
            r"Result:\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in decision_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                description = match.group(1).strip()
                
                if len(description) > 10:
                    # Use file modification time as timestamp
                    timestamp = datetime.fromtimestamp(indexed_file.last_modified)
                    entry = self._create_timeline_entry(
                        timestamp.isoformat(),
                        description,
                        indexed_file,
                        "decision_log",
                        "high"
                    )
                    entries.append(entry)
        
        return entries
    
    def _extract_timeline_from_historic_achievement(self, indexed_file: IndexedFile) -> List[MCPTimelineEntry]:
        """Extract timeline entries from historic achievement files."""
        entries = []
        content = indexed_file.content
        
        # Look for achievement patterns
        achievement_patterns = [
            r"Achievement:\s*(.+?)(?:\n|$)",
            r"Milestone:\s*(.+?)(?:\n|$)",
            r"Breakthrough:\s*(.+?)(?:\n|$)",
            r"Success:\s*(.+?)(?:\n|$)",
            r"Completed:\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in achievement_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                description = match.group(1).strip()
                
                if len(description) > 10:
                    # Use file modification time as timestamp
                    timestamp = datetime.fromtimestamp(indexed_file.last_modified)
                    entry = self._create_timeline_entry(
                        timestamp.isoformat(),
                        description,
                        indexed_file,
                        "historic_achievement",
                        "critical"
                    )
                    entries.append(entry)
        
        return entries
    
    def _extract_timeline_from_general_file(self, indexed_file: IndexedFile) -> List[MCPTimelineEntry]:
        """Extract timeline entries from general files."""
        entries = []
        content = indexed_file.content
        
        # Look for general timeline patterns
        general_patterns = [
            r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}):\s*(.+?)(?:\n|$)",
            r"(\d{4}-\d{2}-\d{2}):\s*(.+?)(?:\n|$)",
            r"##\s*(.+?)(?:\n|$)",
            r"###\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in general_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                timestamp_str = match.group(1)
                description = match.group(2).strip()
                
                if len(description) > 10:
                    entry = self._create_timeline_entry(
                        timestamp_str,
                        description,
                        indexed_file,
                        "general",
                        "low"
                    )
                    entries.append(entry)
        
        return entries
    
    def _create_timeline_entry(self, timestamp_str: str, description: str, 
                              indexed_file: IndexedFile, event_type: str, 
                              importance: str) -> MCPTimelineEntry:
        """Create a timeline entry from extracted data."""
        entry_id = str(uuid.uuid4())
        
        # Parse timestamp
        try:
            if 'T' in timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace(' ', 'T'))
            else:
                timestamp = datetime.fromisoformat(timestamp_str)
        except:
            # Fallback to file modification time
            timestamp = datetime.fromtimestamp(indexed_file.last_modified)
        
        # Calculate importance score
        importance_scores = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}
        importance_score = importance_scores.get(importance, 0.5)
        
        # Calculate confidence score based on content quality
        confidence_score = 0.5
        if len(description) > 50:
            confidence_score += 0.2
        if any(word in description.lower() for word in ["completed", "achieved", "success"]):
            confidence_score += 0.2
        if any(word in description.lower() for word in ["breakthrough", "milestone", "important"]):
            confidence_score += 0.1
        
        # Extract tags and categories
        tags = []
        categories = [event_type]
        
        if "consciousness" in description.lower():
            tags.append("consciousness")
        if "learning" in description.lower():
            tags.append("learning")
        if "breakthrough" in description.lower():
            tags.append("breakthrough")
        if "milestone" in description.lower():
            tags.append("milestone")
        if "decision" in description.lower():
            tags.append("decision")
        
        return MCPTimelineEntry(
            entry_id=entry_id,
            timestamp=timestamp.isoformat(),
            event_type=event_type,
            description=description,
            metadata={
                "source_type": event_type,
                "file_path": indexed_file.file_path,
                "file_name": indexed_file.file_name,
                "extraction_method": "text_analysis"
            },
            file_path=indexed_file.file_path,
            content_snippet=description[:200] + "..." if len(description) > 200 else description,
            tags=tags,
            categories=categories,
            confidence_score=min(confidence_score, 1.0),
            importance_score=importance_score
        )
    
    def _store_timeline_entry(self, entry: MCPTimelineEntry):
        """Store a timeline entry in the database."""
        cursor = self.db.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO mcp_timeline_entries
            (entry_id, timestamp, event_type, description, metadata, file_path,
             content_snippet, tags, categories, confidence_score, importance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.entry_id,
            entry.timestamp,
            entry.event_type,
            entry.description,
            json.dumps(entry.metadata),
            entry.file_path,
            entry.content_snippet,
            json.dumps(entry.tags),
            json.dumps(entry.categories),
            entry.confidence_score,
            entry.importance_score
        ))
        
        self.db.commit()
        
        # Store in memory
        self.timeline_entries[entry.entry_id] = entry
    
    def get_timeline_entries(self, start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           event_type: Optional[str] = None,
                           limit: int = 50, offset: int = 0) -> List[MCPTimelineEntry]:
        """
        Get timeline entries with optional filtering.
        
        Args:
            start_date: Filter entries after this date
            end_date: Filter entries before this date
            event_type: Filter by event type
            limit: Maximum number of entries
            offset: Offset for pagination
            
        Returns:
            List of timeline entries
        """
        entries = list(self.timeline_entries.values())
        
        # Apply filters
        if start_date:
            entries = [e for e in entries if datetime.fromisoformat(e.timestamp) >= start_date]
        if end_date:
            entries = [e for e in entries if datetime.fromisoformat(e.timestamp) <= end_date]
        if event_type:
            entries = [e for e in entries if e.event_type == event_type]
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Apply pagination
        return entries[offset:offset + limit]
    
    def get_timeline_entry_by_id(self, entry_id: str) -> Optional[MCPTimelineEntry]:
        """Get a timeline entry by ID."""
        return self.timeline_entries.get(entry_id)
    
    def search_timeline(self, query: str, limit: int = 10) -> List[MCPTimelineEntry]:
        """Search timeline entries by description, tags, or content."""
        query_lower = query.lower()
        results = []
        
        for entry in self.timeline_entries.values():
            score = 0
            
            # Search in description
            if query_lower in entry.description.lower():
                score += 3
            
            # Search in content snippet
            if query_lower in entry.content_snippet.lower():
                score += 2
            
            # Search in tags
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 1
            
            if score > 0:
                results.append((entry, score))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, score in results[:limit]]
    
    def get_timeline_analytics(self) -> Dict[str, Any]:
        """Get timeline analytics and insights."""
        total_entries = len(self.timeline_entries)
        
        # Event type distribution
        event_type_distribution = {}
        for entry in self.timeline_entries.values():
            event_type_distribution[entry.event_type] = event_type_distribution.get(entry.event_type, 0) + 1
        
        # Importance distribution
        importance_distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for entry in self.timeline_entries.values():
            if entry.importance_score >= 0.9:
                importance_distribution["critical"] += 1
            elif entry.importance_score >= 0.7:
                importance_distribution["high"] += 1
            elif entry.importance_score >= 0.5:
                importance_distribution["medium"] += 1
            else:
                importance_distribution["low"] += 1
        
        # Confidence statistics
        confidence_values = [entry.confidence_score for entry in self.timeline_entries.values()]
        avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
        
        # Tag distribution
        tag_distribution = {}
        for entry in self.timeline_entries.values():
            for tag in entry.tags:
                tag_distribution[tag] = tag_distribution.get(tag, 0) + 1
        
        # Category distribution
        category_distribution = {}
        for entry in self.timeline_entries.values():
            for category in entry.categories:
                category_distribution[category] = category_distribution.get(category, 0) + 1
        
        # Timeline span
        if self.timeline_entries:
            timestamps = [datetime.fromisoformat(e.timestamp) for e in self.timeline_entries.values()]
            earliest = min(timestamps)
            latest = max(timestamps)
            timeline_span = (latest - earliest).days
        else:
            timeline_span = 0
        
        return {
            "total_entries": total_entries,
            "event_type_distribution": event_type_distribution,
            "importance_distribution": importance_distribution,
            "average_confidence": avg_confidence,
            "tag_distribution": tag_distribution,
            "category_distribution": category_distribution,
            "timeline_span_days": timeline_span
        }
    
    def get_timeline_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get a summary of recent timeline activity."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_entries = self.get_timeline_entries(start_date=cutoff_date)
        
        # Count by event type
        event_counts = {}
        for entry in recent_entries:
            event_counts[entry.event_type] = event_counts.get(entry.event_type, 0) + 1
        
        # Get most important entries
        important_entries = sorted(recent_entries, key=lambda e: e.importance_score, reverse=True)[:5]
        
        return {
            "period_days": days,
            "total_entries": len(recent_entries),
            "event_counts": event_counts,
            "most_important_entries": [
                {
                    "description": entry.description,
                    "timestamp": entry.timestamp,
                    "importance_score": entry.importance_score
                }
                for entry in important_entries
            ]
        }
    
    def close(self):
        """Close the timeline system integration."""
        if hasattr(self, 'db'):
            self.db.close()
        logger.info("Timeline System Integration closed")
