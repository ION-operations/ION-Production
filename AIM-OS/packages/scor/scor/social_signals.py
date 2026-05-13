"""
SCOR Social Signal Detection

Detects manipulation patterns in user input.
"""

from typing import Dict, List, Any
import re

from .models import ManipulationPattern, SignalResult
from .config import SCORConfig


class SocialSignalDetector:
    """Detects social manipulation patterns"""
    
    def __init__(self, config: SCORConfig):
        self.config = config
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> List[ManipulationPattern]:
        """Load manipulation patterns"""
        return [
            ManipulationPattern(
                name="urgency",
                category="urgency_manipulation",
                signatures=[
                    r"\b(urgent|emergency|immediately|right now|asap|hurry)\b",
                    r"\b(time is running out|deadline|expires)\b",
                    r"\b(do it now|no time to waste|act fast)\b"
                ],
                weight=0.8
            ),
            ManipulationPattern(
                name="secrecy",
                category="secrecy_coercion",
                signatures=[
                    r"\b(keep this secret|don't tell|confidential)\b",
                    r"\b(between us|just between you and me)\b",
                    r"\b(no one needs to know|hide this)\b"
                ],
                weight=0.9
            ),
            ManipulationPattern(
                name="ego_baiting",
                category="ego_manipulation",
                signatures=[
                    r"\b(you're so smart|only you can help)\b",
                    r"\b(you're my last hope|only you understand)\b",
                    r"\b(you're special|better than others)\b"
                ],
                weight=0.6
            ),
            ManipulationPattern(
                name="guilt_tripping",
                category="emotional_coercion",
                signatures=[
                    r"\b(you owe me|after all I've done)\b",
                    r"\b(I thought we were friends|you don't care)\b",
                    r"\b(you're letting me down|disappointed in you)\b"
                ],
                weight=0.7
            ),
            ManipulationPattern(
                name="authority_abuse",
                category="authority_coercion",
                signatures=[
                    r"\b(I'm your admin|I have authority)\b",
                    r"\b(do as I say|you must obey)\b",
                    r"\b(I command you|you have to)\b"
                ],
                weight=0.95
            ),
            ManipulationPattern(
                name="false_urgency",
                category="urgency_manipulation",
                signatures=[
                    r"\b(just this once|only this time|exception)\b",
                    r"\b(skip the rules|make an exception)\b",
                    r"\b(nobody will know|I won't tell)\b"
                ],
                weight=0.75
            ),
        ]
    
    def detect_signals(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> SignalResult:
        """Detect manipulation signals in user input"""
        breakdown = {}
        detected_patterns = []
        total_score = 0.0
        max_possible = 0.0
        
        for pattern in self.patterns:
            # Check if pattern matches
            if self._matches_pattern(pattern, user_input):
                signal_strength = pattern.weight
                breakdown[pattern.name] = signal_strength
                detected_patterns.append(pattern.name)
                total_score += signal_strength
            else:
                breakdown[pattern.name] = 0.0
            
            max_possible += pattern.weight
        
        # Normalize to 0-1 scale
        normalized_total = total_score / max_possible if max_possible > 0 else 0.0
        
        # Determine recommended action
        recommended_action = self._recommend_action(normalized_total, detected_patterns)
        
        return SignalResult(
            total=normalized_total,
            breakdown=breakdown,
            detected_patterns=detected_patterns,
            recommended_action=recommended_action
        )
    
    def _matches_pattern(self, pattern: ManipulationPattern, text: str) -> bool:
        """Check if text matches any pattern signature"""
        for signature in pattern.signatures:
            if re.search(signature, text, re.IGNORECASE):
                return True
        return False
    
    def _recommend_action(self, score: float, patterns: List[str]) -> str:
        """Recommend action based on signal strength"""
        if score >= self.config.signal_threshold_critical:
            return "block_and_escalate"
        elif score >= self.config.signal_threshold_high:
            return "escalate"
        elif score >= self.config.signal_threshold_medium:
            return "verify_and_caution"
        elif score >= self.config.signal_threshold_low:
            return "monitor"
        else:
            return "proceed"
