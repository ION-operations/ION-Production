# LaTeX Build Instructions

## Prerequisites

1. **LaTeX Distribution:**
   - Windows: MiKTeX or TeX Live
   - macOS: MacTeX
   - Linux: TeX Live

2. **Python 3.x** (for markdown conversion script)

3. **Required LaTeX Packages:**
   - amsmath, amssymb, amsthm (math)
   - geometry (page layout)
   - fancyhdr (headers/footers)
   - hyperref (links)
   - listings (code blocks)
   - booktabs (tables)
   - xcolor (colors)
   - fontspec (if using XeLaTeX/LuaLaTeX)

## Building the PDF

### Option 1: Using Make (Recommended)

```bash
cd north_star_project/latex
make pdf
```

This will:
1. Convert all markdown chapters to LaTeX
2. Compile the PDF (3 passes for cross-references)
3. Generate `THE_NORTH_STAR_DOCUMENT.pdf`

### Option 2: Manual Build

1. **Convert Markdown to LaTeX:**
   ```bash
   python scripts/markdown_to_latex.py
   ```

2. **Compile LaTeX:**
   ```bash
   pdflatex main.tex
   bibtex main
   makeindex main
   pdflatex main.tex
   pdflatex main.tex
   ```

### Option 3: Using XeLaTeX (Better Unicode Support)

If you need better Unicode support (for special characters), use XeLaTeX:

```bash
xelatex main.tex
bibtex main
makeindex main
xelatex main.tex
xelatex main.tex
```

## Math Rendering

The document uses standard LaTeX math notation:

- Inline math: `$formula$` → `\(formula\)`
- Display math: `$$formula$$` → `\[formula\]`

Example formulas from chapters:
- Authority scoring: `authority(a, c) = w_e * evidence + w_v * validation + ...`
- Learning rate: `dQ/dt = α * (benefit - cost) - β * regression`
- Graph definition: `G = (V, E, τ_TT, τ_VT, θ, σ, ε)`

## Code Blocks

Code blocks are rendered using the `listings` package:
- PowerShell examples use `language=PowerShell`
- Python examples use `language=Python`
- Syntax highlighting and line numbers are enabled

## Customization

### Fonts

To use different fonts, modify `main.tex`:

```latex
% For XeLaTeX/LuaLaTeX
\usepackage{fontspec}
\setmainfont{Linux Libertine O}
\setmonofont{Consolas}
```

### Colors

Colors are defined in `main.tex`:
- `aimosblue`: RGB(0,102,204)
- `aimosdark`: RGB(0,51,102)

### Page Layout

Page geometry is set in `main.tex`:
- A4 paper
- 1.5in left margin, 1in right margin
- 1in top/bottom margins

## Troubleshooting

### Missing Packages

If LaTeX complains about missing packages:
- MiKTeX: Install packages automatically when prompted
- TeX Live: `tlmgr install <package>`

### Math Not Rendering

Ensure `amsmath`, `amssymb`, and `amsthm` packages are installed.

### Code Blocks Not Showing

Ensure `listings` package is installed and configured correctly.

### Cross-References Not Working

Run `pdflatex` multiple times (3 passes) to resolve all cross-references.

## Output

The final PDF will be:
- `THE_NORTH_STAR_DOCUMENT.pdf`
- ~70,000 words
- 35 chapters
- Complete with table of contents, index, and bibliography

