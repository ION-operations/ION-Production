#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Textbook: Markdown to LaTeX Converter
Converts unified textbook chapters to LaTeX format for PDF compilation.

This integrates with the existing LaTeX build system at:
knowledge_architecture/systems/plix/textbook/latex/
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import existing markdown_to_latex converter
TEXTBOOK_ROOT = Path(__file__).parent.parent
LATEX_SCRIPT = TEXTBOOK_ROOT.parent.parent / "latex" / "scripts" / "markdown_to_latex.py"

if LATEX_SCRIPT.exists():
    # Import the existing converter
    import importlib.util
    spec = importlib.util.spec_from_file_location("markdown_to_latex", LATEX_SCRIPT)
    markdown_to_latex_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(markdown_to_latex_module)
    markdown_to_latex = markdown_to_latex_module.markdown_to_latex
else:
    print(f"[WARNING] Existing markdown_to_latex.py not found, using basic converter")
    def markdown_to_latex(md_text):
        # Basic fallback converter
        return md_text

def find_all_chapters() -> List[Tuple[int, Path, str]]:
    """Find all chapter files (same as compile_textbook.py)."""
    from compile_textbook import find_all_chapters as _find_all_chapters
    return _find_all_chapters()

def convert_to_latex(chapters: List[Tuple[int, Path, str]], latex_dir: Path) -> None:
    """Convert all chapters to LaTeX format."""
    chapters_dir = latex_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting {len(chapters)} chapters to LaTeX...")
    
    for i, (chapter_num, path, title) in enumerate(chapters, 1):
        print(f"  [{i}/{len(chapters)}] Chapter {chapter_num}: {title}")
        
        try:
            # Read markdown
            md_content = path.read_text(encoding='utf-8')
            
            # Convert to LaTeX
            latex_content = markdown_to_latex(md_content)
            
            # Write LaTeX file
            tex_file = chapters_dir / f"chapter_{chapter_num:02d}.tex"
            latex_output = f"% Chapter {chapter_num}: {title}\n% Auto-generated from unified textbook\n% Do not edit manually\n\n{latex_content}"
            tex_file.write_text(latex_output, encoding='utf-8')
            
        except Exception as e:
            print(f"    [ERROR] {e}")

def main():
    """Main conversion function."""
    # Find chapters
    print("Finding all chapters...")
    chapters = find_all_chapters()
    
    if not chapters:
        print("[ERROR] No chapters found!")
        return 1
    
    print(f"[OK] Found {len(chapters)} chapters")
    
    # Determine LaTeX directory
    latex_dir = TEXTBOOK_ROOT.parent / "latex"
    if not latex_dir.exists():
        print(f"[ERROR] LaTeX directory not found: {latex_dir}")
        print("   Expected: knowledge_architecture/systems/plix/textbook/latex/")
        return 1
    
    # Convert to LaTeX
    convert_to_latex(chapters, latex_dir)
    
    print(f"\n[OK] Conversion complete!")
    print(f"   LaTeX files: {latex_dir / 'chapters'}")
    print(f"   Next: Run 'make pdf' in {latex_dir} to compile PDF")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

