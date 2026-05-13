"""Text parsing helpers for HHNI."""

from __future__ import annotations

import re
from typing import List

_PARAGRAPH_SPLIT_RE = re.compile(r"(?:\r?\n){2,}")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")  # naive fallback if needed


# NL_TAG: VIF-UTIL-001 | Normalize different newline styles to ` | normalize_newlines(text) | []
def normalize_newlines(text: str) -> str:
    """Normalize different newline styles to `\n`."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


# NL_TAG: VIF-UTIL-002 | Strip non empty | strip_non_empty(chunks) | []
def strip_non_empty(chunks: List[str]) -> List[str]:
    return [chunk.strip() for chunk in chunks if chunk and chunk.strip()]


# NL_TAG: VIF-UTIL-003 | Split text into paragraphs using blank-line heuristic. | parse_paragraphs(text) | []
def parse_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs using blank-line heuristic."""
    normalized = normalize_newlines(text or "")
    if not normalized.strip():
        return []
    chunks = _PARAGRAPH_SPLIT_RE.split(normalized)
    return strip_non_empty(chunks)


# NL_TAG: VIF-UTIL-004 | Split a paragraph into sentences using simple punctuation rules. | parse_sentences(paragraph) | []
def parse_sentences(paragraph: str) -> List[str]:
    """Split a paragraph into sentences using simple punctuation rules."""
    text = paragraph.strip()
    if not text:
        return []
    # Use regex that keeps punctuation by splitting on boundaries
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    return strip_non_empty(sentences)
