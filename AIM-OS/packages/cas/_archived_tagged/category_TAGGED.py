"""Category Recognition Component for CAS

Detects how tasks get classified and validates against actual requirements.
Prevents categorization errors that lead to protocol violations.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


# NL_TAG: VIF-MODEL-001 | Categories for task classification. | class TaskCategory | []
class TaskCategory(str, Enum):
    """Categories for task classification."""
    ROUTINE_MAINTENANCE = "routine_maintenance"
    CRITICAL_MEMORY_MODIFICATION = "critical_memory_modification"
    SYSTEM_IMPLEMENTATION = "system_implementation"
    DOCUMENTATION_UPDATE = "documentation_update"
    TESTING_VALIDATION = "testing_validation"
    INTEGRATION_WORK = "integration_work"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_HARDENING = "security_hardening"
    PROTOCOL_IMPLEMENTATION = "protocol_implementation"
    UNKNOWN = "unknown"


# NL_TAG: VIF-MODEL-002 | Protocols that should be activated based on task category. | class RequiredProtocol | []
class RequiredProtocol(str, Enum):
    """Protocols that should be activated based on task category."""
    BITEMPORAL_VERSIONING = "bitemporal_versioning"
    L0_L4_DOCUMENTATION = "l0_l4_documentation"
    VIF_PROVENANCE = "vif_provenance"
    SDF_QUARTET_PARITY = "sdf_quartet_parity"
    APOE_ORCHESTRATION = "apoe_orchestration"
    CAS_INTROSPECTION = "cas_introspection"
    MCP_TOOL_USAGE = "mcp_tool_usage"
    CONFIDENCE_ROUTING = "confidence_routing"
    QUALITY_GATES = "quality_gates"
    NONE = "none"


@dataclass
# NL_TAG: VIF-MODEL-003 | Result of task category recognition. | class CategoryResult | []
class CategoryResult:
    """Result of task category recognition."""
    task_description: str
    detected_category: TaskCategory
    confidence: float
    required_protocols: List[RequiredProtocol]
    validation_passed: bool
    warnings: List[str]
    timestamp: datetime
    
    def is_critical(self) -> bool:
        """Check if this is a critical task requiring special protocols."""
        return self.detected_category in [
            TaskCategory.CRITICAL_MEMORY_MODIFICATION,
            TaskCategory.SECURITY_HARDENING,
            TaskCategory.PROTOCOL_IMPLEMENTATION
        ]


# NL_TAG: VIF-MODEL-004 | Recognizes task categories and validates against requirements. | class CategoryRecognizer | []
class CategoryRecognizer:
    # NL_TAG: VIF-UTIL-001 | Check if this is a critical task requiring special protocols. | is_critical(self) | []
    # NL_TAG_INTENT: VIF-INTENT-001 | Design decision: critical | is_critical | [ADR-TBD]
    def is_critical(self) -> bool:
        """Check if this is a critical task requiring special protocols."""
        return self.detected_category in [
            TaskCategory.CRITICAL_MEMORY_MODIFICATION,
            TaskCategory.SECURITY_HARDENING,
            TaskCategory.PROTOCOL_IMPLEMENTATION
        ]


class CategoryRecognizer:
    """
    Recognizes task categories and validates against requirements.
    
    Uses pattern matching and heuristics to classify tasks and determine
    which protocols should be activated.
    """
    
    # NL_TAG: VIF-UTIL-002 |   init   | __init__(self) | []
    def __init__(self):
        self.category_patterns = self._build_category_patterns()
        self.protocol_mapping = self._build_protocol_mapping()
        
    # NL_TAG: VIF-UTIL-003 | Build pattern matching rules for each category. | _build_category_patterns(self) | []
    def _build_category_patterns(self) -> Dict[TaskCategory, List[str]]:
        """Build pattern matching rules for each category."""
        return {
            TaskCategory.ROUTINE_MAINTENANCE: [
                r"routine", r"maintenance", r"cleanup", r"organize",
                r"refactor", r"optimize", r"update.*docs", r"fix.*typo"
            ],
            TaskCategory.CRITICAL_MEMORY_MODIFICATION: [
                r"modify.*memory", r"update.*AETHER_MEMORY", r"change.*priorities",
                r"edit.*current_understanding", r"modify.*decision_framework",
                r"update.*handoff_protocol", r"bitemporal", r"version.*history"
            ],
            TaskCategory.SYSTEM_IMPLEMENTATION: [
                r"implement", r"build", r"create.*system", r"develop.*feature",
                r"add.*component", r"write.*code", r"build.*package"
            ],
            TaskCategory.DOCUMENTATION_UPDATE: [
                r"document", r"write.*docs", r"update.*readme", r"create.*l[0-4]",
                r"documentation", r"readme", r"wiki", r"guide"
            ],
            TaskCategory.TESTING_VALIDATION: [
                r"test", r"validate", r"verify", r"check.*tests", r"run.*tests",
                r"testing", r"validation", r"unit.*test", r"integration.*test"
            ],
            TaskCategory.INTEGRATION_WORK: [
                r"integrate", r"connect", r"bridge", r"merge", r"combine",
                r"integration", r"connectivity", r"workflow"
            ],
            TaskCategory.PERFORMANCE_OPTIMIZATION: [
                r"optimize", r"performance", r"speed.*up", r"make.*faster",
                r"improve.*speed", r"reduce.*latency", r"increase.*throughput"
            ],
            TaskCategory.SECURITY_HARDENING: [
                r"security", r"secure", r"harden", r"vulnerability", r"threat",
                r"attack", r"encrypt", r"authentication", r"authorization"
            ],
            TaskCategory.PROTOCOL_IMPLEMENTATION: [
                r"protocol", r"standard", r"compliance", r"adhere", r"follow",
                r"implement.*protocol", r"ah.*protocol", r"l0.*l4", r"lucid"
            ]
        }
    
    # NL_TAG: VIF-UTIL-004 | Map task categories to required protocols. | _build_protocol_mapping(self) | []
    def _build_protocol_mapping(self) -> Dict[TaskCategory, List[RequiredProtocol]]:
        """Map task categories to required protocols."""
        return {
            TaskCategory.ROUTINE_MAINTENANCE: [
                RequiredProtocol.QUALITY_GATES,
                RequiredProtocol.CONFIDENCE_ROUTING
            ],
            TaskCategory.CRITICAL_MEMORY_MODIFICATION: [
                RequiredProtocol.BITEMPORAL_VERSIONING,
                RequiredProtocol.VIF_PROVENANCE,
                RequiredProtocol.L0_L4_DOCUMENTATION,
                RequiredProtocol.CAS_INTROSPECTION,
                RequiredProtocol.QUALITY_GATES
            ],
            TaskCategory.SYSTEM_IMPLEMENTATION: [
                RequiredProtocol.L0_L4_DOCUMENTATION,
                RequiredProtocol.VIF_PROVENANCE,
                RequiredProtocol.SDF_QUARTET_PARITY,
                RequiredProtocol.APOE_ORCHESTRATION,
                RequiredProtocol.QUALITY_GATES,
                RequiredProtocol.CONFIDENCE_ROUTING
            ],
            TaskCategory.DOCUMENTATION_UPDATE: [
                RequiredProtocol.L0_L4_DOCUMENTATION,
                RequiredProtocol.VIF_PROVENANCE,
                RequiredProtocol.QUALITY_GATES
            ],
            TaskCategory.TESTING_VALIDATION: [
                RequiredProtocol.VIF_PROVENANCE,
                RequiredProtocol.SDF_QUARTET_PARITY,
                RequiredProtocol.QUALITY_GATES
            ],
            TaskCategory.INTEGRATION_WORK: [
                RequiredProtocol.APOE_ORCHESTRATION,
                RequiredProtocol.VIF_PROVENANCE,
                RequiredProtocol.QUALITY_GATES,
                RequiredProtocol.CONFIDENCE_ROUTING
            ],
            TaskCategory.PERFORMANCE_OPTIMIZATION: [
                RequiredProtocol.VIF_PROVENANCE,
                RequiredProtocol.QUALITY_GATES,
                RequiredProtocol.CONFIDENCE_ROUTING
            ],
            TaskCategory.SECURITY_HARDENING: [
                RequiredProtocol.VIF_PROVENANCE,
                RequiredProtocol.SDF_QUARTET_PARITY,
                RequiredProtocol.QUALITY_GATES,
                RequiredProtocol.CAS_INTROSPECTION
            ],
            TaskCategory.PROTOCOL_IMPLEMENTATION: [
                RequiredProtocol.L0_L4_DOCUMENTATION,
                RequiredProtocol.VIF_PROVENANCE,
                RequiredProtocol.SDF_QUARTET_PARITY,
                RequiredProtocol.CAS_INTROSPECTION,
                RequiredProtocol.QUALITY_GATES
            ],
            TaskCategory.UNKNOWN: [
                RequiredProtocol.CONFIDENCE_ROUTING,
                RequiredProtocol.QUALITY_GATES
            ]
        }
    
    # NL_TAG: VIF-MODEL-005 | Classify a task and determine required protocols. | classify_task(self, task_description) | []
    def classify_task(self, task_description: str) -> CategoryResult:
        """
        Classify a task and determine required protocols.
        
        Args:
            task_description: Description of the task to classify
            
        Returns:
            CategoryResult with classification and protocol requirements
        """
        task_lower = task_description.lower()
        
        # Find best matching category
        best_category = TaskCategory.UNKNOWN
        best_confidence = 0.0
        matched_patterns = []
        
        for category, patterns in self.category_patterns.items():
            category_confidence = 0.0
            category_matches = []
            
            for pattern in patterns:
                if re.search(pattern, task_lower):
                    category_matches.append(pattern)
                    category_confidence += 0.3  # Each pattern match adds confidence
            
            # Boost confidence for multiple matches
            if len(category_matches) > 1:
                category_confidence += 0.2
            
            if category_confidence > best_confidence:
                best_confidence = category_confidence
                best_category = category
                matched_patterns = category_matches
        
        # Normalize confidence to 0.0-1.0
        confidence = min(1.0, best_confidence)
        
        # Get required protocols
        required_protocols = self.protocol_mapping.get(best_category, [])
        
        # Validate classification
        validation_passed, warnings = self._validate_classification(
            best_category, confidence, required_protocols, task_description
        )
        
        return CategoryResult(
            task_description=task_description,
            detected_category=best_category,
            confidence=confidence,
            required_protocols=required_protocols,
            validation_passed=validation_passed,
            warnings=warnings,
            timestamp=datetime.utcnow()
        )
    
    # NL_TAG: VIF-MODEL-006 | Validate the classification result. | _validate_classification(self, category, confidence, protocols, task_description) | []
    # NL_TAG_SPEC: VIF-SPEC-001 | Validates _validate_classification specification | _validate_classification | [spec_file_TBD]
    def _validate_classification(
        self,
        category: TaskCategory,
        confidence: float,
        protocols: List[RequiredProtocol],
        task_description: str
    ) -> tuple[bool, List[str]]:
        """
        Validate the classification result.
        
        Returns:
            (validation_passed, warnings)
        """
        warnings = []
        
        # Check confidence threshold
        if confidence < 0.3:
            warnings.append(f"Low confidence classification: {confidence:.2f}")
        
        # Check for critical tasks with insufficient protocols
        if category == TaskCategory.CRITICAL_MEMORY_MODIFICATION:
            if RequiredProtocol.BITEMPORAL_VERSIONING not in protocols:
                warnings.append("Critical memory modification missing bitemporal versioning protocol")
                return False, warnings
        
        # Check for implementation tasks without documentation protocol
        if category in [TaskCategory.SYSTEM_IMPLEMENTATION, TaskCategory.PROTOCOL_IMPLEMENTATION]:
            if RequiredProtocol.L0_L4_DOCUMENTATION not in protocols:
                warnings.append("Implementation task missing L0-L4 documentation protocol")
                return False, warnings
        
        # Check for security tasks without proper protocols
        if category == TaskCategory.SECURITY_HARDENING:
            if RequiredProtocol.VIF_PROVENANCE not in protocols:
                warnings.append("Security task missing VIF provenance protocol")
                return False, warnings
        
        validation_passed = len(warnings) == 0
        return validation_passed, warnings
    
    # NL_TAG: VIF-UTIL-005 | Get required protocols for a given category. | get_protocol_requirements(self, category) | []
    def get_protocol_requirements(self, category: TaskCategory) -> List[RequiredProtocol]:
        """Get required protocols for a given category."""
        return self.protocol_mapping.get(category, [])
    
    # NL_TAG: VIF-UTIL-006 | Check if a category requires critical protocols. | is_critical_category(self, category) | []
    # NL_TAG_INTENT: VIF-INTENT-002 | Design decision: critical | is_critical_category | [ADR-TBD]
    def is_critical_category(self, category: TaskCategory) -> bool:
        """Check if a category requires critical protocols."""
        return category in [
            TaskCategory.CRITICAL_MEMORY_MODIFICATION,
            TaskCategory.SECURITY_HARDENING,
            TaskCategory.PROTOCOL_IMPLEMENTATION
        ]
    
    # NL_TAG: VIF-MODEL-007 | Analyze patterns in classification errors. | analyze_classification_errors(self, results) | []
    def analyze_classification_errors(self, results: List[CategoryResult]) -> Dict[str, int]:
        """
        Analyze patterns in classification errors.
        
        Returns:
            Dictionary of error patterns and their frequencies
        """
        error_patterns = {
            "low_confidence": 0,
            "missing_bitemporal": 0,
            "missing_documentation": 0,
            "missing_vif": 0,
            "critical_without_protocols": 0
        }
        
        for result in results:
            if result.confidence < 0.3:
                error_patterns["low_confidence"] += 1
            
            if result.detected_category == TaskCategory.CRITICAL_MEMORY_MODIFICATION:
                if RequiredProtocol.BITEMPORAL_VERSIONING not in result.required_protocols:
                    error_patterns["missing_bitemporal"] += 1
            
            if result.detected_category in [TaskCategory.SYSTEM_IMPLEMENTATION, TaskCategory.PROTOCOL_IMPLEMENTATION]:
                if RequiredProtocol.L0_L4_DOCUMENTATION not in result.required_protocols:
                    error_patterns["missing_documentation"] += 1
            
            if result.detected_category == TaskCategory.SECURITY_HARDENING:
                if RequiredProtocol.VIF_PROVENANCE not in result.required_protocols:
                    error_patterns["missing_vif"] += 1
            
            if result.is_critical() and not result.validation_passed:
                error_patterns["critical_without_protocols"] += 1
        
        return error_patterns
