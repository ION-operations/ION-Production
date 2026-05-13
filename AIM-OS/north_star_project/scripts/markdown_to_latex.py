# Conversion script: Markdown to LaTeX
# Converts chapter.md files to chapter.tex files with proper LaTeX formatting

import re
from pathlib import Path

def markdown_to_latex(md_text):
    """Convert markdown to LaTeX"""
    
    # Remove status lines at top
    md_text = re.sub(r'^Status:.*\n', '', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^Mode:.*\n', '', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^Target:.*\n', '', md_text, flags=re.MULTILINE)
    
    # Headers (do this BEFORE escaping backslashes)
    md_text = re.sub(r'^# (.+)$', r'\\section*{\1}', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^## (.+)$', r'\\subsection*{\1}', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^### (.+)$', r'\\subsubsection*{\1}', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^#### (.+)$', r'\\paragraph{\1}', md_text, flags=re.MULTILINE)
    
    # Bold (do this BEFORE escaping)
    md_text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', md_text)
    
    # Italic (do this BEFORE escaping)
    md_text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', md_text)
    
    # Code inline (do this BEFORE escaping)
    md_text = re.sub(r'`([^`]+)`', r'\\texttt{\1}', md_text)
    
    # Code blocks - PowerShell (do this BEFORE escaping)
    md_text = re.sub(
        r'```powershell\n(.*?)\n```',
        r'\\begin{lstlisting}[language=PowerShell, caption=PowerShell Example]\n\1\n\\end{lstlisting}',
        md_text,
        flags=re.DOTALL
    )
    
    # Code blocks - Python (do this BEFORE escaping)
    md_text = re.sub(
        r'```python\n(.*?)\n```',
        r'\\begin{lstlisting}[language=Python, caption=Python Example]\n\1\n\\end{lstlisting}',
        md_text,
        flags=re.DOTALL
    )
    
    # Code blocks - generic (do this BEFORE escaping)
    md_text = re.sub(
        r'```(\w+)?\n(.*?)\n```',
        r'\\begin{lstlisting}[caption=Code Example]\n\2\n\\end{lstlisting}',
        md_text,
        flags=re.DOTALL
    )
    
    # Lists (do this BEFORE escaping)
    md_text = re.sub(r'^- (.+)$', r'\\item \1', md_text, flags=re.MULTILINE)
    
    # Links (do this BEFORE escaping)
    md_text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\\href{\2}{\1}', md_text)
    
    # Escape special LaTeX characters (but preserve math delimiters)
    # First, protect math regions
    math_blocks = []
    def protect_math(m):
        idx = len(math_blocks)
        math_blocks.append(m.group(0))
        return f'__MATH_BLOCK_{idx}__'
    
    # Protect inline math $...$
    md_text = re.sub(r'\$[^$]+\$', protect_math, md_text)
    # Protect display math $$...$$
    md_text = re.sub(r'\$\$[^$]+\$\$', protect_math, md_text)
    
    # Now escape special characters (but NOT backslashes - they're already LaTeX commands)
    md_text = md_text.replace('&', '\\&')
    md_text = md_text.replace('%', '\\%')
    md_text = md_text.replace('#', '\\#')
    md_text = md_text.replace('^', '\\textasciicircum{}')
    md_text = md_text.replace('~', '\\textasciitilde{}')
    
    # Escape underscores and braces (but not in math or LaTeX commands)
    # This is tricky - we'll escape underscores that aren't part of LaTeX commands
    # Simple heuristic: escape _ that aren't preceded by \
    md_text = re.sub(r'(?<!\\)_', '\\_', md_text)
    
    # Escape braces that aren't part of LaTeX commands
    # This is very tricky - for now, we'll be conservative
    # md_text = md_text.replace('{', '\\{')
    # md_text = md_text.replace('}', '\\}')
    
    # DON'T escape backslashes - they're LaTeX commands!
    
    return md_text

def convert_chapter(chapter_dir):
    """Convert a chapter from markdown to LaTeX"""
    md_file = chapter_dir / "chapter.md"
    tex_file = chapter_dir / "chapter.tex"
    
    if not md_file.exists():
        print(f"Warning: {md_file} not found")
        return
    
    md_content = md_file.read_text(encoding='utf-8')
    latex_content = markdown_to_latex(md_content)
    
    # Add LaTeX header
    latex_output = f"% Chapter converted from Markdown\n% Auto-generated - do not edit manually\n\n{latex_content}"
    
    tex_file.write_text(latex_output, encoding='utf-8')
    print(f"Converted: {chapter_dir.name}")

def convert_all_chapters():
    """Convert all chapters"""
    base_dir = Path(__file__).parent.parent
    chapters_dir = base_dir / "chapters"
    
    for chapter_dir in sorted(chapters_dir.iterdir()):
        if chapter_dir.is_dir() and chapter_dir.name[0].isdigit():
            convert_chapter(chapter_dir)

if __name__ == "__main__":
    convert_all_chapters()

