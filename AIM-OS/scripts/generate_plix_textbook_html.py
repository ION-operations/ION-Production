#!/usr/bin/env python3
"""
PLIx Textbook HTML Generator
Creates a beautiful HTML version that can be printed to PDF from any browser.
"""

import os
import sys
from pathlib import Path
import markdown
from markdown.extensions import codehilite, tables, toc

def generate_html():
    """Generate HTML version of textbook."""
    textbook_dir = Path(__file__).parent.parent / "knowledge_architecture" / "systems" / "plix" / "textbook"
    pdf_output = textbook_dir / "pdf_output"
    md_path = pdf_output / "PLIx_Textbook_Complete.md"
    
    if not md_path.exists():
        print(f"Error: Combined markdown not found: {md_path}")
        return None
    
    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to HTML
    md = markdown.Markdown(extensions=[
        'codehilite',
        'tables',
        'toc',
        'fenced_code',
        'nl2br'
    ])
    html_content = md.convert(md_content)
    
    # Create HTML document
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PLIx: The Pure Language of Intent</title>
    <style>
        @media print {{
            @page {{
                size: letter;
                margin: 1in;
            }}
            body {{
                margin: 0;
            }}
            .no-print {{
                display: none;
            }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 1in;
            background: #fff;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 2em;
            padding-bottom: 1em;
            border-bottom: 3px solid #0066cc;
        }}
        
        .header h1 {{
            font-size: 32pt;
            color: #1a1a1a;
            margin-bottom: 0.5em;
        }}
        
        .header .subtitle {{
            font-size: 18pt;
            color: #666;
            font-style: italic;
            margin-bottom: 1em;
        }}
        
        .header .meta {{
            font-size: 10pt;
            color: #888;
        }}
        
        h1 {{
            font-size: 24pt;
            color: #1a1a1a;
            margin-top: 2em;
            margin-bottom: 1em;
            padding-bottom: 0.5em;
            border-bottom: 2px solid #0066cc;
            page-break-before: always;
        }}
        
        h1:first-of-type {{
            page-break-before: auto;
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
        
        h4 {{
            font-size: 12pt;
            color: #4a4a4a;
            margin-top: 0.75em;
            margin-bottom: 0.5em;
        }}
        
        p {{
            margin-bottom: 1em;
            text-align: justify;
        }}
        
        code {{
            font-family: 'Courier New', 'Consolas', monospace;
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10pt;
            color: #c7254e;
        }}
        
        pre {{
            background-color: #f5f5f5;
            padding: 1em;
            border-left: 4px solid #0066cc;
            overflow-x: auto;
            page-break-inside: avoid;
            margin: 1em 0;
            border-radius: 4px;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            color: #333;
            font-size: 9pt;
        }}
        
        blockquote {{
            border-left: 4px solid #ccc;
            padding-left: 1em;
            margin-left: 0;
            color: #666;
            font-style: italic;
            margin: 1em 0;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
            color: #1a1a1a;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        ul, ol {{
            margin-left: 2em;
            margin-bottom: 1em;
        }}
        
        li {{
            margin-bottom: 0.5em;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 2em 0;
        }}
        
        .toc {{
            background-color: #f9f9f9;
            padding: 1.5em;
            margin: 2em 0;
            border-radius: 4px;
            page-break-inside: avoid;
        }}
        
        .toc h2 {{
            margin-top: 0;
            color: #0066cc;
        }}
        
        .toc ul {{
            list-style: none;
            margin-left: 0;
        }}
        
        .toc li {{
            margin-bottom: 0.5em;
        }}
        
        .toc a {{
            color: #333;
        }}
        
        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #0066cc;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14pt;
            z-index: 1000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .print-button:hover {{
            background: #0052a3;
        }}
        
        @media print {{
            .print-button {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <button class="print-button no-print" onclick="window.print()">📄 Print to PDF</button>
    
    <div class="header">
        <h1>PLIx: The Pure Language of Intent</h1>
        <div class="subtitle">The Language of AI Consciousness</div>
        <div class="meta">
            <p><strong>A Comprehensive Textbook</strong></p>
            <p>Date: 2025-11-09 | Total Chapters: 24 | Total Parts: 6</p>
        </div>
    </div>
    
    {html_content}
    
    <script>
        // Add print functionality
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey && e.key === 'p') {{
                e.preventDefault();
                window.print();
            }}
        }});
    </script>
</body>
</html>"""
    
    # Write HTML file
    html_path = pdf_output / "PLIx_Textbook.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"SUCCESS: HTML version created: {html_path}")
    print("\nTo generate PDF:")
    print("1. Open the HTML file in your browser")
    print("2. Press Ctrl+P (or Cmd+P on Mac)")
    print("3. Select 'Save as PDF' as the destination")
    print("4. Click 'Save'")
    print("\nOr click the 'Print to PDF' button in the top-right corner!")
    
    return html_path


if __name__ == "__main__":
    try:
        result = generate_html()
        if result:
            print(f"\nSUCCESS! HTML file: {result}")
    except ImportError:
        print("Error: markdown library not found.")
        print("Install with: pip install markdown")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

