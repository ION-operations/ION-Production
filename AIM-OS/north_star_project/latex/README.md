# LaTeX PDF Generation - Quick Start

## Prerequisites

Install LaTeX distribution:
- **Windows:** [MiKTeX](https://miktex.org/download) (recommended) or [TeX Live](https://www.tug.org/texlive/)
- **macOS:** [MacTeX](https://www.tug.org/mactex/)
- **Linux:** `sudo apt-get install texlive-full` (or use TeX Live)

## Quick Build

1. **Convert Markdown to LaTeX:**
   ```bash
   cd north_star_project
   python scripts/markdown_to_latex.py
   ```

2. **Build PDF:**
   ```bash
   cd latex
   pdflatex main.tex
   pdflatex main.tex  # Run twice for cross-references
   pdflatex main.tex  # Run third time for index
   ```

   Or use the Makefile:
   ```bash
   cd latex
   make pdf
   ```

## Output

The PDF will be generated as:
- `north_star_project/latex/THE_NORTH_STAR_DOCUMENT.pdf`

## Features

✅ **Beautiful Typography:**
- Professional fonts and spacing
- Proper mathematical notation
- Code syntax highlighting

✅ **Math Rendering:**
- Inline math: `$formula$`
- Display math: `$$formula$$`
- Equations numbered automatically

✅ **Code Blocks:**
- PowerShell syntax highlighting
- Python syntax highlighting
- Line numbers and formatting

✅ **Cross-References:**
- Chapter references
- Equation references
- Table/figure references

✅ **Professional Layout:**
- Table of contents
- Index
- Bibliography
- Headers and footers

## Troubleshooting

**Missing packages:** LaTeX will prompt to install missing packages (MiKTeX) or use `tlmgr install <package>` (TeX Live)

**Math not rendering:** Ensure `amsmath` and `amssymb` packages are installed

**Build errors:** Check `main.log` for detailed error messages

## Next Steps

1. Review generated PDF
2. Adjust formatting in `main.tex` if needed
3. Customize colors/fonts as desired
4. Add any missing content

