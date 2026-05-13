# PLIx Textbook PDF Generation Guide

**Date:** 2025-11-09  
**Status:** 📋 **READY FOR PDF GENERATION**  
**Combined Markdown:** ✅ Created

---

## ✅ Combined Markdown Created

The combined markdown file has been successfully created:
- **Location:** `knowledge_architecture/systems/plix/textbook/pdf_output/PLIx_Textbook_Complete.md`
- **Content:** All 24 chapters, table of contents, proper formatting
- **Status:** Ready for PDF conversion

---

## 📄 PDF Generation Options

### **Option 1: Pandoc (Recommended - Best Quality)**

**Installation:**
1. Install Pandoc: https://pandoc.org/installing.html
2. Install LaTeX (for PDF generation):
   - Windows: MiKTeX - https://miktex.org/download
   - Mac: MacTeX - https://www.tug.org/mactex/
   - Linux: `sudo apt-get install texlive-full`

**Generate PDF:**
```bash
cd knowledge_architecture/systems/plix/textbook/pdf_output
pandoc PLIx_Textbook_Complete.md -o PLIx_Textbook.pdf \
  --pdf-engine=xelatex \
  --toc \
  --number-sections \
  --variable mainfont=Georgia \
  --variable sansfont=Arial \
  --variable monofont="Courier New" \
  --variable fontsize=11pt \
  --variable geometry:margin=1in \
  --variable colorlinks=true \
  --variable linkcolor=blue \
  --highlight-style=tango
```

---

### **Option 2: markdown-pdf (Node.js - Simple)**

**Installation:**
```bash
npm install -g markdown-pdf
```

**Generate PDF:**
```bash
cd knowledge_architecture/systems/plix/textbook/pdf_output
markdown-pdf PLIx_Textbook_Complete.md -o PLIx_Textbook.pdf
```

**With Custom CSS (Better Styling):**
```bash
markdown-pdf PLIx_Textbook_Complete.md \
  -o PLIx_Textbook.pdf \
  -s pdf_styles.css \
  --paper-format Letter \
  --paper-orientation portrait \
  --paper-border 1in
```

---

### **Option 3: WeasyPrint (Python - HTML-based)**

**Installation:**
```bash
pip install weasyprint markdown
```

**Generate PDF:**
```python
import markdown
from weasyprint import HTML

with open('PLIx_Textbook_Complete.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

html_content = markdown.markdown(md_content, extensions=['codehilite', 'tables', 'toc'])

html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: letter;
            margin: 1in;
        }}
        body {{
            font-family: Georgia, serif;
            font-size: 11pt;
            line-height: 1.6;
        }}
        h1 {{ font-size: 24pt; page-break-before: always; }}
        h2 {{ font-size: 18pt; }}
        h3 {{ font-size: 14pt; }}
        code {{ font-family: 'Courier New', monospace; }}
        pre {{ background-color: #f5f5f5; padding: 1em; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

HTML(string=html).write_pdf('PLIx_Textbook.pdf')
```

---

### **Option 4: Online Converters**

**Simple Online Tools:**
1. **Markdown to PDF:** https://www.markdowntopdf.com/
2. **Dillinger:** https://dillinger.io/ (Export as PDF)
3. **StackEdit:** https://stackedit.io/ (Export as PDF)

**Steps:**
1. Open `PLIx_Textbook_Complete.md` in the online tool
2. Export as PDF
3. Download the PDF

---

### **Option 5: VS Code Extension**

**Install Extension:**
- **Markdown PDF** by yzane
- Search for "Markdown PDF" in VS Code Extensions

**Generate PDF:**
1. Open `PLIx_Textbook_Complete.md` in VS Code
2. Right-click → "Markdown PDF: Export (pdf)"
3. PDF will be generated in the same directory

---

## 🎨 Custom Styling (Optional)

### **Create Custom CSS for Better Styling**

Create `pdf_styles.css`:

```css
@page {
    size: letter;
    margin: 1in;
    @top-center {
        content: "PLIx: The Pure Language of Intent";
        font-size: 10pt;
        color: #666;
    }
    @bottom-center {
        content: "Page " counter(page);
        font-size: 10pt;
        color: #666;
    }
}

body {
    font-family: Georgia, serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    font-size: 24pt;
    color: #1a1a1a;
    margin-top: 2em;
    margin-bottom: 1em;
    page-break-before: always;
    border-bottom: 2px solid #0066cc;
    padding-bottom: 0.5em;
}

h2 {
    font-size: 18pt;
    color: #2a2a2a;
    margin-top: 1.5em;
    margin-bottom: 0.75em;
}

h3 {
    font-size: 14pt;
    color: #3a3a3a;
    margin-top: 1em;
    margin-bottom: 0.5em;
}

code {
    font-family: 'Courier New', monospace;
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 10pt;
}

pre {
    background-color: #f5f5f5;
    padding: 1em;
    border-left: 4px solid #0066cc;
    overflow-x: auto;
    page-break-inside: avoid;
    font-size: 10pt;
}

blockquote {
    border-left: 4px solid #ccc;
    padding-left: 1em;
    margin-left: 0;
    color: #666;
    font-style: italic;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #f2f2f2;
    font-weight: bold;
}

a {
    color: #0066cc;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}
```

---

## 📊 PDF Quality Checklist

**Before Finalizing PDF:**
- [ ] Table of contents is clickable
- [ ] Page numbers are correct
- [ ] Headers/footers are formatted
- [ ] Code blocks are readable
- [ ] Images/diagrams render correctly
- [ ] Links work (if hyperlinks enabled)
- [ ] Page breaks are appropriate
- [ ] Fonts are readable
- [ ] Margins are consistent
- [ ] Chapter titles are prominent

---

## 🚀 Quick Start (Recommended)

**For Windows Users:**
1. Install Pandoc: Download from https://pandoc.org/installing.html
2. Install MiKTeX: Download from https://miktex.org/download
3. Run the script: `python scripts/generate_plix_textbook_pdf.py`
4. Or manually: Use the Pandoc command above

**For Mac Users:**
1. Install Pandoc: `brew install pandoc`
2. Install MacTeX: Download from https://www.tug.org/mactex/
3. Run the Pandoc command above

**For Linux Users:**
1. Install Pandoc: `sudo apt-get install pandoc`
2. Install LaTeX: `sudo apt-get install texlive-full`
3. Run the Pandoc command above

---

## 📁 File Locations

**Combined Markdown:**
- `knowledge_architecture/systems/plix/textbook/pdf_output/PLIx_Textbook_Complete.md`

**Output PDF (after generation):**
- `knowledge_architecture/systems/plix/textbook/pdf_output/PLIx_Textbook.pdf`

---

**Status:** ✅ **COMBINED MARKDOWN READY**  
**Next Step:** Choose PDF generation method and generate PDF

