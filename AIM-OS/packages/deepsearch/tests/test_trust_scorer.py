"""
Unit Tests: TrustScorer
"""

import pytest
from datetime import datetime, timedelta
from deepsearch.trust_scorer import TrustScorer, score_source


@pytest.fixture
def scorer():
    return TrustScorer()


def test_domain_scoring_edu(scorer):
    """Test .edu domains score high"""
    score = scorer._score_domain("https://mit.edu/research")
    assert score >= 0.90


def test_domain_scoring_com(scorer):
    """Test .com domains score medium"""
    score = scorer._score_domain("https://example.com/page")
    assert 0.60 <= score <= 0.75


def test_domain_scoring_unknown(scorer):
    """Test unknown domains score neutral"""
    score = scorer._score_domain("https://random123abc.xyz/page")
    assert score == 0.50


def test_domain_scoring_special_github(scorer):
    """Test GitHub scores high"""
    score = scorer._score_domain("https://github.com/user/repo")
    assert score >= 0.85


def test_content_scoring_short(scorer):
    """Test short content scores lower"""
    short_content = "Test"
    score = scorer._score_content(short_content)
    assert score < 0.5


def test_content_scoring_long_with_structure(scorer):
    """Test long, structured content scores higher"""
    long_content = """
    # Introduction
    
    This is a well-structured document with multiple paragraphs.
    It contains citations to sources: https://example.com/source1
    
    ## Section 1
    
    More content here. This section has proper paragraphs and good structure.
    Another citation: https://example.com/source2
    
    ## Section 2
    
    Additional content with more details. This is a comprehensive document
    with good grammar and proper sentence structure.
    
    References:
    - https://example.com/ref1
    - https://example.com/ref2
    - https://example.com/ref3
    """
    score = scorer._score_content(long_content)
    assert score > 0.7


def test_recency_scoring_current(scorer):
    """Test current date scores high"""
    score = scorer._score_recency(datetime.now())
    assert score >= 0.85


def test_recency_scoring_old(scorer):
    """Test old date scores lower"""
    old_date = datetime.now() - timedelta(days=730)  # 2 years old
    score = scorer._score_recency(old_date)
    assert score < 0.5


def test_recency_scoring_none(scorer):
    """Test None date assumes recent"""
    score = scorer._score_recency(None)
    assert score >= 0.85


def test_calculate_trust_comprehensive(scorer):
    """Test complete trust calculation"""
    url = "https://mit.edu/research/ai"
    content = """
    # Artificial Intelligence Research
    
    This is a comprehensive research paper about AI. It includes multiple
    sections and citations to credible sources.
    
    ## Methods
    
    Our methodology is well-documented. See: https://doi.org/example
    
    ## Results
    
    The results show significant improvements. More details in the paper.
    
    ## References
    
    - https://scholar.google.com/paper1
    - https://arxiv.org/paper2
    - https://ieee.org/paper3
    """
    
    trust = scorer.calculate_trust(url, content, datetime.now())
    
    # Should be high: .edu domain + good content + recent
    assert trust >= 0.75
    assert 0 <= trust <= 1


def test_calculate_trust_low_quality(scorer):
    """Test trust calculation for low quality source"""
    url = "https://random.com/page"
    content = "short"
    old_date = datetime.now() - timedelta(days=1000)
    
    trust = scorer.calculate_trust(url, content, old_date)
    
    # Should be low: unknown domain + short content + old
    assert trust < 0.5
    assert 0 <= trust <= 1


def test_trust_score_clamped(scorer):
    """Test trust score is clamped to [0, 1]"""
    url = "https://test.com"
    content = "test"
    
    trust = scorer.calculate_trust(url, content)
    
    assert 0 <= trust <= 1


def test_score_source_utility():
    """Test quick scoring utility function"""
    url = "https://github.com/project"
    content = "A well-documented project with good README"
    
    score = score_source(url, content)
    
    assert 0 <= score <= 1
    assert score > 0.5  # GitHub + reasonable content


def test_weights_sum_validation():
    """Test weights must sum to 1.0"""
    with pytest.raises(ValueError, match="must sum to 1.0"):
        TrustScorer(domain_weight=0.5, content_weight=0.3, recency_weight=0.1)


def test_custom_weights():
    """Test custom weight configuration"""
    scorer = TrustScorer(domain_weight=0.5, content_weight=0.3, recency_weight=0.2)
    
    assert scorer.domain_weight == 0.5
    assert scorer.content_weight == 0.3
    assert scorer.recency_weight == 0.2

