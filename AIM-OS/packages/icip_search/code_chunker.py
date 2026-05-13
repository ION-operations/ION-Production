"""
Code Chunker - Extract semantic units from code files

Extracts functions, classes, and methods as searchable chunks.
"""

import ast
import os
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class CodeChunk:
    """Represents a semantic unit of code"""
    file: str
    start_line: int
    end_line: int
    code: str
    language: str
    type: str  # 'function', 'class', 'method'
    name: str
    context: Optional[str] = None


class CodeChunker:
    """Extracts semantic code chunks from files"""
    
    def __init__(self):
        self.supported_languages = ['py', 'python']  # Start with Python
    
    def chunk_file(self, file_path: str, language: str) -> List[CodeChunk]:
        """Extract chunks from single file"""
        if language not in self.supported_languages:
            # Fallback: Whole file as chunk for unsupported languages
            return self._fallback_chunk(file_path, language)
        
        if language in ['py', 'python']:
            return self._chunk_python_file(file_path)
        
        return []
    
    def chunk_codebase(
        self,
        codebase_path: str,
        languages: Optional[List[str]] = None
    ) -> List[CodeChunk]:
        """Extract chunks from entire codebase"""
        if languages is None:
            languages = self.supported_languages
        
        chunks = []
        
        # Walk codebase
        for root, dirs, files in os.walk(codebase_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in [
                'node_modules', '.git', '__pycache__', 'dist', 
                'build', 'coverage', 'venv', '.venv'
            ]]
            
            for filename in files:
                ext = Path(filename).suffix.lstrip('.')
                if ext in languages or filename.endswith('.py'):
                    filepath = os.path.join(root, filename)
                    try:
                        file_chunks = self.chunk_file(filepath, ext)
                        chunks.extend(file_chunks)
                    except Exception as e:
                        print(f"Warning: Failed to chunk {filepath}: {e}")
                        continue
        
        return chunks
    
    def _chunk_python_file(self, file_path: str) -> List[CodeChunk]:
        """Extract chunks from Python file using AST"""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    chunk = self._extract_function(node, file_path, lines)
                    if chunk:
                        chunks.append(chunk)
                
                elif isinstance(node, ast.ClassDef):
                    chunk = self._extract_class(node, file_path, lines)
                    if chunk:
                        chunks.append(chunk)
        
        except Exception as e:
            print(f"Warning: AST parsing failed for {file_path}: {e}")
            return self._fallback_chunk(file_path, 'py')
        
        return chunks
    
    def _extract_function(
        self,
        node: ast.FunctionDef,
        file_path: str,
        lines: List[str]
    ) -> Optional[CodeChunk]:
        """Extract function as chunk"""
        try:
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            
            # Get function code
            code_lines = lines[start_line - 1:end_line]
            code = '\n'.join(code_lines)
            
            # Get context (3 lines before and after)
            context_start = max(0, start_line - 4)
            context_end = min(len(lines), end_line + 3)
            context_lines = lines[context_start:context_end]
            context = '\n'.join(context_lines)
            
            return CodeChunk(
                file=file_path,
                start_line=start_line,
                end_line=end_line,
                code=code,
                language='python',
                type='function',
                name=node.name,
                context=context
            )
        except Exception:
            return None
    
    def _extract_class(
        self,
        node: ast.ClassDef,
        file_path: str,
        lines: List[str]
    ) -> Optional[CodeChunk]:
        """Extract class as chunk"""
        try:
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            
            code_lines = lines[start_line - 1:end_line]
            code = '\n'.join(code_lines)
            
            # Context
            context_start = max(0, start_line - 4)
            context_end = min(len(lines), end_line + 3)
            context = '\n'.join(lines[context_start:context_end])
            
            return CodeChunk(
                file=file_path,
                start_line=start_line,
                end_line=end_line,
                code=code,
                language='python',
                type='class',
                name=node.name,
                context=context
            )
        except Exception:
            return None
    
    def _fallback_chunk(self, file_path: str, language: str) -> List[CodeChunk]:
        """Fallback: Treat whole file as one chunk"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            return [CodeChunk(
                file=file_path,
                start_line=1,
                end_line=len(code.splitlines()),
                code=code,
                language=language,
                type='file',
                name=Path(file_path).name,
                context=None
            )]
        except Exception:
            return []

