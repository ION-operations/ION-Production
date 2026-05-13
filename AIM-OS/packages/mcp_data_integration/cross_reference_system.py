# packages/mcp_data_integration/cross_reference_system.py
"""
Cross-Reference System - Connect related data across sources

This module provides cross-reference capabilities to connect related data
across different sources, enabling relationship discovery and navigation.

Features:
- Automatic relationship discovery
- Manual relationship mapping
- Relationship visualization
- Cross-reference search
- Impact analysis
"""

import json
import re
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .data_indexer import DataIndexer, IndexedFile

logger = logging.getLogger(__name__)

@dataclass
class Relationship:
    """Represents a relationship between two data items."""
    relationship_id: str
    source_path: str
    target_path: str
    relationship_type: str
    strength: float  # 0.0 to 1.0
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class RelationshipGraph:
    """Represents a graph of relationships."""
    nodes: Dict[str, IndexedFile]
    edges: List[Relationship]
    node_connections: Dict[str, Set[str]] = field(default_factory=dict)

class CrossReferenceSystem:
    """
    Cross-reference system for connecting related data.
    
    This class provides capabilities to discover, create, and manage
    relationships between different pieces of consciousness data.
    """
    
    def __init__(self, data_indexer: DataIndexer, db_path: str = "cross_reference.db"):
        """
        Initialize the Cross-Reference System.
        
        Args:
            data_indexer: DataIndexer instance for accessing indexed data
            db_path: Path to relationship database
        """
        self.data_indexer = data_indexer
        self.db_path = db_path
        self.relationships: Dict[str, Relationship] = {}
        self.relationship_graph: Optional[RelationshipGraph] = None
        
        # Initialize database
        self._init_database()
        
        # Load existing relationships
        self._load_relationships()
        
        logger.info("Cross-Reference System initialized")
    
    def _init_database(self):
        """Initialize the relationship database."""
        import sqlite3
        
        self.db = sqlite3.connect(self.db_path)
        cursor = self.db.cursor()
        
        # Create relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id TEXT PRIMARY KEY,
                source_path TEXT NOT NULL,
                target_path TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL NOT NULL,
                description TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_path ON relationships (source_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_target_path ON relationships (target_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_type ON relationships (relationship_type)")
        
        self.db.commit()
        logger.info("Cross-reference database initialized")
    
    def _load_relationships(self):
        """Load existing relationships from database."""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM relationships")
        
        for row in cursor.fetchall():
            relationship = Relationship(
                relationship_id=row[0],
                source_path=row[1],
                target_path=row[2],
                relationship_type=row[3],
                strength=row[4],
                description=row[5],
                metadata=json.loads(row[6]),
                created_at=row[7],
                updated_at=row[8]
            )
            self.relationships[relationship.relationship_id] = relationship
        
        logger.info(f"Loaded {len(self.relationships)} existing relationships")
    
    def discover_relationships(self, auto_create: bool = True) -> List[Relationship]:
        """
        Discover relationships between data items.
        
        Args:
            auto_create: Whether to automatically create discovered relationships
            
        Returns:
            List of discovered relationships
        """
        logger.info("Starting relationship discovery")
        
        discovered_relationships = []
        indexed_files = list(self.data_indexer.indexed_files.values())
        
        # Discover different types of relationships
        discovered_relationships.extend(self._discover_temporal_relationships(indexed_files))
        discovered_relationships.extend(self._discover_content_relationships(indexed_files))
        discovered_relationships.extend(self._discover_structural_relationships(indexed_files))
        discovered_relationships.extend(self._discover_semantic_relationships(indexed_files))
        
        # Remove duplicates
        unique_relationships = self._deduplicate_relationships(discovered_relationships)
        
        # Create relationships if requested
        if auto_create:
            for relationship in unique_relationships:
                self.create_relationship(relationship)
        
        logger.info(f"Discovered {len(unique_relationships)} relationships")
        
        return unique_relationships
    
    def _discover_temporal_relationships(self, indexed_files: List[IndexedFile]) -> List[Relationship]:
        """Discover temporal relationships between files."""
        relationships = []
        
        # Sort files by modification time
        sorted_files = sorted(indexed_files, key=lambda x: x.last_modified)
        
        for i, file1 in enumerate(sorted_files):
            for j, file2 in enumerate(sorted_files[i+1:i+6]):  # Check next 5 files
                # Calculate time difference
                time_diff = file2.last_modified - file1.last_modified
                
                # If files are close in time (within 1 hour), they might be related
                if time_diff < 3600:  # 1 hour
                    strength = max(0.1, 1.0 - (time_diff / 3600))
                    
                    relationship = Relationship(
                        relationship_id=f"temp_{file1.file_path}_{file2.file_path}",
                        source_path=file1.file_path,
                        target_path=file2.file_path,
                        relationship_type="temporal",
                        strength=strength,
                        description=f"Files modified within {time_diff/60:.1f} minutes",
                        metadata={"time_difference": time_diff}
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _discover_content_relationships(self, indexed_files: List[IndexedFile]) -> List[Relationship]:
        """Discover content-based relationships between files."""
        relationships = []
        
        for i, file1 in enumerate(indexed_files):
            for j, file2 in enumerate(indexed_files[i+1:], i+1):
                # Calculate content similarity
                similarity = self._calculate_content_similarity(file1, file2)
                
                if similarity > 0.3:  # Threshold for content similarity
                    relationship = Relationship(
                        relationship_id=f"content_{file1.file_path}_{file2.file_path}",
                        source_path=file1.file_path,
                        target_path=file2.file_path,
                        relationship_type="content",
                        strength=similarity,
                        description=f"Content similarity: {similarity:.2f}",
                        metadata={"similarity_score": similarity}
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _discover_structural_relationships(self, indexed_files: List[IndexedFile]) -> List[Relationship]:
        """Discover structural relationships between files."""
        relationships = []
        
        # Group files by directory structure
        directory_groups = {}
        for file in indexed_files:
            directory = str(Path(file.file_path).parent)
            if directory not in directory_groups:
                directory_groups[directory] = []
            directory_groups[directory].append(file)
        
        # Create relationships within directories
        for directory, files in directory_groups.items():
            if len(files) > 1:
                for i, file1 in enumerate(files):
                    for file2 in files[i+1:]:
                        relationship = Relationship(
                            relationship_id=f"structural_{file1.file_path}_{file2.file_path}",
                            source_path=file1.file_path,
                            target_path=file2.file_path,
                            relationship_type="structural",
                            strength=0.8,  # High strength for same directory
                            description=f"Files in same directory: {directory}",
                            metadata={"directory": directory}
                        )
                        relationships.append(relationship)
        
        return relationships
    
    def _discover_semantic_relationships(self, indexed_files: List[IndexedFile]) -> List[Relationship]:
        """Discover semantic relationships between files."""
        relationships = []
        
        # Look for files with similar tags and categories
        for i, file1 in enumerate(indexed_files):
            for j, file2 in enumerate(indexed_files[i+1:], i+1):
                # Calculate tag similarity
                tag_similarity = self._calculate_tag_similarity(file1.tags, file2.tags)
                
                # Calculate category similarity
                category_similarity = self._calculate_category_similarity(file1.categories, file2.categories)
                
                # Combined semantic similarity
                semantic_similarity = (tag_similarity + category_similarity) / 2
                
                if semantic_similarity > 0.4:  # Threshold for semantic similarity
                    relationship = Relationship(
                        relationship_id=f"semantic_{file1.file_path}_{file2.file_path}",
                        source_path=file1.file_path,
                        target_path=file2.file_path,
                        relationship_type="semantic",
                        strength=semantic_similarity,
                        description=f"Semantic similarity: {semantic_similarity:.2f}",
                        metadata={
                            "tag_similarity": tag_similarity,
                            "category_similarity": category_similarity
                        }
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _calculate_content_similarity(self, file1: IndexedFile, file2: IndexedFile) -> float:
        """Calculate content similarity between two files."""
        # Simple word overlap similarity
        words1 = set(file1.content.lower().split())
        words2 = set(file2.content.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_tag_similarity(self, tags1: List[str], tags2: List[str]) -> float:
        """Calculate tag similarity between two files."""
        if not tags1 or not tags2:
            return 0.0
        
        set1 = set(tags1)
        set2 = set(tags2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_category_similarity(self, categories1: List[str], categories2: List[str]) -> float:
        """Calculate category similarity between two files."""
        if not categories1 or not categories2:
            return 0.0
        
        set1 = set(categories1)
        set2 = set(categories2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _deduplicate_relationships(self, relationships: List[Relationship]) -> List[Relationship]:
        """Remove duplicate relationships."""
        seen = set()
        unique_relationships = []
        
        for relationship in relationships:
            # Create a key for deduplication
            key = tuple(sorted([relationship.source_path, relationship.target_path]))
            
            if key not in seen:
                seen.add(key)
                unique_relationships.append(relationship)
        
        return unique_relationships
    
    def create_relationship(self, relationship: Relationship) -> bool:
        """
        Create a new relationship.
        
        Args:
            relationship: Relationship to create
            
        Returns:
            True if created successfully
        """
        try:
            # Store in memory
            self.relationships[relationship.relationship_id] = relationship
            
            # Store in database
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO relationships
                (relationship_id, source_path, target_path, relationship_type,
                 strength, description, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                relationship.relationship_id,
                relationship.source_path,
                relationship.target_path,
                relationship.relationship_type,
                relationship.strength,
                relationship.description,
                json.dumps(relationship.metadata),
                relationship.created_at,
                relationship.updated_at
            ))
            
            self.db.commit()
            
            # Update relationship graph
            self._update_relationship_graph()
            
            logger.debug(f"Created relationship: {relationship.relationship_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return False
    
    def get_relationships(self, file_path: str, relationship_type: Optional[str] = None) -> List[Relationship]:
        """
        Get relationships for a specific file.
        
        Args:
            file_path: Path to the file
            relationship_type: Optional filter by relationship type
            
        Returns:
            List of relationships
        """
        relationships = []
        
        for relationship in self.relationships.values():
            if relationship.source_path == file_path or relationship.target_path == file_path:
                if relationship_type is None or relationship.relationship_type == relationship_type:
                    relationships.append(relationship)
        
        return relationships
    
    def get_related_files(self, file_path: str, max_depth: int = 2) -> List[str]:
        """
        Get files related to a specific file.
        
        Args:
            file_path: Path to the file
            max_depth: Maximum relationship depth to traverse
            
        Returns:
            List of related file paths
        """
        related_files = set()
        to_process = [(file_path, 0)]
        processed = set()
        
        while to_process:
            current_file, depth = to_process.pop(0)
            
            if current_file in processed or depth > max_depth:
                continue
            
            processed.add(current_file)
            
            # Get direct relationships
            relationships = self.get_relationships(current_file)
            
            for relationship in relationships:
                # Determine the related file
                related_file = (relationship.target_path if relationship.source_path == current_file
                              else relationship.source_path)
                
                if related_file not in processed:
                    related_files.add(related_file)
                    to_process.append((related_file, depth + 1))
        
        return list(related_files)
    
    def get_relationship_graph(self) -> RelationshipGraph:
        """Get the complete relationship graph."""
        if self.relationship_graph is None:
            self._update_relationship_graph()
        
        return self.relationship_graph
    
    def _update_relationship_graph(self):
        """Update the relationship graph."""
        nodes = {}
        edges = list(self.relationships.values())
        node_connections = {}
        
        # Build nodes from indexed files
        for file_path, indexed_file in self.data_indexer.indexed_files.items():
            nodes[file_path] = indexed_file
            node_connections[file_path] = set()
        
        # Build connections
        for relationship in edges:
            if relationship.source_path in node_connections:
                node_connections[relationship.source_path].add(relationship.target_path)
            if relationship.target_path in node_connections:
                node_connections[relationship.target_path].add(relationship.source_path)
        
        self.relationship_graph = RelationshipGraph(
            nodes=nodes,
            edges=edges,
            node_connections=node_connections
        )
    
    def get_relationship_stats(self) -> Dict[str, Any]:
        """Get statistics about relationships."""
        relationship_types = {}
        strength_distribution = {"low": 0, "medium": 0, "high": 0}
        
        for relationship in self.relationships.values():
            # Count by type
            rel_type = relationship.relationship_type
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
            
            # Count by strength
            if relationship.strength < 0.3:
                strength_distribution["low"] += 1
            elif relationship.strength < 0.7:
                strength_distribution["medium"] += 1
            else:
                strength_distribution["high"] += 1
        
        return {
            "total_relationships": len(self.relationships),
            "relationship_types": relationship_types,
            "strength_distribution": strength_distribution,
            "average_strength": sum(r.strength for r in self.relationships.values()) / len(self.relationships) if self.relationships else 0
        }
    
    def search_relationships(self, query: str) -> List[Relationship]:
        """Search relationships by description or metadata."""
        results = []
        query_lower = query.lower()
        
        for relationship in self.relationships.values():
            # Search in description
            if query_lower in relationship.description.lower():
                results.append(relationship)
                continue
            
            # Search in metadata
            for value in relationship.metadata.values():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(relationship)
                    break
        
        return results
    
    def close(self):
        """Close the cross-reference system."""
        if hasattr(self, 'db'):
            self.db.close()
        logger.info("Cross-Reference System closed")

# Import Path at the top
from pathlib import Path
