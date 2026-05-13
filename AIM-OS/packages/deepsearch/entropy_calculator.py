"""
Entropy Calculator - Measure information density using Shannon entropy

Higher entropy = more diverse/informative content
Lower entropy = repetitive/low-information content
"""

import math
from collections import Counter
from typing import Optional, Dict, Any


class EntropyCalculator:
    """Calculates Shannon entropy for text"""
    
    def calculate_entropy(self, text: str, normalize: bool = True) -> float:
        """
        Calculate Shannon entropy of text
        
        Args:
            text: Text to analyze
            normalize: Whether to normalize by max possible entropy
            
        Returns:
            Entropy value (bits per character)
            - Not normalized: 0 to log₂(alphabet_size)
            - Normalized: 0 to 1
        """
        if not text or len(text) == 0:
            return 0.0
        
        # Count character frequencies
        freq = Counter(text)
        total = len(text)
        
        # Calculate Shannon entropy
        entropy = 0.0
        for count in freq.values():
            if count == 0:
                continue
            probability = count / total
            entropy -= probability * math.log2(probability)
        
        # Normalize if requested
        if normalize:
            # Max entropy = log₂(number of unique characters)
            max_entropy = math.log2(len(freq)) if len(freq) > 1 else 1.0
            if max_entropy > 0:
                entropy = entropy / max_entropy
        
        return entropy
    
    def calculate_word_entropy(self, text: str, normalize: bool = True) -> float:
        """
        Calculate entropy at word level (instead of character level)
        
        Often more meaningful for semantic analysis
        """
        if not text or len(text.strip()) == 0:
            return 0.0
        
        # Split into words
        words = text.lower().split()
        if not words:
            return 0.0
        
        # Count word frequencies
        freq = Counter(words)
        total = len(words)
        
        # Calculate entropy
        entropy = 0.0
        for count in freq.values():
            if count == 0:
                continue
            probability = count / total
            entropy -= probability * math.log2(probability)
        
        # Normalize if requested
        if normalize:
            max_entropy = math.log2(len(freq)) if len(freq) > 1 else 1.0
            if max_entropy > 0:
                entropy = entropy / max_entropy
        
        return entropy
    
    def assess_quality(self, text: str) -> Dict[str, Any]:
        """
        Assess content quality using entropy
        
        Returns:
            Dictionary with entropy metrics and quality assessment
        """
        char_entropy = self.calculate_entropy(text, normalize=True)
        word_entropy = self.calculate_word_entropy(text, normalize=True)
        
        # Combined score (favor word entropy slightly)
        combined = (char_entropy * 0.40) + (word_entropy * 0.60)
        
        # Quality classification
        if combined > 0.75:
            quality = "high"
        elif combined > 0.50:
            quality = "medium"
        else:
            quality = "low"
        
        return {
            'char_entropy': char_entropy,
            'word_entropy': word_entropy,
            'combined_entropy': combined,
            'quality': quality,
            'diversity_score': combined,  # Entropy as diversity measure
        }


# Utility for quick entropy calculation
def calculate_entropy(text: str) -> float:
    """Quick entropy calculation (normalized)"""
    calculator = EntropyCalculator()
    return calculator.calculate_entropy(text, normalize=True)

