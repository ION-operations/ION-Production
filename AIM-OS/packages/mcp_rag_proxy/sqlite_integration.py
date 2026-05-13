#!/usr/bin/env python3
"""
SQLite Integration for MCP RAG Proxy

Integrates RAG Proxy with SQLite persistence for tool metadata,
usage history, and learning patterns.

Author: Aether
Date: 2025-10-27
"""

import sqlite3
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ToolUsageRecord:
    """Record of tool usage for learning"""
    tool_id: str
    query: str
    consciousness_state: str
    success: bool
    quality_score: float
    outcome: str
    timestamp: datetime

class SQLiteRAGProxy:
    """RAG Proxy with SQLite persistence"""
    
    def __init__(self, 
                 db_path: str = "rag_proxy.db",
                 tools_metadata_path: str = "tools_metadata.json",
                 max_tools: int = 10,
                 similarity_threshold: float = 0.7,
                 consciousness_weight: float = 0.3):
        self.db_path = db_path
        self.tools_metadata_path = tools_metadata_path
        self.max_tools = max_tools
        self.similarity_threshold = similarity_threshold
        self.consciousness_weight = consciousness_weight
        
        # Initialize database
        self._init_database()
        
        # Load tool metadata
        self.tools_metadata = self._load_tools_metadata()
        
        # Initialize vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Build tool embeddings
        self.tool_embeddings = self._build_tool_embeddings()
        
        logger.info(f"Initialized SQLite RAG Proxy with {len(self.tools_metadata)} tools")
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tool metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_metadata (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                tags TEXT, -- JSON array
                context_keywords TEXT, -- JSON array
                consciousness_relevance REAL,
                usage_frequency REAL,
                dependencies TEXT, -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tool usage history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_usage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT NOT NULL,
                query TEXT NOT NULL,
                consciousness_state TEXT,
                success BOOLEAN,
                quality_score REAL,
                outcome TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tool_id) REFERENCES tool_metadata(id)
            )
        ''')
        
        # Learning patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT, -- JSON
                effectiveness_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                context TEXT, -- JSON
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized successfully")
    
    def _load_tools_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load tool metadata from JSON file and store in SQLite"""
        try:
            with open(self.tools_metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Store in SQLite
            self._store_tools_metadata(metadata)
            
            return metadata
        except FileNotFoundError:
            logger.error(f"Tools metadata file not found: {self.tools_metadata_path}")
            return {}
    
    def _store_tools_metadata(self, metadata: Dict[str, Dict[str, Any]]):
        """Store tool metadata in SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for tool_id, tool_data in metadata.items():
            cursor.execute('''
                INSERT OR REPLACE INTO tool_metadata 
                (id, name, description, category, tags, context_keywords, 
                 consciousness_relevance, usage_frequency, dependencies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tool_id,
                tool_data.get('name', tool_id),
                tool_data.get('description', ''),
                tool_data.get('category', 'unknown'),
                json.dumps(tool_data.get('tags', [])),
                json.dumps(tool_data.get('context_keywords', [])),
                tool_data.get('consciousness_relevance', 0.5),
                tool_data.get('usage_frequency', 0.5),
                json.dumps(tool_data.get('dependencies', []))
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Stored {len(metadata)} tools in SQLite database")
    
    def _build_tool_embeddings(self) -> np.ndarray:
        """Build TF-IDF embeddings for all tools"""
        # Prepare text data for each tool
        tool_texts = []
        for tool_id, tool_data in self.tools_metadata.items():
            # Combine description, tags, and context keywords
            text_parts = [
                tool_data.get('description', ''),
                ' '.join(tool_data.get('tags', [])),
                ' '.join(tool_data.get('context_keywords', []))
            ]
            tool_text = ' '.join(text_parts)
            tool_texts.append(tool_text)
        
        # Fit vectorizer and transform
        embeddings = self.vectorizer.fit_transform(tool_texts)
        return embeddings.toarray()
    
    def select_tools(self, 
                    query: str,
                    consciousness_state: str = "neutral",
                    max_tools: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select most relevant tools based on query and consciousness state"""
        if max_tools is None:
            max_tools = self.max_tools
            
        logger.info(f"Selecting tools for query: '{query}' (consciousness: {consciousness_state})")
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query]).toarray()
        
        # Calculate similarity scores
        similarities = cosine_similarity(query_vector, self.tool_embeddings)[0]
        
        # Get tool selections
        selections = []
        for i, (tool_id, tool_data) in enumerate(self.tools_metadata.items()):
            relevance_score = similarities[i]
            
            # Apply consciousness weighting
            consciousness_relevance = tool_data.get('consciousness_relevance', 0.5)
            consciousness_weight = self._get_consciousness_weight(consciousness_state, consciousness_relevance)
            
            # Apply learning adjustments
            learning_adjustment = self._get_learning_adjustment(tool_id, query, consciousness_state)
            
            # Calculate final score
            final_score = (1 - self.consciousness_weight) * relevance_score + \
                         self.consciousness_weight * consciousness_weight
            final_score *= learning_adjustment
            
            # Only include tools above threshold
            if final_score >= 0.1:  # Lowered threshold for testing
                selection = {
                    "tool_id": tool_id,
                    "name": tool_data.get('name', tool_id),
                    "description": tool_data.get('description', ''),
                    "category": tool_data.get('category', 'unknown'),
                    "final_score": final_score,
                    "relevance_score": relevance_score,
                    "consciousness_weight": consciousness_weight,
                    "learning_adjustment": learning_adjustment
                }
                selections.append(selection)
        
        # Sort by final score and return top N
        selections.sort(key=lambda x: x['final_score'], reverse=True)
        return selections[:max_tools]
    
    def _get_consciousness_weight(self, consciousness_state: str, tool_consciousness_relevance: float) -> float:
        """Calculate consciousness weight based on state and tool relevance"""
        # Map consciousness states to weights
        state_weights = {
            "learning": 1.2,
            "creating": 1.1,
            "analyzing": 1.0,
            "neutral": 1.0,
            "conservative": 0.9,
            "exploratory": 1.1,
            "focused": 1.0
        }
        
        state_weight = state_weights.get(consciousness_state, 1.0)
        return tool_consciousness_relevance * state_weight
    
    def _get_learning_adjustment(self, tool_id: str, query: str, consciousness_state: str) -> float:
        """Get learning-based adjustment for tool selection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get usage history for this tool
        cursor.execute('''
            SELECT success, quality_score 
            FROM tool_usage_history 
            WHERE tool_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (tool_id,))
        
        history = cursor.fetchall()
        conn.close()
        
        if not history:
            return 1.0  # No history, no adjustment
        
        # Calculate success rate and quality average
        successes = sum(1 for success, _ in history if success)
        success_rate = successes / len(history)
        quality_avg = sum(quality for _, quality in history) / len(history)
        
        # Calculate adjustment (0.5 to 2.0 range)
        adjustment = 0.5 + (success_rate * 0.5) + (quality_avg * 0.5)
        
        return min(2.0, max(0.5, adjustment))
    
    def record_tool_usage(self, 
                         tool_id: str,
                         query: str,
                         consciousness_state: str,
                         success: bool,
                         quality_score: float,
                         outcome: str):
        """Record tool usage for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tool_usage_history 
            (tool_id, query, consciousness_state, success, quality_score, outcome)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tool_id, query, consciousness_state, success, quality_score, outcome))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Recorded usage for {tool_id}: success={success}, quality={quality_score}")
    
    def get_tool_usage_stats(self, tool_id: str) -> Dict[str, Any]:
        """Get usage statistics for a specific tool"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_uses,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                AVG(quality_score) as avg_quality,
                MAX(timestamp) as last_used
            FROM tool_usage_history 
            WHERE tool_id = ?
        ''', (tool_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            return {
                "total_uses": result[0],
                "success_rate": result[1] / result[0],
                "avg_quality": result[2],
                "last_used": result[3]
            }
        else:
            return {
                "total_uses": 0,
                "success_rate": 0.0,
                "avg_quality": 0.0,
                "last_used": None
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics from SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tool count
        cursor.execute('SELECT COUNT(*) FROM tool_metadata')
        tool_count = cursor.fetchone()[0]
        
        # Usage count
        cursor.execute('SELECT COUNT(*) FROM tool_usage_history')
        usage_count = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes
            FROM tool_usage_history
        ''')
        result = cursor.fetchone()
        success_rate = result[1] / result[0] if result[0] > 0 else 0.0
        
        # Average quality
        cursor.execute('SELECT AVG(quality_score) FROM tool_usage_history')
        avg_quality = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "total_tools": tool_count,
            "total_usages": usage_count,
            "success_rate": success_rate,
            "avg_quality": avg_quality,
            "database_path": self.db_path
        }

def main():
    """Test SQLite RAG Proxy"""
    # Initialize proxy
    proxy = SQLiteRAGProxy()
    
    # Test queries
    test_queries = [
        "Store memory about user preferences",
        "Start autonomous operation",
        "Track confidence in my decisions",
        "Create a timeline entry",
        "Send message to another AI"
    ]
    
    print("=== SQLite RAG Proxy Test ===")
    print(f"System stats: {proxy.get_system_stats()}")
    print()
    
    for query in test_queries:
        print(f"Query: '{query}'")
        selections = proxy.select_tools(query, "learning")
        
        print(f"Selected {len(selections)} tools:")
        for tool in selections[:3]:  # Show top 3
            print(f"  - {tool['name']} (score: {tool['final_score']:.3f})")
            print(f"    Learning adjustment: {tool['learning_adjustment']:.3f}")
        
        print()
    
    # Test usage recording
    proxy.record_tool_usage(
        tool_id="store_memory",
        query="Store memory about user preferences",
        consciousness_state="learning",
        success=True,
        quality_score=0.9,
        outcome="Successfully stored user preferences"
    )
    
    # Test usage stats
    stats = proxy.get_tool_usage_stats("store_memory")
    print(f"Store memory stats: {stats}")

if __name__ == "__main__":
    main()
