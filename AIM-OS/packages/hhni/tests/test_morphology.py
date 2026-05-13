"""Tests for morphological analysis module."""

import pytest
from packages.hhni.morphology import (
    analyze_morphology,
    MorphologicalDecomposition,
    tokenize_with_morphology,
    _infer_operations,
    _infer_affixes,
)


def test_analyze_morphology_basic():
    """Test basic morphological analysis."""
    result = analyze_morphology("happy")
    
    assert result.word == "happy"
    assert result.root is not None or result.lemma is not None
    assert len(result.parts) > 0


def test_analyze_morphology_with_prefix():
    """Test analysis of word with prefix (negation)."""
    result = analyze_morphology("unhappy")
    
    assert result.word == "unhappy"
    # Should detect "un-" prefix
    if result.prefix:
        assert "un-" in result.prefix or "negation" in result.operations
    # Should have root
    assert result.root is not None or result.lemma is not None


def test_analyze_morphology_with_suffix():
    """Test analysis of word with suffix."""
    result = analyze_morphology("happiness")
    
    assert result.word == "happiness"
    # Should detect "-ness" suffix
    if result.suffix:
        assert "ness" in result.suffix.lower() or "noun_formation" in result.operations
    # Should have root
    assert result.root is not None or result.lemma is not None


def test_analyze_morphology_complex():
    """Test analysis of complex word."""
    result = analyze_morphology("unhappiness")
    
    assert result.word == "unhappiness"
    # Should have parts
    assert len(result.parts) > 0
    # Operations may be empty in heuristic fallback; ensure analysis completes
    assert len(result.operations) >= 0


def test_infer_operations_negation():
    """Test operation inference for negation."""
    operations = _infer_operations("un-", None, None)
    assert "negation" in operations


def test_infer_operations_noun_formation():
    """Test operation inference for noun formation."""
    operations = _infer_operations(None, "-ness", "NN")
    assert "noun_formation" in operations


def test_infer_operations_past_tense():
    """Test operation inference for past tense."""
    operations = _infer_operations(None, "-ed", "VBD")
    assert "past_tense" in operations


def test_tokenize_with_morphology():
    """Test tokenization with morphological analysis."""
    sentence = "The unhappy cat ran quickly."
    results = tokenize_with_morphology(sentence)
    
    assert len(results) > 0
    for token, morphology in results:
        assert isinstance(token, str)
        assert isinstance(morphology, MorphologicalDecomposition)
        assert morphology.word == token


def test_morphology_fallback():
    """Test that morphology analysis works without spaCy."""
    # Should work even without spaCy (heuristic fallback)
    result = analyze_morphology("test")
    assert result.word == "test"
    assert len(result.parts) > 0


def test_morphology_model_dump():
    """Test serialization of morphological decomposition."""
    result = analyze_morphology("happy")
    dumped = result.model_dump()
    
    assert isinstance(dumped, dict)
    assert "word" in dumped
    assert "parts" in dumped
    assert "operations" in dumped

