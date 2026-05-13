"""
Unit Tests: EntropyCalculator
"""

import pytest
from deepsearch.entropy_calculator import EntropyCalculator, calculate_entropy


@pytest.fixture
def calculator():
    return EntropyCalculator()


def test_entropy_empty_string(calculator):
    """Test entropy of empty string is zero"""
    entropy = calculator.calculate_entropy("")
    assert entropy == 0.0


def test_entropy_single_character(calculator):
    """Test entropy of repeated character is low"""
    entropy = calculator.calculate_entropy("aaaaaaa")
    assert entropy == 0.0  # All same character = no entropy


def test_entropy_diverse_characters(calculator):
    """Test entropy of diverse characters is high"""
    entropy = calculator.calculate_entropy("abcdefghijklmnopqrstuvwxyz")
    assert entropy > 0.8  # Very diverse


def test_entropy_normalized(calculator):
    """Test normalized entropy is in [0, 1]"""
    text = "The quick brown fox jumps over the lazy dog"
    entropy = calculator.calculate_entropy(text, normalize=True)
    
    assert 0 <= entropy <= 1


def test_entropy_not_normalized(calculator):
    """Test non-normalized entropy can exceed 1"""
    text = "The quick brown fox jumps over the lazy dog"
    entropy = calculator.calculate_entropy(text, normalize=False)
    
    assert entropy > 1  # Can be larger than 1 when not normalized


def test_word_entropy(calculator):
    """Test word-level entropy"""
    text = "the cat sat on the mat"
    entropy = calculator.calculate_word_entropy(text, normalize=True)
    
    # "the" appears twice, rest once
    assert 0 < entropy < 1


def test_word_entropy_diverse(calculator):
    """Test word entropy for diverse text"""
    text = "apple banana cherry date elderberry fig grape"
    entropy = calculator.calculate_word_entropy(text, normalize=True)
    
    # All unique words = high entropy
    assert entropy > 0.9


def test_assess_quality_high(calculator):
    """Test quality assessment for high-quality text"""
    text = """
    This is a comprehensive document with diverse vocabulary.
    It contains multiple sentences with different words and concepts.
    The information density is high, with minimal repetition.
    Each paragraph contributes unique insights and perspectives.
    """
    
    assessment = calculator.assess_quality(text)
    
    assert 'char_entropy' in assessment
    assert 'word_entropy' in assessment
    assert 'combined_entropy' in assessment
    assert 'quality' in assessment
    assert assessment['quality'] in ['low', 'medium', 'high']
    assert assessment['combined_entropy'] > 0.5


def test_assess_quality_low(calculator):
    """Test quality assessment for repetitive text"""
    text = "test test test test test test"
    
    assessment = calculator.assess_quality(text)
    
    assert assessment['quality'] in ['low', 'medium']
    assert assessment['combined_entropy'] < 0.7


def test_assess_quality_fields(calculator):
    """Test assessment returns all required fields"""
    text = "Sample text for testing entropy calculation"
    
    assessment = calculator.assess_quality(text)
    
    required_fields = ['char_entropy', 'word_entropy', 'combined_entropy', 'quality', 'diversity_score']
    for field in required_fields:
        assert field in assessment


def test_diversity_score_equals_combined(calculator):
    """Test diversity score matches combined entropy"""
    text = "Test text with some diversity"
    
    assessment = calculator.assess_quality(text)
    
    assert assessment['diversity_score'] == assessment['combined_entropy']


def test_calculate_entropy_utility():
    """Test quick entropy calculation utility"""
    text = "The quick brown fox"
    
    entropy = calculate_entropy(text)
    
    assert 0 <= entropy <= 1


def test_entropy_case_sensitive(calculator):
    """Test entropy is case-sensitive"""
    text1 = "AAA"
    text2 = "AaA"
    
    entropy1 = calculator.calculate_entropy(text1)
    entropy2 = calculator.calculate_entropy(text2)
    
    # text2 has more diversity (A and a are different)
    assert entropy2 > entropy1


def test_word_entropy_case_insensitive(calculator):
    """Test word entropy treats case-insensitively"""
    text1 = "The the the"
    text2 = "The The THE"
    
    entropy1 = calculator.calculate_word_entropy(text1)
    entropy2 = calculator.calculate_word_entropy(text2)
    
    # Should be same (all lowercase in word entropy)
    assert entropy1 == entropy2

