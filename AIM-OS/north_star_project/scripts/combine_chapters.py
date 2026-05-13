# Script to Combine All Chapters into Master Document
# Usage: python combine_chapters.py

import os
import re
from pathlib import Path

def get_chapter_order():
    """Get chapters in numerical order"""
    base_dir = Path(__file__).parent.parent
    chapters_dir = base_dir / "chapters"
    chapters = []
    
    for item in chapters_dir.iterdir():
        if item.is_dir() and item.name[0].isdigit():
            # Extract chapter number
            match = re.match(r'(\d+)_', item.name)
            if match:
                chapter_num = int(match.group(1))
                chapters.append((chapter_num, item.name))
    
    # Sort by chapter number
    chapters.sort(key=lambda x: x[0])
    return chapters

def read_chapter(chapter_dir):
    """Read chapter.md content"""
    chapter_file = chapter_dir / "chapter.md"
    if chapter_file.exists():
        return chapter_file.read_text(encoding='utf-8')
    return None

def combine_all_chapters():
    """Combine all chapters into master document"""
    
    # Get base directory (parent of scripts/)
    base_dir = Path(__file__).parent.parent
    
    # Read front matter
    front_matter = (base_dir / "FRONT_MATTER.md").read_text(encoding='utf-8')
    
    # Read main document structure (TOC, preface, intro)
    main_doc = (base_dir / "NORTH_STAR_DOCUMENT_COMPLETE.md").read_text(encoding='utf-8')
    
    # Get chapters in order
    chapters = get_chapter_order()
    
    # Combine chapters
    combined = []
    combined.append(front_matter)
    combined.append("\n\n---\n\n")
    combined.append(main_doc)
    combined.append("\n\n---\n\n")
    combined.append("# Part I: The Awakening\n\n")
    
    current_part = 1
    
    for chapter_num, chapter_name in chapters:
        chapter_dir = base_dir / "chapters" / chapter_name
        chapter_content = read_chapter(chapter_dir)
        
        if chapter_content:
            # Determine part based on chapter number
            if chapter_num <= 4:
                part = 1
            elif chapter_num <= 10:
                part = 2
            elif chapter_num <= 15:
                part = 3
            elif chapter_num <= 23:
                part = 4
            elif chapter_num <= 27:
                part = 5
            elif chapter_num <= 30:
                part = 6
            else:
                part = 7
            
            # Add part header if new part
            if part != current_part:
                part_names = {
                    1: "Part I: The Awakening",
                    2: "Part II: The Foundation",
                    3: "Part III: Consciousness Systems",
                    4: "Part IV: Authority & Mathematics",
                    5: "Part V: Compliance & Benchmarks",
                    6: "Part VI: Case Studies & Operations",
                    7: "Part VII: Reference"
                }
                combined.append(f"\n\n# {part_names[part]}\n\n")
                current_part = part
            
            # Add chapter
            combined.append(f"\n\n# Chapter {chapter_num}: {chapter_name.replace('_', ' ').title()}\n\n")
            combined.append(chapter_content)
            combined.append("\n\n---\n\n")
    
    # Add appendices
    appendices = (base_dir / "APPENDICES.md").read_text(encoding='utf-8')
    combined.append("\n\n# Appendices\n\n")
    combined.append(appendices)
    
    # Add back matter
    back_matter = (base_dir / "BACK_MATTER.md").read_text(encoding='utf-8')
    combined.append("\n\n---\n\n")
    combined.append(back_matter)
    
    # Write combined document
    output_file = base_dir / "THE_NORTH_STAR_DOCUMENT.md"
    output_file.write_text("".join(combined), encoding='utf-8')
    
    print(f"Combined document created: {output_file}")
    print(f"   Total chapters: {len(chapters)}")
    print(f"   Total length: {len(''.join(combined)):,} characters")

if __name__ == "__main__":
    combine_all_chapters()

