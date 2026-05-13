# Unified Textbook Compilation Guide

**Status:** ✅ **READY**  
**Date:** 2025-01-27

---

## 🎯 Overview

The unified textbook compiler combines all 67 chapters into:
1. **Single unified Markdown document** with table of contents
2. **PDF** (via Pandoc/LaTeX) with proper formatting
3. **HTML** (optional, not yet implemented)

---

## 📋 Prerequisites

### For Markdown Compilation
- Python 3.7+
- No additional dependencies

### For PDF Compilation
- **LaTeX Distribution:**
  - **Windows:** MiKTeX or TeX Live
  - **macOS:** MacTeX
  - **Linux:** `texlive-full` package
- **pdflatex** (comes with LaTeX distribution)
- **Make** (optional, for easier building)

**Note:** We use the existing LaTeX build system at `knowledge_architecture/systems/plix/textbook/latex/`

---

## 🚀 Quick Start

### Compile Markdown Only
```bash
cd knowledge_architecture/systems/plix/textbook/unified
python scripts/compile_textbook.py --format markdown
```

**Output:** `compiled/UNIFIED_TEXTBOOK.md`

### Compile PDF
```bash
python scripts/compile_textbook.py --format pdf
```

**Output:** `compiled/UNIFIED_TEXTBOOK.pdf`

**Note:** This uses the existing LaTeX build system. It will:
1. Convert unified textbook chapters to LaTeX format
2. Use the existing `latex/Makefile` to build PDF
3. Copy the final PDF to `compiled/UNIFIED_TEXTBOOK.pdf`

### Compile All Formats
```bash
python scripts/compile_textbook.py --format all
```

### Custom Output Directory
```bash
python scripts/compile_textbook.py --format all --output-dir /path/to/output
```

---

## 📁 Output Structure

```
compiled/
├── UNIFIED_TEXTBOOK.md          # Single unified Markdown (1.2 MB)
└── UNIFIED_TEXTBOOK.pdf         # PDF with TOC and formatting
```

---

## 📊 What Gets Compiled

**All 67 chapters:**
- Part I: AIM-OS Foundations (35 chapters)
- Parts II-VII: PLIx Language (28 chapters)
- Part VIII: Geometric Kernel (8 chapters)

**Features:**
- ✅ Table of contents with chapter numbers and titles
- ✅ All chapters in order (1-67)
- ✅ Cross-references preserved
- ✅ Code blocks preserved
- ✅ Math equations preserved (for PDF)

---

## 🔧 PDF Configuration

The PDF uses the existing LaTeX build system configuration:
- **Document class:** `book` (11pt, A4, twoside)
- **Margins:** 1.5in left, 1in right, 1in top/bottom
- **Table of contents:** Auto-generated
- **Section numbering:** Enabled
- **Code highlighting:** `listings` package
- **Colors:** PLIx blue theme
- **Hyperlinks:** Enabled with color links

**LaTeX Engine:** `pdflatex` (standard LaTeX)

**Build Process:**
1. Convert markdown → LaTeX (using existing `markdown_to_latex.py`)
2. Run `pdflatex` (3 passes for cross-references)
3. Run `bibtex` (if bibliography exists)
4. Run `makeindex` (if index exists)

---

## 🐛 Troubleshooting

### "pdflatex not found"
**Solution:** Install LaTeX distribution:
- **Windows:** MiKTeX (https://miktex.org/)
- **macOS:** MacTeX (https://www.tug.org/mactex/)
- **Linux:** `sudo apt-get install texlive-full`

### "LaTeX directory not found"
**Solution:** Ensure the LaTeX build system exists at:
`knowledge_architecture/systems/plix/textbook/latex/`

If missing, you may need to set it up from the existing PLIx textbook LaTeX system.

### "Makefile not found"
**Solution:** The LaTeX directory should contain a `Makefile`. If missing, you can build manually:
```bash
cd knowledge_architecture/systems/plix/textbook/latex
pdflatex main.tex
bibtex main
makeindex main
pdflatex main.tex
pdflatex main.tex
```

### "Unicode encoding errors"
**Solution:** The script automatically handles Windows console encoding. If issues persist, ensure your terminal supports UTF-8.

### "Chapter numbers duplicated"
**Issue:** Some chapters may have duplicate numbers if internal numbering doesn't match unified numbering.

**Solution:** The script extracts chapter numbers from:
1. Filename (e.g., `Chapter_64_...`)
2. Header (e.g., `Unified Textbook Chapter Number: 64`)

Ensure all chapters have correct unified numbering in headers.

---

## 📝 Notes

### Chapter Numbering
- Chapters are numbered 1-67 in unified order
- Part VIII chapters (60-67) use unified numbering, not internal numbering
- The script extracts numbers from filenames and headers

### Content Processing
- Headers are normalized
- Metadata lines are removed
- Navigation links are preserved
- Code blocks are preserved
- Math equations are preserved

### File Size
- **Markdown:** ~1.2 MB (67 chapters)
- **PDF:** ~5-10 MB (estimated, with formatting)

---

## 🎯 Next Steps

**Planned Enhancements:**
1. HTML compilation
2. EPUB format
3. Index generation (keyword index)
4. Bibliography compilation
5. Custom LaTeX templates
6. Chapter-level PDFs

---

**Status:** ✅ **Markdown compilation working**  
**PDF compilation:** Requires Pandoc + LaTeX  
**HTML compilation:** Not yet implemented

