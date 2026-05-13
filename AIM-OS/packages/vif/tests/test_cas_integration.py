"""Tests for VIF-CAS integration"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone

from vif.witness import VIF, ConfidenceBand, TaskCriticality
from vif.cas_integration import (
    extract_cognitive_context,
    add_cognitive_context_to_witness,
    enhance_confidence_with_cognitive_state,
    create_witness_with_cognitive_context,
    is_cas_available,
    CognitiveContext,
)


# Mock ActivationState for testing
class MockActivationState:
    def __init__(self):
        self.principles_activation = {"principle1": 0.8, "principle2": 0.6}
        self.documents_activation = {"doc1": 0.9, "doc2": 0.7}
        self.concepts_activation = {"concept1": 0.85, "concept2": 0.75}
        self.session_id = "session_123"
        self.timestamp = datetime.now(timezone.utc)
        self.context_size_tokens = 1000
        self.working_attention_items = ["item1", "item2"]
        self.recent_operations = ["op1", "op2"]
        self.documents_read = [("doc1", datetime.now(timezone.utc))]
        self.load_level = "medium"
    
    def get_cold_but_needed(self, required):
        return ["principle3"] if "principle3" in required else []


def test_extract_cognitive_context():
    """Test extracting cognitive context from CAS"""
    activation_state = MockActivationState()
    
    context = extract_cognitive_context(
        activation_state=activation_state,
        task_category="coding",
        task_category_confidence=0.9,
        cognitive_load=0.7,
        attention_breadth="comprehensive",
    )
    
    assert isinstance(context, CognitiveContext)
    assert context.activation_state is not None
    assert context.principles_activation == activation_state.principles_activation
    assert context.task_category == "coding"
    assert context.task_category_confidence == 0.9
    assert context.cognitive_load == 0.7
    assert context.attention_breadth == "comprehensive"


def test_extract_cognitive_context_no_cas():
    """Test graceful degradation when CAS unavailable"""
    context = extract_cognitive_context()
    
    assert isinstance(context, CognitiveContext)
    assert context.activation_state is None


def test_extract_cognitive_context_attention_narrowing():
    """Test detecting attention narrowing"""
    activation_state = MockActivationState()
    
    context = extract_cognitive_context(
        activation_state=activation_state,
        cognitive_load=0.9,  # High load
        attention_breadth="narrow",  # Narrow attention
    )
    
    assert context.attention_narrowing is True


def test_extract_cognitive_context_activation_gap():
    """Test detecting activation gaps"""
    activation_state = MockActivationState()
    
    context = extract_cognitive_context(
        activation_state=activation_state,
        required_principles=["principle1", "principle3"],  # principle3 is cold
    )
    
    assert context.activation_gap == ["principle3"]


def test_add_cognitive_context_to_witness():
    """Test adding cognitive context to VIF witness"""
    vif = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_123",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
    )
    
    context = CognitiveContext(
        task_category="coding",
        cognitive_load=0.7,
        attention_breadth="comprehensive",
    )
    
    updated_vif = add_cognitive_context_to_witness(vif, context)
    
    assert updated_vif.tool_parameters is not None
    assert "cognitive_context" in updated_vif.tool_parameters
    stored_context = updated_vif.tool_parameters["cognitive_context"]
    assert stored_context["task_category"] == "coding"
    assert stored_context["cognitive_load"] == 0.7


def test_enhance_confidence_with_cognitive_state():
    """Test enhancing confidence based on cognitive state"""
    # Normal cognitive state - no reduction
    context = CognitiveContext(
        cognitive_load=0.5,
        attention_breadth="comprehensive",
        attention_narrowing=False,
        failure_mode_detected=None,
    )
    
    enhanced = enhance_confidence_with_cognitive_state(0.95, context)
    
    assert enhanced == 0.95  # No reduction


def test_enhance_confidence_with_high_load():
    """Test confidence reduction with high cognitive load"""
    context = CognitiveContext(
        cognitive_load=0.9,  # High load
        attention_breadth="comprehensive",
    )
    
    enhanced = enhance_confidence_with_cognitive_state(0.95, context)
    
    assert enhanced < 0.95  # Should be reduced


def test_enhance_confidence_with_attention_narrowing():
    """Test confidence reduction with attention narrowing"""
    context = CognitiveContext(
        cognitive_load=0.8,
        attention_breadth="narrow",
        attention_narrowing=True,  # Warning sign
    )
    
    enhanced = enhance_confidence_with_cognitive_state(0.95, context)
    
    assert enhanced < 0.95  # Should be reduced


def test_enhance_confidence_with_failure_mode():
    """Test confidence reduction with detected failure mode"""
    context = CognitiveContext(
        cognitive_load=0.5,
        attention_breadth="comprehensive",
        failure_mode_detected="hallucination_risk",
    )
    
    enhanced = enhance_confidence_with_cognitive_state(0.95, context)
    
    assert enhanced < 0.95  # Should be reduced


def test_enhance_confidence_with_categorization_error():
    """Test confidence reduction with categorization error"""
    context = CognitiveContext(
        cognitive_load=0.5,
        attention_breadth="comprehensive",
        categorization_error="wrong_category",
    )
    
    enhanced = enhance_confidence_with_cognitive_state(0.95, context)
    
    assert enhanced < 0.95  # Should be reduced


def test_create_witness_with_cognitive_context():
    """Test creating witness with cognitive context"""
    activation_state = MockActivationState()
    context = extract_cognitive_context(
        activation_state=activation_state,
        task_category="coding",
        cognitive_load=0.7,
    )
    
    vif = create_witness_with_cognitive_context(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_123",
        prompt_hash="hash1",
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
        cognitive_context=context,
        initial_confidence=0.95,
    )
    
    assert isinstance(vif, VIF)
    assert vif.tool_parameters is not None
    assert "cognitive_context" in vif.tool_parameters
    # Confidence may be enhanced based on cognitive state
    assert vif.confidence_score is not None


def test_create_witness_with_cognitive_context_enhanced_confidence():
    """Test confidence enhancement in witness creation"""
    context = CognitiveContext(
        cognitive_load=0.9,  # High load - should reduce confidence
        attention_breadth="comprehensive",
    )
    
    vif = create_witness_with_cognitive_context(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_123",
        prompt_hash="hash1",
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
        cognitive_context=context,
        initial_confidence=0.95,
    )
    
    # Confidence should be reduced due to high cognitive load
    assert vif.confidence_score < 0.95


def test_is_cas_available():
    """Test checking CAS availability"""
    activation_state = MockActivationState()
    
    assert is_cas_available(activation_state) is True
    assert is_cas_available(None) is False


def test_cognitive_context_dataclass():
    """Test CognitiveContext dataclass"""
    context = CognitiveContext(
        task_category="coding",
        task_category_confidence=0.9,
        cognitive_load=0.7,
        attention_breadth="comprehensive",
        attention_narrowing=False,
        failure_mode_detected=None,
        activation_gap=None,
        session_id="session_123",
        timestamp=datetime.now(timezone.utc),
    )
    
    assert context.task_category == "coding"
    assert context.task_category_confidence == 0.9
    assert context.cognitive_load == 0.7
    assert context.attention_breadth == "comprehensive"
    assert context.attention_narrowing is False
    assert context.failure_mode_detected is None


def test_add_cognitive_context_preserves_existing_tool_parameters():
    """Test that adding cognitive context preserves existing tool parameters"""
    vif = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_123",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
        tool_parameters={
            "existing_param": "value",
        }
    )
    
    context = CognitiveContext(task_category="coding")
    updated_vif = add_cognitive_context_to_witness(vif, context)
    
    assert updated_vif.tool_parameters["existing_param"] == "value"
    assert "cognitive_context" in updated_vif.tool_parameters

