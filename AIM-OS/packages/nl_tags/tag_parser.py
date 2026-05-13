"""NL Tag Parser - Extract NL tags from code files

Supports multiple languages and tag formats:
- Python: # NL: description
- JavaScript/TypeScript: // NL: description
- Multi-line: /* NL: description */
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

from .models import NLTag


class NLTagParser:
    """Extract NL tags from code files"""
    
    # NL tag patterns by language
    TAG_PATTERNS = {
        "python": [
            r"#\s*NL:\s*(.+)",  # # NL: description
            r"#\s*NL\s*-\s*(.+)",  # # NL - description
            r"#\s*NL_TAG:\s*(.+)",  # # NL_TAG: ID | DESC | SYNTAX_REF | DEPS
        ],
        "typescript": [
            r"//\s*NL:\s*(.+)",  # // NL: description
            r"//\s*NL\s*-\s*(.+)",  # // NL - description
            r"//\s*NL_TAG:\s*(.+)",  # // NL_TAG: ID | DESC | SYNTAX_REF | DEPS
        ],
        "javascript": [
            r"//\s*NL:\s*(.+)",  # // NL: description
            r"//\s*NL\s*-\s*(.+)",  # // NL - description
            r"/\*\s*NL:\s*(.+?)\s*\*/",  # /* NL: description */
            r"//\s*NL_TAG:\s*(.+)",  # // NL_TAG: ID | DESC | SYNTAX_REF | DEPS
        ],
        "java": [
            r"//\s*NL:\s*(.+)",  # // NL: description
            r"/\*\s*NL:\s*(.+?)\s*\*/",  # /* NL: description */
            r"//\s*NL_TAG:\s*(.+)",  # // NL_TAG: ID | DESC | SYNTAX_REF | DEPS
        ],
    }
    
    def __init__(self):
        """Initialize parser"""
        self.language_detectors = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".java": "java",
        }
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        path = Path(file_path)
        ext = path.suffix.lower()
        return self.language_detectors.get(ext, "unknown")
    
    def parse_file(self, file_path: str) -> List[NLTag]:
        """Extract all NL tags from a file
        
        Args:
            file_path: Path to code file
            
        Returns:
            List of NLTag objects found in file
        """
        language = self.detect_language(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            # Return empty list if file can't be read
            return []
        
        tags = []
        lines = content.split('\n')
        
        # Extract tags using language-specific patterns
        if language in self.TAG_PATTERNS:
            tags.extend(self._extract_tags_from_lines(file_path, lines, language))
        
        # Also extract from docstrings (Python-specific)
        if language == "python":
            tags.extend(self._extract_tags_from_docstrings(file_path, content))
        
        return tags
    
    def _extract_tags_from_lines(
        self,
        file_path: str,
        lines: List[str],
        language: str
    ) -> List[NLTag]:
        """Extract tags from line comments"""
        tags = []
        patterns = self.TAG_PATTERNS.get(language, [])
        
        for line_num, line in enumerate(lines, start=1):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    tag_text = match.group(1).strip()
                    
                    # Extract associated code block (next few lines)
                    code_block = self._extract_code_block(lines, line_num - 1)
                    
                    tag = NLTag(
                        id=f"{file_path}:{line_num}",
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        column_start=match.start(),
                        tag_text=tag_text,
                        code_block=code_block,
                        language=language,
                        created_at=datetime.now(),
                    )
                    
                    # Automatically parse structured format if detected
                    if "NL_TAG:" in tag_text and "|" in tag_text:
                        tag.parse_structured_format()
                    
                    tags.append(tag)
        
        return tags
    
    def _extract_tags_from_docstrings(
        self,
        file_path: str,
        content: str
    ) -> List[NLTag]:
        """Extract NL tags from Python docstrings"""
        tags = []
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        # Check for NL: prefix in docstring
                        nl_match = re.search(r"NL:\s*(.+)", docstring, re.DOTALL)
                        if nl_match:
                            tag_text = nl_match.group(1).strip()
                            
                            tag = NLTag(
                                id=f"{file_path}:{node.lineno}",
                                file_path=file_path,
                                line_start=node.lineno,
                                line_end=node.lineno + len(docstring.split('\n')),
                                tag_text=tag_text,
                                code_block=ast.get_source_segment(content, node),
                                language="python",
                                created_at=datetime.now(),
                            )
                            
                            # Automatically parse structured format if detected
                            if "NL_TAG:" in tag_text and "|" in tag_text:
                                tag.parse_structured_format()
                            
                            tags.append(tag)
        except SyntaxError:
            # Skip files with syntax errors
            pass
        
        return tags
    
    def _extract_code_block(self, lines: List[str], tag_line_index: int, max_lines: int = 10) -> str:
        """Extract code block following tag (next few lines)"""
        if tag_line_index + 1 >= len(lines):
            return ""
        
        code_lines = []
        for i in range(tag_line_index + 1, min(tag_line_index + 1 + max_lines, len(lines))):
            line = lines[i].strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                code_lines.append(lines[i])
                if len(code_lines) >= 5:  # Limit to 5 lines
                    break
        
        return '\n'.join(code_lines)

