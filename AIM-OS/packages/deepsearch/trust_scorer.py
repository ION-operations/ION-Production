"""
Trust Scorer - Calculate trust scores for sources

Combines domain reputation, content quality, and recency into 0-1 trust score.
"""

import re
import math
from urllib.parse import urlparse
from typing import Optional, Dict
from datetime import datetime, timedelta


class TrustScorer:
    """Calculates trust scores for sources"""
    
    # Domain reputation weights (0-1)
    DOMAIN_WEIGHTS = {
        '.edu': 0.95,      # Educational institutions
        '.ac.uk': 0.95,    # UK academic
        '.gov': 0.90,      # Government
        '.org': 0.80,      # Non-profit organizations
        '.mil': 0.85,      # Military
        '.int': 0.85,      # International organizations
        '.com': 0.70,      # Commercial
        '.net': 0.65,      # Network
        '.io': 0.65,       # Tech
        '.co': 0.60,       # Company
        'github.com': 0.85,  # Code repositories (high trust)
        'stackoverflow.com': 0.80,  # Q&A (high trust)
        'arxiv.org': 0.95,  # Research papers (very high)
        'wikipedia.org': 0.75,  # Wikipedia (medium-high)
    }
    
    def __init__(
        self,
        domain_weight: float = 0.40,
        content_weight: float = 0.40,
        recency_weight: float = 0.20
    ):
        """
        Initialize trust scorer
        
        Args:
            domain_weight: Weight for domain reputation (0-1)
            content_weight: Weight for content quality (0-1)
            recency_weight: Weight for recency (0-1)
        """
        self.domain_weight = domain_weight
        self.content_weight = content_weight
        self.recency_weight = recency_weight
        
        # Validate weights sum to 1.0
        total = domain_weight + content_weight + recency_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def calculate_trust(
        self,
        url: str,
        content: str,
        published_date: Optional[datetime] = None
    ) -> float:
        """
        Calculate trust score for source
        
        Args:
            url: Source URL
            content: Source content (text)
            published_date: Publication date (None = now)
            
        Returns:
            Trust score 0-1 (higher = more trustworthy)
        """
        domain_score = self._score_domain(url)
        content_score = self._score_content(content)
        recency_score = self._score_recency(published_date)
        
        trust = (
            domain_score * self.domain_weight +
            content_score * self.content_weight +
            recency_score * self.recency_weight
        )
        
        return min(1.0, max(0.0, trust))  # Clamp to [0, 1]
    
    def _score_domain(self, url: str) -> float:
        """Score domain reputation"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check specific domains first
            for known_domain, weight in self.DOMAIN_WEIGHTS.items():
                if known_domain in domain:
                    return weight
            
            # Check TLD
            if '.' in domain:
                tld = '.' + domain.split('.')[-1]
                if tld in self.DOMAIN_WEIGHTS:
                    return self.DOMAIN_WEIGHTS[tld]
            
            # Default: Neutral
            return 0.50
            
        except Exception:
            return 0.50
    
    def _score_content(self, content: str) -> float:
        """
        Score content quality
        
        Considers:
        - Length (longer = more substantial)
        - Citation presence (links to sources)
        - Paragraph structure (organized)
        - Grammar quality (spelling, punctuation)
        """
        if not content:
            return 0.0
        
        score = 0.0
        
        # Length score (logarithmic)
        length = len(content)
        if length < 100:
            length_score = 0.3
        elif length < 500:
            length_score = 0.5
        elif length < 2000:
            length_score = 0.7
        else:
            length_score = 0.9
        score += length_score * 0.30
        
        # Citation presence (URLs in content)
        url_pattern = re.compile(r'https?://\S+')
        num_citations = len(url_pattern.findall(content))
        citation_score = min(1.0, num_citations / 5)  # 5+ citations = max score
        score += citation_score * 0.25
        
        # Paragraph structure
        paragraphs = content.split('\n\n')
        num_paragraphs = len([p for p in paragraphs if len(p.strip()) > 50])
        paragraph_score = min(1.0, num_paragraphs / 5)  # 5+ paragraphs = well-structured
        score += paragraph_score * 0.20
        
        # Grammar quality (simple heuristic: punctuation presence)
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        grammar_score = 0.8 if 10 < avg_sentence_length < 30 else 0.5  # Reasonable sentence length
        score += grammar_score * 0.25
        
        return min(1.0, score)
    
    def _score_recency(self, published_date: Optional[datetime]) -> float:
        """
        Score content recency
        
        Uses exponential decay: newer content scores higher
        """
        if published_date is None:
            # Assume current if no date
            return 0.90
        
        # Calculate age in days
        age_days = (datetime.now() - published_date).days
        
        if age_days < 0:
            # Future date? Suspicious, low score
            return 0.30
        
        # Exponential decay with half-life of 365 days
        half_life = 365
        decay_constant = 0.693 / half_life  # ln(2) / half_life
        recency_score = math.exp(-decay_constant * age_days)
        
        return max(0.10, min(1.0, recency_score))  # Clamp to [0.1, 1.0]


# Utility for quick scoring
def score_source(url: str, content: str, date: Optional[datetime] = None) -> float:
    """Quick trust score calculation"""
    scorer = TrustScorer()
    return scorer.calculate_trust(url, content, date)

