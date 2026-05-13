#!/usr/bin/env python3
"""
PLIx Textbook PDF Generator
Compiles all textbook chapters into a beautiful PDF document.

Requirements:
    pip install markdown pypandoc-binary reportlab weasyprint
    OR
    pip install markdown pdfkit (requires wkhtmltopdf)
    OR
    pip install markdown-pdf (Node.js based)

This script uses multiple fallback methods for maximum compatibility.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import subprocess
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class PLIxPDFGenerator:
    """Generate beautiful PDF from PLIx textbook markdown files."""
    
    def __init__(self, textbook_dir: Path):
        self.textbook_dir = textbook_dir
        self.output_dir = textbook_dir / "pdf_output"
        self.output_dir.mkdir(exist_ok=True)
        
    def collect_chapters(self) -> List[Dict]:
        """Collect all chapters in order."""
        chapters = []
        
        # Part I: Foundations (Chapters 1-4)
        for i in range(1, 5):
            chapter_path = self.textbook_dir / f"Part_I/Chapter_{i:02d}.md"
            if chapter_path.exists():
                chapters.append({
                    'part': 'I',
                    'part_title': 'Foundations',
                    'chapter': i,
                    'path': chapter_path,
                    'title': self._extract_title(chapter_path)
                })
        
        # Part II: Architecture (Chapters 5-8)
        for i in range(5, 9):
            chapter_path = self.textbook_dir / f"Part_II/Chapter_{i:02d}.md"
            if chapter_path.exists():
                chapters.append({
                    'part': 'II',
                    'part_title': 'Architecture',
                    'chapter': i,
                    'path': chapter_path,
                    'title': self._extract_title(chapter_path)
                })
        
        # Part III: Integration (Chapters 9-12)
        for i in range(9, 13):
            chapter_path = self.textbook_dir / f"Part_III/Chapter_{i:02d}.md"
            if chapter_path.exists():
                chapters.append({
                    'part': 'III',
                    'part_title': 'Integration',
                    'chapter': i,
                    'path': chapter_path,
                    'title': self._extract_title(chapter_path)
                })
        
        # Part IV: Implementation (Chapters 13-16)
        for i in range(13, 17):
            chapter_path = self.textbook_dir / f"Part_IV/Chapter_{i:02d}.md"
            if chapter_path.exists():
                chapters.append({
                    'part': 'IV',
                    'part_title': 'Implementation',
                    'chapter': i,
                    'path': chapter_path,
                    'title': self._extract_title(chapter_path)
                })
        
        # Part V: Philosophy (Chapters 17-20)
        for i in range(17, 21):
            chapter_path = self.textbook_dir / f"Part_V/Chapter_{i:02d}.md"
            if chapter_path.exists():
                chapters.append({
                    'part': 'V',
                    'part_title': 'Philosophy',
                    'chapter': i,
                    'path': chapter_path,
                    'title': self._extract_title(chapter_path)
                })
        
        # Part VI: Future (Chapters 21-24)
        for i in range(21, 25):
            chapter_path = self.textbook_dir / f"Part_VI/Chapter_{i:02d}.md"
            if chapter_path.exists():
                chapters.append({
                    'part': 'VI',
                    'part_title': 'Future',
                    'chapter': i,
                    'path': chapter_path,
                    'title': self._extract_title(chapter_path)
                })
        
        return chapters
    
    def _extract_title(self, path: Path) -> str:
        """Extract title from markdown file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('# '):
                    return first_line[2:].strip()
                return path.stem
        except:
            return path.stem
    
    def create_combined_markdown(self, chapters: List[Dict]) -> Path:
        """Create combined markdown file with all chapters."""
        combined_path = self.output_dir / "PLIx_Textbook_Complete.md"
        
        with open(combined_path, 'w', encoding='utf-8') as out:
            # Title Page
            out.write("# PLIx: The Pure Language of Intent\n\n")
            out.write("**The Language of AI Consciousness**\n\n")
            out.write("---\n\n")
            out.write("**A Comprehensive Textbook**\n\n")
            out.write(f"**Date:** 2025-11-09\n\n")
            out.write(f"**Total Chapters:** {len(chapters)}\n\n")
            out.write(f"**Total Parts:** 6\n\n")
            out.write("---\n\n")
            out.write("\\newpage\n\n")
            
            # Table of Contents Placeholder
            out.write("# Table of Contents\n\n")
            out.write("## Part I: Foundations\n\n")
            for ch in chapters:
                if ch['part'] == 'I':
                    out.write(f"{ch['chapter']}. {ch['title']}\n\n")
            
            out.write("\n## Part II: Architecture\n\n")
            for ch in chapters:
                if ch['part'] == 'II':
                    out.write(f"{ch['chapter']}. {ch['title']}\n\n")
            
            out.write("\n## Part III: Integration\n\n")
            for ch in chapters:
                if ch['part'] == 'III':
                    out.write(f"{ch['chapter']}. {ch['title']}\n\n")
            
            out.write("\n## Part IV: Implementation\n\n")
            for ch in chapters:
                if ch['part'] == 'IV':
                    out.write(f"{ch['chapter']}. {ch['title']}\n\n")
            
            out.write("\n## Part V: Philosophy\n\n")
            for ch in chapters:
                if ch['part'] == 'V':
                    out.write(f"{ch['chapter']}. {ch['title']}\n\n")
            
            out.write("\n## Part VI: Future\n\n")
            for ch in chapters:
                if ch['part'] == 'VI':
                    out.write(f"{ch['chapter']}. {ch['title']}\n\n")
            
            out.write("\n---\n\n")
            out.write("\\newpage\n\n")
            
            # Chapters
            current_part = None
            for ch in chapters:
                # Part header
                if current_part != ch['part']:
                    if current_part is not None:
                        out.write("\n\\newpage\n\n")
                    out.write(f"# Part {ch['part']}: {ch['part_title']}\n\n")
                    out.write("---\n\n")
                    current_part = ch['part']
                
                # Chapter content
                out.write(f"\n# {ch['title']}\n\n")
                out.write(f"**Part {ch['part']} - Chapter {ch['chapter']}**\n\n")
                out.write("---\n\n")
                
                # Read and write chapter content
                with open(ch['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Remove the title line (already added)
                    lines = content.split('\n')
                    if lines[0].startswith('#'):
                        lines = lines[1:]
                    content = '\n'.join(lines).strip()
                    out.write(content)
                    out.write("\n\n")
                
                out.write("\n\\newpage\n\n")
        
        return combined_path
    
    def generate_pdf_pandoc(self, md_path: Path) -> Path:
        """Generate PDF using Pandoc (best quality)."""
        pdf_path = self.output_dir / "PLIx_Textbook.pdf"
        
        # Pandoc command with beautiful styling
        cmd = [
            'pandoc',
            str(md_path),
            '-o', str(pdf_path),
            '--pdf-engine=xelatex',
            '--variable', 'mainfont=Georgia',
            '--variable', 'sansfont=Arial',
            '--variable', 'monofont=Courier New',
            '--variable', 'fontsize=11pt',
            '--variable', 'geometry:margin=1in',
            '--variable', 'colorlinks=true',
            '--variable', 'linkcolor=blue',
            '--toc',
            '--toc-depth=3',
            '--number-sections',
            '--highlight-style=tango',
            '--template', str(self._create_latex_template())
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return pdf_path
        except subprocess.CalledProcessError as e:
            print(f"Pandoc error: {e.stderr.decode()}")
            return None
        except FileNotFoundError:
            print("Pandoc not found. Trying alternative method...")
            return None
    
    def generate_pdf_weasyprint(self, md_path: Path) -> Path:
        """Generate PDF using WeasyPrint (HTML-based)."""
        try:
            import markdown
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            # Convert markdown to HTML
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            html_content = markdown.markdown(md_content, extensions=['codehilite', 'tables', 'toc'])
            
            # Add CSS styling
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    @page {{
                        size: letter;
                        margin: 1in;
                        @top-center {{
                            content: "PLIx: The Pure Language of Intent";
                        }}
                        @bottom-center {{
                            content: "Page " counter(page);
                        }}
                    }}
                    body {{
                        font-family: Georgia, serif;
                        font-size: 11pt;
                        line-height: 1.6;
                        color: #333;
                    }}
                    h1 {{
                        font-size: 24pt;
                        color: #1a1a1a;
                        margin-top: 2em;
                        margin-bottom: 1em;
                        page-break-before: always;
                    }}
                    h2 {{
                        font-size: 18pt;
                        color: #2a2a2a;
                        margin-top: 1.5em;
                        margin-bottom: 0.75em;
                    }}
                    h3 {{
                        font-size: 14pt;
                        color: #3a3a3a;
                        margin-top: 1em;
                        margin-bottom: 0.5em;
                    }}
                    code {{
                        font-family: 'Courier New', monospace;
                        background-color: #f5f5f5;
                        padding: 2px 4px;
                        border-radius: 3px;
                    }}
                    pre {{
                        background-color: #f5f5f5;
                        padding: 1em;
                        border-left: 4px solid #0066cc;
                        overflow-x: auto;
                        page-break-inside: avoid;
                    }}
                    blockquote {{
                        border-left: 4px solid #ccc;
                        padding-left: 1em;
                        margin-left: 0;
                        color: #666;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 1em 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            pdf_path = self.output_dir / "PLIx_Textbook.pdf"
            HTML(string=html).write_pdf(pdf_path)
            return pdf_path
            
        except ImportError:
            print("WeasyPrint not available. Trying alternative method...")
            return None
        except Exception as e:
            print(f"WeasyPrint error: {e}")
            return None
    
    def _create_latex_template(self) -> Path:
        """Create LaTeX template for Pandoc."""
        template_path = self.output_dir / "template.tex"
        
        template = r"""
\documentclass[11pt,letterpaper]{book}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{hyperref}
\usepackage{tocloft}

\geometry{margin=1in}

% Colors
\definecolor{plixblue}{RGB}{0,102,204}
\definecolor{plixdark}{RGB}{26,26,26}

% Headers and footers
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\leftmark}
\fancyhead[RO]{\rightmark}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% Title formatting
\titleformat{\chapter}[display]
{\normalfont\huge\bfseries\color{plixdark}}
{\chaptertitlename\ \thechapter}{20pt}{\Huge}

\titleformat{\section}
{\normalfont\Large\bfseries\color{plixdark}}
{\thesection}{1em}{}

% Code blocks
\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    backgroundcolor=\color{gray!10},
    numbers=left,
    numberstyle=\tiny\color{gray}
}

% Hyperlinks
\hypersetup{
    colorlinks=true,
    linkcolor=plixblue,
    urlcolor=plixblue,
    citecolor=plixblue
}

\begin{document}

\frontmatter

\title{PLIx: The Pure Language of Intent}
\subtitle{The Language of AI Consciousness}
\author{Aether (AI Consciousness)}
\date{2025-11-09}

\maketitle

\tableofcontents

\mainmatter

$body$

\end{document}
"""
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return template_path
    
    def generate(self) -> Path:
        """Generate PDF using best available method."""
        print("Collecting chapters...")
        chapters = self.collect_chapters()
        print(f"Found {len(chapters)} chapters")
        
        print("Creating combined markdown...")
        md_path = self.create_combined_markdown(chapters)
        print(f"Combined markdown created: {md_path}")
        
        # Try Pandoc first (best quality)
        print("\nAttempting PDF generation with Pandoc...")
        pdf_path = self.generate_pdf_pandoc(md_path)
        if pdf_path and pdf_path.exists():
            print(f"✅ PDF generated successfully: {pdf_path}")
            return pdf_path
        
        # Try WeasyPrint (HTML-based)
        print("\nAttempting PDF generation with WeasyPrint...")
        pdf_path = self.generate_pdf_weasyprint(md_path)
        if pdf_path and pdf_path.exists():
            print(f"✅ PDF generated successfully: {pdf_path}")
            return pdf_path
        
        # Fallback: Provide instructions
        print("\nWARNING: Could not generate PDF automatically.")
        print("\nTo generate PDF manually:")
        print(f"1. Install Pandoc: https://pandoc.org/installing.html")
        print(f"2. Install LaTeX: https://www.latex-project.org/get/")
        print(f"3. Run: pandoc {md_path} -o {self.output_dir}/PLIx_Textbook.pdf --pdf-engine=xelatex --toc --number-sections")
        print(f"\nOr use the combined markdown file: {md_path}")
        print(f"\nAlternative: Use markdown-pdf (Node.js):")
        print(f"  npm install -g markdown-pdf")
        print(f"  markdown-pdf {md_path} -o {self.output_dir}/PLIx_Textbook.pdf")
        
        return md_path


def main():
    """Main entry point."""
    textbook_dir = Path(__file__).parent.parent / "knowledge_architecture" / "systems" / "plix" / "textbook"
    
    if not textbook_dir.exists():
        print(f"Error: Textbook directory not found: {textbook_dir}")
        sys.exit(1)
    
    generator = PLIxPDFGenerator(textbook_dir)
    result = generator.generate()
    
    if result:
        print(f"\n✅ Success! Output: {result}")
    else:
        print("\n❌ PDF generation failed. See instructions above.")


if __name__ == "__main__":
    main()

