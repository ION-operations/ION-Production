"""
Master Index - Persistent storage for DEEPSEARCH results

Uses SQLite for fast queries and incremental updates.
"""

import sqlite3
import hashlib
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class MasterIndex:
    """SQLite-based persistent index for DEEPSEARCH"""
    
    def __init__(self, index_path: str = ".deepsearch/master_index.db"):
        """
        Initialize master index
        
        Args:
            index_path: Path to SQLite database file
        """
        self.index_path = index_path
        self.conn: Optional[sqlite3.Connection] = None
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database and schema exist"""
        # Create directory if needed
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Connect
        self.conn = sqlite3.connect(self.index_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dicts
        
        # Create schema
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS sources (
                url TEXT PRIMARY KEY,
                content_hash TEXT,
                trust_score REAL,
                entropy REAL,
                content TEXT,
                metadata TEXT,  -- JSON
                crawled_at TIMESTAMP,
                updated_at TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_trust_score ON sources(trust_score);
            CREATE INDEX IF NOT EXISTS idx_entropy ON sources(entropy);
            CREATE INDEX IF NOT EXISTS idx_crawled_at ON sources(crawled_at);
            
            CREATE TABLE IF NOT EXISTS file_hashes (
                file_path TEXT PRIMARY KEY,
                content_hash TEXT,
                updated_at TIMESTAMP
            );
        ''')
        self.conn.commit()
    
    def add_source(
        self,
        url: str,
        content: str,
        trust_score: float,
        entropy: float,
        metadata: Optional[Dict] = None
    ):
        """Add or update source in index"""
        content_hash = self._hash_content(content)
        now = datetime.now().isoformat()
        
        self.conn.execute('''
            INSERT OR REPLACE INTO sources 
            (url, content_hash, trust_score, entropy, content, metadata, crawled_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            url,
            content_hash,
            trust_score,
            entropy,
            content,
            json.dumps(metadata) if metadata else None,
            now,
            now
        ))
        self.conn.commit()
    
    def get_source(self, url: str) -> Optional[Dict]:
        """Get source by URL"""
        cursor = self.conn.execute(
            'SELECT * FROM sources WHERE url = ?',
            (url,)
        )
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def needs_update(self, url: str, current_content: str) -> bool:
        """Check if source needs update (content changed)"""
        source = self.get_source(url)
        if not source:
            return True  # New source
        
        current_hash = self._hash_content(current_content)
        return current_hash != source['content_hash']
    
    def query(
        self,
        min_trust: Optional[float] = None,
        min_entropy: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query sources with filters
        
        Args:
            min_trust: Minimum trust score filter
            min_entropy: Minimum entropy filter
            limit: Maximum results
            
        Returns:
            List of source dicts, ordered by trust * entropy (quality score)
        """
        conditions = []
        params = []
        
        if min_trust is not None:
            conditions.append('trust_score >= ?')
            params.append(min_trust)
        
        if min_entropy is not None:
            conditions.append('entropy >= ?')
            params.append(min_entropy)
        
        where_clause = ' AND '.join(conditions) if conditions else '1=1'
        
        cursor = self.conn.execute(f'''
            SELECT *,
                   (trust_score * entropy) as quality_score
            FROM sources
            WHERE {where_clause}
            ORDER BY quality_score DESC
            LIMIT ?
        ''', params + [limit])
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_file_hash(self, file_path: str, content: str):
        """Update file hash in cache"""
        content_hash = self._hash_content(content)
        now = datetime.now().isoformat()
        
        self.conn.execute('''
            INSERT OR REPLACE INTO file_hashes 
            (file_path, content_hash, updated_at)
            VALUES (?, ?, ?)
        ''', (file_path, content_hash, now))
        self.conn.commit()
    
    def file_needs_update(self, file_path: str, current_content: str) -> bool:
        """Check if file needs reindexing"""
        cursor = self.conn.execute(
            'SELECT content_hash FROM file_hashes WHERE file_path = ?',
            (file_path,)
        )
        row = cursor.fetchone()
        
        if not row:
            return True
        
        current_hash = self._hash_content(current_content)
        return current_hash != row['content_hash']
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total_sources,
                AVG(trust_score) as avg_trust,
                AVG(entropy) as avg_entropy,
                MAX(trust_score) as max_trust,
                MIN(trust_score) as min_trust
            FROM sources
        ''')
        row = cursor.fetchone()
        
        return dict(row) if row else {}
    
    def clear(self):
        """Clear all sources (for testing)"""
        self.conn.execute('DELETE FROM sources')
        self.conn.execute('DELETE FROM file_hashes')
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    @staticmethod
    def _hash_content(content: str) -> str:
        """Hash content for change detection"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

