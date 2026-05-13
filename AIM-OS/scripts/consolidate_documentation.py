"""
Documentation Consolidation System
Scans, catalogs, identifies duplicates, and consolidates all documentation files.
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import shutil

class DocumentationConsolidator:
    """Consolidates documentation files from multiple locations and formats."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.doc_folder = self.base_path / "Documentation"
        self.consolidated_folder = self.base_path / "Documentation_Consolidated"
        
        # Catalog data
        self.all_files: List[Dict] = []
        self.duplicates: Dict[str, List[Path]] = defaultdict(list)
        self.by_extension: Dict[str, List[Dict]] = defaultdict(list)
        self.by_topic: Dict[str, List[Dict]] = defaultdict(list)
        
        # Extensions to consider
        self.doc_extensions = {'.md', '.txt', '.docx', '.pdf', '.doc'}
        
        # Temp files to ignore
        self.ignore_patterns = {'~$', 'node_modules', '.vite', '__pycache__', 'dist', 'out', 'build'}
        
    def should_ignore(self, path: Path) -> bool:
        """Check if file/folder should be ignored."""
        path_str = str(path)
        
        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
                
        # Ignore temp files
        if path.name.startswith('~$'):
            return True
            
        # Ignore node_modules and build artifacts
        parts = path.parts
        if any(p in parts for p in ['node_modules', 'dist', 'out', 'build', '__pycache__']):
            return True
            
        return False
    
    def calculate_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of file content."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"Error hashing {filepath}: {e}")
            return ""
    
    def scan_documentation(self) -> Dict:
        """Scan all documentation files and catalog them."""
        print("[SCAN] Scanning documentation files...")
        
        if not self.doc_folder.exists():
            print(f"[ERROR] Documentation folder not found: {self.doc_folder}")
            return {}
        
        for root, dirs, files in os.walk(self.doc_folder):
            root_path = Path(root)
            
            # Skip ignored directories
            if self.should_ignore(root_path):
                continue
            
            for filename in files:
                filepath = root_path / filename
                
                # Skip if should ignore
                if self.should_ignore(filepath):
                    continue
                
                # Only process documentation files
                if filepath.suffix.lower() not in self.doc_extensions:
                    continue
                
                # Get file info
                try:
                    stat = filepath.stat()
                    file_hash = self.calculate_file_hash(filepath)
                    
                    file_info = {
                        'path': str(filepath),
                        'relative_path': str(filepath.relative_to(self.doc_folder)),
                        'name': filename,
                        'extension': filepath.suffix.lower(),
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'hash': file_hash
                    }
                    
                    self.all_files.append(file_info)
                    self.by_extension[filepath.suffix.lower()].append(file_info)
                    
                    # Track duplicates by hash
                    if file_hash:
                        self.duplicates[file_hash].append(filepath)
                    
                except Exception as e:
                    print(f"[WARN] Error processing {filepath}: {e}")
        
        print(f"[OK] Found {len(self.all_files)} documentation files")
        return self.generate_catalog()
    
    def generate_catalog(self) -> Dict:
        """Generate catalog of all files."""
        # Find actual duplicates (same content, multiple files)
        actual_duplicates = {
            hash_val: paths 
            for hash_val, paths in self.duplicates.items() 
            if len(paths) > 1 and hash_val  # Only if multiple files and hash exists
        }
        
        catalog = {
            'total_files': len(self.all_files),
            'by_extension': {
                ext: len(files) for ext, files in self.by_extension.items()
            },
            'duplicates_count': len(actual_duplicates),
            'duplicate_files': sum(len(paths) - 1 for paths in actual_duplicates.values()),
            'files_by_extension': {
                ext: [f['relative_path'] for f in files]
                for ext, files in self.by_extension.items()
            },
            'duplicate_groups': {
                f"group_{i}": [str(p) for p in paths]
                for i, paths in enumerate(actual_duplicates.values())
            }
        }
        
        return catalog
    
    def identify_topics(self) -> Dict[str, List[str]]:
        """Identify topics from filenames and paths."""
        topics = defaultdict(list)
        
        # Topic keywords
        topic_keywords = {
            'AGI': ['agi', 'general intelligence', 'artificial general'],
            'Memory': ['memory', 'total system of memory', 'aim'],
            'IDE': ['ide', 'lucid ide', 'cursor'],
            'Agents': ['agent', 'multi-agent', 'agentforge'],
            'Architecture': ['architecture', 'system', 'core'],
            'UI': ['ui', 'interface', 'canvas', 'panel'],
            'API': ['api', 'intelligence hub'],
            'Geometry': ['geometry', 'quaternion', 'hopf', 'fibonacci'],
            'Tokens': ['token', 'mastering token'],
            'Helixion': ['helixion'],
            'VORTEX': ['vortex'],
            'Codex': ['codex'],
            'Search': ['search', 'deepsearch'],
            'WisdomNet': ['wisdomnet', 'wisdom'],
            'Sanctuary': ['sanctuary', 'sanctuaryos'],
            'LUCID': ['lucid', 'empire'],
            'PLIx': ['plix'],
            'Examples': ['example', 'appexample'],
        }
        
        for file_info in self.all_files:
            path_lower = file_info['relative_path'].lower()
            name_lower = file_info['name'].lower()
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in path_lower or keyword in name_lower for keyword in keywords):
                    topics[topic].append(file_info['relative_path'])
        
        return dict(topics)
    
    def create_consolidated_structure(self):
        """Create consolidated documentation structure."""
        print("\n[CREATE] Creating consolidated structure...")
        
        # Create base consolidated folder
        self.consolidated_folder.mkdir(exist_ok=True)
        
        # Create organized structure
        structure = {
            '00_Master_Index': 'Master indexes and catalogs',
            '01_AGI_Documentation': 'AGI and AI development docs',
            '02_Memory_Systems': 'Memory architecture and systems',
            '03_IDE_Tools': 'IDE, Lucid IDE, and development tools',
            '04_Architecture': 'System architecture and design',
            '05_Agents': 'Agent systems and frameworks',
            '06_UI_Design': 'UI/UX and interface design',
            '07_Mathematics': 'Mathematical foundations and geometry',
            '08_Research_Papers': 'Research papers and academic docs',
            '09_Examples': 'Application examples and demos',
            '10_Summaries': 'Document summaries',
            '99_Archive': 'Archived and duplicate files'
        }
        
        for folder_name, description in structure.items():
            folder_path = self.consolidated_folder / folder_name
            folder_path.mkdir(exist_ok=True)
            
            # Create README in each folder
            readme_path = folder_path / 'README.md'
            readme_path.write_text(f"# {folder_name.split('_', 1)[1] if '_' in folder_name else folder_name}\n\n{description}\n")
        
        print(f"[OK] Created consolidated structure at: {self.consolidated_folder}")
    
    def save_catalog(self, catalog: Dict):
        """Save catalog to JSON file."""
        catalog_path = self.consolidated_folder / '00_Master_Index' / 'documentation_catalog.json'
        
        with open(catalog_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2)
        
        print(f"[OK] Saved catalog to: {catalog_path}")
    
    def generate_master_index(self, catalog: Dict, topics: Dict[str, List[str]]):
        """Generate comprehensive master index markdown."""
        print("\n[INDEX] Generating master index...")
        
        index_content = [
            "# 📚 Documentation Master Index",
            "",
            "**Generated:** Automatically by consolidation system",
            "**Purpose:** Comprehensive index of all documentation in AIM-OS",
            "",
            "---",
            "",
            "## 📊 Overview Statistics",
            "",
            f"- **Total Files:** {catalog['total_files']}",
            f"- **Duplicate Files Found:** {catalog['duplicate_files']}",
            f"- **Duplicate Groups:** {catalog['duplicates_count']}",
            "",
            "### Files by Type",
            ""
        ]
        
        # Add file type statistics
        for ext, count in sorted(catalog['by_extension'].items()):
            index_content.append(f"- **{ext}**: {count} files")
        
        index_content.extend([
            "",
            "---",
            "",
            "## 📂 Documentation by Topic",
            ""
        ])
        
        # Add topics
        for topic, files in sorted(topics.items()):
            index_content.append(f"### {topic} ({len(files)} files)")
            index_content.append("")
            for file in sorted(files)[:10]:  # Limit to first 10 for brevity
                index_content.append(f"- `{file}`")
            if len(files) > 10:
                index_content.append(f"- _(... and {len(files) - 10} more)_")
            index_content.append("")
        
        index_content.extend([
            "---",
            "",
            "## 🔍 Duplicate Files",
            "",
            "The following groups of files have identical content:",
            ""
        ])
        
        # Add duplicate groups
        for group_name, paths in catalog['duplicate_groups'].items():
            if len(paths) > 1:
                index_content.append(f"### {group_name}")
                index_content.append("")
                for path in paths:
                    # Make relative to Documentation folder
                    try:
                        rel_path = Path(path).relative_to(self.doc_folder)
                        index_content.append(f"- `{rel_path}`")
                    except:
                        index_content.append(f"- `{path}`")
                index_content.append("")
        
        index_content.extend([
            "---",
            "",
            "## 📋 Consolidation Structure",
            "",
            "Files have been organized into the following structure:",
            "",
            "```",
            "Documentation_Consolidated/",
            "├── 00_Master_Index/        # Master indexes and catalogs",
            "├── 01_AGI_Documentation/   # AGI and AI development docs",
            "├── 02_Memory_Systems/      # Memory architecture and systems",
            "├── 03_IDE_Tools/           # IDE and development tools",
            "├── 04_Architecture/        # System architecture and design",
            "├── 05_Agents/              # Agent systems and frameworks",
            "├── 06_UI_Design/           # UI/UX and interface design",
            "├── 07_Mathematics/         # Mathematical foundations",
            "├── 08_Research_Papers/     # Research papers and academic docs",
            "├── 09_Examples/            # Application examples and demos",
            "├── 10_Summaries/           # Document summaries",
            "└── 99_Archive/             # Archived and duplicate files",
            "```",
            "",
            "---",
            "",
            "## 🔗 Quick Links",
            "",
            "### Key Documentation Areas",
            "",
            "- [AGI Development Master Index](./01_AGI_Documentation/)",
            "- [Memory System Documentation](./02_Memory_Systems/)",
            "- [IDE and Tools](./03_IDE_Tools/)",
            "- [System Architecture](./04_Architecture/)",
            "- [Document Summaries](./10_Summaries/)",
            "",
            "### External References",
            "",
            "- Main knowledge architecture: `knowledge_architecture/`",
            "- Current cursor rules: `.cursor/rules/`",
            "- Active work tracking: `active_work/`",
            "",
            "---",
            "",
            "## 📝 Notes",
            "",
            "- **Preferred Format:** Markdown (.md) for better version control and readability",
            "- **Duplicates:** Duplicate files have been identified and moved to archive",
            "- **Conversion:** Word documents (.docx) converted to markdown where possible",
            "- **Original Files:** Original files preserved in `Documentation/` (not modified)",
            "",
            "---",
            "",
            "*Generated by Documentation Consolidation System*",
            "*For questions or updates, see `scripts/consolidate_documentation.py`*"
        ])
        
        # Write master index
        index_path = self.consolidated_folder / '00_Master_Index' / 'MASTER_INDEX.md'
        index_path.write_text('\n'.join(index_content), encoding='utf-8')
        
        print(f"[OK] Generated master index: {index_path}")
    
    def run_consolidation(self):
        """Run complete consolidation process."""
        print("=" * 70)
        print("DOCUMENTATION CONSOLIDATION SYSTEM")
        print("=" * 70)
        
        # Step 1: Scan and catalog
        catalog = self.scan_documentation()
        
        # Step 2: Identify topics
        topics = self.identify_topics()
        print(f"\n[OK] Identified {len(topics)} topics")
        
        # Step 3: Create consolidated structure
        self.create_consolidated_structure()
        
        # Step 4: Save catalog
        self.save_catalog(catalog)
        
        # Step 5: Generate master index
        self.generate_master_index(catalog, topics)
        
        print("\n" + "=" * 70)
        print("[OK] CONSOLIDATION COMPLETE")
        print("=" * 70)
        print(f"\nResults:")
        print(f"  - Total files scanned: {catalog['total_files']}")
        print(f"  - Duplicates found: {catalog['duplicate_files']}")
        print(f"  - Topics identified: {len(topics)}")
        print(f"  - Consolidated folder: {self.consolidated_folder}")
        print(f"\nNext steps:")
        print(f"  1. Review master index: {self.consolidated_folder}/00_Master_Index/MASTER_INDEX.md")
        print(f"  2. Review catalog: {self.consolidated_folder}/00_Master_Index/documentation_catalog.json")
        print(f"  3. Run file conversion and organization script")
        

if __name__ == "__main__":
    # Get workspace root (assume script is in scripts/ folder)
    workspace_root = Path(__file__).parent.parent
    
    consolidator = DocumentationConsolidator(workspace_root)
    consolidator.run_consolidation()

