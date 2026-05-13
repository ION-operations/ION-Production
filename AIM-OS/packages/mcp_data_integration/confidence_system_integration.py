# packages/mcp_data_integration/confidence_system_integration.py
"""
Confidence System Integration - Connect MCP confidence tools with file system confidence data

This module provides integration between MCP confidence tools and the file system
confidence data, enabling comprehensive confidence tracking and analysis.

Features:
- Confidence data extraction from file system
- MCP confidence format conversion
- Confidence trend analysis
- Confidence calibration tracking
- Confidence analytics and insights
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
class MCPConfidenceRecord:
    """Represents a confidence record in MCP format."""
    record_id: str
    confidence_score: float  # 0.0 to 1.0
    context: str
    reasoning: str
    timestamp: str
    file_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    predicted_outcome: Optional[str] = None
    actual_outcome: Optional[str] = None
    calibration_error: Optional[float] = None

@dataclass
class ConfidenceTrend:
    """Represents a confidence trend over time."""
    trend_id: str
    start_date: datetime
    end_date: datetime
    trend_type: str  # increasing, decreasing, stable, volatile
    average_confidence: float
    confidence_variance: float
    data_points: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConfidenceSystemIntegration:
    """
    Confidence system integration for MCP tools.
    
    This class provides integration between MCP confidence tools and the file system
    confidence data, enabling comprehensive confidence tracking and analysis.
    """
    
    def __init__(self, data_indexer: DataIndexer, db_path: str = "confidence_integration.db"):
        """
        Initialize the Confidence System Integration.
        
        Args:
            data_indexer: DataIndexer instance for accessing indexed data
            db_path: Path to confidence integration database
        """
        self.data_indexer = data_indexer
        self.db_path = db_path
        self.confidence_records: Dict[str, MCPConfidenceRecord] = {}
        self.confidence_trends: Dict[str, ConfidenceTrend] = {}
        
        # Initialize database
        self._init_database()
        
        # Load existing confidence records
        self._load_confidence_records()
        
        logger.info("Confidence System Integration initialized")
    
    def _init_database(self):
        """Initialize the confidence integration database."""
        import sqlite3
        
        self.db = sqlite3.connect(self.db_path)
        cursor = self.db.cursor()
        
        # Create confidence records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcp_confidence_records (
                record_id TEXT PRIMARY KEY,
                confidence_score REAL NOT NULL,
                context TEXT NOT NULL,
                reasoning TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                file_path TEXT,
                metadata TEXT NOT NULL,
                tags TEXT,
                categories TEXT,
                predicted_outcome TEXT,
                actual_outcome TEXT,
                calibration_error REAL
            )
        """)
        
        # Create confidence trends table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS confidence_trends (
                trend_id TEXT PRIMARY KEY,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                trend_type TEXT NOT NULL,
                average_confidence REAL NOT NULL,
                confidence_variance REAL NOT NULL,
                data_points INTEGER NOT NULL,
                metadata TEXT NOT NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence_timestamp ON mcp_confidence_records (timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence_score ON mcp_confidence_records (confidence_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence_file_path ON mcp_confidence_records (file_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trend_start_date ON confidence_trends (start_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trend_type ON confidence_trends (trend_type)")
        
        self.db.commit()
        logger.info("Confidence integration database initialized")
    
    def _load_confidence_records(self):
        """Load existing confidence records from database."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM mcp_confidence_records")
        
        for row in cursor.fetchall():
            record = MCPConfidenceRecord(
                record_id=row[0],
                confidence_score=row[1],
                context=row[2],
                reasoning=row[3],
                timestamp=row[4],
                file_path=row[5] or "",
                metadata=json.loads(row[6]),
                tags=json.loads(row[7]) if row[7] else [],
                categories=json.loads(row[8]) if row[8] else [],
                predicted_outcome=row[9],
                actual_outcome=row[10],
                calibration_error=row[11]
            )
            self.confidence_records[record.record_id] = record
        
        # Load confidence trends
        cursor.execute("SELECT * FROM confidence_trends")
        for row in cursor.fetchall():
            trend = ConfidenceTrend(
                trend_id=row[0],
                start_date=datetime.fromisoformat(row[1]),
                end_date=datetime.fromisoformat(row[2]),
                trend_type=row[3],
                average_confidence=row[4],
                confidence_variance=row[5],
                data_points=row[6],
                metadata=json.loads(row[7])
            )
            self.confidence_trends[trend.trend_id] = trend
        
        logger.info(f"Loaded {len(self.confidence_records)} confidence records and {len(self.confidence_trends)} trends")
    
    def extract_confidence_from_files(self) -> List[MCPConfidenceRecord]:
        """
        Extract confidence data from all indexed files.
        
        Returns:
            List of extracted confidence records
        """
        logger.info("Extracting confidence data from indexed files")
        
        extracted_records = []
        
        for file_path, indexed_file in self.data_indexer.indexed_files.items():
            # Extract confidence from different file types
            if indexed_file.file_type == "thought_journal":
                records = self._extract_confidence_from_thought_journal(indexed_file)
                extracted_records.extend(records)
            elif indexed_file.file_type == "decision_log":
                records = self._extract_confidence_from_decision_log(indexed_file)
                extracted_records.extend(records)
            elif indexed_file.file_type == "timeline_entry":
                records = self._extract_confidence_from_timeline_entry(indexed_file)
                extracted_records.extend(records)
            else:
                # Try to extract confidence from any file
                records = self._extract_confidence_from_general_file(indexed_file)
                extracted_records.extend(records)
        
        # Process and store confidence records
        for record in extracted_records:
            self._store_confidence_record(record)
        
        logger.info(f"Extracted {len(extracted_records)} confidence records from files")
        return extracted_records
    
    def _extract_confidence_from_thought_journal(self, indexed_file: IndexedFile) -> List[MCPConfidenceRecord]:
        """Extract confidence data from thought journal files."""
        records = []
        content = indexed_file.content
        
        # Look for confidence patterns in thought journals
        confidence_patterns = [
            r"Confidence[:\s]+(\d+\.?\d*)",
            r"confident[:\s]+(\d+\.?\d*)",
            r"certainty[:\s]+(\d+\.?\d*)",
            r"(\d+\.?\d*)[:\s]+confidence",
            r"(\d+\.?\d*)[:\s]+confident",
            r"I'm\s+(\d+\.?\d*)\s+confident",
            r"I'm\s+(\d+\.?\d*)\s+certain"
        ]
        
        for pattern in confidence_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                confidence_str = match.group(1)
                try:
                    confidence_score = float(confidence_str)
                    # Normalize to 0-1 range if needed
                    if confidence_score > 1.0:
                        confidence_score = confidence_score / 100.0
                    confidence_score = max(0.0, min(1.0, confidence_score))
                    
                    # Get context around the confidence statement
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end]
                    
                    record = self._create_confidence_record(
                        confidence_score,
                        context,
                        indexed_file,
                        "thought_journal"
                    )
                    records.append(record)
                except ValueError:
                    continue
        
        return records
    
    def _extract_confidence_from_decision_log(self, indexed_file: IndexedFile) -> List[MCPConfidenceRecord]:
        """Extract confidence data from decision log files."""
        records = []
        content = indexed_file.content
        
        # Look for confidence patterns in decision logs
        confidence_patterns = [
            r"Confidence[:\s]+(\d+\.?\d*)",
            r"confidence[:\s]+(\d+\.?\d*)",
            r"certainty[:\s]+(\d+\.?\d*)",
            r"(\d+\.?\d*)[:\s]+confidence",
            r"(\d+\.?\d*)[:\s]+confident"
        ]
        
        for pattern in confidence_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                confidence_str = match.group(1)
                try:
                    confidence_score = float(confidence_str)
                    if confidence_score > 1.0:
                        confidence_score = confidence_score / 100.0
                    confidence_score = max(0.0, min(1.0, confidence_score))
                    
                    # Get context around the confidence statement
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end]
                    
                    record = self._create_confidence_record(
                        confidence_score,
                        context,
                        indexed_file,
                        "decision_log"
                    )
                    records.append(record)
                except ValueError:
                    continue
        
        return records
    
    def _extract_confidence_from_timeline_entry(self, indexed_file: IndexedFile) -> List[MCPConfidenceRecord]:
        """Extract confidence data from timeline entry files."""
        records = []
        content = indexed_file.content
        
        # Look for confidence patterns in timeline entries
        confidence_patterns = [
            r"Confidence[:\s]+(\d+\.?\d*)",
            r"confident[:\s]+(\d+\.?\d*)",
            r"certainty[:\s]+(\d+\.?\d*)",
            r"(\d+\.?\d*)[:\s]+confidence"
        ]
        
        for pattern in confidence_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                confidence_str = match.group(1)
                try:
                    confidence_score = float(confidence_str)
                    if confidence_score > 1.0:
                        confidence_score = confidence_score / 100.0
                    confidence_score = max(0.0, min(1.0, confidence_score))
                    
                    # Get context around the confidence statement
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end]
                    
                    record = self._create_confidence_record(
                        confidence_score,
                        context,
                        indexed_file,
                        "timeline_entry"
                    )
                    records.append(record)
                except ValueError:
                    continue
        
        return records
    
    def _extract_confidence_from_general_file(self, indexed_file: IndexedFile) -> List[MCPConfidenceRecord]:
        """Extract confidence data from general files."""
        records = []
        content = indexed_file.content
        
        # Look for general confidence patterns
        confidence_patterns = [
            r"Confidence[:\s]+(\d+\.?\d*)",
            r"confident[:\s]+(\d+\.?\d*)",
            r"certainty[:\s]+(\d+\.?\d*)",
            r"(\d+\.?\d*)[:\s]+confidence",
            r"(\d+\.?\d*)[:\s]+confident"
        ]
        
        for pattern in confidence_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                confidence_str = match.group(1)
                try:
                    confidence_score = float(confidence_str)
                    if confidence_score > 1.0:
                        confidence_score = confidence_score / 100.0
                    confidence_score = max(0.0, min(1.0, confidence_score))
                    
                    # Get context around the confidence statement
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end]
                    
                    record = self._create_confidence_record(
                        confidence_score,
                        context,
                        indexed_file,
                        "general"
                    )
                    records.append(record)
                except ValueError:
                    continue
        
        return records
    
    def _create_confidence_record(self, confidence_score: float, context: str,
                                 indexed_file: IndexedFile, source_type: str) -> MCPConfidenceRecord:
        """Create a confidence record from extracted data."""
        record_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat()
        
        # Extract reasoning from context
        reasoning = "Extracted from file content"
        if "because" in context.lower():
            because_match = re.search(r"because\s+(.+?)(?:\n|$)", context, re.IGNORECASE)
            if because_match:
                reasoning = because_match.group(1).strip()
        elif "reason" in context.lower():
            reason_match = re.search(r"reason[:\s]+(.+?)(?:\n|$)", context, re.IGNORECASE)
            if reason_match:
                reasoning = reason_match.group(1).strip()
        
        # Extract tags and categories
        tags = []
        categories = [source_type]
        
        if "consciousness" in context.lower():
            tags.append("consciousness")
        if "learning" in context.lower():
            tags.append("learning")
        if "decision" in context.lower():
            tags.append("decision")
        if "breakthrough" in context.lower():
            tags.append("breakthrough")
        if "milestone" in context.lower():
            tags.append("milestone")
        
        # Determine confidence level
        if confidence_score >= 0.9:
            tags.append("high_confidence")
        elif confidence_score >= 0.7:
            tags.append("medium_confidence")
        else:
            tags.append("low_confidence")
        
        return MCPConfidenceRecord(
            record_id=record_id,
            confidence_score=confidence_score,
            context=context,
            reasoning=reasoning,
            timestamp=current_time,
            file_path=indexed_file.file_path,
            metadata={
                "source_type": source_type,
                "file_name": indexed_file.file_name,
                "extraction_method": "text_analysis"
            },
            tags=tags,
            categories=categories
        )
    
    def _store_confidence_record(self, record: MCPConfidenceRecord):
        """Store a confidence record in the database."""
        cursor = self.db.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO mcp_confidence_records
            (record_id, confidence_score, context, reasoning, timestamp, file_path,
             metadata, tags, categories, predicted_outcome, actual_outcome, calibration_error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.record_id,
            record.confidence_score,
            record.context,
            record.reasoning,
            record.timestamp,
            record.file_path,
            json.dumps(record.metadata),
            json.dumps(record.tags),
            json.dumps(record.categories),
            record.predicted_outcome,
            record.actual_outcome,
            record.calibration_error
        ))
        
        self.db.commit()
        
        # Store in memory
        self.confidence_records[record.record_id] = record
    
    def get_confidence_records(self, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             min_confidence: Optional[float] = None,
                             max_confidence: Optional[float] = None,
                             limit: int = 50, offset: int = 0) -> List[MCPConfidenceRecord]:
        """
        Get confidence records with optional filtering.
        
        Args:
            start_date: Filter records after this date
            end_date: Filter records before this date
            min_confidence: Minimum confidence score
            max_confidence: Maximum confidence score
            limit: Maximum number of records
            offset: Offset for pagination
            
        Returns:
            List of confidence records
        """
        records = list(self.confidence_records.values())
        
        # Apply filters
        if start_date:
            records = [r for r in records if datetime.fromisoformat(r.timestamp) >= start_date]
        if end_date:
            records = [r for r in records if datetime.fromisoformat(r.timestamp) <= end_date]
        if min_confidence is not None:
            records = [r for r in records if r.confidence_score >= min_confidence]
        if max_confidence is not None:
            records = [r for r in records if r.confidence_score <= max_confidence]
        
        # Sort by timestamp (newest first)
        records.sort(key=lambda r: r.timestamp, reverse=True)
        
        # Apply pagination
        return records[offset:offset + limit]
    
    def get_confidence_record_by_id(self, record_id: str) -> Optional[MCPConfidenceRecord]:
        """Get a confidence record by ID."""
        return self.confidence_records.get(record_id)
    
    def update_confidence_record(self, record_id: str, actual_outcome: str) -> bool:
        """
        Update a confidence record with actual outcome.
        
        Args:
            record_id: ID of the record to update
            actual_outcome: Actual outcome that occurred
            
        Returns:
            True if updated successfully
        """
        if record_id not in self.confidence_records:
            return False
        
        record = self.confidence_records[record_id]
        record.actual_outcome = actual_outcome
        
        # Calculate calibration error if we have both predicted and actual outcomes
        if record.predicted_outcome and record.actual_outcome:
            # Simple calibration error calculation
            # In a real system, this would be more sophisticated
            predicted_confidence = record.confidence_score
            actual_confidence = 1.0 if record.actual_outcome == record.predicted_outcome else 0.0
            record.calibration_error = abs(predicted_confidence - actual_confidence)
        
        # Update in database
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE mcp_confidence_records 
            SET actual_outcome = ?, calibration_error = ?
            WHERE record_id = ?
        """, (record.actual_outcome, record.calibration_error, record_id))
        
        self.db.commit()
        
        logger.info(f"Updated confidence record {record_id} with actual outcome")
        return True
    
    def analyze_confidence_trends(self, days: int = 30) -> List[ConfidenceTrend]:
        """
        Analyze confidence trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of confidence trends
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_records = [r for r in self.confidence_records.values() 
                         if datetime.fromisoformat(r.timestamp) >= cutoff_date]
        
        if not recent_records:
            return []
        
        # Sort by timestamp
        recent_records.sort(key=lambda r: r.timestamp)
        
        # Calculate trends
        trends = []
        window_size = max(1, len(recent_records) // 10)  # 10 windows
        
        for i in range(0, len(recent_records), window_size):
            window_records = recent_records[i:i + window_size]
            if len(window_records) < 2:
                continue
            
            # Calculate trend statistics
            confidence_scores = [r.confidence_score for r in window_records]
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            variance = sum((score - avg_confidence) ** 2 for score in confidence_scores) / len(confidence_scores)
            
            # Determine trend type
            if len(confidence_scores) >= 2:
                first_half = confidence_scores[:len(confidence_scores)//2]
                second_half = confidence_scores[len(confidence_scores)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                if second_avg > first_avg + 0.1:
                    trend_type = "increasing"
                elif second_avg < first_avg - 0.1:
                    trend_type = "decreasing"
                elif variance > 0.1:
                    trend_type = "volatile"
                else:
                    trend_type = "stable"
            else:
                trend_type = "stable"
            
            trend = ConfidenceTrend(
                trend_id=str(uuid.uuid4()),
                start_date=datetime.fromisoformat(window_records[0].timestamp),
                end_date=datetime.fromisoformat(window_records[-1].timestamp),
                trend_type=trend_type,
                average_confidence=avg_confidence,
                confidence_variance=variance,
                data_points=len(window_records),
                metadata={"analysis_period_days": days}
            )
            
            trends.append(trend)
            
            # Store trend in database
            self._store_confidence_trend(trend)
        
        return trends
    
    def _store_confidence_trend(self, trend: ConfidenceTrend):
        """Store a confidence trend in the database."""
        cursor = self.db.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO confidence_trends
            (trend_id, start_date, end_date, trend_type, average_confidence,
             confidence_variance, data_points, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trend.trend_id,
            trend.start_date.isoformat(),
            trend.end_date.isoformat(),
            trend.trend_type,
            trend.average_confidence,
            trend.confidence_variance,
            trend.data_points,
            json.dumps(trend.metadata)
        ))
        
        self.db.commit()
        
        # Store in memory
        self.confidence_trends[trend.trend_id] = trend
    
    def get_confidence_analytics(self) -> Dict[str, Any]:
        """Get confidence analytics and insights."""
        total_records = len(self.confidence_records)
        
        # Confidence score distribution
        confidence_scores = [r.confidence_score for r in self.confidence_records.values()]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Confidence level distribution
        confidence_levels = {"high": 0, "medium": 0, "low": 0}
        for score in confidence_scores:
            if score >= 0.8:
                confidence_levels["high"] += 1
            elif score >= 0.5:
                confidence_levels["medium"] += 1
            else:
                confidence_levels["low"] += 1
        
        # Tag distribution
        tag_distribution = {}
        for record in self.confidence_records.values():
            for tag in record.tags:
                tag_distribution[tag] = tag_distribution.get(tag, 0) + 1
        
        # Category distribution
        category_distribution = {}
        for record in self.confidence_records.values():
            for category in record.categories:
                category_distribution[category] = category_distribution.get(category, 0) + 1
        
        # Calibration statistics
        calibrated_records = [r for r in self.confidence_records.values() if r.calibration_error is not None]
        avg_calibration_error = sum(r.calibration_error for r in calibrated_records) / len(calibrated_records) if calibrated_records else 0
        
        return {
            "total_records": total_records,
            "average_confidence": avg_confidence,
            "confidence_level_distribution": confidence_levels,
            "tag_distribution": tag_distribution,
            "category_distribution": category_distribution,
            "calibrated_records": len(calibrated_records),
            "average_calibration_error": avg_calibration_error,
            "total_trends": len(self.confidence_trends)
        }
    
    def search_confidence_records(self, query: str, limit: int = 10) -> List[MCPConfidenceRecord]:
        """Search confidence records by context, reasoning, or tags."""
        query_lower = query.lower()
        results = []
        
        for record in self.confidence_records.values():
            score = 0
            
            # Search in context
            if query_lower in record.context.lower():
                score += 3
            
            # Search in reasoning
            if query_lower in record.reasoning.lower():
                score += 2
            
            # Search in tags
            for tag in record.tags:
                if query_lower in tag.lower():
                    score += 1
            
            if score > 0:
                results.append((record, score))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [record for record, score in results[:limit]]
    
    def close(self):
        """Close the confidence system integration."""
        if hasattr(self, 'db'):
            self.db.close()
        logger.info("Confidence System Integration closed")
