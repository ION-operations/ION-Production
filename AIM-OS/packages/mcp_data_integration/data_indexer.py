# packages/mcp_data_integration/data_indexer.py
"""
Data Indexer - Core indexing system for consciousness data

This module provides comprehensive indexing of all consciousness data in the
AETHER_MEMORY directory, enabling fast retrieval and search capabilities.

Features:
- Full-text indexing of all markdown files
- Metadata extraction and indexing
- Semantic search indexing
- Real-time index updates
- Incremental indexing
"""

import os
import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IndexedFile:
    """Represents an indexed file with metadata."""
    file_path: str
    file_name: str
    file_type: str
    content: str
    metadata: Dict[str, Any]
    file_hash: str
    file_size: int
    last_modified: float
    indexed_at: float
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)

@dataclass
class SearchResult:
    """Represents a search result."""
    file_path: str
    file_name: str
    content_snippet: str
    relevance_score: float
    metadata: Dict[str, Any]
    matched_terms: List[str]

class DataIndexer:
    """
    Core data indexing system for consciousness data.
    
    This class provides comprehensive indexing of all consciousness data,
    enabling fast retrieval and search capabilities for MCP tools.
    """
    
    def __init__(self, aether_memory_path: str, index_db_path: str = "mcp_data_integration.db"):
        """
        Initialize the DataIndexer.
        
        Args:
            aether_memory_path: Path to AETHER_MEMORY directory
            index_db_path: Path to SQLite index database
        """
        self.aether_memory_path = Path(aether_memory_path)
        self.index_db_path = index_db_path
        self.db_connection = None
        self.indexed_files: Dict[str, IndexedFile] = {}
        
        # Initialize database
        self._init_database()
        
        logger.info(f"DataIndexer initialized for {aether_memory_path}")
    
    def _init_database(self):
        """Initialize the SQLite database for indexing."""
        self.db_connection = sqlite3.connect(self.index_db_path)
        cursor = self.db_connection.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS indexed_files (
                file_path TEXT PRIMARY KEY,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                last_modified REAL NOT NULL,
                indexed_at REAL NOT NULL,
                tags TEXT,
                categories TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                term TEXT NOT NULL,
                position INTEGER NOT NULL,
                context TEXT,
                FOREIGN KEY (file_path) REFERENCES indexed_files (file_path)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY (file_path) REFERENCES indexed_files (file_path)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_term ON search_index (term)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_file ON search_index (file_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metadata_key ON metadata_index (key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metadata_file ON metadata_index (file_path)")
        
        self.db_connection.commit()
        logger.info("Database initialized successfully")
    
    def index_all_files(self) -> int:
        """
        Index all files in the AETHER_MEMORY directory.
        
        Returns:
            Number of files indexed
        """
        logger.info("Starting full index of AETHER_MEMORY directory")
        
        indexed_count = 0
        for file_path in self.aether_memory_path.rglob("*.md"):
            try:
                if self._should_index_file(file_path):
                    self._index_file(file_path)
                    indexed_count += 1
            except Exception as e:
                logger.error(f"Error indexing {file_path}: {e}")
        
        logger.info(f"Indexed {indexed_count} files")
        return indexed_count
    
    def _should_index_file(self, file_path: Path) -> bool:
        """
        Determine if a file should be indexed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be indexed
        """
        # Skip hidden files and directories
        if file_path.name.startswith('.'):
            return False
        
        # Skip if file is too large (>10MB)
        if file_path.stat().st_size > 10 * 1024 * 1024:
            logger.warning(f"Skipping large file: {file_path}")
            return False
        
        return True
    
    def _index_file(self, file_path: Path):
        """
        Index a single file.
        
        Args:
            file_path: Path to the file to index
        """
        try:
            # Read file content with multiple encoding fallbacks
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                # If all encodings fail, read as binary and decode with errors='replace'
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='replace')
            
            # Calculate file hash
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            # Get file metadata
            stat = file_path.stat()
            last_modified = stat.st_mtime
            file_size = stat.st_size
            
            # Extract metadata
            metadata = self._extract_metadata(file_path, content)
            
            # Determine file type and categories
            file_type = self._determine_file_type(file_path, content)
            categories = self._determine_categories(file_path, content)
            tags = self._extract_tags(content)
            
            # Create IndexedFile object
            indexed_file = IndexedFile(
                file_path=str(file_path),
                file_name=file_path.name,
                file_type=file_type,
                content=content,
                metadata=metadata,
                file_hash=file_hash,
                file_size=file_size,
                last_modified=last_modified,
                indexed_at=time.time(),
                tags=tags,
                categories=categories
            )
            
            # Store in memory
            self.indexed_files[str(file_path)] = indexed_file
            
            # Store in database
            self._store_in_database(indexed_file)
            
            # Create search index
            self._create_search_index(indexed_file)
            
            logger.debug(f"Indexed file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e}")
    
    def _extract_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """
        Extract metadata from a file.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": len(content),
            "line_count": len(content.splitlines()),
            "word_count": len(content.split()),
            "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        # Extract markdown metadata
        if content.startswith('---'):
            try:
                # Find end of frontmatter
                end_marker = content.find('---', 3)
                if end_marker > 0:
                    frontmatter = content[3:end_marker]
                    # Simple YAML parsing (basic implementation)
                    for line in frontmatter.splitlines():
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip().strip('"\'')
            except Exception as e:
                logger.debug(f"Error parsing frontmatter for {file_path}: {e}")
        
        # Extract title from first heading
        for line in content.splitlines():
            if line.startswith('#'):
                metadata["title"] = line.lstrip('#').strip()
                break
        
        return metadata
    
    def _determine_file_type(self, file_path: Path, content: str) -> str:
        """
        Determine the type of file based on path and content.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            File type string
        """
        # Determine by directory structure
        if "thought_journals" in str(file_path):
            return "thought_journal"
        elif "decision_logs" in str(file_path):
            return "decision_log"
        elif "context_timeline" in str(file_path):
            return "timeline_entry"
        elif "learning_logs" in str(file_path):
            return "learning_log"
        elif "safety_audit_journey" in str(file_path):
            return "safety_audit"
        elif "tool_audit" in str(file_path):
            return "tool_audit"
        elif "historic_achievements" in str(file_path):
            return "historic_achievement"
        elif "consciousness_exploration" in str(file_path):
            return "consciousness_exploration"
        else:
            return "general"
    
    def _determine_categories(self, file_path: Path, content: str) -> List[str]:
        """
        Determine categories for a file.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            List of categories
        """
        categories = []
        
        # Add file type as category
        file_type = self._determine_file_type(file_path, content)
        categories.append(file_type)
        
        # Add content-based categories
        content_lower = content.lower()
        
        if "confidence" in content_lower:
            categories.append("confidence")
        if "decision" in content_lower:
            categories.append("decision")
        if "breakthrough" in content_lower:
            categories.append("breakthrough")
        if "milestone" in content_lower:
            categories.append("milestone")
        if "audit" in content_lower:
            categories.append("audit")
        if "consciousness" in content_lower:
            categories.append("consciousness")
        if "learning" in content_lower:
            categories.append("learning")
        
        return categories
    
    def _extract_tags(self, content: str) -> List[str]:
        """
        Extract tags from file content.
        
        Args:
            content: File content
            
        Returns:
            List of tags
        """
        tags = []
        
        # Look for tags in content
        content_lower = content.lower()
        
        # Common tags based on content analysis
        tag_keywords = {
            "autonomous": ["autonomous", "autonomy", "self-directed"],
            "consciousness": ["consciousness", "conscious", "awareness"],
            "learning": ["learning", "learned", "insight", "breakthrough"],
            "decision": ["decision", "decided", "chose", "choice"],
            "confidence": ["confidence", "confident", "certainty"],
            "quality": ["quality", "excellent", "perfect", "flawless"],
            "breakthrough": ["breakthrough", "discovery", "realization"],
            "milestone": ["milestone", "achievement", "complete", "finished"],
            "audit": ["audit", "review", "analysis", "assessment"],
            "safety": ["safety", "secure", "protected", "safe"]
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    def _store_in_database(self, indexed_file: IndexedFile):
        """
        Store an indexed file in the database.
        
        Args:
            indexed_file: IndexedFile object to store
        """
        cursor = self.db_connection.cursor()
        
        # Insert or update indexed file
        cursor.execute("""
            INSERT OR REPLACE INTO indexed_files 
            (file_path, file_name, file_type, content, metadata, file_hash, 
             file_size, last_modified, indexed_at, tags, categories)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            indexed_file.file_path,
            indexed_file.file_name,
            indexed_file.file_type,
            indexed_file.content,
            json.dumps(indexed_file.metadata),
            indexed_file.file_hash,
            indexed_file.file_size,
            indexed_file.last_modified,
            indexed_file.indexed_at,
            json.dumps(indexed_file.tags),
            json.dumps(indexed_file.categories)
        ))
        
        # Store metadata separately for better querying
        for key, value in indexed_file.metadata.items():
            cursor.execute("""
                INSERT OR REPLACE INTO metadata_index 
                (file_path, key, value)
                VALUES (?, ?, ?)
            """, (indexed_file.file_path, key, str(value)))
        
        self.db_connection.commit()
    
    def _create_search_index(self, indexed_file: IndexedFile):
        """
        Create search index for a file.
        
        Args:
            indexed_file: IndexedFile object to index
        """
        cursor = self.db_connection.cursor()
        
        # Remove existing search index for this file
        cursor.execute("DELETE FROM search_index WHERE file_path = ?", (indexed_file.file_path,))
        
        # Create search index
        words = indexed_file.content.lower().split()
        for position, word in enumerate(words):
            # Clean word (remove punctuation)
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) > 2:  # Only index words longer than 2 characters
                # Get context (surrounding words)
                start = max(0, position - 5)
                end = min(len(words), position + 6)
                context = ' '.join(words[start:end])
                
                cursor.execute("""
                    INSERT INTO search_index 
                    (file_path, term, position, context)
                    VALUES (?, ?, ?, ?)
                """, (indexed_file.file_path, clean_word, position, context))
        
        self.db_connection.commit()
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search for files based on query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of SearchResult objects
        """
        cursor = self.db_connection.cursor()
        
        # Simple search implementation
        search_terms = query.lower().split()
        results = []
        
        for term in search_terms:
            cursor.execute("""
                SELECT DISTINCT si.file_path, si.context, if.file_name, if.metadata
                FROM search_index si
                JOIN indexed_files if ON si.file_path = if.file_path
                WHERE si.term LIKE ?
                ORDER BY si.position
                LIMIT ?
            """, (f"%{term}%", limit * 2))  # Get more results for ranking
            
            for row in cursor.fetchall():
                file_path, context, file_name, metadata = row
                
                # Calculate relevance score (simple implementation)
                relevance_score = self._calculate_relevance_score(term, context)
                
                result = SearchResult(
                    file_path=file_path,
                    file_name=file_name,
                    content_snippet=context,
                    relevance_score=relevance_score,
                    metadata=json.loads(metadata),
                    matched_terms=[term]
                )
                results.append(result)
        
        # Sort by relevance score and remove duplicates
        results = sorted(results, key=lambda x: x.relevance_score, reverse=True)
        seen_files = set()
        unique_results = []
        for result in results:
            if result.file_path not in seen_files:
                unique_results.append(result)
                seen_files.add(result.file_path)
                if len(unique_results) >= limit:
                    break
        
        return unique_results
    
    def _calculate_relevance_score(self, term: str, context: str) -> float:
        """
        Calculate relevance score for a search result.
        
        Args:
            term: Search term
            context: Context around the term
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        # Simple relevance scoring
        term_count = context.lower().count(term.lower())
        context_length = len(context.split())
        
        if context_length == 0:
            return 0.0
        
        # Base score from term frequency
        base_score = min(term_count / context_length, 1.0)
        
        # Boost score for exact matches
        if term.lower() in context.lower():
            base_score += 0.2
        
        return min(base_score, 1.0)
    
    def get_file_by_path(self, file_path: str) -> Optional[IndexedFile]:
        """
        Get an indexed file by path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            IndexedFile object or None if not found
        """
        return self.indexed_files.get(file_path)
    
    def get_files_by_type(self, file_type: str) -> List[IndexedFile]:
        """
        Get all files of a specific type.
        
        Args:
            file_type: Type of files to retrieve
            
        Returns:
            List of IndexedFile objects
        """
        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT file_path FROM indexed_files WHERE file_type = ?
        """, (file_type,))
        
        results = []
        for row in cursor.fetchall():
            file_path = row[0]
            if file_path in self.indexed_files:
                results.append(self.indexed_files[file_path])
        
        return results
    
    def get_files_by_category(self, category: str) -> List[IndexedFile]:
        """
        Get all files in a specific category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of IndexedFile objects
        """
        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT file_path FROM indexed_files 
            WHERE categories LIKE ?
        """, (f"%{category}%",))
        
        results = []
        for row in cursor.fetchall():
            file_path = row[0]
            if file_path in self.indexed_files:
                results.append(self.indexed_files[file_path])
        
        return results
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Returns:
            Dictionary of index statistics
        """
        cursor = self.db_connection.cursor()
        
        # Get file counts by type
        cursor.execute("""
            SELECT file_type, COUNT(*) FROM indexed_files GROUP BY file_type
        """)
        file_types = dict(cursor.fetchall())
        
        # Get total files
        cursor.execute("SELECT COUNT(*) FROM indexed_files")
        total_files = cursor.fetchone()[0]
        
        # Get total search terms
        cursor.execute("SELECT COUNT(*) FROM search_index")
        total_terms = cursor.fetchone()[0]
        
        # Get total metadata entries
        cursor.execute("SELECT COUNT(*) FROM metadata_index")
        total_metadata = cursor.fetchone()[0]
        
        return {
            "total_files": total_files,
            "file_types": file_types,
            "total_search_terms": total_terms,
            "total_metadata_entries": total_metadata,
            "indexed_files_in_memory": len(self.indexed_files)
        }
    
    def close(self):
        """Close the database connection."""
        if self.db_connection:
            self.db_connection.close()
            logger.info("Database connection closed")
