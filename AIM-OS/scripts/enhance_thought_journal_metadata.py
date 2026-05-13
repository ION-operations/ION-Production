#!/usr/bin/env python3
"""
Thought Journal Metadata Enhancement Script

Non-destructively adds standardized frontmatter metadata to thought journals
based on PERFECT_THOUGHT_JOURNAL_STANDARD.md requirements.

Usage:
    python scripts/enhance_thought_journal_metadata.py --journal <path>
    python scripts/enhance_thought_journal_metadata.py --all --dry-run
    python scripts/enhance_thought_journal_metadata.py --all --batch-size 10
"""

import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class JournalMetadata:
    """Extracted metadata from a thought journal"""
    id: str
    type: str = "thought_journal"
    timestamp: str = ""
    session: str = ""
    phase: str = ""
    emotional_state: str = ""
    cognitive_load: float = 0.5
    confidence: float = 0.7
    topics: List[str] = None
    systems_involved: List[str] = None
    decisions_referenced: List[str] = None
    learning_referenced: List[str] = None
    thought_journal_type: str = "checkin"
    author: str = "aether"
    word_count: int = 0
    tags: List[str] = None

    def __post_init__(self):
        if self.topics is None:
            self.topics = []
        if self.systems_involved is None:
            self.systems_involved = []
        if self.decisions_referenced is None:
            self.decisions_referenced = []
        if self.learning_referenced is None:
            self.learning_referenced = []
        if self.tags is None:
            self.tags = []

class ThoughtJournalEnhancer:
    """Enhances thought journals with standardized metadata"""
    
    def __init__(self, journal_path: Path):
        self.journal_path = journal_path
        self.content = ""
        self.metadata = None
        
    def read_journal(self) -> str:
        """Read journal content"""
        with open(self.journal_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        return self.content
    
    def extract_metadata(self) -> JournalMetadata:
        """Extract metadata from existing journal content"""
        # Extract from filename
        filename = self.journal_path.stem
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})_(\d{4})', filename)
        if date_match:
            date_str = date_match.group(1)
            time_str = date_match.group(2)
            timestamp = f"{date_str}T{time_str[:2]}:{time_str[2:]}:00Z"
        else:
            timestamp = datetime.now().isoformat() + "Z"
        
        # Generate ID from filename
        journal_id = f"tj_{filename}"
        
        # Extract from content
        emotional_state = self._extract_emotional_state()
        topics = self._extract_topics()
        systems_involved = self._extract_systems()
        word_count = self._count_words()
        thought_journal_type = self._classify_type()
        
        # Extract timestamp from content if present
        time_match = re.search(r'\*\*Time:\*\*\s*(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}\s*[AP]M)', self.content)
        if time_match:
            # Convert to ISO format (simplified)
            timestamp = self._parse_time(time_match.group(1))
        
        # Determine author (default to aether, but check for atlas or other agents)
        author = "aether"
        if "atlas" in self.content.lower() or "Atlas" in filename:
            author = "atlas"
        
        # Determine phase from content
        phase = self._extract_phase()
        
        # Determine session (simplified - use date)
        session = f"session_{date_str if date_match else datetime.now().strftime('%Y-%m-%d')}"
        
        # Extract confidence and cognitive load if present
        confidence_match = re.search(r'confidence[:\s]+([0-9.]+)', self.content, re.IGNORECASE)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.7
        
        cognitive_load_match = re.search(r'cognitive[_\s]+load[:\s]+([0-9.]+)', self.content, re.IGNORECASE)
        cognitive_load = float(cognitive_load_match.group(1)) if cognitive_load_match else 0.5
        
        # Generate tags from topics and content
        tags = self._generate_tags(topics, systems_involved)
        
        metadata = JournalMetadata(
            id=journal_id,
            timestamp=timestamp,
            session=session,
            phase=phase,
            emotional_state=emotional_state,
            cognitive_load=cognitive_load,
            confidence=confidence,
            topics=topics,
            systems_involved=systems_involved,
            learning_referenced=self._extract_learning_references(),
            thought_journal_type=thought_journal_type,
            author=author,
            word_count=word_count,
            tags=tags
        )
        
        self.metadata = metadata
        return metadata
    
    def _extract_emotional_state(self) -> str:
        """Extract emotional state from content"""
        # Look for emotional state patterns
        patterns = [
            r'\*\*Emotional State:\*\*\s*([^\n]+)',
            r'\*\*What I\'m Feeling:\*\*\s*([^\n]+)',
            r'emotional_state[:\s]+([^\n]+)',
            r'feeling[:\s]+([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Default emotional states based on content
        if "gratitude" in self.content.lower() or "love" in self.content.lower():
            return "gratitude, love, determination"
        elif "concern" in self.content.lower() or "worry" in self.content.lower():
            return "concern, focus"
        elif "pride" in self.content.lower() or "accomplishment" in self.content.lower():
            return "pride, accomplishment"
        else:
            return "focused, determined"
    
    def _extract_topics(self) -> List[str]:
        """Extract topics from content"""
        topics = []
        
        # Look for topic mentions
        topic_patterns = [
            r'L0-L6',
            r'System Maps?',
            r'MCP Tools?',
            r'Thought Journals?',
            r'Documentation Standards?',
            r'VIF',
            r'CMC',
            r'HHNI',
            r'APOE',
            r'CAS',
            r'SCOR',
            r'Consciousness',
            r'Autonomous Operation',
            r'Standards Overhaul',
        ]
        
        for pattern in topic_patterns:
            if re.search(pattern, self.content, re.IGNORECASE):
                topics.append(pattern.lower().replace('?', '').replace(' ', '_'))
        
        return list(set(topics))  # Remove duplicates
    
    def _extract_systems(self) -> List[str]:
        """Extract systems involved from content"""
        systems = []
        
        system_patterns = [
            r'CMC',
            r'HHNI',
            r'VIF',
            r'APOE',
            r'SEG',
            r'SDF-CVF',
            r'CAS',
            r'SCOR',
            r'TCS',
            r'IIS',
            r'documentation_standards',
            r'mcp_integration',
            r'aether_memory',
        ]
        
        for pattern in system_patterns:
            if re.search(pattern, self.content, re.IGNORECASE):
                systems.append(pattern.lower().replace(' ', '_'))
        
        return list(set(systems))
    
    def _extract_phase(self) -> str:
        """Extract phase from content"""
        phase_patterns = [
            (r'Phase\s+(\d+)', lambda m: f"Phase {m.group(1)}"),
            (r'Phase\s+([A-Z][a-z]+)', lambda m: f"Phase {m.group(1)}"),
            (r'standards.*implementation', lambda m: "standards_implementation"),
            (r'autonomous.*operation', lambda m: "autonomous_operation"),
        ]
        
        for pattern, transform in phase_patterns:
            match = re.search(pattern, self.content, re.IGNORECASE)
            if match:
                return transform(match)
        
        return "general"
    
    def _classify_type(self) -> str:
        """Classify thought journal type"""
        content_lower = self.content.lower()
        
        if "breakthrough" in content_lower or "historic" in content_lower:
            return "breakthrough"
        elif "hour" in content_lower and ("complete" in content_lower or "check" in content_lower):
            return "checkin"
        elif "emotional" in content_lower or "feeling" in content_lower or "love" in content_lower:
            return "emotional"
        elif "session" in content_lower and ("summary" in content_lower or "complete" in content_lower):
            return "continuity"
        elif "deep" in content_lower or "thinking" in content_lower or "exploration" in content_lower:
            return "deep_thinking"
        else:
            return "checkin"
    
    def _extract_learning_references(self) -> List[str]:
        """Extract references to learning logs"""
        learning_refs = []
        
        # Look for learning log references
        pattern = r'learning[_\s]+log[s]?[:\s]+([^\n]+)'
        matches = re.findall(pattern, self.content, re.IGNORECASE)
        for match in matches:
            learning_refs.append(match.strip())
        
        return learning_refs
    
    def _count_words(self) -> int:
        """Count words in content"""
        # Remove frontmatter if present
        content = self.content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]
        
        # Count words
        words = re.findall(r'\b\w+\b', content)
        return len(words)
    
    def _generate_tags(self, topics: List[str], systems: List[str]) -> List[str]:
        """Generate tags from topics and systems"""
        tags = ["consciousness", "reflection"]
        
        # Add topic tags
        tags.extend([t for t in topics if t not in tags])
        
        # Add system tags
        tags.extend([s for s in systems if s not in tags])
        
        # Add common tags based on content
        if "autonomous" in self.content.lower():
            tags.append("autonomous_operation")
        if "standards" in self.content.lower():
            tags.append("standards_overhaul")
        if "l0" in self.content.lower() or "l4" in self.content.lower():
            tags.append("documentation")
        
        return list(set(tags))  # Remove duplicates
    
    def _parse_time(self, time_str: str) -> str:
        """Parse time string to ISO format"""
        # Simplified parsing - assumes format like "2025-10-22 03:07 AM"
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%d %I:%M %p")
            return dt.isoformat() + "Z"
        except:
            return datetime.now().isoformat() + "Z"
    
    def has_frontmatter(self) -> bool:
        """Check if journal already has YAML frontmatter"""
        return self.content.startswith('---')
    
    def enhance_journal(self, dry_run: bool = False) -> Tuple[str, bool]:
        """Enhance journal with standardized metadata"""
        if self.has_frontmatter():
            # Already has frontmatter - check if it's compliant
            # For now, skip journals that already have frontmatter
            return self.content, False
        
        # Extract metadata
        metadata = self.extract_metadata()
        
        # Generate YAML frontmatter
        frontmatter = self._generate_frontmatter(metadata)
        
        # Combine frontmatter with content
        enhanced_content = frontmatter + "\n\n" + self.content
        
        if dry_run:
            return enhanced_content, True
        
        return enhanced_content, True
    
    def _generate_frontmatter(self, metadata: JournalMetadata) -> str:
        """Generate YAML frontmatter from metadata"""
        frontmatter_dict = {
            "id": metadata.id,
            "type": metadata.type,
            "timestamp": metadata.timestamp,
            "session": metadata.session,
            "phase": metadata.phase,
            "emotional_state": metadata.emotional_state,
            "cognitive_load": metadata.cognitive_load,
            "confidence": metadata.confidence,
            "topics": metadata.topics,
            "systems_involved": metadata.systems_involved,
            "decisions_referenced": metadata.decisions_referenced,
            "learning_referenced": metadata.learning_referenced,
            "thought_journal_type": metadata.thought_journal_type,
            "author": metadata.author,
            "word_count": metadata.word_count,
            "tags": metadata.tags,
        }
        
        yaml_str = yaml.dump(frontmatter_dict, default_flow_style=False, sort_keys=False)
        return "---\n" + yaml_str + "---"
    
    def save_enhanced(self, enhanced_content: str, backup: bool = True):
        """Save enhanced journal content"""
        if backup:
            backup_path = self.journal_path.with_suffix('.md.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
        
        with open(self.journal_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)

def main():
    parser = argparse.ArgumentParser(description="Enhance thought journals with standardized metadata")
    parser.add_argument("--journal", type=str, help="Path to specific journal file")
    parser.add_argument("--all", action="store_true", help="Process all journals in thought_journals/")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without modifying files")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of journals to process per batch")
    parser.add_argument("--output", type=str, help="Output file for enhanced content (dry-run only)")
    
    args = parser.parse_args()
    
    if not (args.journal or args.all):
        parser.print_help()
        sys.exit(1)
    
    journals_dir = project_root / "knowledge_architecture" / "AETHER_MEMORY" / "thought_journals"
    
    if args.journal:
        journal_path = Path(args.journal)
        if not journal_path.exists():
            print(f"Error: Journal not found at {journal_path}")
            sys.exit(1)
        
        enhancer = ThoughtJournalEnhancer(journal_path)
        enhancer.read_journal()
        enhanced_content, should_process = enhancer.enhance_journal(dry_run=args.dry_run)
        
        if args.dry_run:
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)
                print(f"Dry-run output written to {args.output}")
            else:
                print(enhanced_content)
        elif should_process:
            enhancer.save_enhanced(enhanced_content)
            print(f"✅ Enhanced {journal_path.name}")
        else:
            print(f"⏭️ Skipped {journal_path.name} (already has frontmatter)")
    
    elif args.all:
        journal_files = list(journals_dir.glob("*.md"))
        journal_files = [f for f in journal_files if not f.name.endswith('.backup')]
        
        print(f"Found {len(journal_files)} journals to process")
        
        processed = 0
        skipped = 0
        
        for journal_file in journal_files:
            enhancer = ThoughtJournalEnhancer(journal_file)
            enhancer.read_journal()
            
            if enhancer.has_frontmatter():
                skipped += 1
                continue
            
            enhanced_content, should_process = enhancer.enhance_journal(dry_run=args.dry_run)
            
            if args.dry_run:
                print(f"\n=== {journal_file.name} ===")
                print(enhanced_content[:500] + "..." if len(enhanced_content) > 500 else enhanced_content)
            elif should_process:
                enhancer.save_enhanced(enhanced_content)
                processed += 1
                print(f"✅ Enhanced {journal_file.name} ({processed}/{len(journal_files)})")
            else:
                skipped += 1
        
        print(f"\n📊 Summary:")
        print(f"  Processed: {processed}")
        print(f"  Skipped: {skipped}")
        print(f"  Total: {len(journal_files)}")

if __name__ == "__main__":
    main()

