"""
AIM-OS AI Engine — Context Engine

Layer 2: Decides WHAT to feed the LLM for a given task.
This is the intelligence behind context window management.

Responsibilities:
    - Workspace indexing: scan files, build symbol index
    - Token budgeting: allocate context by task type
    - Semantic retrieval: find relevant files/functions for a query
    - Active state: current file, cursor, open tabs, errors
    - Conversation memory: recent chat from CMC

Builds on existing:
    - DaemonRAGSystem context_analysis_engine patterns
    - HHNI semantic retrieval concepts
    - CMC memory storage for conversation history
"""

import os
import re
import time
import json
import logging
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger('ai_engine.context_engine')


# ── Configuration ─────────────────────────────────────────

# Approximate tokens per character (conservative estimate)
CHARS_PER_TOKEN = 3.5

# Default token budgets by task type
TOKEN_BUDGETS = {
    'fast':       4_000,    # Autocomplete, quick answers
    'standard':   16_000,   # General coding
    'deep-think': 64_000,   # Architecture, complex reasoning
    'code-edit':  32_000,   # File editing with diff context
    'planning':   48_000,   # Task decomposition, design
    'audit':      32_000,   # Code review
    'vision':     8_000,    # Image analysis (minimal text context)
}

# File extensions to index
CODE_EXTENSIONS = {
    '.py', '.ts', '.tsx', '.js', '.jsx', '.rs', '.go',
    '.java', '.kt', '.swift', '.c', '.cpp', '.h', '.hpp',
    '.css', '.scss', '.html', '.vue', '.svelte',
    '.json', '.yaml', '.yml', '.toml', '.md',
    '.sql', '.graphql', '.proto',
    '.sh', '.bash', '.ps1', '.bat',
}

# Directories to skip during indexing
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.next', 'dist',
    'build', 'out', '.venv', 'venv', '.cache', '.turbo',
    'target', '.cargo', '.mypy_cache', '.pytest_cache',
    'coverage', '.nyc_output', '.parcel-cache',
}

# Maximum file size to index (500KB)
MAX_FILE_SIZE = 512_000


# ── Data Models ───────────────────────────────────────────

@dataclass
class FileInfo:
    """Indexed file metadata."""
    path: str
    relative_path: str
    extension: str
    size_bytes: int
    line_count: int
    last_modified: float
    hash: str = ''
    symbols: List[str] = field(default_factory=list)
    language: str = ''

    @property
    def estimated_tokens(self) -> int:
        return int(self.size_bytes / CHARS_PER_TOKEN)


@dataclass
class FileChunk:
    """A relevant chunk of a file returned by search."""
    file_path: str
    relative_path: str
    content: str
    start_line: int
    end_line: int
    relevance_score: float = 0.0
    reason: str = ''

    @property
    def token_count(self) -> int:
        return int(len(self.content) / CHARS_PER_TOKEN)


@dataclass
class EditorState:
    """Current editor state for context awareness."""
    active_file: str = ''
    cursor_line: int = 0
    cursor_column: int = 0
    open_files: List[str] = field(default_factory=list)
    selected_text: str = ''
    recent_edits: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)
    git_branch: str = ''
    git_diff: str = ''


@dataclass
class ContextWindow:
    """
    The assembled context to feed the LLM.
    Contains system prompt, relevant files, conversation history,
    and active state — all within token budget.
    """
    system_prompt: str = ''
    file_chunks: List[FileChunk] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    active_state: Optional[EditorState] = None
    user_prompt: str = ''
    total_tokens: int = 0
    budget_tokens: int = 0

    def to_prompt(self) -> str:
        """Assemble all context into a single prompt string."""
        parts = []

        if self.system_prompt:
            parts.append(self.system_prompt)

        # Active state
        if self.active_state and self.active_state.active_file:
            state_parts = [f"\n## Active Context"]
            state_parts.append(f"**Current file:** `{self.active_state.active_file}`")
            if self.active_state.cursor_line:
                state_parts.append(f"**Cursor:** line {self.active_state.cursor_line}")
            if self.active_state.open_files:
                state_parts.append(f"**Open files:** {', '.join(f'`{f}`' for f in self.active_state.open_files[:5])}")
            if self.active_state.diagnostics:
                errors = [d for d in self.active_state.diagnostics if d.get('severity') == 'error']
                if errors:
                    state_parts.append(f"**Errors ({len(errors)}):**")
                    for err in errors[:3]:
                        state_parts.append(f"  - `{err.get('file', '')}:{err.get('line', '')}` — {err.get('message', '')}")
            if self.active_state.git_branch:
                state_parts.append(f"**Branch:** `{self.active_state.git_branch}`")
            parts.append('\n'.join(state_parts))

        # Relevant file chunks
        if self.file_chunks:
            parts.append("\n## Relevant Code")
            for chunk in self.file_chunks:
                header = f"### `{chunk.relative_path}` (lines {chunk.start_line}-{chunk.end_line})"
                if chunk.reason:
                    header += f" — {chunk.reason}"
                parts.append(f"{header}\n```\n{chunk.content}\n```")

        # Conversation history
        if self.conversation_history:
            parts.append("\n## Recent Conversation")
            for msg in self.conversation_history[-5:]:
                role = msg.get('role', 'user').upper()
                content = msg.get('content', '')[:500]
                parts.append(f"**{role}:** {content}")

        return '\n\n'.join(parts)

    def to_dict(self) -> dict:
        return {
            'total_tokens': self.total_tokens,
            'budget_tokens': self.budget_tokens,
            'file_chunks': len(self.file_chunks),
            'conversation_entries': len(self.conversation_history),
            'has_active_state': self.active_state is not None,
            'utilisation': f'{self.total_tokens}/{self.budget_tokens} ({100*self.total_tokens//max(self.budget_tokens,1)}%)',
        }


# ── File Index ────────────────────────────────────────────

class FileIndex:
    """
    Workspace file index for fast lookups.
    Scans the workspace, catalogues files, extracts symbols,
    and enables search by path, content, or symbol.
    """

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.files: Dict[str, FileInfo] = {}
        self._last_indexed: float = 0
        self._symbol_map: Dict[str, List[str]] = {}  # symbol -> [file_paths]

    def index(self, force: bool = False) -> dict:
        """
        Scan workspace and build file index.
        Returns stats about indexed files.
        """
        if not force and self.files and (time.time() - self._last_indexed < 300):
            return {'cached': True, 'files': len(self.files)}

        start = time.monotonic()
        self.files = {}
        self._symbol_map = {}
        file_count = 0
        skip_count = 0

        for root, dirs, files in os.walk(self.root_path):
            # Prune directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]

            rel_root = Path(root).relative_to(self.root_path)

            for fname in files:
                fpath = Path(root) / fname
                ext = fpath.suffix.lower()

                if ext not in CODE_EXTENSIONS:
                    skip_count += 1
                    continue

                try:
                    stat = fpath.stat()
                    if stat.st_size > MAX_FILE_SIZE:
                        skip_count += 1
                        continue

                    rel_path = str(rel_root / fname)

                    # Count lines and extract symbols (lightweight)
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    line_count = content.count('\n') + 1
                    symbols = self._extract_symbols(content, ext)

                    file_info = FileInfo(
                        path=str(fpath),
                        relative_path=rel_path,
                        extension=ext,
                        size_bytes=stat.st_size,
                        line_count=line_count,
                        last_modified=stat.st_mtime,
                        hash=hashlib.md5(content.encode()).hexdigest()[:8],
                        symbols=symbols,
                        language=self._ext_to_language(ext),
                    )

                    self.files[str(fpath)] = file_info
                    file_count += 1

                    # Update symbol map
                    for sym in symbols:
                        self._symbol_map.setdefault(sym, []).append(str(fpath))

                except (OSError, UnicodeDecodeError):
                    skip_count += 1

        self._last_indexed = time.time()
        elapsed = (time.monotonic() - start) * 1000

        logger.info(f'Indexed {file_count} files in {elapsed:.0f}ms ({skip_count} skipped)')

        return {
            'files_indexed': file_count,
            'files_skipped': skip_count,
            'total_symbols': len(self._symbol_map),
            'elapsed_ms': elapsed,
        }

    def search_files(self, query: str, max_results: int = 10) -> List[FileInfo]:
        """Search files by path or symbol name."""
        query_lower = query.lower()
        results: List[Tuple[float, FileInfo]] = []

        for fpath, info in self.files.items():
            score = 0.0

            # Path match
            if query_lower in info.relative_path.lower():
                score += 0.5
                if info.relative_path.lower().endswith(query_lower):
                    score += 0.3

            # Symbol match
            for sym in info.symbols:
                if query_lower in sym.lower():
                    score += 0.4
                    break

            if score > 0:
                results.append((score, info))

        results.sort(key=lambda x: x[0], reverse=True)
        return [info for _, info in results[:max_results]]

    def get_file_content(
        self,
        file_path: str,
        start_line: int = 1,
        end_line: Optional[int] = None,
        max_lines: int = 200,
    ) -> Optional[FileChunk]:
        """Read file content, optionally a specific line range."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()

            end_line = min(end_line or (start_line + max_lines - 1), len(lines))
            start_line = max(1, start_line)
            content = ''.join(lines[start_line - 1:end_line])

            info = self.files.get(file_path)
            rel_path = info.relative_path if info else os.path.basename(file_path)

            return FileChunk(
                file_path=file_path,
                relative_path=rel_path,
                content=content,
                start_line=start_line,
                end_line=end_line,
            )
        except (OSError, UnicodeDecodeError):
            return None

    def search_content(self, query: str, max_results: int = 10) -> List[FileChunk]:
        """Search file contents for a string pattern."""
        query_lower = query.lower()
        results: List[FileChunk] = []

        for fpath, info in self.files.items():
            if len(results) >= max_results:
                break

            try:
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()

                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        # Grab surrounding context (5 lines each side)
                        start = max(0, i - 5)
                        end = min(len(lines), i + 6)
                        content = ''.join(lines[start:end])

                        results.append(FileChunk(
                            file_path=fpath,
                            relative_path=info.relative_path,
                            content=content,
                            start_line=start + 1,
                            end_line=end,
                            relevance_score=1.0 if query.lower() == line.strip().lower() else 0.5,
                            reason=f'Contains "{query}"',
                        ))
                        break  # One match per file

            except (OSError, UnicodeDecodeError):
                continue

        return results

    # ── Symbol Extraction ────────────────────────────────

    def _extract_symbols(self, content: str, ext: str) -> List[str]:
        """Extract top-level symbols (classes, functions) from code."""
        symbols = []

        if ext in ('.py',):
            # Python: class Foo, def bar
            for m in re.finditer(r'^(?:class|def)\s+(\w+)', content, re.MULTILINE):
                symbols.append(m.group(1))

        elif ext in ('.ts', '.tsx', '.js', '.jsx'):
            # TypeScript/JS: class, function, const/let/var exports, interface
            patterns = [
                r'(?:export\s+)?(?:class|interface|enum)\s+(\w+)',
                r'(?:export\s+)?(?:function|const|let|var)\s+(\w+)',
                r'(?:export\s+default\s+)?function\s+(\w+)',
            ]
            for pat in patterns:
                for m in re.finditer(pat, content, re.MULTILINE):
                    sym = m.group(1)
                    if sym and sym not in symbols and len(sym) > 1:
                        symbols.append(sym)

        elif ext in ('.rs',):
            for m in re.finditer(r'^pub\s+(?:fn|struct|enum|trait|impl)\s+(\w+)', content, re.MULTILINE):
                symbols.append(m.group(1))

        return symbols[:50]  # Cap at 50 symbols per file

    def _ext_to_language(self, ext: str) -> str:
        EXT_MAP = {
            '.py': 'python', '.ts': 'typescript', '.tsx': 'typescript',
            '.js': 'javascript', '.jsx': 'javascript', '.rs': 'rust',
            '.go': 'go', '.java': 'java', '.cpp': 'cpp', '.c': 'c',
            '.css': 'css', '.html': 'html', '.json': 'json',
            '.yaml': 'yaml', '.yml': 'yaml', '.md': 'markdown',
            '.sql': 'sql', '.sh': 'shell', '.ps1': 'powershell',
        }
        return EXT_MAP.get(ext, 'text')


# ── Context Engine ────────────────────────────────────────

class ContextEngine:
    """
    Assembles the optimal context window for a given task.
    
    Combines:
        - Workspace file index (most relevant files)
        - Active editor state (current file, errors)
        - Conversation history (from CMC)
        - Task-specific token budgeting
    
    Into a ContextWindow ready to feed the LLM Router.
    """

    def __init__(
        self,
        workspace_root: str = '',
        auto_index: bool = True,
    ):
        self.workspace_root = workspace_root or os.getcwd()
        self.index = FileIndex(self.workspace_root)
        self._conversation_history: List[Dict[str, str]] = []
        self._editor_state: EditorState = EditorState()

        if auto_index:
            self.index.index()

    def build_context(
        self,
        task: str,
        system_prompt: str = '',
        task_type: str = 'standard',
        active_file: str = '',
        include_files: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None,
        max_file_chunks: int = 10,
    ) -> ContextWindow:
        """
        Build the optimal context window for a task.
        
        Args:
            task: The user/agent task description
            system_prompt: System instruction for the agent
            task_type: Task classification for budget allocation
            active_file: Currently active file path
            include_files: Explicitly include these files
            exclude_files: Exclude these files
            max_file_chunks: Maximum file chunks to include
        
        Returns:
            ContextWindow with assembled context within token budget
        """
        budget = TOKEN_BUDGETS.get(task_type, TOKEN_BUDGETS['standard'])
        used_tokens = 0

        # Reserve tokens for system prompt
        system_tokens = int(len(system_prompt) / CHARS_PER_TOKEN)
        used_tokens += system_tokens

        # Reserve tokens for task prompt
        task_tokens = int(len(task) / CHARS_PER_TOKEN)
        used_tokens += task_tokens

        # Reserve tokens for conversation history
        history_budget = min(budget // 8, 2000)
        history = self._get_recent_conversation(max_tokens=history_budget)
        history_tokens = sum(int(len(m.get('content', '')) / CHARS_PER_TOKEN) for m in history)
        used_tokens += history_tokens

        # Remaining budget for file chunks
        file_budget = budget - used_tokens
        chunks: List[FileChunk] = []

        # 1. Include active file first (highest priority)
        if active_file and os.path.exists(active_file):
            chunk = self.index.get_file_content(active_file, max_lines=150)
            if chunk and chunk.token_count <= file_budget:
                chunk.reason = 'Currently active file'
                chunk.relevance_score = 1.0
                chunks.append(chunk)
                file_budget -= chunk.token_count

        # 2. Include explicitly requested files
        if include_files:
            for fpath in include_files:
                if file_budget <= 0:
                    break
                if os.path.exists(fpath) and fpath != active_file:
                    chunk = self.index.get_file_content(fpath, max_lines=100)
                    if chunk and chunk.token_count <= file_budget:
                        chunk.reason = 'Explicitly included'
                        chunk.relevance_score = 0.9
                        chunks.append(chunk)
                        file_budget -= chunk.token_count

        # 3. Search for relevant files based on task description
        if file_budget > 0 and len(chunks) < max_file_chunks:
            # Extract keywords from task
            keywords = self._extract_keywords(task)
            excluded = set(exclude_files or [])
            included_paths = {c.file_path for c in chunks}

            for keyword in keywords[:5]:
                if file_budget <= 0 or len(chunks) >= max_file_chunks:
                    break

                # Search by content
                search_results = self.index.search_content(keyword, max_results=3)
                for result in search_results:
                    if result.file_path in included_paths or result.file_path in excluded:
                        continue
                    if result.token_count > file_budget:
                        continue

                    chunks.append(result)
                    included_paths.add(result.file_path)
                    file_budget -= result.token_count

        # Calculate total tokens
        total_tokens = used_tokens + sum(c.token_count for c in chunks)

        return ContextWindow(
            system_prompt=system_prompt,
            file_chunks=chunks,
            conversation_history=history,
            active_state=self._editor_state if self._editor_state.active_file else None,
            user_prompt=task,
            total_tokens=total_tokens,
            budget_tokens=budget,
        )

    # ── State Management ─────────────────────────────────

    def update_editor_state(
        self,
        active_file: str = '',
        cursor_line: int = 0,
        open_files: Optional[List[str]] = None,
        diagnostics: Optional[List[Dict]] = None,
        git_branch: str = '',
    ):
        """Update the current editor state for context awareness."""
        if active_file:
            self._editor_state.active_file = active_file
        if cursor_line:
            self._editor_state.cursor_line = cursor_line
        if open_files is not None:
            self._editor_state.open_files = open_files
        if diagnostics is not None:
            self._editor_state.diagnostics = diagnostics
        if git_branch:
            self._editor_state.git_branch = git_branch

    def add_conversation_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self._conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': time.time(),
        })
        # Keep last 50 messages
        if len(self._conversation_history) > 50:
            self._conversation_history = self._conversation_history[-50:]

    def reindex(self, force: bool = True) -> dict:
        """Re-index the workspace."""
        return self.index.index(force=force)

    # ── Status ───────────────────────────────────────────

    def status(self) -> dict:
        return {
            'workspace_root': self.workspace_root,
            'indexed_files': len(self.index.files),
            'total_symbols': len(self.index._symbol_map),
            'conversation_messages': len(self._conversation_history),
            'active_file': self._editor_state.active_file,
            'open_files': len(self._editor_state.open_files),
            'last_indexed': self.index._last_indexed,
            'token_budgets': TOKEN_BUDGETS,
        }

    # ── Internal ─────────────────────────────────────────

    def _get_recent_conversation(self, max_tokens: int = 2000) -> List[Dict[str, str]]:
        """Get recent conversation history within token budget."""
        result = []
        tokens = 0
        for msg in reversed(self._conversation_history):
            msg_tokens = int(len(msg.get('content', '')) / CHARS_PER_TOKEN)
            if tokens + msg_tokens > max_tokens:
                break
            result.insert(0, msg)
            tokens += msg_tokens
        return result

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant search keywords from a task description."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'shall', 'would', 'could', 'should', 'may', 'might', 'can',
            'need', 'must', 'to', 'of', 'in', 'for', 'on', 'with', 'at',
            'by', 'from', 'this', 'that', 'these', 'those', 'it', 'its',
            'and', 'or', 'but', 'not', 'so', 'if', 'then', 'else',
            'when', 'where', 'how', 'what', 'which', 'who', 'why',
            'add', 'create', 'make', 'build', 'update', 'fix', 'change',
            'implement', 'write', 'modify', 'please', 'help', 'me',
        }

        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        # Deduplicate while preserving order
        seen: Set[str] = set()
        unique = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)

        return unique
