"""Tests for CAS Activation Tracking component."""

import pytest
from datetime import datetime, timedelta, UTC
from cas.activation import ActivationTracker, ActivationState


class TestActivationTracker:
    
    def test_initialization(self):
        """Test ActivationTracker initialization."""
        tracker = ActivationTracker("test_session")
        assert tracker.session_id == "test_session"
        assert len(tracker.usage_history) == 0
        assert len(tracker.last_access) == 0
    
    def test_record_principle_use(self):
        """Test recording principle usage."""
        tracker = ActivationTracker("test_session")
        tracker.record_principle_use("CMC_bitemporal")
        
        assert "CMC_bitemporal" in tracker.usage_history
        assert "CMC_bitemporal" in tracker.last_access
        assert len(tracker.usage_history["CMC_bitemporal"]) == 1
    
    def test_record_document_read(self):
        """Test recording document reads."""
        tracker = ActivationTracker("test_session")
        tracker.record_document_read("/path/to/doc.md")
        
        assert "/path/to/doc.md" in tracker.usage_history
        assert "/path/to/doc.md" in tracker.last_access
    
    def test_calculate_activation_never_used(self):
        """Test activation calculation for never-used item."""
        tracker = ActivationTracker("test_session")
        activation = tracker.calculate_activation("unknown_principle")
        
        assert activation == 0.0
    
    def test_calculate_activation_recent_use(self):
        """Test activation calculation for recently used item."""
        tracker = ActivationTracker("test_session")
        tracker.record_principle_use("test_principle")
        
        activation = tracker.calculate_activation("test_principle")
        assert activation > 0.0
        assert activation <= 1.0
    
    def test_capture_state(self):
        """Test capturing complete activation state."""
        tracker = ActivationTracker("test_session")
        tracker.record_principle_use("CMC_bitemporal")
        tracker.record_document_read("/test/doc.md")
        
        state = tracker.capture_state(
            current_task="Test task",
            cognitive_load=0.5,
            context_tokens=1000
        )
        
        assert isinstance(state, ActivationState)
        assert state.session_id == "test_session"
        assert "CMC_bitemporal" in state.principles_activation
        assert "/test/doc.md" in state.documents_activation
        assert state.context_size_tokens == 1000
        assert state.load_level == 0.5
    
    def test_is_hot_is_cold(self):
        """Test hot/cold detection methods."""
        tracker = ActivationTracker("test_session")
        tracker.record_principle_use("test_principle")
        
        state = tracker.capture_state()
        
        # Mock activation level
        state.principles_activation["test_principle"] = 0.8
        assert state.is_hot("test_principle")
        assert not state.is_cold("test_principle")
        
        state.principles_activation["test_principle"] = 0.2
        assert not state.is_hot("test_principle")
        assert state.is_cold("test_principle")
    
    def test_get_cold_but_needed(self):
        """Test identifying cold but needed principles."""
        tracker = ActivationTracker("test_session")
        state = tracker.capture_state()
        
        # Mock some activations
        state.principles_activation = {
            "hot_principle": 0.8,
            "cold_principle": 0.2,
            "another_cold": 0.1
        }
        
        required = ["hot_principle", "cold_principle", "another_cold"]
        cold_needed = state.get_cold_but_needed(required)
        
        assert "hot_principle" not in cold_needed
        assert "cold_principle" in cold_needed
        assert "another_cold" in cold_needed
    
    def test_get_activation_warnings(self):
        """Test activation warning generation."""
        tracker = ActivationTracker("test_session")
        state = tracker.capture_state()
        
        # Mock critical principle being cold
        state.principles_activation = {
            "CMC_bitemporal": 0.2,  # Cold
            "VIF_provenance": 0.8,  # Hot
            "SDF_quartet": 0.9      # Hot
        }
        state.load_level = 0.9  # High load
        state.working_attention_items = 15  # High
        
        warnings = tracker.get_activation_warnings(state)
        
        assert len(warnings) > 0
        assert any("CMC_bitemporal" in warning for warning in warnings)
        assert any("High cognitive load" in warning for warning in warnings)
        assert any("Too many working attention items" in warning for warning in warnings)


class TestActivationState:
    
    def test_initialization(self):
        """Test ActivationState initialization."""
        state = ActivationState(
            timestamp=datetime.now(UTC),
            session_id="test_session"
        )
        
        assert state.session_id == "test_session"
        assert len(state.principles_activation) == 0
        assert len(state.documents_activation) == 0
        assert len(state.concepts_activation) == 0
    
    def test_is_hot_default_threshold(self):
        """Test is_hot with default threshold."""
        state = ActivationState(
            timestamp=datetime.now(UTC),
            session_id="test_session",
            principles_activation={"test": 0.8}
        )
        
        assert state.is_hot("test")
        assert not state.is_hot("nonexistent")
    
    def test_is_cold_default_threshold(self):
        """Test is_cold with default threshold."""
        state = ActivationState(
            timestamp=datetime.now(UTC),
            session_id="test_session",
            principles_activation={"test": 0.2}
        )
        
        assert state.is_cold("test")
        assert not state.is_cold("nonexistent")
    
    def test_custom_thresholds(self):
        """Test custom thresholds for hot/cold detection."""
        state = ActivationState(
            timestamp=datetime.now(UTC),
            session_id="test_session",
            principles_activation={"test": 0.5}
        )
        
        # Custom thresholds
        assert state.is_hot("test", threshold=0.4)
        assert not state.is_hot("test", threshold=0.6)
        assert state.is_cold("test", threshold=0.6)
        assert not state.is_cold("test", threshold=0.4)
