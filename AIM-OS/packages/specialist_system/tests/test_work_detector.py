"""
Tests for Work Detector
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from specialist_system.work_detector import WorkDetector, IntentAnalysis
from specialist_system.relevance_calculator import Work


class TestWorkDetector:
    """Tests for WorkDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = WorkDetector()
    
    def test_detect_ui_work(self):
        """Test detecting UI work from message."""
        message = "Design a new button component with React and Tailwind"
        
        work = self.detector.detect_work(message)
        
        assert work.description == message
        assert 'UI' in work.domain
        assert 'React' in work.systems
        assert 'Tailwind' in work.systems
        assert 'component-patterns' in work.patterns
        assert work.complexity > 0.0
    
    def test_detect_language_work(self):
        """Test detecting language work from message."""
        message = "Define PLIx language lexicon and grammar rules"
        
        work = self.detector.detect_work(message)
        
        assert work.description == message
        assert 'Language' in work.domain
        assert 'PLIx' in work.systems
        assert 'lexicon-patterns' in work.patterns
        assert work.complexity > 0.0
    
    def test_detect_chat_work(self):
        """Test detecting chat work from message."""
        message = "Build a chat interface with real-time messaging"
        
        work = self.detector.detect_work(message)
        
        assert work.description == message
        assert 'Chat' in work.domain
        assert work.complexity > 0.0
    
    def test_detect_integration_work(self):
        """Test detecting integration work from message."""
        message = "Create REST API endpoints for user authentication"
        
        work = self.detector.detect_work(message)
        
        assert work.description == message
        assert 'Integration' in work.domain
        assert 'REST' in work.systems
        assert 'api-patterns' in work.patterns
        assert work.complexity > 0.0
    
    def test_detect_work_with_intent_analysis(self):
        """Test detecting work with intent analysis."""
        message = "Build a component"
        
        intent_analysis = IntentAnalysis(
            intent='task',
            mode='building',
            domains=['UI', 'Design'],
            systems=['React'],
            complexity=0.8
        )
        
        work = self.detector.detect_work(message, intent_analysis)
        
        assert work.description == message
        assert 'UI' in work.domain
        assert 'Design' in work.domain
        assert 'React' in work.systems
        assert work.complexity == 0.8
    
    def test_detect_ambiguous_work(self):
        """Test detecting ambiguous work."""
        message = "Help me with this"
        
        work = self.detector.detect_work(message)
        
        assert work.description == message
        # Should have low complexity
        assert work.complexity < 0.5
        # May or may not have domains/systems (ambiguous)
    
    def test_extract_domains(self):
        """Test domain extraction."""
        message = "I need to design a UI component"
        
        domains = self.detector._extract_domains(message, None)
        
        assert 'UI' in domains
    
    def test_extract_systems(self):
        """Test system extraction."""
        message = "Build with React and Vue"
        
        systems = self.detector._extract_systems(message, None)
        
        assert 'React' in systems
        assert 'Vue' in systems
    
    def test_extract_patterns(self):
        """Test pattern extraction."""
        message = "Create a reusable component pattern"
        
        patterns = self.detector._extract_patterns(message)
        
        assert 'component-patterns' in patterns
    
    def test_assess_complexity_simple(self):
        """Test complexity assessment for simple message."""
        message = "What is React?"
        
        complexity = self.detector._assess_complexity(message, None)
        
        assert complexity < 0.5  # Simple question
    
    def test_assess_complexity_complex(self):
        """Test complexity assessment for complex message."""
        message = "I need to build a complete chat interface with real-time messaging, user authentication, message threading, file uploads, emoji support, and integration with our existing REST API backend. The UI should be responsive and use React with Tailwind CSS. We also need to implement proper error handling and retry logic."
        
        complexity = self.detector._assess_complexity(message, None)
        
        assert complexity > 0.7  # Complex task
    
    def test_assess_complexity_with_intent(self):
        """Test complexity assessment with intent analysis."""
        message = "Build component"
        
        intent_analysis = IntentAnalysis(
            intent='task',
            mode='building',
            complexity=0.9
        )
        
        complexity = self.detector._assess_complexity(message, intent_analysis)
        
        assert complexity == 0.9
    
    def test_multiple_domains(self):
        """Test detecting multiple domains."""
        message = "Build a chat UI component with React"
        
        work = self.detector.detect_work(message)
        
        assert 'UI' in work.domain
        assert 'Chat' in work.domain
        assert 'React' in work.systems

