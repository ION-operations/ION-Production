"""Confidence Bands for User Trust

Provides user-friendly confidence indicators:
- Band A (🟢 Green): High confidence (≥0.90) - "Trust this"
- Band B (🟡 Yellow): Medium confidence (0.70-0.89) - "Review this"
- Band C (🔴 Red): Low confidence (<0.70) - "Don't trust this"
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


# NL_TAG: VIF-CONF-001 | Confidence band levels | class ConfidenceBand | []
# NL_TAG_INTENT: VIF-INTENT-001 | Design decision: confidence | ConfidenceBand | [ADR-TBD]
class ConfidenceBand(str, Enum):
    """Confidence band levels"""
    A = "A"  # High confidence (green)
    B = "B"  # Medium confidence (yellow)
    C = "C"  # Low confidence (red)


@dataclass
# NL_TAG: VIF-CONF-002 | Definition of a confidence band | class BandDefinition | []
# NL_TAG_INTENT: VIF-INTENT-002 | Design decision: confidence | BandDefinition | [ADR-TBD]
class BandDefinition:
    """Definition of a confidence band"""
    band: ConfidenceBand
    name: str
    color: str
    emoji: str
    min_confidence: float
    max_confidence: float
    user_message: str
    recommended_action: str


# Standard band definitions
STANDARD_BANDS = {
    ConfidenceBand.A: BandDefinition(
        band=ConfidenceBand.A,
        name="High Confidence",
        color="green",
        emoji="🟢",
        min_confidence=0.90,
        max_confidence=1.00,
        user_message="This answer is highly reliable",
        recommended_action="Trust this response"
    ),
    ConfidenceBand.B: BandDefinition(
        band=ConfidenceBand.B,
        name="Medium Confidence",
        color="yellow",
        emoji="🟡",
        min_confidence=0.70,
        max_confidence=0.89,
        user_message="This answer is moderately reliable",
        recommended_action="Review before acting on this"
    ),
    ConfidenceBand.C: BandDefinition(
        band=ConfidenceBand.C,
        name="Low Confidence",
        color="red",
        emoji="🔴",
        min_confidence=0.00,
        max_confidence=0.69,
        user_message="This answer may be unreliable",
        recommended_action="Verify independently before using"
    ),
}


# NL_TAG: VIF-CONF-003 | Determine confidence band from score | determine_band(confidence) | []
# NL_TAG_INTENT: VIF-INTENT-003 | Design decision: confidence | determine_band | [ADR-TBD]
def determine_band(confidence: float) -> ConfidenceBand:
    """Determine confidence band from score
    
    Args:
        confidence: Confidence score (0.0-1.0)
        
    Returns:
        ConfidenceBand (A, B, or C)
        
    Examples:
        >>> determine_band(0.95)
        <ConfidenceBand.A: 'A'>
        >>> determine_band(0.75)
        <ConfidenceBand.B: 'B'>
        >>> determine_band(0.50)
        <ConfidenceBand.C: 'C'>
    """
    if confidence >= 0.90:
        return ConfidenceBand.A
    elif confidence >= 0.70:
        return ConfidenceBand.B
    else:
        return ConfidenceBand.C


# NL_TAG: VIF-CONF-004 | Get definition for a band | get_band_definition(band) | []
# NL_TAG_INTENT: VIF-INTENT-004 | Design decision: confidence | get_band_definition | [ADR-TBD]
def get_band_definition(band: ConfidenceBand) -> BandDefinition:
    """Get definition for a band
    
    Args:
        band: ConfidenceBand
        
    Returns:
        BandDefinition with all UI info
    """
    return STANDARD_BANDS[band]


# NL_TAG: VIF-CONF-005 | Format confidence score for user display | format_confidence_for_user(confidence) | []
# NL_TAG_INTENT: VIF-INTENT-005 | Design decision: confidence | format_confidence_for_user | [ADR-TBD]
def format_confidence_for_user(
    confidence: float,
    *,
    include_emoji: bool = True,
    include_percentage: bool = True,
    include_message: bool = True,
) -> str:
    """Format confidence score for user display
    
    Args:
        confidence: Confidence score (0.0-1.0)
        include_emoji: Include emoji indicator
        include_percentage: Include percentage value
        include_message: Include user message
        
    Returns:
        Formatted string for user
        
    Examples:
        >>> format_confidence_for_user(0.95)
        '🟢 95% - This answer is highly reliable'
        
        >>> format_confidence_for_user(0.75, include_message=False)
        '🟡 75%'
    """
    band = determine_band(confidence)
    definition = get_band_definition(band)
    
    parts = []
    
    if include_emoji:
        parts.append(definition.emoji)
    
    if include_percentage:
        parts.append(f"{confidence * 100:.0f}%")
    
    if include_message:
        parts.append(f"- {definition.user_message}")
    
    return " ".join(parts)


# NL_TAG: VIF-CONF-006 | Format band as badge (for UI) | format_band_badge(band) | []
# NL_TAG_INTENT: VIF-INTENT-006 | Design decision: confidence | format_band_badge | [ADR-TBD]
def format_band_badge(band: ConfidenceBand) -> str:
    """Format band as badge (for UI)
    
    Args:
        band: ConfidenceBand
        
    Returns:
        Badge string
        
    Examples:
        >>> format_band_badge(ConfidenceBand.A)
        '🟢 Band A'
    """
    definition = get_band_definition(band)
    return f"{definition.emoji} Band {band.value}"


# NL_TAG: VIF-CONF-007 | Get color for confidence score | get_confidence_color(confidence) | []
# NL_TAG_INTENT: VIF-INTENT-007 | Design decision: confidence | get_confidence_color | [ADR-TBD]
def get_confidence_color(confidence: float) -> str:
    """Get color for confidence score
    
    Args:
        confidence: Confidence score
        
    Returns:
        Color name ('green', 'yellow', 'red')
    """
    band = determine_band(confidence)
    return get_band_definition(band).color


# NL_TAG: VIF-CONF-008 | Get recommended user action for confidence level | get_recommended_action(confidence) | []
# NL_TAG_INTENT: VIF-INTENT-008 | Design decision: confidence | get_recommended_action | [ADR-TBD]
def get_recommended_action(confidence: float) -> str:
    """Get recommended user action for confidence level
    
    Args:
        confidence: Confidence score
        
    Returns:
        Recommended action string
    """
    band = determine_band(confidence)
    return get_band_definition(band).recommended_action


# NL_TAG: VIF-CONF-009 | Determine if UI should show warning | should_show_warning(confidence) | []
# NL_TAG_INTENT: VIF-INTENT-009 | Design decision: confidence | should_show_warning | [ADR-TBD]
def should_show_warning(confidence: float) -> bool:
    """Determine if UI should show warning
    
    Args:
        confidence: Confidence score
        
    Returns:
        True if Band C (low confidence)
    """
    return determine_band(confidence) == ConfidenceBand.C


# NL_TAG: VIF-CONF-010 | Get info for all bands (for UI documentation) | get_all_band_info() | []
def get_all_band_info() -> List[Dict]:
    """Get info for all bands (for UI documentation)
    
    Returns:
        List of band definitions as dicts
    """
    return [
        {
            "band": band.value,
            "name": defn.name,
            "color": defn.color,
            "emoji": defn.emoji,
            "range": f"{defn.min_confidence:.0%} - {defn.max_confidence:.0%}",
            "message": defn.user_message,
            "action": defn.recommended_action,
        }
        for band, defn in STANDARD_BANDS.items()
    ]


# NL_TAG: VIF-CONF-011 | Route operations based on confidence bands | class BandRouter | []
# NL_TAG_INTENT: VIF-INTENT-010 | Design decision: confidence | BandRouter | [ADR-TBD]
class BandRouter:
    """Route operations based on confidence bands
    
    Different bands can trigger different workflows:
    - Band A: Proceed automatically
    - Band B: Proceed with user notification
    - Band C: Request user review before proceeding
    """
    
    # NL_TAG: VIF-CONF-012 | Initialize band router | __init__(self, auto_proceed_bands, review_required_bands) | []
    def __init__(
        self,
        auto_proceed_bands: Optional[List[ConfidenceBand]] = None,
        review_required_bands: Optional[List[ConfidenceBand]] = None,
    ):
        """Initialize band router
        
        Args:
            auto_proceed_bands: Bands that can proceed automatically
            review_required_bands: Bands that require human review
        """
        self.auto_proceed_bands = auto_proceed_bands or [ConfidenceBand.A]
        self.review_required_bands = review_required_bands or [ConfidenceBand.C]
    
    # NL_TAG: VIF-CONF-013 | Determine routing for confidence score | route(self, confidence) | []
    # NL_TAG_INTENT: VIF-INTENT-011 | Design decision: confidence | route | [ADR-TBD]
    def route(self, confidence: float) -> str:
        """Determine routing for confidence score
        
        Args:
            confidence: Confidence score
            
        Returns:
            Routing decision: 'auto_proceed', 'notify', or 'review_required'
        """
        band = determine_band(confidence)
        
        if band in self.auto_proceed_bands:
            return "auto_proceed"
        elif band in self.review_required_bands:
            return "review_required"
        else:
            return "notify"
    
    # NL_TAG: VIF-CONF-014 | Check if can proceed automatically | can_auto_proceed(self, confidence) | []
    # NL_TAG_INTENT: VIF-INTENT-012 | Design decision: confidence | can_auto_proceed | [ADR-TBD]
    def can_auto_proceed(self, confidence: float) -> bool:
        """Check if can proceed automatically
        
        Args:
            confidence: Confidence score
            
        Returns:
            True if band allows auto-proceed
        """
        return self.route(confidence) == "auto_proceed"

