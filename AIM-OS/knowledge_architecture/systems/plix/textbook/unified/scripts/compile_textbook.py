#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Textbook Compiler
Compiles all 67 chapters into:
1. Single unified Markdown document with index
2. PDF (via LaTeX/Pandoc)
3. HTML (optional)

Usage:
    python compile_textbook.py [--format markdown|pdf|html|all] [--output-dir OUTPUT]
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
TEXTBOOK_ROOT = Path(__file__).parent.parent
CHAPTER_DIRS = [
    "Part_I_AIMOS_Foundations",
    "Part_II_Foundations",
    "Part_III_Architecture",
    "Part_IV_Integration",
    "Part_V_Implementation",
    "Part_VI_Philosophy",
    "Part_VII_Future",
    "Part_VIII",
]

# Part I subdirectories
PART_I_SUBDIRS = [
    "Part_I.1_The_Awakening",
    "Part_I.2_The_Foundation",
    "Part_I.3_Consciousness_Systems",
    "Part_I.4_Authority_Mathematics",
]

# Also check Part_I.5, Part_I.6, Part_I.7 (directly in unified/)
PART_I_DIRECT = ["Part_I.5_Compliance_Benchmarks", "Part_I.6_Case_Studies_Operations", "Part_I.7_Reference"]

def find_all_chapters() -> List[Tuple[int, Path, str]]:
    """Find all chapter files and return sorted list of (chapter_num, path, title)."""
    chapters = []
    
    # Part I chapters
    part_i_base = TEXTBOOK_ROOT / "Part_I_AIMOS_Foundations"
    for subdir in PART_I_SUBDIRS:
        subdir_path = part_i_base / subdir
        if subdir_path.exists():
            for chapter_file in sorted(subdir_path.glob("Chapter_*.md")):
                chapter_num = extract_chapter_number(chapter_file)
                if chapter_num:
                    title = extract_title(chapter_file)
                    chapters.append((chapter_num, chapter_file, title))
    
    # Part I direct chapters
    for subdir_name in PART_I_DIRECT:
        subdir_path = TEXTBOOK_ROOT / subdir_name
        if subdir_path.exists():
            for chapter_file in sorted(subdir_path.glob("Chapter_*.md")):
                chapter_num = extract_chapter_number(chapter_file)
                if chapter_num:
                    title = extract_title(chapter_file)
                    chapters.append((chapter_num, chapter_file, title))
    
    # Parts II-VIII
    for part_dir in CHAPTER_DIRS[1:]:  # Skip Part I (already handled)
        part_path = TEXTBOOK_ROOT / part_dir
        if part_path.exists():
            for chapter_file in sorted(part_path.glob("Chapter_*.md")):
                chapter_num = extract_chapter_number(chapter_file)
                if chapter_num:
                    title = extract_title(chapter_file)
                    chapters.append((chapter_num, chapter_file, title))
    
    # Sort by chapter number
    chapters.sort(key=lambda x: x[0])
    return chapters

def extract_chapter_number(path: Path) -> int:
    """Extract chapter number from content header (prioritized) or filename."""
    # PRIORITY 1: Try content header first (unified numbering)
    try:
        content = path.read_text(encoding='utf-8')
        # Look for "Unified Textbook Chapter Number: X" (highest priority)
        match = re.search(r'Unified Textbook Chapter Number[:\s]*(\d+)', content)
        if match:
            return int(match.group(1))
    except:
        pass
    
    # PRIORITY 2: Try filename (may have internal numbering)
    match = re.search(r'Chapter[_\s]*(\d+)', path.name)
    if match:
        num = int(match.group(1))
        # If filename number is 21-28 and we're in Part_VIII, it's actually 60-67
        if 'Part_VIII' in str(path) and 21 <= num <= 28:
            return num + 39  # Convert 21-28 to 60-67
        return num
    
    # PRIORITY 3: Try content header "# Chapter X:"
    try:
        content = path.read_text(encoding='utf-8')
        match = re.search(r'^#\s*Chapter\s+(\d+):', content, re.MULTILINE)
        if match:
            num = int(match.group(1))
            # Same conversion for Part VIII
            if 'Part_VIII' in str(path) and 21 <= num <= 28:
                return num + 39
            return num
    except:
        pass
    
    return None

def extract_title(path: Path) -> str:
    """Extract chapter title from file."""
    try:
        content = path.read_text(encoding='utf-8')
        # Look for "# Chapter X: Title"
        match = re.search(r'^#\s*Chapter\s+\d+[:\s]+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
    except:
        pass
    return path.stem

def generate_table_of_contents(chapters: List[Tuple[int, Path, str]]) -> str:
    """Generate table of contents from chapters."""
    toc = ["# Table of Contents\n"]
    
    current_part = None
    part_chapters = []
    
    for chapter_num, path, title in chapters:
        # Determine part from chapter number
        if chapter_num <= 35:
            part = "Part I: AIM-OS Foundations"
        elif chapter_num <= 39:
            part = "Part II: Foundations"
        elif chapter_num <= 43:
            part = "Part III: Architecture"
        elif chapter_num <= 47:
            part = "Part IV: Integration"
        elif chapter_num <= 51:
            part = "Part V: Implementation"
        elif chapter_num <= 55:
            part = "Part VI: Philosophy"
        elif chapter_num <= 59:
            part = "Part VII: Future"
        else:
            part = "Part VIII: Geometric Kernel"
        
        if part != current_part:
            if current_part is not None:
                toc.append(f"\n## {current_part}\n")
                for ch_num, _, ch_title in part_chapters:
                    toc.append(f"- **Chapter {ch_num}:** {ch_title}\n")
                part_chapters = []
            current_part = part
        
        part_chapters.append((chapter_num, path, title))
    
    # Add last part
    if part_chapters:
        toc.append(f"\n## {current_part}\n")
        for ch_num, _, ch_title in part_chapters:
            toc.append(f"- **Chapter {ch_num}:** {ch_title}\n")
    
    return "".join(toc)

def compile_markdown(chapters: List[Tuple[int, Path, str]], output_path: Path) -> None:
    """Compile all chapters into single Markdown document."""
    print(f"Compiling {len(chapters)} chapters into unified Markdown...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# The Complete AIM-OS Textbook\n")
        f.write("## From Philosophy to Geometric Kernel Implementation\n\n")
        f.write(f"**Version:** 1.0.0 (Unified Edition)\n")
        f.write(f"**Compiled:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Chapters:** {len(chapters)}\n")
        f.write(f"**Total Parts:** 8\n\n")
        f.write("---\n\n")
        
        # Write table of contents
        f.write(generate_table_of_contents(chapters))
        f.write("\n---\n\n")
        
        # Write chapters
        for i, (chapter_num, path, title) in enumerate(chapters, 1):
            print(f"  [{i}/{len(chapters)}] Chapter {chapter_num}: {title}")
            
            f.write(f"\n\n# Chapter {chapter_num}: {title}\n\n")
            f.write("---\n\n")
            
            # Read and write chapter content
            try:
                content = path.read_text(encoding='utf-8')
                # Remove the header line (we already wrote it)
                content = re.sub(r'^#\s*Chapter\s+\d+[:\s]+.+$', '', content, flags=re.MULTILINE)
                # Remove metadata lines at top
                content = re.sub(r'^\*\*Part.*?\*\*\s*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'^\*\*Unified Textbook Chapter Number.*?\*\*\s*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'^---\s*$', '', content, flags=re.MULTILINE)
                # Clean up multiple blank lines
                content = re.sub(r'\n{3,}', '\n\n', content)
                
                f.write(content)
                f.write("\n\n---\n\n")
            except Exception as e:
                print(f"    ERROR reading {path}: {e}")
                f.write(f"*[Error loading chapter content: {e}]*\n\n")
    
    print(f"\n[OK] Unified Markdown compiled: {output_path}")
    print(f"   Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

def compile_pdf(markdown_path: Path, output_path: Path) -> None:
    """Compile Markdown to PDF via LaTeX (using existing LaTeX system)."""
    print(f"\nCompiling PDF from Markdown using LaTeX...")
    
    import subprocess
    
    # Check if pdflatex is available
    try:
        subprocess.run(['pdflatex', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] pdflatex not found. Install LaTeX to generate PDF.")
        print("   Windows: MiKTeX (https://miktex.org/)")
        print("   macOS: MacTeX (https://www.tug.org/mactex/)")
        print("   Linux: sudo apt-get install texlive-full")
        return
    
    # Use existing LaTeX build system
    latex_dir = TEXTBOOK_ROOT.parent / "latex"
    if not latex_dir.exists():
        print(f"[ERROR] LaTeX directory not found: {latex_dir}")
        print("   Expected: knowledge_architecture/systems/plix/textbook/latex/")
        return
    
    # Check if Makefile exists
    makefile = latex_dir / "Makefile"
    if not makefile.exists():
        print(f"[ERROR] Makefile not found: {makefile}")
        print("   Need to set up LaTeX build system first")
        return
    
    # Option 1: Use Make (if available)
    try:
        subprocess.run(['make', '--version'], capture_output=True, check=True)
        print("Using Make to build PDF...")
        result = subprocess.run(
            ['make', 'pdf'],
            cwd=str(latex_dir),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Copy output PDF
            pdf_output = latex_dir / "PLIx_Textbook.pdf"
            if pdf_output.exists():
                import shutil
                shutil.copy2(pdf_output, output_path)
                print(f"[OK] PDF compiled: {output_path}")
                print(f"   Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
            else:
                print("[ERROR] PDF not generated (check build logs)")
        else:
            print(f"[ERROR] Make build failed:")
            print(result.stderr)
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # Make not available, try manual build
    
    # Option 2: Manual LaTeX build
    print("Using pdflatex directly...")
    main_tex = latex_dir / "main.tex"
    if not main_tex.exists():
        print(f"[ERROR] main.tex not found: {main_tex}")
        return
    
    try:
        # First pass
        print("  Running pdflatex (pass 1/3)...")
        subprocess.run(['pdflatex', '-interaction=nonstopmode', str(main_tex)], 
                      cwd=str(latex_dir), capture_output=True, check=False)
        
        # BibTeX (if bibliography exists)
        bib_file = latex_dir / "main.bib"
        if bib_file.exists():
            print("  Running bibtex...")
            subprocess.run(['bibtex', 'main'], cwd=str(latex_dir), 
                         capture_output=True, check=False)
        
        # Makeindex (if index exists)
        idx_file = latex_dir / "main.idx"
        if idx_file.exists():
            print("  Running makeindex...")
            subprocess.run(['makeindex', 'main'], cwd=str(latex_dir), 
                         capture_output=True, check=False)
        
        # Second pass
        print("  Running pdflatex (pass 2/3)...")
        subprocess.run(['pdflatex', '-interaction=nonstopmode', str(main_tex)], 
                      cwd=str(latex_dir), capture_output=True, check=False)
        
        # Third pass (for cross-references)
        print("  Running pdflatex (pass 3/3)...")
        subprocess.run(['pdflatex', '-interaction=nonstopmode', str(main_tex)], 
                      cwd=str(latex_dir), capture_output=True, check=False)
        
        # Copy output PDF
        pdf_output = latex_dir / "main.pdf"
        if pdf_output.exists():
            import shutil
            shutil.copy2(pdf_output, output_path)
            print(f"[OK] PDF compiled: {output_path}")
            print(f"   Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        else:
            print("[ERROR] PDF not generated (check build logs in latex/ directory)")
            
    except Exception as e:
        print(f"[ERROR] {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Compile unified textbook')
    parser.add_argument('--format', choices=['markdown', 'pdf', 'html', 'all'], 
                       default='all', help='Output format')
    parser.add_argument('--output-dir', type=Path, default=TEXTBOOK_ROOT / 'compiled',
                       help='Output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all chapters
    print("Finding all chapters...")
    chapters = find_all_chapters()
    
    if not chapters:
        print("[ERROR] No chapters found!")
        return 1
    
    print(f"[OK] Found {len(chapters)} chapters")
    
    # Compile formats
    if args.format in ['markdown', 'all']:
        markdown_path = args.output_dir / 'UNIFIED_TEXTBOOK.md'
        compile_markdown(chapters, markdown_path)
    
    if args.format in ['pdf', 'all']:
        if args.format == 'pdf':
            # Need to compile markdown first
            markdown_path = args.output_dir / 'UNIFIED_TEXTBOOK.md'
            if not markdown_path.exists():
                compile_markdown(chapters, markdown_path)
        
        pdf_path = args.output_dir / 'UNIFIED_TEXTBOOK.pdf'
        compile_pdf(markdown_path, pdf_path)
    
    if args.format in ['html', 'all']:
        print("\n[WARNING] HTML compilation not yet implemented")
    
    print("\n[OK] Compilation complete!")
    return 0

if __name__ == '__main__':
    sys.exit(main())

