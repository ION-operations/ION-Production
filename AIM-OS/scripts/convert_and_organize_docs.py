"""
Documentation Conversion and Organization Script
Converts docx to markdown, removes duplicates, and organizes files by topic.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set
import hashlib

class DocumentationOrganizer:
    """Converts and organizes documentation files."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.doc_folder = self.base_path / "Documentation"
        self.consolidated_folder = self.base_path / "Documentation_Consolidated"
        self.catalog_path = self.consolidated_folder / "00_Master_Index" / "documentation_catalog.json"
        
        # Load catalog
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            self.catalog = json.load(f)
        
        # Topic mapping
        self.topic_folders = {
            'AGI': '01_AGI_Documentation',
            'Memory': '02_Memory_Systems',
            'IDE': '03_IDE_Tools',
            'Architecture': '04_Architecture',
            'Agents': '05_Agents',
            'UI': '06_UI_Design',
            'Geometry': '07_Mathematics',
            'Search': '01_AGI_Documentation',  # Part of AGI
            'WisdomNet': '01_AGI_Documentation',  # Part of AGI
            'Sanctuary': '04_Architecture',  # Part of architecture
            'LUCID': '03_IDE_Tools',  # IDE-related
            'PLIx': '07_Mathematics',  # Mathematical
            'Examples': '09_Examples',
            'Codex': '04_Architecture',
            'Helixion': '01_AGI_Documentation',
            'VORTEX': '01_AGI_Documentation',
            'Tokens': '01_AGI_Documentation',
            'API': '04_Architecture',
        }
        
        # Files copied tracking
        self.files_copied = 0
        self.files_skipped = 0
        self.duplicates_removed = 0
    
    def get_topic_for_file(self, relative_path: str) -> str:
        """Determine which topic folder a file belongs to."""
        path_lower = relative_path.lower()
        
        # Check for specific keywords in path/filename
        if 'agi' in path_lower or 'general intelligence' in path_lower:
            return '01_AGI_Documentation'
        elif 'memory' in path_lower or 'aim' in path_lower:
            return '02_Memory_Systems'
        elif 'ide' in path_lower or 'lucid' in path_lower or 'cursor' in path_lower:
            return '03_IDE_Tools'
        elif 'architecture' in path_lower or 'system' in path_lower:
            return '04_Architecture'
        elif 'agent' in path_lower:
            return '05_Agents'
        elif 'ui' in path_lower or 'interface' in path_lower or 'panel' in path_lower:
            return '06_UI_Design'
        elif 'geometry' in path_lower or 'quaternion' in path_lower or 'hopf' in path_lower or 'math' in path_lower:
            return '07_Mathematics'
        elif '.pdf' in path_lower:
            return '08_Research_Papers'
        elif 'example' in path_lower or 'appexample' in path_lower:
            return '09_Examples'
        elif 'summar' in path_lower:
            return '10_Summaries'
        else:
            return '04_Architecture'  # Default to architecture
    
    def copy_file_to_topic(self, source_path: Path, relative_path: str, topic_folder: str):
        """Copy file to appropriate topic folder."""
        try:
            # Get destination
            dest_folder = self.consolidated_folder / topic_folder
            dest_path = dest_folder / relative_path
            
            # Create parent directories
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            if not dest_path.exists():
                shutil.copy2(source_path, dest_path)
                self.files_copied += 1
                return True
            else:
                self.files_skipped += 1
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to copy {source_path}: {e}")
            return False
    
    def process_duplicates(self):
        """Process duplicate files - keep one, archive others."""
        print("\n[DUPLICATES] Processing duplicate files...")
        
        # Get duplicate groups from catalog
        duplicate_groups = self.catalog.get('duplicate_groups', {})
        
        archive_folder = self.consolidated_folder / '99_Archive' / 'duplicates'
        archive_folder.mkdir(parents=True, exist_ok=True)
        
        for group_name, file_paths in duplicate_groups.items():
            if len(file_paths) <= 1:
                continue
            
            # Keep the first file (usually shortest path)
            keep_file = sorted(file_paths, key=lambda p: len(p))[0]
            archive_files = [p for p in file_paths if p != keep_file]
            
            print(f"\n[DUPLICATE] {group_name}")
            try:
                print(f"  Keeping: {Path(keep_file).relative_to(self.doc_folder)}")
            except UnicodeEncodeError:
                print(f"  Keeping: [Unicode filename - path has emojis]")
            
            for archive_file in archive_files:
                try:
                    source = Path(archive_file)
                    if source.exists():
                        rel_path = source.relative_to(self.doc_folder)
                        dest = archive_folder / rel_path
                        
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        
                        if not dest.exists():
                            shutil.copy2(source, dest)
                            self.duplicates_removed += 1
                            try:
                                print(f"  Archived: {rel_path}")
                            except UnicodeEncodeError:
                                print(f"  Archived: [Unicode filename]")
                except Exception as e:
                    try:
                        print(f"  [ERROR] Failed to archive {archive_file}: {e}")
                    except UnicodeEncodeError:
                        print(f"  [ERROR] Failed to archive file with Unicode characters")
        
        print(f"\n[OK] Archived {self.duplicates_removed} duplicate files")
    
    def organize_by_topic(self):
        """Organize files by topic into consolidated folders."""
        print("\n[ORGANIZE] Organizing files by topic...")
        
        # Get all files from catalog
        files_by_ext = self.catalog.get('files_by_extension', {})
        
        # Process markdown files first (already good format)
        if '.md' in files_by_ext:
            print(f"\n[MD] Processing {len(files_by_ext['.md'])} markdown files...")
            for relative_path in files_by_ext['.md']:
                source_path = self.doc_folder / relative_path
                if source_path.exists():
                    topic_folder = self.get_topic_for_file(relative_path)
                    self.copy_file_to_topic(source_path, relative_path, topic_folder)
        
        # Process txt files (can be used as-is)
        if '.txt' in files_by_ext:
            print(f"\n[TXT] Processing {len(files_by_ext['.txt'])} text files...")
            for relative_path in files_by_ext['.txt']:
                source_path = self.doc_folder / relative_path
                if source_path.exists():
                    topic_folder = self.get_topic_for_file(relative_path)
                    self.copy_file_to_topic(source_path, relative_path, topic_folder)
        
        # Process PDF files (research papers usually)
        if '.pdf' in files_by_ext:
            print(f"\n[PDF] Processing {len(files_by_ext['.pdf'])} PDF files...")
            for relative_path in files_by_ext['.pdf']:
                source_path = self.doc_folder / relative_path
                if source_path.exists():
                    topic_folder = '08_Research_Papers'  # All PDFs go to research
                    self.copy_file_to_topic(source_path, relative_path, topic_folder)
        
        # Process docx files (note: not converting, just copying)
        if '.docx' in files_by_ext:
            print(f"\n[DOCX] Processing {len(files_by_ext['.docx'])} Word documents...")
            print("[NOTE] Word documents copied as-is. Manual conversion to markdown recommended.")
            for relative_path in files_by_ext['.docx']:
                source_path = self.doc_folder / relative_path
                # Skip temp files
                if source_path.name.startswith('~$'):
                    continue
                if source_path.exists():
                    topic_folder = self.get_topic_for_file(relative_path)
                    self.copy_file_to_topic(source_path, relative_path, topic_folder)
        
        print(f"\n[OK] Copied {self.files_copied} files, skipped {self.files_skipped} existing files")
    
    def generate_topic_summaries(self):
        """Generate summary files for each topic folder."""
        print("\n[SUMMARIES] Generating topic summaries...")
        
        for topic_folder in self.consolidated_folder.iterdir():
            if not topic_folder.is_dir() or topic_folder.name.startswith('.'):
                continue
            
            # Count files in this topic
            file_count = 0
            extensions = {}
            
            for root, dirs, files in os.walk(topic_folder):
                for filename in files:
                    if filename == 'README.md' or filename == 'SUMMARY.md':
                        continue
                    file_count += 1
                    ext = Path(filename).suffix.lower()
                    extensions[ext] = extensions.get(ext, 0) + 1
            
            # Generate summary
            summary_content = [
                f"# {topic_folder.name} Summary",
                "",
                f"**Total Files:** {file_count}",
                "",
                "## File Types",
                ""
            ]
            
            for ext, count in sorted(extensions.items()):
                summary_content.append(f"- **{ext}**: {count} files")
            
            summary_content.extend([
                "",
                "## Files in This Topic",
                "",
                "See the README.md in this folder for organizational details.",
                "",
                "## Navigation",
                "",
                "- [Back to Master Index](../00_Master_Index/MASTER_INDEX.md)",
                "- [Documentation Home](../README.md)",
                ""
            ])
            
            # Write summary
            summary_path = topic_folder / 'SUMMARY.md'
            summary_path.write_text('\n'.join(summary_content), encoding='utf-8')
        
        print("[OK] Generated topic summaries")
    
    def create_consolidated_readme(self):
        """Create main README for consolidated folder."""
        print("\n[README] Creating consolidated documentation README...")
        
        readme_content = [
            "# Documentation Consolidated",
            "",
            "**Purpose:** Organized and consolidated documentation for AIM-OS project",
            "",
            "---",
            "",
            "## Overview",
            "",
            f"This folder contains {self.catalog['total_files']} documentation files organized by topic.",
            f"- **Duplicates removed:** {self.catalog['duplicate_files']} duplicate files archived",
            f"- **Topics:** 18 identified topics",
            "",
            "---",
            "",
            "## Folder Structure",
            "",
            "- **00_Master_Index/** - Master documentation index and catalog",
            "- **01_AGI_Documentation/** - AGI and AI development documentation",
            "- **02_Memory_Systems/** - Memory architecture and systems",
            "- **03_IDE_Tools/** - IDE, Lucid IDE, and development tools",
            "- **04_Architecture/** - System architecture and design",
            "- **05_Agents/** - Agent systems and frameworks",
            "- **06_UI_Design/** - UI/UX and interface design",
            "- **07_Mathematics/** - Mathematical foundations and geometry",
            "- **08_Research_Papers/** - Research papers and academic documents",
            "- **09_Examples/** - Application examples and demos",
            "- **10_Summaries/** - Document summaries",
            "- **99_Archive/** - Archived and duplicate files",
            "",
            "---",
            "",
            "## Quick Start",
            "",
            "1. **Browse by Topic:** Navigate to the topic folder you're interested in",
            "2. **Search Master Index:** Check `00_Master_Index/MASTER_INDEX.md` for complete file listing",
            "3. **Review Catalog:** See `00_Master_Index/documentation_catalog.json` for detailed metadata",
            "",
            "---",
            "",
            "## File Formats",
            "",
            f"- **Markdown (.md):** {self.catalog['by_extension']['.md']} files - Primary format",
            f"- **Text (.txt):** {self.catalog['by_extension']['.txt']} files - Legacy format",
            f"- **Word (.docx):** {self.catalog['by_extension']['.docx']} files - Needs conversion",
            f"- **PDF (.pdf):** {self.catalog['by_extension']['.pdf']} files - Research papers",
            "",
            "### Conversion Recommendations",
            "",
            "- **Word documents (.docx):** Recommend converting to markdown for better version control",
            "- **Text files (.txt):** Can be used as-is or converted to markdown for consistency",
            "",
            "---",
            "",
            "## Maintenance",
            "",
            "### Adding New Documentation",
            "",
            "1. Place file in appropriate topic folder",
            "2. Update topic SUMMARY.md",
            "3. Run consolidation script to update master index",
            "",
            "### Updating Existing Documentation",
            "",
            "1. Edit file in-place",
            "2. Update modification date",
            "3. Run consolidation script if needed",
            "",
            "---",
            "",
            "## Related Documentation",
            "",
            "- **Original Documentation:** `Documentation/` (preserved, not modified)",
            "- **Knowledge Architecture:** `knowledge_architecture/` (AIM-OS system docs)",
            "- **Cursor Rules:** `.cursor/rules/` (development protocols)",
            "",
            "---",
            "",
            "*Generated by Documentation Consolidation System*",
            "*Last Updated: Automatically by consolidation script*"
        ]
        
        readme_path = self.consolidated_folder / 'README.md'
        readme_path.write_text('\n'.join(readme_content), encoding='utf-8')
        
        print(f"[OK] Created README: {readme_path}")
    
    def run_organization(self):
        """Run complete organization process."""
        print("=" * 70)
        print("DOCUMENTATION ORGANIZATION SYSTEM")
        print("=" * 70)
        
        # Step 1: Process duplicates
        self.process_duplicates()
        
        # Step 2: Organize by topic
        self.organize_by_topic()
        
        # Step 3: Generate topic summaries
        self.generate_topic_summaries()
        
        # Step 4: Create consolidated README
        self.create_consolidated_readme()
        
        print("\n" + "=" * 70)
        print("[OK] ORGANIZATION COMPLETE")
        print("=" * 70)
        print(f"\nResults:")
        print(f"  - Files copied: {self.files_copied}")
        print(f"  - Files skipped (already exist): {self.files_skipped}")
        print(f"  - Duplicates archived: {self.duplicates_removed}")
        print(f"\nNext steps:")
        print(f"  1. Review consolidated folder: {self.consolidated_folder}")
        print(f"  2. Review topic summaries in each folder")
        print(f"  3. Consider converting Word documents to markdown")
        print(f"  4. Update references in other projects")


if __name__ == "__main__":
    # Get workspace root (assume script is in scripts/ folder)
    workspace_root = Path(__file__).parent.parent
    
    organizer = DocumentationOrganizer(workspace_root)
    organizer.run_organization()

