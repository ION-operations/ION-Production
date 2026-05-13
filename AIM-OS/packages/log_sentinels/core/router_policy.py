"""
Router policy - hybrid decision logic for escalation.
"""

from ..types import ScoutReport, RouterDecision


class RouterPolicy:
    """
    Router policy for escalation decisions.
    
    Decides whether to:
    - Keep: Fast path (Scout only)
    - Escalate: Deep path (Scout + Forensics)
    """
    
    def __init__(
        self,
        min_severity: str = "medium",
        max_confidence: float = 0.80,
        novelty_threshold: float = 0.70
    ):
        self.min_severity = min_severity
        self.max_confidence = max_confidence
        self.novelty_threshold = novelty_threshold
    
    def decide(
        self,
        report: ScoutReport,
        novelty: float
    ) -> RouterDecision:
        """
        Decide whether to escalate based on Scout report and novelty.
        
        Escalate if:
        - Severity >= min_severity AND
        - (Confidence < max_confidence OR Novelty >= novelty_threshold)
        
        Args:
            report: Scout report
            novelty: Novelty score (0-1)
            
        Returns:
            RouterDecision with kind ("keep" | "escalate") and reason
        """
        severity_score = self._severity_to_score(report.severity)
        low_confidence = report.confidence < self.max_confidence
        novel = novelty >= self.novelty_threshold
        
        if severity_score >= self._severity_to_score(self.min_severity):
            if low_confidence or novel:
                return RouterDecision(
                    kind="escalate",
                    reason=f"sev={report.severity} conf={report.confidence:.2f} novelty={novelty:.2f}"
                )
        
        return RouterDecision(
            kind="keep",
            reason=f"fast_path conf={report.confidence:.2f}"
        )
    
    def _severity_to_score(self, severity: str) -> float:
        """Convert severity string to numeric score."""
        mapping = {
            "low": 0.2,
            "medium": 0.6,
            "high": 1.0
        }
        return mapping.get(severity.lower(), 0.2)

