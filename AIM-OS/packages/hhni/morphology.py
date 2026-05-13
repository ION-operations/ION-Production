"""Morphological analysis for HHNI SUBWORD level enhancement.

This module provides morphological decomposition of words into their parts
(prefix, root, suffix) and learned operations (negation, tense, etc.).

Enables understanding words through their parts, as described in the semantic
organization enhancement research.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Try to import spaCy (optional dependency)
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None  # type: ignore

# Global spaCy model (lazy-loaded)
_nlp_model = None


@dataclass
class MorphologicalDecomposition:
    """Morphological analysis of a word.
    
    Represents the decomposition of a word into its morphological parts
    (prefix, root, suffix) and learned operations.
    """
    word: str                          # Original word
    root: Optional[str] = None         # Core meaning (e.g., "happy")
    prefix: Optional[str] = None       # Prefix (e.g., "un-")
    suffix: Optional[str] = None      # Suffix (e.g., "-ness")
    stem: Optional[str] = None        # Stem (root + base)
    lemma: Optional[str] = None        # Dictionary form
    pos_tag: Optional[str] = None      # Part of speech
    operations: List[str] = field(default_factory=list)  # Learned operations
    parts: List[str] = field(default_factory=list)       # All parts (prefix, root, suffix)
    
    def model_dump(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "word": self.word,
            "root": self.root,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "stem": self.stem,
            "lemma": self.lemma,
            "pos_tag": self.pos_tag,
            "operations": self.operations,
            "parts": self.parts,
        }


def get_nlp_model():
    """Get or load spaCy model (lazy loading).
    
    Returns:
        spaCy model or None if not available.
    """
    global _nlp_model
    
    if not SPACY_AVAILABLE:
        return None
    
    if _nlp_model is None:
        try:
            _nlp_model = spacy.load("en_core_web_sm")
            logger.info("spacy model loaded: en_core_web_sm")
        except OSError:
            logger.warning(
                "spacy model 'en_core_web_sm' not found. "
                "Install with: python -m spacy download en_core_web_sm"
            )
            return None
    
    return _nlp_model


def _infer_affixes(word: str, root: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Infer prefix and suffix from word and root.
    
    Args:
        word: Original word
        root: Root/lemma (if known)
        
    Returns:
        Tuple of (prefix, suffix) or (None, None) if cannot infer.
    """
    if not root or root == word:
        return None, None
    
    # Common prefixes
    prefixes = [
        "un-", "non-", "in-", "im-", "il-", "ir-", "dis-", "de-",
        "re-", "pre-", "over-", "under-", "out-", "up-", "down-",
        "anti-", "pro-", "co-", "ex-", "sub-", "super-", "trans-",
    ]
    
    # Common suffixes
    suffixes = [
        "-ness", "-ity", "-tion", "-sion", "-ment", "-ance", "-ence",
        "-ly", "-able", "-ible", "-ful", "-less", "-ous", "-ious",
        "-ed", "-ing", "-s", "-es", "-er", "-est", "-ize", "-ise",
    ]
    
    # Check for prefix
    prefix = None
    for p in prefixes:
        if word.startswith(p) and len(word) > len(p):
            prefix = p
            break
    
    # Check for suffix
    suffix = None
    for s in suffixes:
        if word.endswith(s) and len(word) > len(s):
            suffix = s
            break
    
    return prefix, suffix


def _infer_operations(
    prefix: Optional[str],
    suffix: Optional[str],
    pos_tag: Optional[str]
) -> List[str]:
    """Infer learned operations from morphology.
    
    Args:
        prefix: Prefix (if any)
        suffix: Suffix (if any)
        pos_tag: Part of speech tag
        
    Returns:
        List of operation names.
    """
    operations = []
    
    # Prefix operations
    if prefix:
        if prefix in ["un-", "non-", "in-", "im-", "il-", "ir-", "dis-"]:
            operations.append("negation")
        elif prefix == "re-":
            operations.append("repetition")
        elif prefix == "pre-":
            operations.append("temporal_before")
        elif prefix == "over-":
            operations.append("intensity_high")
        elif prefix == "under-":
            operations.append("intensity_low")
        elif prefix == "anti-":
            operations.append("opposition")
        elif prefix == "pro-":
            operations.append("support")
    
    # Suffix operations
    if suffix:
        if suffix in ["-ness", "-ity"]:
            operations.append("noun_formation")
        elif suffix == "-ly":
            operations.append("adverb_formation")
        elif suffix in ["-able", "-ible"]:
            operations.append("adjective_formation")
        elif suffix == "-ed":
            operations.append("past_tense")
        elif suffix == "-ing":
            operations.append("present_participle")
        elif suffix in ["-s", "-es"]:
            operations.append("plural" if pos_tag == "NNS" else "third_person")
        elif suffix == "-er":
            operations.append("comparative")
        elif suffix == "-est":
            operations.append("superlative")
        elif suffix in ["-ize", "-ise"]:
            operations.append("verb_formation")
    
    return operations


def _combine_parts(
    prefix: Optional[str],
    root: Optional[str],
    suffix: Optional[str]
) -> List[str]:
    """Combine morphological parts into list.
    
    Args:
        prefix: Prefix (if any)
        root: Root (if any)
        suffix: Suffix (if any)
        
    Returns:
        List of parts in order: [prefix, root, suffix] (excluding None).
    """
    parts = []
    if prefix:
        parts.append(prefix)
    if root:
        parts.append(root)
    if suffix:
        parts.append(suffix)
    return parts if parts else []


def analyze_morphology(word: str) -> MorphologicalDecomposition:
    """Analyze word morphology.
    
    Uses spaCy if available, falls back to heuristic analysis.
    
    Args:
        word: Word to analyze
        
    Returns:
        MorphologicalDecomposition with analysis results.
    """
    # Clean word (remove punctuation)
    clean_word = re.sub(r'[^\w\s-]', '', word)
    if not clean_word:
        # Fallback: return basic decomposition
        return MorphologicalDecomposition(
            word=word,
            root=word,
            stem=word,
            lemma=word,
            parts=[word]
        )
    
    nlp = get_nlp_model()
    
    if nlp is None:
        # Fallback: basic heuristic analysis
        return _analyze_morphology_heuristic(clean_word)
    
    # Use spaCy for analysis
    try:
        doc = nlp(clean_word)
        if not doc or len(doc) == 0:
            return _analyze_morphology_heuristic(clean_word)
        
        token = doc[0]
        
        # Extract morphological features
        lemma = token.lemma_ if token.lemma_ != clean_word else clean_word
        pos_tag = token.pos_
        root = lemma if lemma != clean_word else None
        
        # Infer prefix/suffix
        prefix, suffix = _infer_affixes(clean_word, root)
        
        # Infer operations
        operations = _infer_operations(prefix, suffix, pos_tag)
        
        # Combine parts
        parts = _combine_parts(prefix, root or clean_word, suffix)
        
        return MorphologicalDecomposition(
            word=word,
            root=root,
            prefix=prefix,
            suffix=suffix,
            stem=lemma,
            lemma=lemma,
            pos_tag=pos_tag,
            operations=operations,
            parts=parts
        )
    
    except Exception as e:
        logger.warning(f"spacy analysis failed for '{word}': {e}, using heuristic")
        return _analyze_morphology_heuristic(clean_word)


def _analyze_morphology_heuristic(word: str) -> MorphologicalDecomposition:
    """Heuristic morphological analysis (fallback when spaCy unavailable).
    
    Args:
        word: Word to analyze
        
    Returns:
        MorphologicalDecomposition with heuristic analysis.
    """
    # Try to infer prefix/suffix without root
    prefix, suffix = _infer_affixes(word, None)
    
    # Infer root (word without prefix/suffix)
    root = word
    if prefix:
        root = root[len(prefix):]
    if suffix:
        root = root[:-len(suffix)] if len(root) > len(suffix) else root
    
    # Infer operations
    operations = _infer_operations(prefix, suffix, None)
    
    # Combine parts
    parts = _combine_parts(prefix, root, suffix)
    
    return MorphologicalDecomposition(
        word=word,
        root=root if root != word else None,
        prefix=prefix,
        suffix=suffix,
        stem=root,
        lemma=root,
        operations=operations,
        parts=parts if parts else [word]
    )


def tokenize_with_morphology(sentence: str) -> List[Tuple[str, MorphologicalDecomposition]]:
    """Tokenize sentence with morphological analysis.
    
    Args:
        sentence: Sentence to tokenize
        
    Returns:
        List of (token, MorphologicalDecomposition) tuples.
    """
    # Basic tokenization (same as current _tokenize)
    tokens = re.findall(r"\w+|\S", sentence)
    tokens = [token for token in tokens if token.strip()]
    
    # Morphological analysis for each token
    results = []
    for token in tokens:
        decomposition = analyze_morphology(token)
        results.append((token, decomposition))
    
    return results

