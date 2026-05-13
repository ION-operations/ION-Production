# packages/mcp_data_integration/goal_system_integration.py
"""
Goal System Integration - Connect MCP goal tools with file system goals

This module provides integration between MCP goal tools and the file system
goal management, enabling MCP tools to access and manage all goal data.

Features:
- Goal extraction from file system
- MCP goal format conversion
- Goal progress tracking
- Goal relationship mapping
- Goal analytics and insights
"""

import json
import re
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .data_indexer import DataIndexer, IndexedFile

logger = logging.getLogger(__name__)

@dataclass
class MCPGoal:
    """Represents a goal in MCP format."""
    goal_id: str
    name: str
    description: str
    status: str  # planned, in_progress, completed, blocked, cancelled
    priority: str  # critical, high, medium, low
    progress: float  # 0.0 to 1.0
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: str = ""
    parent_goal_id: Optional[str] = None
    child_goal_ids: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)

@dataclass
class GoalRelationship:
    """Represents a relationship between goals."""
    relationship_id: str
    source_goal_id: str
    target_goal_id: str
    relationship_type: str  # depends_on, blocks, enables, related_to
    strength: float  # 0.0 to 1.0
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class GoalSystemIntegration:
    """
    Goal system integration for MCP tools.
    
    This class provides integration between MCP goal tools and the file system
    goal management, enabling comprehensive goal tracking and management.
    """
    
    def __init__(self, data_indexer: DataIndexer, db_path: str = "goal_integration.db"):
        """
        Initialize the Goal System Integration.
        
        Args:
            data_indexer: DataIndexer instance for accessing indexed data
            db_path: Path to goal integration database
        """
        self.data_indexer = data_indexer
        self.db_path = db_path
        self.goals: Dict[str, MCPGoal] = {}
        self.goal_relationships: Dict[str, GoalRelationship] = {}
        
        # Initialize database
        self._init_database()
        
        # Load existing goals
        self._load_goals()
        
        logger.info("Goal System Integration initialized")
    
    def _init_database(self):
        """Initialize the goal integration database."""
        import sqlite3
        
        self.db = sqlite3.connect(self.db_path)
        cursor = self.db.cursor()
        
        # Create goals table
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
                metadata TEXT NOT NULL,
                file_path TEXT,
                parent_goal_id TEXT,
                child_goal_ids TEXT,
                tags TEXT,
                categories TEXT
            )
        """)
        
        # Create goal relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goal_relationships (
                relationship_id TEXT PRIMARY KEY,
                source_goal_id TEXT NOT NULL,
                target_goal_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL NOT NULL,
                description TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_goal_status ON mcp_goals (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_goal_priority ON mcp_goals (priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_goal_file_path ON mcp_goals (file_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_source ON goal_relationships (source_goal_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_target ON goal_relationships (target_goal_id)")
        
        self.db.commit()
        logger.info("Goal integration database initialized")
    
    def _load_goals(self):
        """Load existing goals from database."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM mcp_goals")
        
        for row in cursor.fetchall():
            goal = MCPGoal(
                goal_id=row[0],
                name=row[1],
                description=row[2],
                status=row[3],
                priority=row[4],
                progress=row[5],
                created_at=row[6],
                updated_at=row[7],
                metadata=json.loads(row[8]),
                file_path=row[9] or "",
                parent_goal_id=row[10],
                child_goal_ids=json.loads(row[11]) if row[11] else [],
                tags=json.loads(row[12]) if row[12] else [],
                categories=json.loads(row[13]) if row[13] else []
            )
            self.goals[goal.goal_id] = goal
        
        # Load relationships
        cursor.execute("SELECT * FROM goal_relationships")
        for row in cursor.fetchall():
            relationship = GoalRelationship(
                relationship_id=row[0],
                source_goal_id=row[1],
                target_goal_id=row[2],
                relationship_type=row[3],
                strength=row[4],
                description=row[5],
                metadata=json.loads(row[6])
            )
            self.goal_relationships[relationship.relationship_id] = relationship
        
        logger.info(f"Loaded {len(self.goals)} goals and {len(self.goal_relationships)} relationships")
    
    def extract_goals_from_files(self) -> List[MCPGoal]:
        """
        Extract goals from all indexed files.
        
        Returns:
            List of extracted goals
        """
        logger.info("Extracting goals from indexed files")
        
        extracted_goals = []
        
        for file_path, indexed_file in self.data_indexer.indexed_files.items():
            # Extract goals from different file types
            if indexed_file.file_type == "decision_log":
                goals = self._extract_goals_from_decision_log(indexed_file)
                extracted_goals.extend(goals)
            elif indexed_file.file_type == "thought_journal":
                goals = self._extract_goals_from_thought_journal(indexed_file)
                extracted_goals.extend(goals)
            elif indexed_file.file_type == "timeline_entry":
                goals = self._extract_goals_from_timeline_entry(indexed_file)
                extracted_goals.extend(goals)
            elif "goal" in indexed_file.file_name.lower():
                goals = self._extract_goals_from_goal_file(indexed_file)
                extracted_goals.extend(goals)
        
        # Process and store goals
        for goal in extracted_goals:
            self._store_goal(goal)
        
        logger.info(f"Extracted {len(extracted_goals)} goals from files")
        return extracted_goals
    
    def _extract_goals_from_decision_log(self, indexed_file: IndexedFile) -> List[MCPGoal]:
        """Extract goals from decision log files."""
        goals = []
        content = indexed_file.content
        
        # Look for decision patterns
        decision_patterns = [
            r"Decision:\s*(.+?)(?:\n|$)",
            r"Goal:\s*(.+?)(?:\n|$)",
            r"Objective:\s*(.+?)(?:\n|$)",
            r"Target:\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in decision_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                goal_text = match.group(1).strip()
                if len(goal_text) > 10:  # Filter out very short matches
                    goal = self._create_goal_from_text(
                        goal_text, 
                        indexed_file, 
                        "decision_log",
                        "medium"
                    )
                    goals.append(goal)
        
        return goals
    
    def _extract_goals_from_thought_journal(self, indexed_file: IndexedFile) -> List[MCPGoal]:
        """Extract goals from thought journal files."""
        goals = []
        content = indexed_file.content
        
        # Look for goal patterns in thought journals
        goal_patterns = [
            r"I want to\s+(.+?)(?:\n|\.|$)",
            r"I need to\s+(.+?)(?:\n|\.|$)",
            r"I should\s+(.+?)(?:\n|\.|$)",
            r"Next:\s*(.+?)(?:\n|$)",
            r"TODO:\s*(.+?)(?:\n|$)",
            r"Goal:\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in goal_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                goal_text = match.group(1).strip()
                if len(goal_text) > 10:
                    goal = self._create_goal_from_text(
                        goal_text,
                        indexed_file,
                        "thought_journal",
                        "low"
                    )
                    goals.append(goal)
        
        return goals
    
    def _extract_goals_from_timeline_entry(self, indexed_file: IndexedFile) -> List[MCPGoal]:
        """Extract goals from timeline entry files."""
        goals = []
        content = indexed_file.content
        
        # Look for milestone patterns
        milestone_patterns = [
            r"Milestone:\s*(.+?)(?:\n|$)",
            r"Completed:\s*(.+?)(?:\n|$)",
            r"Achieved:\s*(.+?)(?:\n|$)",
            r"Breakthrough:\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in milestone_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                goal_text = match.group(1).strip()
                if len(goal_text) > 10:
                    goal = self._create_goal_from_text(
                        goal_text,
                        indexed_file,
                        "timeline_entry",
                        "high"
                    )
                    goal.status = "completed"  # Timeline entries often represent completed goals
                    goals.append(goal)
        
        return goals
    
    def _extract_goals_from_goal_file(self, indexed_file: IndexedFile) -> List[MCPGoal]:
        """Extract goals from dedicated goal files."""
        goals = []
        content = indexed_file.content
        
        # Look for structured goal patterns
        goal_patterns = [
            r"##\s*(.+?)(?:\n|$)",
            r"###\s*(.+?)(?:\n|$)",
            r"-\s*(.+?)(?:\n|$)",
            r"\*\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in goal_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                goal_text = match.group(1).strip()
                if len(goal_text) > 10 and not goal_text.startswith("#"):
                    goal = self._create_goal_from_text(
                        goal_text,
                        indexed_file,
                        "goal_file",
                        "high"
                    )
                    goals.append(goal)
        
        return goals
    
    def _create_goal_from_text(self, goal_text: str, indexed_file: IndexedFile, 
                              source_type: str, priority: str) -> MCPGoal:
        """Create a goal from extracted text."""
        goal_id = str(uuid.uuid4())
        current_time = datetime.utcnow().isoformat()
        
        # Extract priority from text
        if any(word in goal_text.lower() for word in ["critical", "urgent", "important"]):
            priority = "critical"
        elif any(word in goal_text.lower() for word in ["high", "priority"]):
            priority = "high"
        elif any(word in goal_text.lower() for word in ["low", "optional"]):
            priority = "low"
        
        # Determine status
        status = "planned"
        if any(word in goal_text.lower() for word in ["completed", "done", "finished", "achieved"]):
            status = "completed"
        elif any(word in goal_text.lower() for word in ["in progress", "working", "doing"]):
            status = "in_progress"
        elif any(word in goal_text.lower() for word in ["blocked", "stuck", "waiting"]):
            status = "blocked"
        
        # Calculate progress
        progress = 0.0
        if status == "completed":
            progress = 1.0
        elif status == "in_progress":
            progress = 0.5
        elif status == "blocked":
            progress = 0.25
        
        # Extract tags and categories
        tags = []
        categories = [source_type]
        
        if "consciousness" in goal_text.lower():
            tags.append("consciousness")
        if "learning" in goal_text.lower():
            tags.append("learning")
        if "breakthrough" in goal_text.lower():
            tags.append("breakthrough")
        if "milestone" in goal_text.lower():
            tags.append("milestone")
        
        return MCPGoal(
            goal_id=goal_id,
            name=goal_text[:100],  # Truncate if too long
            description=goal_text,
            status=status,
            priority=priority,
            progress=progress,
            created_at=current_time,
            updated_at=current_time,
            metadata={
                "source_type": source_type,
                "file_path": indexed_file.file_path,
                "file_name": indexed_file.file_name,
                "extraction_method": "text_analysis"
            },
            file_path=indexed_file.file_path,
            tags=tags,
            categories=categories
        )
    
    def _store_goal(self, goal: MCPGoal):
        """Store a goal in the database."""
        cursor = self.db.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO mcp_goals
            (goal_id, name, description, status, priority, progress, created_at, updated_at,
             metadata, file_path, parent_goal_id, child_goal_ids, tags, categories)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            goal.goal_id,
            goal.name,
            goal.description,
            goal.status,
            goal.priority,
            goal.progress,
            goal.created_at,
            goal.updated_at,
            json.dumps(goal.metadata),
            goal.file_path,
            goal.parent_goal_id,
            json.dumps(goal.child_goal_ids),
            json.dumps(goal.tags),
            json.dumps(goal.categories)
        ))
        
        self.db.commit()
        
        # Store in memory
        self.goals[goal.goal_id] = goal
    
    def get_goals(self, status: Optional[str] = None, priority: Optional[str] = None,
                  limit: int = 50, offset: int = 0) -> List[MCPGoal]:
        """
        Get goals with optional filtering.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            limit: Maximum number of goals
            offset: Offset for pagination
            
        Returns:
            List of goals
        """
        goals = list(self.goals.values())
        
        # Apply filters
        if status:
            goals = [g for g in goals if g.status == status]
        if priority:
            goals = [g for g in goals if g.priority == priority]
        
        # Sort by priority and created_at
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        goals.sort(key=lambda g: (priority_order.get(g.priority, 4), g.created_at))
        
        # Apply pagination
        return goals[offset:offset + limit]
    
    def get_goal_by_id(self, goal_id: str) -> Optional[MCPGoal]:
        """Get a goal by ID."""
        return self.goals.get(goal_id)
    
    def update_goal_progress(self, goal_id: str, progress: float, 
                           status: Optional[str] = None) -> bool:
        """
        Update goal progress and status.
        
        Args:
            goal_id: ID of the goal to update
            progress: New progress (0.0 to 1.0)
            status: New status (optional)
            
        Returns:
            True if updated successfully
        """
        if goal_id not in self.goals:
            return False
        
        goal = self.goals[goal_id]
        goal.progress = max(0.0, min(1.0, progress))
        goal.updated_at = datetime.utcnow().isoformat()
        
        if status:
            goal.status = status
        
        # Update in database
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE mcp_goals 
            SET progress = ?, status = ?, updated_at = ?
            WHERE goal_id = ?
        """, (goal.progress, goal.status, goal.updated_at, goal_id))
        
        self.db.commit()
        
        logger.info(f"Updated goal {goal_id}: progress={goal.progress}, status={goal.status}")
        return True
    
    def create_goal_relationship(self, source_goal_id: str, target_goal_id: str,
                               relationship_type: str, strength: float = 0.5,
                               description: str = "") -> bool:
        """
        Create a relationship between goals.
        
        Args:
            source_goal_id: Source goal ID
            target_goal_id: Target goal ID
            relationship_type: Type of relationship
            strength: Relationship strength (0.0 to 1.0)
            description: Relationship description
            
        Returns:
            True if created successfully
        """
        if source_goal_id not in self.goals or target_goal_id not in self.goals:
            return False
        
        relationship_id = str(uuid.uuid4())
        relationship = GoalRelationship(
            relationship_id=relationship_id,
            source_goal_id=source_goal_id,
            target_goal_id=target_goal_id,
            relationship_type=relationship_type,
            strength=strength,
            description=description,
            metadata={"created_at": datetime.utcnow().isoformat()}
        )
        
        # Store in database
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO goal_relationships
            (relationship_id, source_goal_id, target_goal_id, relationship_type,
             strength, description, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            relationship.relationship_id,
            relationship.source_goal_id,
            relationship.target_goal_id,
            relationship.relationship_type,
            relationship.strength,
            relationship.description,
            json.dumps(relationship.metadata)
        ))
        
        self.db.commit()
        
        # Store in memory
        self.goal_relationships[relationship_id] = relationship
        
        logger.info(f"Created goal relationship: {source_goal_id} -> {target_goal_id}")
        return True
    
    def get_goal_relationships(self, goal_id: str) -> List[GoalRelationship]:
        """Get all relationships for a goal."""
        relationships = []
        for relationship in self.goal_relationships.values():
            if relationship.source_goal_id == goal_id or relationship.target_goal_id == goal_id:
                relationships.append(relationship)
        return relationships
    
    def get_goal_analytics(self) -> Dict[str, Any]:
        """Get goal analytics and insights."""
        total_goals = len(self.goals)
        
        # Status distribution
        status_distribution = {}
        for goal in self.goals.values():
            status_distribution[goal.status] = status_distribution.get(goal.status, 0) + 1
        
        # Priority distribution
        priority_distribution = {}
        for goal in self.goals.values():
            priority_distribution[goal.priority] = priority_distribution.get(goal.priority, 0) + 1
        
        # Progress statistics
        progress_values = [goal.progress for goal in self.goals.values()]
        avg_progress = sum(progress_values) / len(progress_values) if progress_values else 0
        
        # Category distribution
        category_distribution = {}
        for goal in self.goals.values():
            for category in goal.categories:
                category_distribution[category] = category_distribution.get(category, 0) + 1
        
        # Tag distribution
        tag_distribution = {}
        for goal in self.goals.values():
            for tag in goal.tags:
                tag_distribution[tag] = tag_distribution.get(tag, 0) + 1
        
        return {
            "total_goals": total_goals,
            "status_distribution": status_distribution,
            "priority_distribution": priority_distribution,
            "average_progress": avg_progress,
            "category_distribution": category_distribution,
            "tag_distribution": tag_distribution,
            "total_relationships": len(self.goal_relationships)
        }
    
    def search_goals(self, query: str, limit: int = 10) -> List[MCPGoal]:
        """Search goals by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for goal in self.goals.values():
            score = 0
            
            # Search in name
            if query_lower in goal.name.lower():
                score += 3
            
            # Search in description
            if query_lower in goal.description.lower():
                score += 2
            
            # Search in tags
            for tag in goal.tags:
                if query_lower in tag.lower():
                    score += 1
            
            if score > 0:
                results.append((goal, score))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [goal for goal, score in results[:limit]]
    
    def close(self):
        """Close the goal system integration."""
        if hasattr(self, 'db'):
            self.db.close()
        logger.info("Goal System Integration closed")
