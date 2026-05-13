"""
Learning Engine for RAG MCP Proxy

Tracks tool usage outcomes and continuously improves tool selection accuracy
through pattern recognition and adaptive learning.

Author: Solo
Date: 2025-10-30
"""

from __future__ import annotations

import logging
import sqlite3
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ToolUsageRecord:
    """Record of tool usage for learning"""
    tool_id: str
    query: str
    selected_tools: List[str]  # All tools selected for this query
    consciousness_state: str
    tool_used: Optional[str] = None  # Which tool was actually used
    success: bool = False
    quality_score: float = 0.0
    outcome: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class LearningPattern:
    """Pattern learned from usage history"""
    pattern_type: str  # "query_similarity", "tool_combo", "context_match"
    pattern_data: Dict[str, Any]
    effectiveness_score: float
    sample_count: int
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class LearningEngine:
    """Learning engine for continuous improvement of tool selection"""
    
    def __init__(self, db_path: str = "rag_learning.db"):
        """Initialize learning engine
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self._init_database()
        logger.info(f"Learning Engine initialized (db: {self.db_path})")
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tool usage history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_usage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT NOT NULL,
                query TEXT NOT NULL,
                selected_tools TEXT, -- JSON array
                consciousness_state TEXT,
                tool_used TEXT,
                success BOOLEAN,
                quality_score REAL,
                outcome TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Learning patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT, -- JSON
                effectiveness_score REAL,
                sample_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tool performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_performance (
                tool_id TEXT PRIMARY KEY,
                total_uses INTEGER DEFAULT 0,
                successful_uses INTEGER DEFAULT 0,
                avg_quality REAL DEFAULT 0.0,
                last_used TIMESTAMP,
                success_rate REAL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Query-tool success patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_tool_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_pattern TEXT NOT NULL,
                tool_id TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                avg_quality REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(query_pattern, tool_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Learning database initialized")
    
    def record_usage(
        self,
        record: ToolUsageRecord
    ):
        """Record tool usage for learning
        
        Args:
            record: Tool usage record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tool_usage_history 
            (tool_id, query, selected_tools, consciousness_state, tool_used, 
             success, quality_score, outcome, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.tool_id,
            record.query,
            json.dumps(record.selected_tools),
            record.consciousness_state,
            record.tool_used,
            record.success,
            record.quality_score,
            record.outcome,
            record.timestamp.isoformat() if isinstance(record.timestamp, datetime) else record.timestamp
        ))
        
        # Update tool performance metrics
        self._update_tool_performance(record.tool_id, record.success, record.quality_score)
        
        # Update query-tool patterns
        if record.tool_used:
            self._update_query_pattern(record.query, record.tool_used, record.success, record.quality_score)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Recorded usage: {record.tool_id} (success={record.success}, quality={record.quality_score:.2f})")
    
    def _update_tool_performance(
        self,
        tool_id: str,
        success: bool,
        quality_score: float
    ):
        """Update tool performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current metrics
        cursor.execute('''
            SELECT total_uses, successful_uses, avg_quality
            FROM tool_performance
            WHERE tool_id = ?
        ''', (tool_id,))
        
        result = cursor.fetchone()
        
        if result:
            total_uses, successful_uses, avg_quality = result
            total_uses += 1
            successful_uses += (1 if success else 0)
            # Weighted average
            new_avg_quality = ((avg_quality * (total_uses - 1)) + quality_score) / total_uses
            success_rate = successful_uses / total_uses
            
            cursor.execute('''
                UPDATE tool_performance
                SET total_uses = ?, successful_uses = ?, avg_quality = ?,
                    success_rate = ?, last_used = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE tool_id = ?
            ''', (total_uses, successful_uses, new_avg_quality, success_rate, tool_id))
        else:
            # First use
            cursor.execute('''
                INSERT INTO tool_performance
                (tool_id, total_uses, successful_uses, avg_quality, success_rate, last_used)
                VALUES (?, 1, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (tool_id, 1 if success else 0, quality_score, 1.0 if success else 0.0))
        
        conn.commit()
        conn.close()
    
    def _update_query_pattern(
        self,
        query: str,
        tool_id: str,
        success: bool,
        quality_score: float
    ):
        """Update query-tool success patterns"""
        # Normalize query for pattern matching (simplified)
        query_pattern = self._normalize_query(query)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT success_count, failure_count, avg_quality
            FROM query_tool_patterns
            WHERE query_pattern = ? AND tool_id = ?
        ''', (query_pattern, tool_id))
        
        result = cursor.fetchone()
        
        if result:
            success_count, failure_count, avg_quality = result
            if success:
                success_count += 1
            else:
                failure_count += 1
            
            total = success_count + failure_count
            new_avg_quality = ((avg_quality * (total - 1)) + quality_score) / total
            
            cursor.execute('''
                UPDATE query_tool_patterns
                SET success_count = ?, failure_count = ?, avg_quality = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE query_pattern = ? AND tool_id = ?
            ''', (success_count, failure_count, new_avg_quality, query_pattern, tool_id))
        else:
            # New pattern
            cursor.execute('''
                INSERT INTO query_tool_patterns
                (query_pattern, tool_id, success_count, failure_count, avg_quality)
                VALUES (?, ?, ?, ?, ?)
            ''', (query_pattern, tool_id, 1 if success else 0, 0 if success else 1, quality_score))
        
        conn.commit()
        conn.close()
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for pattern matching"""
        # Simple normalization: lowercase, remove extra spaces
        normalized = query.lower().strip()
        # Could add more sophisticated normalization here
        return normalized[:200]  # Limit length
    
    def get_tool_adjustment(
        self,
        tool_id: str,
        query: str
    ) -> float:
        """Get learning-based adjustment factor for tool selection
        
        Args:
            tool_id: Tool identifier
            query: Current query
            
        Returns:
            Adjustment factor (0.5 to 2.0, where 1.0 = no adjustment)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get tool performance
        cursor.execute('''
            SELECT success_rate, avg_quality, total_uses
            FROM tool_performance
            WHERE tool_id = ?
        ''', (tool_id,))
        
        perf_result = cursor.fetchone()
        
        # Get query-tool pattern
        query_pattern = self._normalize_query(query)
        cursor.execute('''
            SELECT success_count, failure_count, avg_quality
            FROM query_tool_patterns
            WHERE query_pattern = ? AND tool_id = ?
        ''', (query_pattern, tool_id))
        
        pattern_result = cursor.fetchone()
        
        conn.close()
        
        # Calculate adjustment
        adjustment = 1.0  # Default: no adjustment
        
        # Tool performance adjustment
        if perf_result:
            success_rate, avg_quality, total_uses = perf_result
            if total_uses > 0:
                # Boost tools with high success rate and quality
                perf_adjustment = 0.5 + (success_rate * 0.5) + (avg_quality * 0.5)
                adjustment *= perf_adjustment
        
        # Query pattern adjustment
        if pattern_result:
            success_count, failure_count, avg_quality = pattern_result
            total = success_count + failure_count
            if total > 0:
                pattern_success_rate = success_count / total
                # Strong boost for tools that match query patterns
                pattern_adjustment = 0.7 + (pattern_success_rate * 0.6) + (avg_quality * 0.4)
                adjustment *= pattern_adjustment
        
        # Clamp to reasonable range
        return min(2.0, max(0.5, adjustment))
    
    def get_tool_performance(self, tool_id: str) -> Dict[str, Any]:
        """Get performance metrics for a tool
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Performance metrics dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT total_uses, successful_uses, avg_quality, success_rate, last_used
            FROM tool_performance
            WHERE tool_id = ?
        ''', (tool_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "tool_id": tool_id,
                "total_uses": result[0],
                "successful_uses": result[1],
                "avg_quality": result[2],
                "success_rate": result[3],
                "last_used": result[4]
            }
        else:
            return {
                "tool_id": tool_id,
                "total_uses": 0,
                "successful_uses": 0,
                "avg_quality": 0.0,
                "success_rate": 0.0,
                "last_used": None
            }
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get overall learning statistics
        
        Returns:
            Statistics dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total usage records
        cursor.execute('SELECT COUNT(*) FROM tool_usage_history')
        total_records = cursor.fetchone()[0]
        
        # Total tools tracked
        cursor.execute('SELECT COUNT(*) FROM tool_performance')
        total_tools = cursor.fetchone()[0]
        
        # Overall success rate
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes
            FROM tool_usage_history
        ''')
        result = cursor.fetchone()
        overall_success_rate = result[1] / result[0] if result[0] > 0 else 0.0
        
        # Average quality
        cursor.execute('SELECT AVG(quality_score) FROM tool_usage_history')
        avg_quality = cursor.fetchone()[0] or 0.0
        
        # Pattern count
        cursor.execute('SELECT COUNT(*) FROM learning_patterns')
        pattern_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_records": total_records,
            "total_tools_tracked": total_tools,
            "overall_success_rate": overall_success_rate,
            "avg_quality": avg_quality,
            "pattern_count": pattern_count
        }
    
    def identify_patterns(self, min_samples: int = 5) -> List[LearningPattern]:
        """Identify learning patterns from usage history
        
        Args:
            min_samples: Minimum samples required for a pattern
            
        Returns:
            List of identified patterns
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find successful query-tool combinations
        cursor.execute('''
            SELECT query_pattern, tool_id, 
                   success_count, failure_count, avg_quality
            FROM query_tool_patterns
            WHERE (success_count + failure_count) >= ?
            ORDER BY (success_count / (success_count + failure_count)) DESC
            LIMIT 20
        ''', (min_samples,))
        
        patterns = []
        for row in cursor.fetchall():
            query_pattern, tool_id, success_count, failure_count, avg_quality = row
            total = success_count + failure_count
            effectiveness = (success_count / total) * avg_quality
            
            pattern = LearningPattern(
                pattern_type="query_tool_match",
                pattern_data={
                    "query_pattern": query_pattern,
                    "tool_id": tool_id
                },
                effectiveness_score=effectiveness,
                sample_count=total
            )
            patterns.append(pattern)
        
        conn.close()
        
        logger.info(f"Identified {len(patterns)} learning patterns")
        return patterns

