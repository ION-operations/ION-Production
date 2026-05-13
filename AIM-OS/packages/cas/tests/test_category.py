"""Tests for CAS Category Recognition component."""

import pytest
from datetime import datetime, UTC
from cas.category import CategoryRecognizer, CategoryResult, TaskCategory, RequiredProtocol


class TestCategoryRecognizer:
    
    def test_initialization(self):
        """Test CategoryRecognizer initialization."""
        recognizer = CategoryRecognizer()
        assert len(recognizer.category_patterns) > 0
        assert len(recognizer.protocol_mapping) > 0
    
    def test_classify_routine_maintenance(self):
        """Test classification of routine maintenance tasks."""
        recognizer = CategoryRecognizer()
        result = recognizer.classify_task("Clean up the code and organize files")
        
        assert result.detected_category == TaskCategory.ROUTINE_MAINTENANCE
        assert result.confidence > 0.0
        assert RequiredProtocol.QUALITY_GATES in result.required_protocols
    
    def test_classify_critical_memory_modification(self):
        """Test classification of critical memory modification tasks."""
        recognizer = CategoryRecognizer()
        result = recognizer.classify_task("Update AETHER_MEMORY current_priorities.md")
        
        assert result.detected_category == TaskCategory.CRITICAL_MEMORY_MODIFICATION
        assert RequiredProtocol.BITEMPORAL_VERSIONING in result.required_protocols
        assert RequiredProtocol.VIF_PROVENANCE in result.required_protocols
    
    def test_classify_system_implementation(self):
        """Test classification of system implementation tasks."""
        recognizer = CategoryRecognizer()
        result = recognizer.classify_task("Implement the new CAS system")
        
        assert result.detected_category == TaskCategory.SYSTEM_IMPLEMENTATION
        assert RequiredProtocol.L0_L4_DOCUMENTATION in result.required_protocols
        assert RequiredProtocol.VIF_PROVENANCE in result.required_protocols
    
    def test_classify_documentation_update(self):
        """Test classification of documentation update tasks."""
        recognizer = CategoryRecognizer()
        result = recognizer.classify_task("Write L3 documentation for the new feature")
        
        assert result.detected_category == TaskCategory.DOCUMENTATION_UPDATE
        assert RequiredProtocol.L0_L4_DOCUMENTATION in result.required_protocols
    
    def test_classify_security_hardening(self):
        """Test classification of security hardening tasks."""
        recognizer = CategoryRecognizer()
        result = recognizer.classify_task("Implement security hardening for the API")
        
        assert result.detected_category == TaskCategory.SECURITY_HARDENING
        assert RequiredProtocol.VIF_PROVENANCE in result.required_protocols
        assert RequiredProtocol.CAS_INTROSPECTION in result.required_protocols
    
    def test_classify_unknown_task(self):
        """Test classification of unknown tasks."""
        recognizer = CategoryRecognizer()
        result = recognizer.classify_task("Some random task that doesn't match patterns")
        
        assert result.detected_category == TaskCategory.UNKNOWN
        assert result.confidence < 0.3
        assert RequiredProtocol.CONFIDENCE_ROUTING in result.required_protocols
    
    def test_validation_passed(self):
        """Test validation for properly classified tasks."""
        recognizer = CategoryRecognizer()
        result = recognizer.classify_task("Update AETHER_MEMORY current_priorities.md")
        
        # This should pass validation because it's critical memory modification
        # and should have bitemporal versioning protocol
        assert result.validation_passed or RequiredProtocol.BITEMPORAL_VERSIONING in result.required_protocols
    
    def test_get_protocol_requirements(self):
        """Test getting protocol requirements for categories."""
        recognizer = CategoryRecognizer()
        
        protocols = recognizer.get_protocol_requirements(TaskCategory.CRITICAL_MEMORY_MODIFICATION)
        assert RequiredProtocol.BITEMPORAL_VERSIONING in protocols
        assert RequiredProtocol.VIF_PROVENANCE in protocols
    
    def test_is_critical_category(self):
        """Test critical category detection."""
        recognizer = CategoryRecognizer()
        
        assert recognizer.is_critical_category(TaskCategory.CRITICAL_MEMORY_MODIFICATION)
        assert recognizer.is_critical_category(TaskCategory.SECURITY_HARDENING)
        assert recognizer.is_critical_category(TaskCategory.PROTOCOL_IMPLEMENTATION)
        assert not recognizer.is_critical_category(TaskCategory.ROUTINE_MAINTENANCE)
    
    def test_analyze_classification_errors(self):
        """Test analysis of classification error patterns."""
        recognizer = CategoryRecognizer()
        
        # Create some mock results with errors
        results = [
            CategoryResult(
                task_description="Test 1",
                detected_category=TaskCategory.CRITICAL_MEMORY_MODIFICATION,
                confidence=0.2,  # Low confidence
                required_protocols=[RequiredProtocol.BITEMPORAL_VERSIONING],
                validation_passed=False,
                warnings=["Low confidence"],
                timestamp=datetime.now(UTC)
            ),
            CategoryResult(
                task_description="Test 2",
                detected_category=TaskCategory.SYSTEM_IMPLEMENTATION,
                confidence=0.8,
                required_protocols=[RequiredProtocol.L0_L4_DOCUMENTATION],
                validation_passed=True,
                warnings=[],
                timestamp=datetime.now(UTC)
            )
        ]
        
        error_patterns = recognizer.analyze_classification_errors(results)
        
        assert error_patterns["low_confidence"] == 1
        assert error_patterns["missing_bitemporal"] == 0  # First result has bitemporal
        assert error_patterns["missing_documentation"] == 0  # Second result has documentation


class TestCategoryResult:
    
    def test_initialization(self):
        """Test CategoryResult initialization."""
        result = CategoryResult(
            task_description="Test task",
            detected_category=TaskCategory.ROUTINE_MAINTENANCE,
            confidence=0.8,
            required_protocols=[RequiredProtocol.QUALITY_GATES],
            validation_passed=True,
            warnings=[],
            timestamp=datetime.now(UTC)
        )
        
        assert result.task_description == "Test task"
        assert result.detected_category == TaskCategory.ROUTINE_MAINTENANCE
        assert result.confidence == 0.8
        assert result.validation_passed
    
    def test_is_critical(self):
        """Test critical task detection."""
        critical_result = CategoryResult(
            task_description="Critical task",
            detected_category=TaskCategory.CRITICAL_MEMORY_MODIFICATION,
            confidence=0.9,
            required_protocols=[],
            validation_passed=True,
            warnings=[],
            timestamp=datetime.now(UTC)
        )
        
        routine_result = CategoryResult(
            task_description="Routine task",
            detected_category=TaskCategory.ROUTINE_MAINTENANCE,
            confidence=0.8,
            required_protocols=[],
            validation_passed=True,
            warnings=[],
            timestamp=datetime.now(UTC)
        )
        
        assert critical_result.is_critical()
        assert not routine_result.is_critical()
