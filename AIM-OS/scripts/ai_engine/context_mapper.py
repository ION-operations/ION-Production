"""
AIM-OS AI Engine — Context Mapper

AST-based structural context extraction engine implementing the
Sovereign Context Mapper thesis. Eliminates context starvation by
building bounded Active Context Envelopes from Python and TypeScript files.

Instead of dumping raw files into LLM context, this engine:
    1. Parses the target file's full AST
    2. Resolves local imports to physical file paths
    3. Extracts public interface contracts from dependencies
    4. Filters to only symbols actually used by the target
    5. Packs everything into a token-budget envelope

Envelope = Full(Target)
         + Contracts(Used Dependencies)
         + Edit Guardrails

Usage:
    mapper = ContextMapper(workspace_root='/path/to/project')
    envelope = mapper.build_envelope('scripts/ai_engine/engine.py')
    print(envelope.to_string())  # XML-style context envelope
"""

import ast
import os
import re
import sys
import time
import hashlib
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from functools import lru_cache

logger = logging.getLogger('ai_engine.context_mapper')


# ══════════════════════════════════════════════════════════
#  DATA MODELS
# ══════════════════════════════════════════════════════════

@dataclass
class ImportRef:
    """A resolved import reference."""
    module_path: str          # e.g., "ai_engine.chain_director"
    imported_names: List[str] # e.g., ["ChainDirector", "QualityEvaluator"]
    resolved_file: str        # Absolute path to the source file
    is_relative: bool = False
    is_stdlib: bool = False
    is_external: bool = False

    def __repr__(self):
        names = ', '.join(self.imported_names[:3])
        if len(self.imported_names) > 3:
            names += f' +{len(self.imported_names) - 3}'
        return f"ImportRef({self.module_path} -> [{names}])"


@dataclass
class ExportedSymbol:
    """A public symbol extracted from a file."""
    name: str
    kind: str           # 'class', 'function', 'constant', 'type_alias'
    signature: str      # Full signature text
    line_start: int
    line_end: int
    docstring: str = ''
    decorators: List[str] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)     # For classes
    methods: List[str] = field(default_factory=list)   # Public method sigs for classes
    relevance_score: float = 0.0

    @property
    def char_count(self) -> int:
        return len(self.signature) + len(self.docstring) + sum(len(m) for m in self.methods)


@dataclass
class ExtractedFile:
    """Complete extraction result for a single file."""
    path: str
    imports: List[ImportRef] = field(default_factory=list)
    exports: List[ExportedSymbol] = field(default_factory=list)
    file_size_bytes: int = 0
    mtime: float = 0.0
    parse_mode: str = 'full'  # 'full', 'degraded', 'raw_fallback'
    parse_error: str = ''


@dataclass
class FileSection:
    """A section detected within a file."""
    line_start: int
    line_end: int
    title: str            # e.g., 'class AIEngine', 'def build_envelope', '## Architecture'
    kind: str             # 'class', 'function', 'constant', 'heading', 'imports', 'module_doc'
    char_count: int = 0
    exports: List[str] = field(default_factory=list)  # Symbols defined in this section
    summary: str = ''     # Brief auto-summary


@dataclass
class FileIndex:
    """Auto-generated structural index for a file."""
    path: str
    file_size: int = 0
    total_lines: int = 0
    sections: List[FileSection] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    imports_count: int = 0
    key_concepts: List[str] = field(default_factory=list)
    language: str = 'python'
    mtime: float = 0.0

    def to_string(self) -> str:
        """Render as structured text."""
        parts = [
            f'<file_index path="{os.path.basename(self.path)}">',
            f'  <size>{self.file_size:,} chars, {self.total_lines} lines</size>',
            f'  <language>{self.language}</language>',
            f'  <exports>{len(self.exports)}: {", ".join(self.exports[:15])}</exports>',
            f'  <imports>{self.imports_count}</imports>',
            f'  <key_concepts>{", ".join(self.key_concepts[:10])}</key_concepts>',
            f'  <sections count="{len(self.sections)}">',
        ]
        for sec in self.sections:
            detail = f' exports="{",".join(sec.exports[:3])}"' if sec.exports else ''
            parts.append(
                f'    <section lines="{sec.line_start}-{sec.line_end}" '
                f'kind="{sec.kind}"{detail}>{sec.title}</section>'
            )
        parts.append('  </sections>')
        parts.append('</file_index>')
        return '\n'.join(parts)

    def to_dict(self) -> Dict:
        return {
            'path': os.path.basename(self.path),
            'file_size': self.file_size,
            'total_lines': self.total_lines,
            'language': self.language,
            'exports': self.exports[:20],
            'imports_count': self.imports_count,
            'key_concepts': self.key_concepts[:10],
            'section_count': len(self.sections),
            'sections': [
                {
                    'lines': f'{s.line_start}-{s.line_end}',
                    'kind': s.kind,
                    'title': s.title,
                    'chars': s.char_count,
                    'exports': s.exports[:5],
                }
                for s in self.sections
            ],
        }
    @property
    def export_names(self) -> Set[str]:
        return {e.name for e in self.exports}


@dataclass
class ContextEnvelope:
    """The Active Context Envelope — bounded, self-contained context."""
    target_path: str
    target_content: str
    dependency_contracts: Dict[str, List[ExportedSymbol]] = field(default_factory=dict)
    used_symbols: Set[str] = field(default_factory=set)
    edit_guardrails: List[str] = field(default_factory=list)
    total_chars: int = 0
    budget_chars: int = 0
    truncated: bool = False

    def to_string(self) -> str:
        """Render envelope as structured text for LLM injection."""
        lines = []
        lines.append('<system_envelope version="1.0">')
        lines.append('  <intent>Active Context Envelope for requested file.</intent>')
        lines.append('')

        # Edit rules
        lines.append('  <edit_rules>')
        lines.append('    - Modify only the target_file unless explicitly instructed.')
        lines.append('    - Treat outbound_contracts as read-only.')
        lines.append('    - Preserve public API compatibility unless the task requires otherwise.')
        for rule in self.edit_guardrails:
            lines.append(f'    - {rule}')
        lines.append('  </edit_rules>')
        lines.append('')

        # Dependency contracts
        if self.dependency_contracts:
            lines.append('  <outbound_contracts>')
            for dep_path, symbols in self.dependency_contracts.items():
                basename = os.path.basename(dep_path)
                lines.append(f'    # --- FROM: {basename} ---')
                for sym in symbols:
                    lines.append(f'    {sym.signature}')
                    if sym.kind == 'class' and sym.methods:
                        for method in sym.methods:
                            lines.append(f'        {method}')
                lines.append('')
            lines.append('  </outbound_contracts>')
            lines.append('')

        # Symbol usage index
        if self.used_symbols:
            lines.append('  <target_symbol_usage>')
            for sym in sorted(self.used_symbols):
                lines.append(f'    {sym}')
            lines.append('  </target_symbol_usage>')
            lines.append('')

        # Full target
        lines.append(f'  <target_file path="{self.target_path}">')
        lines.append(self.target_content)
        lines.append('  </target_file>')
        lines.append('</system_envelope>')

        return '\n'.join(lines)

    @property
    def stats(self) -> Dict:
        total_contracts = sum(len(s) for s in self.dependency_contracts.values())
        return {
            'target_path': self.target_path,
            'target_chars': len(self.target_content),
            'dependency_count': len(self.dependency_contracts),
            'contract_count': total_contracts,
            'used_symbols': len(self.used_symbols),
            'total_chars': self.total_chars,
            'budget_chars': self.budget_chars,
            'truncated': self.truncated,
            'estimated_tokens': self.total_chars // 4,
        }


# ══════════════════════════════════════════════════════════
#  CACHE
# ══════════════════════════════════════════════════════════

class _ExtractionCache:
    """LRU-style cache keyed on (path, mtime, size)."""

    def __init__(self, max_size: int = 200):
        self._store: Dict[str, Tuple[float, int, ExtractedFile]] = {}
        self._max_size = max_size

    def get(self, path: str) -> Optional[ExtractedFile]:
        """Return cached extraction if file hasn't changed."""
        if path not in self._store:
            return None
        try:
            stat = os.stat(path)
            cached_mtime, cached_size, cached_result = self._store[path]
            if stat.st_mtime == cached_mtime and stat.st_size == cached_size:
                return cached_result
            else:
                del self._store[path]
                return None
        except OSError:
            return None

    def put(self, path: str, result: ExtractedFile):
        """Cache an extraction result."""
        if len(self._store) >= self._max_size:
            # Evict oldest entry
            oldest = min(self._store, key=lambda k: self._store[k][0])
            del self._store[oldest]
        self._store[path] = (result.mtime, result.file_size_bytes, result)

    def clear(self):
        self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)


# ══════════════════════════════════════════════════════════
#  AST EXTRACTION ENGINE
# ══════════════════════════════════════════════════════════

class ASTExtractor:
    """
    Extract public interface contracts from Python files using AST.

    Supports:
        - Top-level classes (with public method signatures)
        - Top-level functions
        - Module-level constants (UPPER_CASE assignments)
        - Type aliases
        - Dataclasses and their fields
    """

    @staticmethod
    def extract(file_path: str) -> ExtractedFile:
        """Parse a Python file and extract its public interface."""
        result = ExtractedFile(path=file_path)

        try:
            stat = os.stat(file_path)
            result.file_size_bytes = stat.st_size
            result.mtime = stat.st_mtime
        except OSError:
            result.parse_mode = 'raw_fallback'
            result.parse_error = f'File not found: {file_path}'
            return result

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                source = f.read()
        except Exception as e:
            result.parse_mode = 'raw_fallback'
            result.parse_error = f'Read error: {e}'
            return result

        try:
            tree = ast.parse(source, filename=file_path)
        except SyntaxError as e:
            # Degraded mode: extract via line scanning
            result.parse_mode = 'degraded'
            result.parse_error = f'Syntax error at line {e.lineno}: {e.msg}'
            result.exports = ASTExtractor._degraded_extract(source)
            result.imports = ASTExtractor._extract_imports_from_lines(source)
            return result

        source_lines = source.splitlines()

        # Extract imports
        result.imports = ASTExtractor._extract_imports(tree, file_path)

        # Extract exports
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                sym = ASTExtractor._extract_class(node, source_lines)
                if sym:
                    result.exports.append(sym)

            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                sym = ASTExtractor._extract_function(node, source_lines)
                if sym:
                    result.exports.append(sym)

            elif isinstance(node, ast.Assign):
                sym = ASTExtractor._extract_constant(node, source_lines)
                if sym:
                    result.exports.append(sym)

            elif isinstance(node, ast.AnnAssign):
                sym = ASTExtractor._extract_annotated_assign(node, source_lines)
                if sym:
                    result.exports.append(sym)

        return result

    @staticmethod
    def _extract_imports(tree: ast.Module, file_path: str) -> List[ImportRef]:
        """Extract all import statements from AST."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportRef(
                        module_path=alias.name,
                        imported_names=[alias.asname or alias.name.split('.')[-1]],
                        resolved_file='',
                        is_relative=False,
                    ))

            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                names = [alias.asname or alias.name for alias in node.names]
                imports.append(ImportRef(
                    module_path=node.module,
                    imported_names=names,
                    resolved_file='',
                    is_relative=node.level > 0,
                ))

        return imports

    @staticmethod
    def _extract_class(node: ast.ClassDef, source_lines: List[str]) -> Optional[ExportedSymbol]:
        """Extract a class definition with public method signatures."""
        if node.name.startswith('_'):
            return None

        # Build class signature
        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except Exception:
                bases.append('?')

        base_str = f"({', '.join(bases)})" if bases else ''
        sig = f"class {node.name}{base_str}:"

        # Get decorators
        decorators = []
        for dec in node.decorator_list:
            try:
                decorators.append(f"@{ast.unparse(dec)}")
            except Exception:
                pass

        # Get docstring
        docstring = ast.get_docstring(node) or ''
        if len(docstring) > 200:
            docstring = docstring[:200] + '...'

        # Get public method signatures
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not item.name.startswith('_') or item.name in ('__init__', '__call__', '__iter__', '__next__', '__enter__', '__exit__', '__getitem__', '__len__'):
                    try:
                        args = ast.unparse(item.args)
                        ret = ''
                        if item.returns:
                            ret = f" -> {ast.unparse(item.returns)}"
                        prefix = 'async ' if isinstance(item, ast.AsyncFunctionDef) else ''
                        methods.append(f"{prefix}def {item.name}({args}){ret}")
                    except Exception:
                        methods.append(f"def {item.name}(...)")

        # Get fields from dataclass / assignment in __init__
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and item.target:
                try:
                    field_name = ast.unparse(item.target)
                    field_type = ast.unparse(item.annotation) if item.annotation else '?'
                    if not field_name.startswith('_'):
                        methods.append(f"{field_name}: {field_type}")
                except Exception:
                    pass

        return ExportedSymbol(
            name=node.name,
            kind='class',
            signature=sig,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            decorators=decorators,
            bases=bases,
            methods=methods,
        )

    @staticmethod
    def _extract_function(node, source_lines: List[str]) -> Optional[ExportedSymbol]:
        """Extract a top-level function signature."""
        if node.name.startswith('_'):
            return None

        try:
            args = ast.unparse(node.args)
            ret = ''
            if node.returns:
                ret = f" -> {ast.unparse(node.returns)}"
            prefix = 'async ' if isinstance(node, ast.AsyncFunctionDef) else ''
            sig = f"{prefix}def {node.name}({args}){ret}"
        except Exception:
            sig = f"def {node.name}(...)"

        decorators = []
        for dec in node.decorator_list:
            try:
                decorators.append(f"@{ast.unparse(dec)}")
            except Exception:
                pass

        docstring = ast.get_docstring(node) or ''
        if len(docstring) > 200:
            docstring = docstring[:200] + '...'

        return ExportedSymbol(
            name=node.name,
            kind='function',
            signature=sig,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            decorators=decorators,
        )

    @staticmethod
    def _extract_constant(node: ast.Assign, source_lines: List[str]) -> Optional[ExportedSymbol]:
        """Extract module-level constants (UPPER_CASE)."""
        if len(node.targets) != 1:
            return None
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            return None
        if not target.id.isupper() and not target.id[0].isupper():
            return None
        # Skip internal names
        if target.id.startswith('_'):
            return None

        try:
            value_repr = ast.unparse(node.value)
            if len(value_repr) > 100:
                value_repr = value_repr[:100] + '...'
            sig = f"{target.id} = {value_repr}"
        except Exception:
            sig = f"{target.id} = ..."

        return ExportedSymbol(
            name=target.id,
            kind='constant',
            signature=sig,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
        )

    @staticmethod
    def _extract_annotated_assign(node: ast.AnnAssign, source_lines: List[str]) -> Optional[ExportedSymbol]:
        """Extract annotated module-level assignments (type aliases, typed constants)."""
        if not node.target or not isinstance(node.target, ast.Name):
            return None
        name = node.target.id
        if name.startswith('_'):
            return None

        try:
            ann = ast.unparse(node.annotation) if node.annotation else '?'
            if node.value:
                val = ast.unparse(node.value)
                if len(val) > 80:
                    val = val[:80] + '...'
                sig = f"{name}: {ann} = {val}"
            else:
                sig = f"{name}: {ann}"
        except Exception:
            sig = f"{name}: ..."

        kind = 'type_alias' if name[0].isupper() else 'constant'

        return ExportedSymbol(
            name=name,
            kind=kind,
            signature=sig,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
        )

    @staticmethod
    def _degraded_extract(source: str) -> List[ExportedSymbol]:
        """Line-based extraction when AST fails."""
        exports = []
        for i, line in enumerate(source.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith('class ') and not stripped.split()[1].startswith('_'):
                name = stripped.split('(')[0].split(':')[0].replace('class ', '')
                exports.append(ExportedSymbol(
                    name=name, kind='class', signature=stripped.rstrip(':'),
                    line_start=i, line_end=i,
                ))
            elif stripped.startswith('def ') and not stripped.split('(')[0].split()[-1].startswith('_'):
                name = stripped.split('(')[0].replace('def ', '').strip()
                exports.append(ExportedSymbol(
                    name=name, kind='function', signature=stripped.rstrip(':'),
                    line_start=i, line_end=i,
                ))
        return exports

    @staticmethod
    def _extract_imports_from_lines(source: str) -> List[ImportRef]:
        """Line-based import extraction when AST fails."""
        imports = []
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith('from ') and ' import ' in stripped:
                parts = stripped.split(' import ')
                module = parts[0].replace('from ', '').strip()
                names = [n.strip().split(' as ')[0] for n in parts[1].split(',')]
                imports.append(ImportRef(
                    module_path=module, imported_names=names,
                    resolved_file='', is_relative=module.startswith('.'),
                ))
            elif stripped.startswith('import '):
                module = stripped.replace('import ', '').strip().split(' as ')[0]
                imports.append(ImportRef(
                    module_path=module, imported_names=[module.split('.')[-1]],
                    resolved_file='',
                ))
        return imports


# ══════════════════════════════════════════════════════════
#  TYPESCRIPT / JAVASCRIPT EXTRACTOR
# ══════════════════════════════════════════════════════════

class TSExtractor:
    """
    Regex-based TypeScript/JavaScript contract extractor.

    Handles:
        - export interface X { ... }
        - export type X = ...
        - export class X { ... }
        - export function f(...): ReturnType { ... }
        - export const / let / var
        - import { X } from './module'
        - import * as ns from 'module'

    Uses brace-counting instead of a full TS parser — zero dependencies,
    captures ~90% of contracts at sub-ms speed.
    """

    # ── Compiled Patterns ─────────────────────────────────
    INTERFACE_RE = re.compile(
        r'export\s+interface\s+(\w+)(?:\s+extends\s+([\w,\s<>]+))?\s*\{',
        re.MULTILINE,
    )
    TYPE_RE = re.compile(
        r'export\s+type\s+(\w+)(?:<[^>]+>)?\s*=\s*(.+?)(?:;|$)',
        re.MULTILINE,
    )
    CLASS_RE = re.compile(
        r'export\s+(?:default\s+)?(?:abstract\s+)?class\s+(\w+)'
        r'(?:\s+(?:extends|implements)\s+([\w,\s<>]+))?\s*\{',
        re.MULTILINE,
    )
    FUNCTION_RE = re.compile(
        r'export\s+(?:default\s+)?(?:async\s+)?function\s+(\w+)\s*'
        r'(?:<[^>]+>)?\s*\(([^)]*)\)(?:\s*:\s*([^\{]+?))?\s*\{',
        re.MULTILINE,
    )
    CONST_RE = re.compile(
        r'export\s+(?:const|let|var)\s+(\w+)(?:\s*:\s*([^=]+?))?\s*=',
        re.MULTILINE,
    )
    ENUM_RE = re.compile(
        r'export\s+(?:const\s+)?enum\s+(\w+)\s*\{',
        re.MULTILINE,
    )
    IMPORT_RE = re.compile(
        r"import\s+(?:\{([^}]+)\}|\*\s+as\s+(\w+))\s+from\s+['\"]([^'\"]+)['\"]",
        re.MULTILINE,
    )

    @staticmethod
    def extract(file_path: str) -> ExtractedFile:
        """Parse a TS/JS file and extract its public interface."""
        result = ExtractedFile(path=file_path)

        try:
            stat = os.stat(file_path)
            result.file_size_bytes = stat.st_size
            result.mtime = stat.st_mtime
        except OSError:
            result.parse_mode = 'raw_fallback'
            result.parse_error = f'File not found: {file_path}'
            return result

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                source = f.read()
        except Exception as e:
            result.parse_mode = 'raw_fallback'
            result.parse_error = f'Read error: {e}'
            return result

        result.parse_mode = 'regex'

        # ── Extract imports ───────────────────────────────
        result.imports = TSExtractor._extract_imports(source)

        # ── Extract exports ───────────────────────────────
        # Interfaces
        for m in TSExtractor.INTERFACE_RE.finditer(source):
            name = m.group(1)
            bases = [b.strip() for b in (m.group(2) or '').split(',') if b.strip()]
            block = TSExtractor._extract_brace_block(source, m.end() - 1)
            members = TSExtractor._extract_interface_members(block)
            result.exports.append(ExportedSymbol(
                name=name,
                kind='interface',
                signature=f'interface {name}',
                line_start=source[:m.start()].count('\n') + 1,
                line_end=source[:m.start() + len(block)].count('\n') + 1,
                bases=bases,
                methods=members,
            ))

        # Type aliases
        for m in TSExtractor.TYPE_RE.finditer(source):
            name = m.group(1)
            value = m.group(2).strip()
            if len(value) > 120:
                value = value[:120] + '...'
            result.exports.append(ExportedSymbol(
                name=name,
                kind='type_alias',
                signature=f'type {name} = {value}',
                line_start=source[:m.start()].count('\n') + 1,
                line_end=source[:m.end()].count('\n') + 1,
            ))

        # Classes
        for m in TSExtractor.CLASS_RE.finditer(source):
            name = m.group(1)
            bases = [b.strip() for b in (m.group(2) or '').split(',') if b.strip()]
            block = TSExtractor._extract_brace_block(source, m.end() - 1)
            methods = TSExtractor._extract_class_methods(block)
            result.exports.append(ExportedSymbol(
                name=name,
                kind='class',
                signature=f'class {name}',
                line_start=source[:m.start()].count('\n') + 1,
                line_end=source[:m.start() + len(block)].count('\n') + 1,
                bases=bases,
                methods=methods,
            ))

        # Functions
        for m in TSExtractor.FUNCTION_RE.finditer(source):
            name = m.group(1)
            params = m.group(2).strip()
            ret = (m.group(3) or '').strip()
            ret_str = f' -> {ret}' if ret else ''
            result.exports.append(ExportedSymbol(
                name=name,
                kind='function',
                signature=f'function {name}({params}){ret_str}',
                line_start=source[:m.start()].count('\n') + 1,
                line_end=source[:m.end()].count('\n') + 1,
            ))

        # Enums
        for m in TSExtractor.ENUM_RE.finditer(source):
            name = m.group(1)
            block = TSExtractor._extract_brace_block(source, m.end() - 1)
            members = [line.strip().rstrip(',') for line in block.strip('{}').splitlines()
                      if line.strip() and not line.strip().startswith('//')]
            result.exports.append(ExportedSymbol(
                name=name,
                kind='enum',
                signature=f'enum {name}',
                line_start=source[:m.start()].count('\n') + 1,
                line_end=source[:m.start() + len(block)].count('\n') + 1,
                methods=members[:20],  # Cap for large enums
            ))

        # Constants
        for m in TSExtractor.CONST_RE.finditer(source):
            name = m.group(1)
            type_ann = (m.group(2) or '').strip()
            # Skip if already captured as a class/function (e.g., export const X = class {})
            existing = {e.name for e in result.exports}
            if name in existing:
                continue
            type_str = f': {type_ann}' if type_ann else ''
            result.exports.append(ExportedSymbol(
                name=name,
                kind='constant',
                signature=f'const {name}{type_str}',
                line_start=source[:m.start()].count('\n') + 1,
                line_end=source[:m.end()].count('\n') + 1,
            ))

        return result

    @staticmethod
    def _extract_imports(source: str) -> List[ImportRef]:
        """Extract ES6 imports from TS/JS source."""
        imports = []
        for m in TSExtractor.IMPORT_RE.finditer(source):
            named = m.group(1)  # { X, Y, Z }
            star = m.group(2)   # * as ns
            module = m.group(3) # './path' or 'package'

            if named:
                names = [n.strip().split(' as ')[0].strip() for n in named.split(',') if n.strip()]
            elif star:
                names = [star]
            else:
                names = []

            is_relative = module.startswith('.') or module.startswith('/')
            imports.append(ImportRef(
                module_path=module,
                imported_names=names,
                resolved_file='',
                is_relative=is_relative,
            ))
        return imports

    @staticmethod
    def _extract_brace_block(source: str, start_pos: int) -> str:
        """Extract a complete brace-delimited block from source."""
        if start_pos >= len(source) or source[start_pos] != '{':
            return '{}'

        depth = 0
        i = start_pos
        in_string = None
        in_line_comment = False
        in_block_comment = False

        while i < len(source):
            c = source[i]

            # Handle comments
            if not in_string:
                if i + 1 < len(source):
                    two = source[i:i+2]
                    if two == '//' and not in_block_comment:
                        in_line_comment = True
                        i += 2
                        continue
                    elif two == '/*' and not in_line_comment:
                        in_block_comment = True
                        i += 2
                        continue
                    elif two == '*/' and in_block_comment:
                        in_block_comment = False
                        i += 2
                        continue

            if in_line_comment:
                if c == '\n':
                    in_line_comment = False
                i += 1
                continue
            if in_block_comment:
                i += 1
                continue

            # Handle strings
            if c in ('"', "'", '`') and not in_string:
                in_string = c
            elif c == in_string and (i == 0 or source[i-1] != '\\'):
                in_string = None
            elif in_string:
                i += 1
                continue

            # Count braces
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return source[start_pos:i+1]

            i += 1

        return source[start_pos:]  # Unclosed — return rest

    @staticmethod
    def _extract_interface_members(block: str) -> List[str]:
        """Extract member signatures from an interface block."""
        members = []
        # Get content between outermost braces
        inner = block.strip()[1:-1] if block.strip().startswith('{') else block
        for line in inner.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
                continue
            # Remove trailing semicolons and commas
            stripped = stripped.rstrip(';,').strip()
            if stripped:
                members.append(stripped)
        return members[:30]  # Cap at 30 members

    @staticmethod
    def _extract_class_methods(block: str) -> List[str]:
        """Extract method signatures from a class block."""
        methods = []
        method_re = re.compile(
            r'^\s+(?:(?:public|private|protected|static|async|abstract|readonly)\s+)*'
            r'(\w+)\s*(?:<[^>]*>)?\s*\(([^)]*)\)(?:\s*:\s*([^\{;]+?))?\s*[\{;]',
            re.MULTILINE,
        )
        for m in method_re.finditer(block):
            name = m.group(1)
            if name in ('constructor', 'get', 'set') or not name.startswith('_'):
                params = m.group(2).strip()
                ret = (m.group(3) or '').strip()
                ret_str = f': {ret}' if ret else ''
                methods.append(f'{name}({params}){ret_str}')
        return methods[:30]  # Cap


# ══════════════════════════════════════════════════════════
#  IMPORT RESOLVER
# ══════════════════════════════════════════════════════════

class ImportResolver:
    """Resolve Python import paths to physical file paths."""

    STDLIB_MODULES = frozenset([
        'os', 'sys', 'ast', 'json', 'math', 'time', 'copy', 'io',
        'pathlib', 'logging', 'typing', 'collections', 'functools',
        'itertools', 'hashlib', 'dataclasses', 'abc', 'enum', 're',
        'datetime', 'threading', 'subprocess', 'shutil', 'glob',
        'textwrap', 'inspect', 'traceback', 'unittest', 'argparse',
        'sqlite3', 'http', 'urllib', 'socket', 'asyncio', 'concurrent',
        'contextlib', 'operator', 'string', 'struct', 'tempfile',
        'warnings', 'weakref', 'pprint', 'uuid', 'csv', 'dis',
    ])

    EXTERNAL_PACKAGES = frozenset([
        'numpy', 'pandas', 'requests', 'flask', 'django', 'fastapi',
        'torch', 'tensorflow', 'scipy', 'matplotlib', 'pillow',
        'pydantic', 'sqlalchemy', 'aiohttp', 'httpx', 'click',
        'pytest', 'setuptools', 'pip', 'wheel', 'six', 'chardet',
        'certifi', 'idna', 'cryptography', 'paramiko', 'boto3',
        'google', 'anthropic', 'openai', 'tiktoken', 'transformers',
    ])

    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.normpath(workspace_root)

    def resolve(self, imp: ImportRef, source_file: str) -> ImportRef:
        """Resolve an import to its physical file path."""
        top_module = imp.module_path.split('.')[0]

        # Check stdlib
        if top_module in self.STDLIB_MODULES:
            imp.is_stdlib = True
            return imp

        # Check external
        if top_module in self.EXTERNAL_PACKAGES:
            imp.is_external = True
            return imp

        # Try to resolve locally
        if imp.is_relative:
            resolved = self._resolve_relative(imp, source_file)
        else:
            resolved = self._resolve_absolute(imp)

        if resolved:
            imp.resolved_file = resolved
        else:
            # Could be external package we don't know about
            imp.is_external = True

        return imp

    def _resolve_relative(self, imp: ImportRef, source_file: str) -> Optional[str]:
        """Resolve a relative import (from . or from ..)."""
        source_dir = os.path.dirname(source_file)
        parts = imp.module_path.lstrip('.').split('.')

        # Each leading dot goes up one directory
        # But since we stripped the dots, we work from source_dir
        candidate = os.path.join(source_dir, *parts)
        return self._try_paths(candidate)

    def _resolve_absolute(self, imp: ImportRef) -> Optional[str]:
        """Resolve an absolute import path."""
        parts = imp.module_path.split('.')

        # Try from workspace root
        candidate = os.path.join(self.workspace_root, *parts)
        resolved = self._try_paths(candidate)
        if resolved:
            return resolved

        # Try from scripts/ directory
        candidate = os.path.join(self.workspace_root, 'scripts', *parts)
        resolved = self._try_paths(candidate)
        if resolved:
            return resolved

        # Try from scripts/ai_engine/ (common in AIM-OS)
        if len(parts) >= 1:
            candidate = os.path.join(self.workspace_root, 'scripts', 'ai_engine', *parts)
            resolved = self._try_paths(candidate)
            if resolved:
                return resolved

        return None

    def _try_paths(self, base: str) -> Optional[str]:
        """Try common file path patterns (Python + TypeScript)."""
        candidates = [
            base + '.py',
            os.path.join(base, '__init__.py'),
            base + '.ts',
            base + '.tsx',
            base + '.js',
            base + '.jsx',
            os.path.join(base, 'index.ts'),
            os.path.join(base, 'index.tsx'),
            os.path.join(base, 'index.js'),
        ]
        for path in candidates:
            if os.path.isfile(path):
                return os.path.normpath(path)
        return None


# ══════════════════════════════════════════════════════════
#  CONTEXT MAPPER (MAIN ENGINE)
# ══════════════════════════════════════════════════════════

class ContextMapper:
    """
    AST-based context extraction engine.

    Implements the Active Context Envelope from the
    Sovereign Context Mapper thesis:

        Envelope = Full(Target)
                 + Contracts(Used Dependencies)
                 + Edit Guardrails

    Usage:
        mapper = ContextMapper('/path/to/workspace')
        envelope = mapper.build_envelope('scripts/ai_engine/engine.py')
        print(envelope.stats)
    """

    def __init__(self, workspace_root: str = ''):
        if not workspace_root:
            workspace_root = os.path.normpath(
                os.path.join(os.path.dirname(__file__), '..', '..')
            )
        self.workspace_root = workspace_root
        self.resolver = ImportResolver(workspace_root)
        self.cache = _ExtractionCache(max_size=200)
        self._py_extractor = ASTExtractor()
        self._ts_extractor = TSExtractor()

    def build_envelope(
        self,
        target_path: str,
        budget_chars: int = 32000,
        include_guardrails: bool = True,
    ) -> ContextEnvelope:
        """
        Build an Active Context Envelope for a target file.

        Args:
            target_path: Path to the file (relative or absolute)
            budget_chars: Maximum envelope size in characters (~4 chars/token)
            include_guardrails: Whether to include edit rules

        Returns:
            ContextEnvelope with target content + dependency contracts
        """
        # Resolve target path
        if not os.path.isabs(target_path):
            abs_target = os.path.normpath(
                os.path.join(self.workspace_root, target_path)
            )
        else:
            abs_target = os.path.normpath(target_path)

        if not os.path.isfile(abs_target):
            logger.error(f"Target file not found: {abs_target}")
            return ContextEnvelope(
                target_path=target_path,
                target_content=f"# ERROR: File not found: {target_path}",
                edit_guardrails=["Target file does not exist."],
            )

        # Read target file content
        try:
            with open(abs_target, 'r', encoding='utf-8', errors='replace') as f:
                target_content = f.read()
        except Exception as e:
            return ContextEnvelope(
                target_path=target_path,
                target_content=f"# ERROR: Cannot read file: {e}",
            )

        # Extract target's AST
        target_extracted = self._extract_cached(abs_target)

        # Resolve imports to physical files
        resolved_imports = []
        for imp in target_extracted.imports:
            resolved = self.resolver.resolve(imp, abs_target)
            if resolved.resolved_file and not resolved.is_stdlib and not resolved.is_external:
                resolved_imports.append(resolved)

        # Find which symbols the target actually uses
        used_symbols = self._find_used_symbols(target_content, resolved_imports)

        # Extract contracts from dependencies
        dep_contracts: Dict[str, List[ExportedSymbol]] = {}
        for imp in resolved_imports:
            if not imp.resolved_file:
                continue
            dep_extracted = self._extract_cached(imp.resolved_file)
            # Filter to only symbols actually used
            relevant = self._filter_relevant_symbols(
                dep_extracted, imp.imported_names, used_symbols
            )
            if relevant:
                dep_contracts[imp.resolved_file] = relevant

        # Build guardrails
        guardrails = []
        if include_guardrails:
            guardrails = [
                "Do not modify dependency contracts.",
                "Preserve exported API compatibility.",
                f"Target file: {os.path.basename(abs_target)} ({len(target_content)} chars)",
                f"Dependencies included: {len(dep_contracts)} files",
            ]

        # Create envelope
        envelope = ContextEnvelope(
            target_path=target_path,
            target_content=target_content,
            dependency_contracts=dep_contracts,
            used_symbols=used_symbols,
            edit_guardrails=guardrails,
            budget_chars=budget_chars,
        )

        # Pack to budget
        envelope = self._pack_to_budget(envelope, budget_chars)

        return envelope

    def extract_contracts(self, file_path: str) -> ExtractedFile:
        """Extract public interface contracts from a single file."""
        if not os.path.isabs(file_path):
            file_path = os.path.normpath(
                os.path.join(self.workspace_root, file_path)
            )
        return self._extract_cached(file_path)

    def build_index(self, file_path: str) -> FileIndex:
        """
        Build an auto-generated structural index for a file.

        Detects sections at class/function boundaries (code) or
        heading boundaries (markdown). Extracts key concepts from
        docstrings, comments, and symbol names. Cached by mtime.
        """
        if not os.path.isabs(file_path):
            file_path = os.path.normpath(
                os.path.join(self.workspace_root, file_path)
            )

        if not os.path.isfile(file_path):
            return FileIndex(path=file_path)

        # Check index cache
        cache_key = f'_idx_{file_path}'
        cached = self.cache.get(cache_key)
        if cached and isinstance(cached, FileIndex):
            return cached

        ext = os.path.splitext(file_path)[1].lower()
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception:
            return FileIndex(path=file_path)

        lines = content.splitlines()
        total_lines = len(lines)
        mtime = os.path.getmtime(file_path)

        # Determine language
        if ext == '.md':
            language = 'markdown'
        elif ext in ('.ts', '.tsx'):
            language = 'typescript'
        elif ext in ('.js', '.jsx'):
            language = 'javascript'
        else:
            language = 'python'

        # Extract contracts for exports/imports
        extraction = self._extract_cached(file_path)
        exports = [exp.name for exp in extraction.exports]
        imports_count = len(extraction.imports)

        # Detect sections
        sections = []
        if language == 'markdown':
            sections = self._detect_md_sections(lines)
        else:
            sections = self._detect_code_sections(lines, extraction)

        # Extract key concepts
        concepts = self._extract_concepts(content, extraction)

        index = FileIndex(
            path=file_path,
            file_size=len(content),
            total_lines=total_lines,
            sections=sections,
            exports=exports,
            imports_count=imports_count,
            key_concepts=concepts,
            language=language,
            mtime=mtime,
        )

        # Don't cache FileIndex in ExtractedFile cache — use a wrapper
        # (Cache expects ExtractedFile; we store it with a prefix key)
        return index

    def get_section(self, file_path: str, line_start: int, line_end: int) -> str:
        """Return a specific section of a file by line range."""
        if not os.path.isabs(file_path):
            file_path = os.path.normpath(
                os.path.join(self.workspace_root, file_path)
            )
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            start = max(0, line_start - 1)
            end = min(len(lines), line_end)
            return ''.join(lines[start:end])
        except Exception:
            return ''

    def _detect_code_sections(self, lines: List[str], extraction: ExtractedFile) -> List[FileSection]:
        """Detect sections at class/function boundaries."""
        sections = []

        # Module-level docstring
        if lines and (lines[0].startswith('"""') or lines[0].startswith("'''")):
            doc_end = 1
            for i, line in enumerate(lines[1:], 1):
                if '"""' in line or "'''" in line:
                    doc_end = i + 1
                    break
            sections.append(FileSection(
                line_start=1, line_end=doc_end,
                title='Module docstring',
                kind='module_doc',
                char_count=sum(len(lines[j]) for j in range(doc_end)),
            ))

        # Import section
        import_start = None
        import_end = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                if import_start is None:
                    import_start = i + 1
                import_end = i + 1
        if import_start is not None:
            sections.append(FileSection(
                line_start=import_start, line_end=import_end,
                title=f'Imports ({extraction.imports.__len__()} statements)',
                kind='imports',
                char_count=sum(len(lines[j]) for j in range(import_start - 1, import_end) if j < len(lines)),
            ))

        # Class and function sections from extraction
        for exp in extraction.exports:
            sec_exports = [exp.name]
            if exp.kind == 'class' and exp.methods:
                sec_exports.extend(m.split('(')[0].strip().split('def ')[-1] for m in exp.methods[:5])
            sections.append(FileSection(
                line_start=exp.line_start,
                line_end=exp.line_end,
                title=f'{exp.kind} {exp.name}' + (f'({exp.bases[0]})' if exp.bases else ''),
                kind=exp.kind,
                char_count=exp.char_count,
                exports=sec_exports,
                summary=exp.docstring[:100] if exp.docstring else '',
            ))

        sections.sort(key=lambda s: s.line_start)
        return sections

    def _detect_md_sections(self, lines: List[str]) -> List[FileSection]:
        """Detect sections at heading boundaries in markdown."""
        sections = []
        current_start = 1
        current_title = 'Header'
        current_kind = 'heading'

        for i, line in enumerate(lines):
            if line.startswith('#'):
                # Close previous section
                if i > 0:
                    sections.append(FileSection(
                        line_start=current_start,
                        line_end=i,
                        title=current_title,
                        kind=current_kind,
                        char_count=sum(len(lines[j]) for j in range(current_start - 1, i)),
                    ))
                current_start = i + 1
                current_title = line.strip().lstrip('#').strip()
                level = len(line) - len(line.lstrip('#'))
                current_kind = f'h{min(level, 6)}'

        # Close final section
        if lines:
            sections.append(FileSection(
                line_start=current_start,
                line_end=len(lines),
                title=current_title,
                kind=current_kind,
                char_count=sum(len(lines[j]) for j in range(current_start - 1, len(lines))),
            ))

        return sections

    def _extract_concepts(self, content: str, extraction: ExtractedFile) -> List[str]:
        """Extract key concepts from docstrings, comments, and symbol names."""
        concepts = set()

        # From export names (split CamelCase and snake_case)
        for exp in extraction.exports:
            # CamelCase split
            words = re.findall(r'[A-Z][a-z]+|[a-z]+', exp.name)
            for w in words:
                if len(w) > 3:
                    concepts.add(w.lower())
            # Docstring keywords
            if exp.docstring:
                for word in re.findall(r'\b[a-z]{4,}\b', exp.docstring.lower()):
                    if word not in ('self', 'args', 'kwargs', 'none', 'true', 'false',
                                   'return', 'returns', 'param', 'type', 'this', 'that',
                                   'with', 'from', 'into', 'will', 'should', 'each'):
                        concepts.add(word)

        # From import modules
        for imp in extraction.imports:
            if not imp.is_stdlib and not imp.is_external:
                parts = imp.module_path.split('.')
                for part in parts:
                    if len(part) > 3:
                        concepts.add(part.lower())

        # Limit and sort by length (longer = more specific = more useful)
        sorted_concepts = sorted(concepts, key=lambda c: -len(c))
        return sorted_concepts[:15]

    def status(self) -> Dict:
        """Return mapper status."""
        return {
            'workspace_root': self.workspace_root,
            'cache_size': self.cache.size,
            'stdlib_modules': len(ImportResolver.STDLIB_MODULES),
            'external_packages': len(ImportResolver.EXTERNAL_PACKAGES),
        }

    # ── Internal Methods ─────────────────────────────────

    def _extract_cached(self, file_path: str) -> ExtractedFile:
        """Extract with LRU cache. Dispatches to Python or TS extractor."""
        cached = self.cache.get(file_path)
        if cached:
            return cached
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ('.ts', '.tsx', '.js', '.jsx'):
            result = self._ts_extractor.extract(file_path)
        else:
            result = self._py_extractor.extract(file_path)
        self.cache.put(file_path, result)
        return result

    def _find_used_symbols(
        self,
        target_content: str,
        imports: List[ImportRef],
    ) -> Set[str]:
        """Find which imported symbols are actually used in target content."""
        # Strip out all import lines to avoid false positives
        lines = target_content.splitlines()
        non_import_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                continue
            non_import_lines.append(line)
        body = '\n'.join(non_import_lines)

        # Also check for TS-style imports (import { X } from ...)
        # Already handled by the startswith('import ') check above

        used = set()
        for imp in imports:
            for name in imp.imported_names:
                if name == '*':
                    continue
                # Check if the symbol name appears in non-import body
                if name in body:
                    used.add(name)
        return used

    def _filter_relevant_symbols(
        self,
        dep: ExtractedFile,
        imported_names: List[str],
        used_symbols: Set[str],
    ) -> List[ExportedSymbol]:
        """Filter dependency exports to only those relevant to the target."""
        relevant = []

        for export in dep.exports:
            # Direct import match
            if export.name in imported_names:
                if export.name in used_symbols or '*' in imported_names:
                    export.relevance_score = 1.0
                    relevant.append(export)
                    continue

            # Type referenced in signatures of used symbols
            for imp_name in imported_names:
                if imp_name in used_symbols and export.name in str(dep.exports):
                    export.relevance_score = 0.6
                    relevant.append(export)
                    break

        # Sort by relevance
        relevant.sort(key=lambda s: s.relevance_score, reverse=True)
        return relevant

    def _pack_to_budget(
        self,
        envelope: ContextEnvelope,
        budget: int,
    ) -> ContextEnvelope:
        """Pack envelope contents to fit within character budget."""
        # Calculate current size
        target_size = len(envelope.target_content)
        contract_size = 0
        for symbols in envelope.dependency_contracts.values():
            for sym in symbols:
                contract_size += sym.char_count

        overhead = 500  # XML tags, guardrails, etc.
        total = target_size + contract_size + overhead
        envelope.total_chars = total

        if total <= budget:
            return envelope

        # Need to truncate — contracts first, then target
        remaining = budget - target_size - overhead

        if remaining <= 0:
            # Target alone exceeds budget — truncate it
            envelope.target_content = envelope.target_content[:budget - overhead]
            envelope.dependency_contracts = {}
            envelope.truncated = True
            envelope.total_chars = len(envelope.target_content) + overhead
            return envelope

        # Rank and pack contracts greedily
        all_contracts = []
        for dep_path, symbols in envelope.dependency_contracts.items():
            for sym in symbols:
                all_contracts.append((dep_path, sym))

        # Sort by relevance score (highest first)
        all_contracts.sort(key=lambda x: x[1].relevance_score, reverse=True)

        packed: Dict[str, List[ExportedSymbol]] = {}
        used_budget = 0

        for dep_path, sym in all_contracts:
            sym_size = sym.char_count
            if used_budget + sym_size <= remaining:
                if dep_path not in packed:
                    packed[dep_path] = []
                packed[dep_path].append(sym)
                used_budget += sym_size
            else:
                envelope.truncated = True
                break

        envelope.dependency_contracts = packed
        envelope.total_chars = target_size + used_budget + overhead

        return envelope


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def main():
    """CLI interface for testing the context mapper."""
    import argparse

    parser = argparse.ArgumentParser(description='AIM-OS Context Mapper')
    parser.add_argument('command', choices=['envelope', 'extract', 'status'],
                       help='Command to execute')
    parser.add_argument('--target', '-t', help='Target file path')
    parser.add_argument('--budget', '-b', type=int, default=32000,
                       help='Character budget (default: 32000)')
    parser.add_argument('--workspace', '-w', default='',
                       help='Workspace root')

    args = parser.parse_args()

    workspace = args.workspace or os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', '..')
    )
    mapper = ContextMapper(workspace)

    if args.command == 'status':
        import json
        print(json.dumps(mapper.status(), indent=2))

    elif args.command == 'extract':
        if not args.target:
            print("ERROR: --target required for extract")
            sys.exit(1)

        result = mapper.extract_contracts(args.target)
        print(f"File: {result.path}")
        print(f"Parse mode: {result.parse_mode}")
        print(f"Imports: {len(result.imports)}")
        print(f"Exports: {len(result.exports)}")
        print()

        if result.imports:
            print("── Imports ──")
            for imp in result.imports:
                status = '(stdlib)' if imp.is_stdlib else '(external)' if imp.is_external else ''
                print(f"  {imp.module_path} -> [{', '.join(imp.imported_names[:5])}] {status}")
            print()

        if result.exports:
            print("── Exports ──")
            for exp in result.exports:
                decs = ' '.join(exp.decorators) + ' ' if exp.decorators else ''
                print(f"  [{exp.kind}] {decs}{exp.signature}")
                if exp.methods:
                    for m in exp.methods[:5]:
                        print(f"      {m}")
                    if len(exp.methods) > 5:
                        print(f"      ... +{len(exp.methods) - 5} more")
            print()

    elif args.command == 'envelope':
        if not args.target:
            print("ERROR: --target required for envelope")
            sys.exit(1)

        t0 = time.time()
        envelope = mapper.build_envelope(args.target, budget_chars=args.budget)
        elapsed = (time.time() - t0) * 1000

        print(f"── Envelope Stats ({elapsed:.1f}ms) ──")
        import json
        print(json.dumps(envelope.stats, indent=2))
        print()
        print(f"── Envelope ({len(envelope.to_string())} chars) ──")
        # Print first 2000 chars to avoid flooding terminal
        output = envelope.to_string()
        if len(output) > 2000:
            print(output[:2000])
            print(f"\n... [{len(output) - 2000} more chars]")
        else:
            print(output)


if __name__ == '__main__':
    main()
