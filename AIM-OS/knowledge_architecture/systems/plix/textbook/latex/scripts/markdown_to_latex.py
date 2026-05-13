#!/usr/bin/env python3
"""
PLIx Textbook: Markdown to LaTeX Converter
Converts PLIx textbook markdown chapters to LaTeX format
"""

import re
from pathlib import Path
import sys

def markdown_to_latex(md_text):
    """Convert markdown to LaTeX"""
    
    # Remove status/metadata lines at top
    md_text = re.sub(r'^\*\*Part:\*\*.*\n', '', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^\*\*Chapter:\*\*.*\n', '', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^\*\*Target Word Count:\*\*.*\n', '', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^\*\*Status:\*\*.*\n', '', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^---\s*\n', '', md_text, flags=re.MULTILINE)
    
    # Remove chapter title lines that are already in main.tex
    md_text = re.sub(r'^# Chapter \d+:.+$', '', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^\*\*Part [IVX]+ - Chapter \d+\*\*$', '', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^---\s*$', '', md_text, flags=re.MULTILINE)
    
    # Protect code blocks first (before any other processing)
    code_blocks = []
    def protect_code(m):
        idx = len(code_blocks)
        code_blocks.append(m.group(0))
        return f'__CODE_BLOCK_{idx}__'
    
    # Protect Python code blocks
    md_text = re.sub(r'```python\n(.*?)\n```', protect_code, md_text, flags=re.DOTALL)
    # Protect TypeScript/JavaScript code blocks
    md_text = re.sub(r'```(?:typescript|javascript)\n(.*?)\n```', protect_code, md_text, flags=re.DOTALL)
    # Protect generic code blocks (but not already protected ones)
    md_text = re.sub(r'```(\w+)?\n(.*?)\n```', protect_code, md_text, flags=re.DOTALL)
    # Protect inline code (but not in code blocks)
    md_text = re.sub(r'`([^`\n]+)`', protect_code, md_text)
    
    # Protect math regions
    math_blocks = []
    def protect_math(m):
        idx = len(math_blocks)
        math_blocks.append(m.group(0))
        return f'__MATH_BLOCK_{idx}__'
    
    # Protect inline math $...$
    md_text = re.sub(r'\$[^$\n]+\$', protect_math, md_text)
    # Protect display math $$...$$
    md_text = re.sub(r'\$\$[^$]+\$\$', protect_math, md_text, flags=re.DOTALL)
    
    # Now convert headers (after protecting code/math)
    md_text = re.sub(r'^## (.+)$', r'\\section*{\1}', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^### (.+)$', r'\\subsection*{\1}', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^#### (.+)$', r'\\subsubsection*{\1}', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^##### (.+)$', r'\\paragraph{\1}', md_text, flags=re.MULTILINE)
    
    # Bold (do this BEFORE escaping)
    md_text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', md_text)
    
    # Italic - be careful not to match bold markers
    md_text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'\\textit{\1}', md_text)
    
    # Restore code blocks and convert to LaTeX
    # Note: lstlisting environment handles special characters automatically
    for idx, code_block in enumerate(code_blocks):
        placeholder = f'__CODE_BLOCK_{idx}__'
        if code_block.startswith('```python'):
            content = code_block.replace('```python\n', '').replace('\n```', '').strip()
            # Don't escape - lstlisting handles special chars
            latex_code = f'\\begin{{lstlisting}}[language=Python, caption=Python Example]\n{content}\n\\end{{lstlisting}}'
        elif code_block.startswith('```typescript') or code_block.startswith('```javascript'):
            content = code_block.replace('```typescript\n', '').replace('```javascript\n', '').replace('\n```', '').strip()
            # Remove language specification - JavaScript not supported
            latex_code = f'\\begin{{lstlisting}}[caption=Code Example]\n{content}\n\\end{{lstlisting}}'
        elif code_block.startswith('```'):
            # Extract language if present
            lines = code_block.split('\n')
            first_line = lines[0]
            if '```' in first_line and len(first_line) > 3:
                lang = first_line[3:].strip()
                content = '\n'.join(lines[1:-1])
            else:
                content = '\n'.join(lines[1:-1])
            # Don't escape - lstlisting handles special chars
            latex_code = f'\\begin{{lstlisting}}[caption=Code Example]\n{content}\n\\end{{lstlisting}}'
        else:
            # Inline code - need to escape special chars
            content = code_block.strip('`')
            content = content.replace('\\', '\\textbackslash{}')
            content = content.replace('{', '\\{')
            content = content.replace('}', '\\}')
            content = content.replace('&', '\\&')
            content = content.replace('%', '\\%')
            content = content.replace('#', '\\#')
            content = content.replace('^', '\\textasciicircum{}')
            content = content.replace('~', '\\textasciitilde{}')
            content = content.replace('_', '\\_')
            latex_code = f'\\texttt{{{content}}}'
        md_text = md_text.replace(placeholder, latex_code)
    
    # Replace Unicode arrows and special characters with LaTeX equivalents
    # Do this BEFORE list processing to avoid math mode issues
    md_text = md_text.replace('→', '\\textrightarrow{}')
    md_text = md_text.replace('↓', '\\textdownarrow{}')
    md_text = md_text.replace('κ', '\\textkappa{}')
    md_text = md_text.replace('∀', '\\textforall{}')
    
    # Fix parameter interpolation ${} syntax - escape dollar signs (before list processing)
    md_text = re.sub(r'\$\{([^}]+)\}', r'\\texttt{\$\\{\1\\}\}', md_text)
    
    # Lists - handle properly with lookahead
    lines = md_text.split('\n')
    result_lines = []
    in_itemize = False
    in_enumerate = False
    
    for i, line in enumerate(lines):
        # Check if this is a list item
        is_list_item = bool(re.match(r'^- (.+)$', line) or re.match(r'^\d+\. (.+)$', line))
        # Check if next non-empty line is also a list item
        next_is_list_item = False
        for j in range(i + 1, len(lines)):
            if lines[j].strip():
                next_is_list_item = bool(re.match(r'^- (.+)$', lines[j]) or re.match(r'^\d+\. (.+)$', lines[j]))
                break
        
        if re.match(r'^- (.+)$', line):
            if not in_itemize:
                if in_enumerate:
                    result_lines.append('\\end{enumerate}')
                    in_enumerate = False
                result_lines.append('\\begin{itemize}')
                in_itemize = True
            result_lines.append(re.sub(r'^- (.+)$', r'\\item \1', line))
        elif re.match(r'^\d+\. (.+)$', line):
            if not in_enumerate:
                if in_itemize:
                    result_lines.append('\\end{itemize}')
                    in_itemize = False
                result_lines.append('\\begin{enumerate}')
                in_enumerate = True
            result_lines.append(re.sub(r'^\d+\. (.+)$', r'\\item \1', line))
        else:
            # Only close list if next non-empty line is NOT a list item
            if not next_is_list_item:
                if in_itemize:
                    result_lines.append('\\end{itemize}')
                    in_itemize = False
                if in_enumerate:
                    result_lines.append('\\end{enumerate}')
                    in_enumerate = False
            result_lines.append(line)
    
    # Close any open lists at end
    if in_itemize:
        result_lines.append('\\end{itemize}')
    if in_enumerate:
        result_lines.append('\\end{enumerate}')
    
    md_text = '\n'.join(result_lines)
    
    # Links
    md_text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\\href{\2}{\1}', md_text)
    
    # Replace Unicode arrows and special characters with LaTeX equivalents (before math restoration)
    md_text = md_text.replace('→', '$\\rightarrow$')
    md_text = md_text.replace('↓', '$\\downarrow$')
    md_text = md_text.replace('κ', '$\\kappa$')
    md_text = md_text.replace('∀', '$\\forall$')
    
    # Fix parameter interpolation ${} syntax - escape dollar signs
    md_text = re.sub(r'\$\{([^}]+)\}', r'\\texttt{\$\\{\1\\}\}', md_text)
    
    # Restore math blocks (before final escaping)
    for idx, math_block in enumerate(math_blocks):
        md_text = md_text.replace(f'__MATH_BLOCK_{idx}__', math_block)
    
    # Escape special LaTeX characters (but not in code blocks or math)
    # Code blocks are already converted, math blocks are restored
    # We need to escape carefully - split by protected regions
    parts = []
    current_pos = 0
    
    # Find all protected regions (code blocks, math)
    protected_regions = []
    for match in re.finditer(r'(\\begin\{lstlisting\}.*?\\end\{lstlisting\}|\$[^$]+\$|\$\$[^$]+\$\$)', md_text, flags=re.DOTALL):
        protected_regions.append((match.start(), match.end(), match.group(0)))
    
    # Build result by escaping non-protected parts
    for start, end, protected in protected_regions:
        # Add escaped text before protected region
        if start > current_pos:
            text_to_escape = md_text[current_pos:start]
            escaped = text_to_escape.replace('&', '\\&')
            escaped = escaped.replace('%', '\\%')
            escaped = escaped.replace('#', '\\#')
            escaped = escaped.replace('^', '\\textasciicircum{}')
            escaped = escaped.replace('~', '\\textasciitilde{}')
            # Escape underscores (but not in LaTeX commands)
            escaped = re.sub(r'(?<!\\)_', '\\_', escaped)
            parts.append(escaped)
        # Add protected region as-is
        parts.append(protected)
        current_pos = end
    
    # Add remaining text
    if current_pos < len(md_text):
        text_to_escape = md_text[current_pos:]
        escaped = text_to_escape.replace('&', '\\&')
        escaped = escaped.replace('%', '\\%')
        escaped = escaped.replace('#', '\\#')
        escaped = escaped.replace('^', '\\textasciicircum{}')
        escaped = escaped.replace('~', '\\textasciitilde{}')
        escaped = re.sub(r'(?<!\\)_', '\\_', escaped)
        parts.append(escaped)
    
    if protected_regions:
        md_text = ''.join(parts)
    else:
        # No protected regions, escape everything
        md_text = md_text.replace('&', '\\&')
        md_text = md_text.replace('%', '\\%')
        md_text = md_text.replace('#', '\\#')
        md_text = md_text.replace('^', '\\textasciicircum{}')
        md_text = md_text.replace('~', '\\textasciitilde{}')
        md_text = re.sub(r'(?<!\\)_', '\\_', md_text)
    
    return md_text

def convert_textbook_chapters():
    """Convert all PLIx textbook chapters from markdown to LaTeX"""
    # Script is in: knowledge_architecture/systems/plix/textbook/latex/scripts/
    # Textbook is in: knowledge_architecture/systems/plix/textbook/
    script_dir = Path(__file__).parent  # scripts/
    latex_dir = script_dir.parent  # latex/
    textbook_dir = latex_dir.parent  # textbook/
    
    latex_dir.mkdir(exist_ok=True)
    
    chapters_dir = latex_dir / "chapters"
    chapters_dir.mkdir(exist_ok=True)
    
    # Collect all chapters
    chapters = []
    for part_num in ['I', 'II', 'III', 'IV', 'V', 'VI']:
        part_dir = textbook_dir / f"Part_{part_num}"
        for i in range(1, 25):  # 24 chapters total
            chapter_file = part_dir / f"Chapter_{i:02d}.md"
            if chapter_file.exists():
                # Determine which part this chapter belongs to
                if part_num == 'I' and 1 <= i <= 4:
                    chapters.append((i, chapter_file, part_num))
                elif part_num == 'II' and 5 <= i <= 8:
                    chapters.append((i, chapter_file, part_num))
                elif part_num == 'III' and 9 <= i <= 12:
                    chapters.append((i, chapter_file, part_num))
                elif part_num == 'IV' and 13 <= i <= 16:
                    chapters.append((i, chapter_file, part_num))
                elif part_num == 'V' and 17 <= i <= 20:
                    chapters.append((i, chapter_file, part_num))
                elif part_num == 'VI' and 21 <= i <= 24:
                    chapters.append((i, chapter_file, part_num))
    
    # Convert chapters
    for chapter_num, md_file, part_num in chapters:
        md_content = md_file.read_text(encoding='utf-8')
        latex_content = markdown_to_latex(md_content)
        
        # Write LaTeX file
        tex_file = chapters_dir / f"chapter_{chapter_num:02d}.tex"
        latex_output = f"% Chapter {chapter_num} converted from Markdown\n% Auto-generated - do not edit manually\n\n{latex_content}"
        tex_file.write_text(latex_output, encoding='utf-8')
        print(f"Converted: Chapter {chapter_num} (Part {part_num})")
    
    print(f"\nConverted {len(chapters)} chapters to LaTeX")
    return len(chapters)

if __name__ == "__main__":
    try:
        count = convert_textbook_chapters()
        print(f"\nSUCCESS: Converted {count} chapters")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
