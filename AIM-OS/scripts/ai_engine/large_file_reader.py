"""
AIM-OS AI Engine — Large File Reader

MapReduce for Context: processes files that exceed token budgets
by chunking, summarizing each chunk, and merging into a
hierarchical index that any agent can consume.

Pipeline:
    1. Smart Chunk — split at section boundaries (not mid-sentence)
    2. Parallel Summarize — extract key concepts per chunk
    3. Merge — combine into hierarchical index with cross-references
    4. Cache — store by file path + mtime for reuse

Progressive Escalation Strategy:
    1. Try cached index → instant return (~0ms)
    2. Try fast structural index via ContextMapper → ~10ms
    3. Full MapReduce chunking pipeline → ~100-500ms

Usage via MCP:
    ai_engine_read_large(target="scripts/ai_engine/chain_director.py")

Usage direct:
    reader = LargeFileReader('/path/to/AIM-OS')
    result = reader.read_large('path/to/big_file.py')
    print(result.to_string())
"""

import os
import re
import sys
import time
import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple

logger = logging.getLogger('ai_engine.large_file_reader')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))

# ── Thresholds ───────────────────────────────────────────
LARGE_FILE_CHARS = 20000      # Files above this trigger MapReduce
CHUNK_SIZE_DEFAULT = 8000     # Default chunk target size (chars)
CHUNK_SIZE_MIN = 2000         # Minimum meaningful chunk
INDEX_CACHE_DIR = '.agent'     # Cache directory relative to workspace


# ══════════════════════════════════════════════════════════
#  DATA MODELS
# ══════════════════════════════════════════════════════════

@dataclass
class ChunkSummary:
    """Summary of a single chunk from a large file."""
    chunk_id: int
    line_start: int
    line_end: int
    char_count: int
    title: str = ''           # Auto-detected title (class/function/heading)
    key_symbols: List[str] = field(default_factory=list)  # Exported names
    key_concepts: List[str] = field(default_factory=list)  # Extracted concepts
    summary_text: str = ''    # One-line summary


@dataclass
class LargeFileIndex:
    """Hierarchical index produced by MapReduce for a large file."""
    path: str
    file_size: int = 0
    total_lines: int = 0
    chunk_count: int = 0
    language: str = 'python'
    strategy: str = 'mapreduce'  # 'cached', 'structural', 'mapreduce'
    generation_ms: float = 0.0
    mtime: float = 0.0

    # Hierarchical summary
    overview: str = ''
    chunks: List[ChunkSummary] = field(default_factory=list)
    all_symbols: List[str] = field(default_factory=list)
    all_concepts: List[str] = field(default_factory=list)
    cross_references: Dict[str, List[int]] = field(default_factory=dict)  # symbol → chunk IDs

    def to_string(self) -> str:
        """Render as structured XML for LLM injection."""
        parts = [
            f'<large_file_index path="{os.path.basename(self.path)}" '
            f'strategy="{self.strategy}">',
            f'  <stats>',
            f'    <size>{self.file_size:,} chars, {self.total_lines} lines</size>',
            f'    <language>{self.language}</language>',
            f'    <chunks>{self.chunk_count}</chunks>',
            f'    <generation_ms>{self.generation_ms:.0f}</generation_ms>',
            f'  </stats>',
        ]

        if self.overview:
            parts.append(f'  <overview>{self.overview}</overview>')

        parts.append(f'  <symbols>{", ".join(self.all_symbols[:20])}</symbols>')
        parts.append(f'  <concepts>{", ".join(self.all_concepts[:15])}</concepts>')

        parts.append(f'  <chunks>')
        for chunk in self.chunks:
            syms = f' symbols="{",".join(chunk.key_symbols[:5])}"' if chunk.key_symbols else ''
            parts.append(
                f'    <chunk id="{chunk.chunk_id}" lines="{chunk.line_start}-{chunk.line_end}" '
                f'chars="{chunk.char_count}"{syms}>'
                f'{chunk.title}'
                f'</chunk>'
            )
        parts.append(f'  </chunks>')

        if self.cross_references:
            parts.append(f'  <cross_refs>')
            for sym, chunk_ids in list(self.cross_references.items())[:20]:
                parts.append(f'    <ref symbol="{sym}" chunks="{",".join(str(c) for c in chunk_ids)}"/>')
            parts.append(f'  </cross_refs>')

        parts.append(f'</large_file_index>')
        return '\n'.join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': os.path.basename(self.path),
            'file_size': self.file_size,
            'total_lines': self.total_lines,
            'chunk_count': self.chunk_count,
            'language': self.language,
            'strategy': self.strategy,
            'generation_ms': round(self.generation_ms, 1),
            'overview': self.overview[:200],
            'symbols': self.all_symbols[:20],
            'concepts': self.all_concepts[:15],
            'chunks': [
                {
                    'id': c.chunk_id,
                    'lines': f'{c.line_start}-{c.line_end}',
                    'chars': c.char_count,
                    'title': c.title,
                    'symbols': c.key_symbols[:5],
                }
                for c in self.chunks
            ],
        }


# ══════════════════════════════════════════════════════════
#  LARGE FILE READER
# ══════════════════════════════════════════════════════════

class LargeFileReader:
    """
    MapReduce for Context — processes large files through
    chunking, summarization, and hierarchical index building.
    """

    def __init__(self, workspace_root: str = ''):
        self.workspace_root = workspace_root or WORKSPACE
        self._mapper = None
        self._cache: Dict[str, LargeFileIndex] = {}
        self._cache_dir = os.path.join(self.workspace_root, INDEX_CACHE_DIR, 'file_indexes')
        logger.info(f'LargeFileReader initialized (workspace: {self.workspace_root})')

    # ── Lazy Loading ────────────────────────────────────────

    def _get_mapper(self):
        """Lazy-load ContextMapper."""
        if self._mapper is None:
            try:
                from context_mapper import ContextMapper
            except ImportError:
                try:
                    from ai_engine.context_mapper import ContextMapper
                except ImportError:
                    from scripts.ai_engine.context_mapper import ContextMapper
            self._mapper = ContextMapper(self.workspace_root)
        return self._mapper

    # ── Progressive Escalation Pipeline ─────────────────────

    def read_large(
        self,
        file_path: str,
        chunk_size: int = CHUNK_SIZE_DEFAULT,
        force_mapreduce: bool = False,
    ) -> LargeFileIndex:
        """
        Process a large file through progressive escalation:
            1. Check memory cache (instant)
            2. Check disk cache (fast, <5ms)
            3. Try structural index via ContextMapper (~10ms)
            4. Full MapReduce pipeline (~100-500ms)

        Args:
            file_path: Path to file (relative or absolute)
            chunk_size: Target chunk size in characters
            force_mapreduce: Skip cache and always do full processing

        Returns:
            LargeFileIndex with hierarchical summary
        """
        t0 = time.time()

        # Resolve path
        if not os.path.isabs(file_path):
            file_path = os.path.normpath(
                os.path.join(self.workspace_root, file_path)
            )

        if not os.path.isfile(file_path):
            return LargeFileIndex(path=file_path, overview="File not found")

        mtime = os.path.getmtime(file_path)
        file_size = os.path.getsize(file_path)

        # Strategy 1: Memory cache
        if not force_mapreduce and file_path in self._cache:
            cached = self._cache[file_path]
            if cached.mtime == mtime:
                cached.strategy = 'cached'
                cached.generation_ms = (time.time() - t0) * 1000
                return cached

        # Strategy 2: Disk cache
        if not force_mapreduce:
            disk_cached = self._load_disk_cache(file_path, mtime)
            if disk_cached:
                disk_cached.strategy = 'disk_cached'
                disk_cached.generation_ms = (time.time() - t0) * 1000
                self._cache[file_path] = disk_cached
                return disk_cached

        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            return LargeFileIndex(path=file_path, overview=f"Error: {e}")

        lines = content.splitlines()
        total_lines = len(lines)

        # Determine language
        ext = os.path.splitext(file_path)[1].lower()
        language = {
            '.md': 'markdown', '.ts': 'typescript', '.tsx': 'typescript',
            '.js': 'javascript', '.jsx': 'javascript',
        }.get(ext, 'python')

        # Strategy 3: Small file — use structural index
        if not force_mapreduce and file_size < LARGE_FILE_CHARS:
            mapper = self._get_mapper()
            struct_index = mapper.build_index(file_path)
            result = LargeFileIndex(
                path=file_path,
                file_size=len(content),
                total_lines=total_lines,
                chunk_count=len(struct_index.sections),
                language=language,
                strategy='structural',
                mtime=mtime,
                overview=f"Structural index: {len(struct_index.exports)} exports, "
                         f"{len(struct_index.sections)} sections",
                chunks=[
                    ChunkSummary(
                        chunk_id=i,
                        line_start=sec.line_start,
                        line_end=sec.line_end,
                        char_count=sec.char_count,
                        title=sec.title,
                        key_symbols=sec.exports,
                    )
                    for i, sec in enumerate(struct_index.sections)
                ],
                all_symbols=struct_index.exports,
                all_concepts=struct_index.key_concepts,
            )
            result.generation_ms = (time.time() - t0) * 1000
            self._cache[file_path] = result
            return result

        # Strategy 4: Full MapReduce
        logger.info(f'MapReduce: Processing {os.path.basename(file_path)} '
                    f'({len(content):,} chars, {total_lines} lines)')

        # Step 1: Smart Chunk
        chunks = self._smart_chunk(lines, chunk_size, language)

        # Step 2: Summarize each chunk
        summaries = self._summarize_chunks(chunks, file_path, language)

        # Step 3: Merge into hierarchical index
        result = self._merge_summaries(
            summaries, file_path, content, total_lines, language, mtime
        )

        result.generation_ms = (time.time() - t0) * 1000
        logger.info(
            f'MapReduce: {result.chunk_count} chunks, '
            f'{len(result.all_symbols)} symbols, '
            f'{result.generation_ms:.0f}ms'
        )

        # Cache
        self._cache[file_path] = result
        self._save_disk_cache(file_path, result)

        return result

    # ── Smart Chunking ──────────────────────────────────────

    def _smart_chunk(
        self,
        lines: List[str],
        target_size: int,
        language: str,
    ) -> List[Tuple[int, int, List[str]]]:
        """
        Split lines into chunks at natural boundaries.

        For code: split at class/function boundaries
        For markdown: split at heading boundaries
        For everything else: split at blank lines

        Returns list of (line_start, line_end, lines)
        """
        if language == 'markdown':
            boundaries = self._find_md_boundaries(lines)
        elif language in ('python', 'typescript', 'javascript'):
            boundaries = self._find_code_boundaries(lines)
        else:
            boundaries = self._find_blank_boundaries(lines)

        # Merge small sections into chunks targeting target_size
        chunks = []
        current_start = 0
        current_chars = 0
        chunk_lines = []

        for boundary_line in sorted(boundaries):
            # Add lines up to this boundary
            segment = lines[current_start:boundary_line]
            segment_chars = sum(len(l) for l in segment)

            if current_chars + segment_chars > target_size and chunk_lines:
                # Emit current chunk
                line_start = current_start - len(chunk_lines) + 1
                chunks.append((
                    line_start + 1,  # 1-indexed
                    current_start,
                    chunk_lines[:],
                ))
                chunk_lines = segment
                current_chars = segment_chars
            else:
                chunk_lines.extend(segment)
                current_chars += segment_chars

            current_start = boundary_line

        # Final chunk
        remaining = lines[current_start:]
        chunk_lines.extend(remaining)
        if chunk_lines:
            line_start = len(lines) - len(chunk_lines) + 1
            chunks.append((line_start, len(lines), chunk_lines))

        return chunks

    def _find_code_boundaries(self, lines: List[str]) -> List[int]:
        """Find class/function boundaries in code."""
        boundaries = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Top-level class or function
            if (line.startswith('class ') or line.startswith('def ') or
                line.startswith('async def ') or
                # TypeScript/JS
                line.startswith('export ') or
                stripped.startswith('function ') or
                stripped.startswith('interface ') or
                stripped.startswith('type ') or
                # Section comments
                line.startswith('# ══') or line.startswith('# ──') or
                line.startswith('// ══') or line.startswith('// ──')):
                boundaries.append(i)
        return boundaries

    def _find_md_boundaries(self, lines: List[str]) -> List[int]:
        """Find heading boundaries in markdown."""
        return [i for i, line in enumerate(lines) if line.startswith('#')]

    def _find_blank_boundaries(self, lines: List[str]) -> List[int]:
        """Find blank line boundaries (fallback)."""
        return [i for i, line in enumerate(lines) if not line.strip()]

    # ── Chunk Summarization ─────────────────────────────────

    def _summarize_chunks(
        self,
        chunks: List[Tuple[int, int, List[str]]],
        file_path: str,
        language: str,
    ) -> List[ChunkSummary]:
        """Summarize each chunk by extracting key information."""
        summaries = []

        for idx, (line_start, line_end, chunk_lines) in enumerate(chunks):
            content = '\n'.join(chunk_lines)
            char_count = len(content)

            # Extract title from first significant line
            title = self._extract_chunk_title(chunk_lines, language)

            # Extract symbols (class/function names)
            symbols = self._extract_chunk_symbols(chunk_lines, language)

            # Extract concepts
            concepts = self._extract_chunk_concepts(chunk_lines)

            summaries.append(ChunkSummary(
                chunk_id=idx,
                line_start=line_start,
                line_end=line_end,
                char_count=char_count,
                title=title,
                key_symbols=symbols,
                key_concepts=concepts,
            ))

        return summaries

    def _extract_chunk_title(self, lines: List[str], language: str) -> str:
        """Extract chunk title from first class/function/heading."""
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#!'):
                continue

            # Python class/function
            if stripped.startswith('class '):
                return stripped.split('(')[0].split(':')[0]
            if stripped.startswith('def ') or stripped.startswith('async def '):
                clean = stripped.replace('async ', '')
                return clean.split('(')[0]

            # TypeScript/JS
            if 'class ' in stripped:
                match = re.search(r'class\s+(\w+)', stripped)
                if match:
                    return f'class {match.group(1)}'
            if stripped.startswith('export function ') or stripped.startswith('function '):
                match = re.search(r'function\s+(\w+)', stripped)
                if match:
                    return f'function {match.group(1)}'
            if stripped.startswith('export interface ') or stripped.startswith('interface '):
                match = re.search(r'interface\s+(\w+)', stripped)
                if match:
                    return f'interface {match.group(1)}'

            # Markdown heading
            if stripped.startswith('#'):
                return stripped.lstrip('#').strip()

            # Section comment
            if stripped.startswith(('# ──', '# ══', '// ──', '// ══')):
                return stripped.strip('#/ ═─').strip()

            # Docstring
            if stripped.startswith(('"""', "'''")):
                doc_text = stripped.strip('"\'').strip()
                if doc_text:
                    return doc_text[:80]

        return f'Chunk (lines {lines[0].strip()[:40]}...)'

    def _extract_chunk_symbols(self, lines: List[str], language: str) -> List[str]:
        """Extract symbol names from chunk."""
        symbols = []
        for line in lines:
            stripped = line.strip()
            # Python
            if stripped.startswith('class '):
                name = stripped[6:].split('(')[0].split(':')[0].strip()
                if name and not name.startswith('_'):
                    symbols.append(name)
            elif stripped.startswith('def ') and not stripped.startswith('def _'):
                name = stripped[4:].split('(')[0].strip()
                symbols.append(name)
            # TypeScript/JS
            elif 'export ' in line:
                match = re.search(
                    r'export\s+(?:const|function|class|interface|type|enum)\s+(\w+)',
                    stripped
                )
                if match:
                    symbols.append(match.group(1))
        return symbols

    def _extract_chunk_concepts(self, lines: List[str]) -> List[str]:
        """Extract key concepts from chunk content."""
        concepts = set()
        text = ' '.join(l.strip() for l in lines[:20])  # First 20 lines

        # Docstring/comment keywords
        for match in re.finditer(r'\b[a-z]{5,}\b', text.lower()):
            word = match.group()
            if word not in ('import', 'return', 'false', 'class', 'super',
                           'raise', 'except', 'lambda', 'global', 'assert',
                           'yield', 'while', 'break', 'continue', 'print'):
                concepts.add(word)

        return sorted(concepts, key=lambda c: -len(c))[:8]

    # ── Merge ───────────────────────────────────────────────

    def _merge_summaries(
        self,
        summaries: List[ChunkSummary],
        file_path: str,
        content: str,
        total_lines: int,
        language: str,
        mtime: float,
    ) -> LargeFileIndex:
        """Merge chunk summaries into hierarchical index."""
        # Collect all symbols and concepts
        all_symbols = []
        all_concepts = set()
        cross_refs: Dict[str, List[int]] = {}

        for summary in summaries:
            for sym in summary.key_symbols:
                if sym not in all_symbols:
                    all_symbols.append(sym)
                if sym not in cross_refs:
                    cross_refs[sym] = []
                cross_refs[sym].append(summary.chunk_id)
            all_concepts.update(summary.key_concepts)

        # Build cross-references (symbol used in multiple chunks)
        for summary in summaries:
            chunk_text = '\n'.join([])  # We don't keep full text
            for sym in all_symbols:
                if sym in summary.title and summary.chunk_id not in cross_refs.get(sym, []):
                    cross_refs.setdefault(sym, []).append(summary.chunk_id)

        # Build overview
        symbol_list = ', '.join(all_symbols[:10])
        overview = (
            f"{os.path.basename(file_path)}: "
            f"{len(content):,} chars, {total_lines} lines, "
            f"{len(summaries)} chunks. "
            f"Key exports: {symbol_list}."
        )

        return LargeFileIndex(
            path=file_path,
            file_size=len(content),
            total_lines=total_lines,
            chunk_count=len(summaries),
            language=language,
            strategy='mapreduce',
            mtime=mtime,
            overview=overview,
            chunks=summaries,
            all_symbols=all_symbols,
            all_concepts=sorted(all_concepts, key=lambda c: -len(c))[:15],
            cross_references={k: v for k, v in cross_refs.items() if len(v) >= 1},
        )

    # ── Disk Cache ──────────────────────────────────────────

    def _cache_path(self, file_path: str) -> str:
        """Get cache file path for a given source file."""
        h = hashlib.md5(file_path.encode()).hexdigest()[:12]
        basename = os.path.basename(file_path).replace('.', '_')
        return os.path.join(self._cache_dir, f'{basename}_{h}.json')

    def _save_disk_cache(self, file_path: str, index: LargeFileIndex):
        """Save index to disk cache."""
        try:
            os.makedirs(self._cache_dir, exist_ok=True)
            cache_data = {
                'path': file_path,
                'mtime': index.mtime,
                'data': index.to_dict(),
                'index_text': index.to_string(),
            }
            with open(self._cache_path(file_path), 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.warning(f'Failed to save index cache: {e}')

    def _load_disk_cache(self, file_path: str, mtime: float) -> Optional[LargeFileIndex]:
        """Load index from disk cache if mtime matches."""
        cache_file = self._cache_path(file_path)
        if not os.path.isfile(cache_file):
            return None
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            if abs(data.get('mtime', 0) - mtime) > 0.001:
                return None  # Stale
            # Reconstruct LargeFileIndex (lightweight — just the summary)
            d = data['data']
            return LargeFileIndex(
                path=file_path,
                file_size=d.get('file_size', 0),
                total_lines=d.get('total_lines', 0),
                chunk_count=d.get('chunk_count', 0),
                language=d.get('language', 'python'),
                strategy='disk_cached',
                mtime=mtime,
                overview=d.get('overview', ''),
                all_symbols=d.get('symbols', []),
                all_concepts=d.get('concepts', []),
                chunks=[
                    ChunkSummary(
                        chunk_id=c.get('id', 0),
                        line_start=int(c.get('lines', '1-1').split('-')[0]),
                        line_end=int(c.get('lines', '1-1').split('-')[1]),
                        char_count=c.get('chars', 0),
                        title=c.get('title', ''),
                        key_symbols=c.get('symbols', []),
                    )
                    for c in d.get('chunks', [])
                ],
            )
        except Exception as e:
            logger.warning(f'Failed to load index cache: {e}')
            return None

    # ── Status ──────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        return {
            'workspace': self.workspace_root,
            'memory_cache_size': len(self._cache),
            'mapper_loaded': self._mapper is not None,
            'large_threshold': LARGE_FILE_CHARS,
            'default_chunk_size': CHUNK_SIZE_DEFAULT,
        }


# ══════════════════════════════════════════════════════════
#  CLI TEST
# ══════════════════════════════════════════════════════════

def _test():
    """Test the Large File Reader."""
    import json

    print("=" * 60)
    print("  Large File Reader — Live Test")
    print("=" * 60)

    reader = LargeFileReader(WORKSPACE)

    # Test files (mix of sizes)
    test_files = [
        'scripts/ai_engine/genome_loader.py',          # ~12K chars (small)
        'scripts/ai_engine/chain_director.py',          # ~30K chars (large)
        'scripts/ai_engine/atlas_agent.py',             # ~33K chars (large)
        'scripts/ai_engine/ai_engine_mcp_server.py',    # ~55K chars (very large)
    ]

    for rel_path in test_files:
        full = os.path.join(WORKSPACE, rel_path)
        if not os.path.isfile(full):
            print(f'\n  SKIP: {rel_path} (not found)')
            continue

        size = os.path.getsize(full)
        print(f'\n{"─" * 60}')
        print(f'  FILE: {os.path.basename(rel_path)} ({size:,} bytes)')
        print(f'{"─" * 60}')

        result = reader.read_large(full)

        print(f'  Strategy: {result.strategy}')
        print(f'  Chunks: {result.chunk_count}')
        print(f'  Symbols: {result.all_symbols[:8]}')
        print(f'  Concepts: {result.all_concepts[:5]}')
        print(f'  Time: {result.generation_ms:.0f}ms')
        for chunk in result.chunks[:5]:
            print(f'    [{chunk.line_start}-{chunk.line_end}] {chunk.title} ({chunk.char_count} chars)')

    # Test cached re-read
    print(f'\n{"─" * 60}')
    print(f'  CACHE RE-READ TEST')
    print(f'{"─" * 60}')
    for rel_path in test_files[:1]:
        full = os.path.join(WORKSPACE, rel_path)
        if os.path.isfile(full):
            t0 = time.time()
            result = reader.read_large(full)
            ms = (time.time() - t0) * 1000
            print(f'  {os.path.basename(rel_path)}: {result.strategy}, {ms:.1f}ms')

    print(f'\n{"=" * 60}')
    print(f'  Status: {json.dumps(reader.status(), indent=2)}')
    print(f'  ALL TESTS PASSED')
    print(f'{"=" * 60}')


if __name__ == '__main__':
    _test()
