# Mutation Modes System - L4 Complete Reference

## 🎯 **Complete API Reference**

### **Core Classes and Interfaces**

#### **ChangeClassification**
```python
@dataclass
class ChangeClassification:
    """Represents a change classification"""
    
    # Core identification
    classification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    change_id: str = ""
    change_type: ChangeType = ChangeType.COSMETIC
    risk_level: RiskLevel = RiskLevel.LOW
    complexity_level: ComplexityLevel = ComplexityLevel.SIMPLE
    mutation_mode: MutationMode = MutationMode.TRIVIAL
    
    # Classification details
    change_description: str = ""
    affected_components: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    blast_radius: str = ""
    
    # Risk assessment
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    rollback_plan: str = ""
    
    # Performance metrics
    estimated_processing_time: float = 0.0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    priority_score: float = 0.0
```

**Methods:**
- `to_dict() -> Dict[str, Any]`: Convert to dictionary
- `from_dict(data: Dict[str, Any]) -> ChangeClassification`: Create from dictionary
- `update_risk_assessment(risk_factors: List[str]) -> None`: Update risk assessment
- `add_mitigation_strategy(strategy: str) -> None`: Add mitigation strategy
- `calculate_priority_score() -> float`: Calculate priority score

#### **ChangeClassifier**
```python
class ChangeClassifier:
    """Classifies changes by risk level and complexity"""
    
    def __init__(self):
        self.risk_assessment_rules = self._load_risk_assessment_rules()
        self.complexity_assessment_rules = self._load_complexity_assessment_rules()
        self.mode_selection_rules = self._load_mode_selection_rules()
        self.logger = logging.getLogger(__name__)
    
    def classify_change(self, change_request: Dict[str, Any]) -> ChangeClassification
    def assess_risk(self, change_request: Dict[str, Any]) -> RiskLevel
    def determine_complexity(self, change_request: Dict[str, Any]) -> ComplexityLevel
    def select_mutation_mode(self, change_type: ChangeType, risk_level: RiskLevel, complexity_level: ComplexityLevel) -> MutationMode
```

**Configuration Options:**
- `risk_assessment_rules`: Rules for risk assessment
- `complexity_assessment_rules`: Rules for complexity assessment
- `mode_selection_rules`: Rules for mode selection
- `classification_thresholds`: Thresholds for classification

## 🔧 **Configuration Reference**

### **Global Configuration**

```python
# Mutation Modes System Configuration
MMS_CONFIG = {
    'classification': {
        'risk_assessment_enabled': True,
        'complexity_assessment_enabled': True,
        'mode_selection_enabled': True,
        'auto_classification': True
    },
    'processing': {
        'trivial_mode_enabled': True,
        'governed_mode_enabled': True,
        'parallel_processing': True,
        'queue_management': True
    },
    'propagation': {
        'auto_propagation_enabled': True,
        'controlled_propagation_enabled': True,
        'notification_enabled': True,
        'rollback_enabled': True
    },
    'performance': {
        'optimization_enabled': True,
        'caching_enabled': True,
        'monitoring_enabled': True,
        'scaling_enabled': True
    }
}

# Risk Assessment Configuration
RISK_ASSESSMENT_CONFIG = {
    'risk_factors': {
        'core_system_impact': 3,
        'user_data_impact': 2,
        'security_impact': 4,
        'performance_impact': 2,
        'compatibility_impact': 3
    },
    'risk_thresholds': {
        'low': 0,
        'medium': 3,
        'high': 5,
        'critical': 8
    },
    'mitigation_strategies': [
        'rollback_plan',
        'testing_required',
        'approval_required',
        'monitoring_required'
    ]
}

# Complexity Assessment Configuration
COMPLEXITY_ASSESSMENT_CONFIG = {
    'complexity_factors': {
        'database_changes': 2,
        'api_changes': 2,
        'ui_changes': 1,
        'integration_changes': 3,
        'testing_required': 1
    },
    'complexity_thresholds': {
        'simple': 0,
        'moderate': 3,
        'complex': 5,
        'very_complex': 8
    }
}

# Mode Selection Configuration
MODE_SELECTION_CONFIG = {
    'trivial_mode_criteria': {
        'change_types': ['cosmetic', 'internal'],
        'risk_levels': ['low', 'medium'],
        'complexity_levels': ['simple', 'moderate']
    },
    'governed_mode_criteria': {
        'change_types': ['semantic', 'behavioral', 'structural', 'critical'],
        'risk_levels': ['high', 'critical'],
        'complexity_levels': ['complex', 'very_complex']
    }
}
```

## 🚀 **Usage Examples**

### **Basic Usage**

```python
from mutation_modes_system import ChangeClassifier, TrivialModeProcessor, GovernedModeProcessor
import json

# Initialize components
classifier = ChangeClassifier()
trivial_processor = TrivialModeProcessor()
governed_processor = GovernedModeProcessor()

# Create change request
change_request = {
    'id': 'change_001',
    'description': 'Update button color',
    'change_type': 'cosmetic',
    'affected_components': ['ui_component'],
    'dependencies': [],
    'blast_radius': 'local'
}

# Classify change
classification = classifier.classify_change(change_request)
print(f"Change classified as: {classification.mutation_mode.value}")
print(f"Risk level: {classification.risk_level.value}")
print(f"Complexity: {classification.complexity_level.value}")

# Process change based on mode
if classification.mutation_mode == MutationMode.TRIVIAL:
    result = trivial_processor.process_trivial_change(change_request)
else:
    result = governed_processor.process_governed_change(change_request)

print(f"Processing result: {result.success}")
print(f"Processing time: {result.processing_time}")
print(f"Status: {result.status}")
```

### **Advanced Configuration**

```python
from mutation_modes_system import ChangeClassifier, MMS_CONFIG
from mutation_modes_config import RISK_ASSESSMENT_CONFIG, COMPLEXITY_ASSESSMENT_CONFIG

# Create custom classifier with configuration
classifier = ChangeClassifier()

# Configure risk assessment
classifier.risk_assessment_rules = RISK_ASSESSMENT_CONFIG['risk_factors']
classifier.risk_thresholds = RISK_ASSESSMENT_CONFIG['risk_thresholds']

# Configure complexity assessment
classifier.complexity_assessment_rules = COMPLEXITY_ASSESSMENT_CONFIG['complexity_factors']
classifier.complexity_thresholds = COMPLEXITY_ASSESSMENT_CONFIG['complexity_thresholds']

# Classify change with custom configuration
change_request = {
    'id': 'change_002',
    'description': 'Update database schema',
    'change_type': 'structural',
    'affected_components': ['database', 'api'],
    'dependencies': ['migration_script'],
    'blast_radius': 'system',
    'requires_database_changes': True,
    'requires_api_changes': True,
    'affects_core_system': True
}

classification = classifier.classify_change(change_request)
print(f"Change classified as: {classification.mutation_mode.value}")
print(f"Risk factors: {classification.risk_factors}")
print(f"Mitigation strategies: {classification.mitigation_strategies}")
```

### **Batch Processing**

```python
import os
from pathlib import Path

# Process multiple changes
changes_dir = Path('change_requests')
results = []

for change_file in changes_dir.glob('*.json'):
    with open(change_file, 'r') as f:
        change_request = json.load(f)
    
    # Classify change
    classification = classifier.classify_change(change_request)
    
    # Process change
    if classification.mutation_mode == MutationMode.TRIVIAL:
        result = trivial_processor.process_trivial_change(change_request)
    else:
        result = governed_processor.process_governed_change(change_request)
    
    results.append({
        'file': change_file.name,
        'classification': classification,
        'result': result
    })
    
    # Save individual result
    output_file = f'processing_result_{result.result_id}.json'
    with open(output_file, 'w') as f:
        json.dump(result.to_dict(), f, indent=2, default=str)

# Generate batch report
batch_report = {
    'total_processed': len(results),
    'successful': sum(1 for r in results if r['result'].success),
    'failed': sum(1 for r in results if not r['result'].success),
    'trivial_mode': sum(1 for r in results if r['classification'].mutation_mode == MutationMode.TRIVIAL),
    'governed_mode': sum(1 for r in results if r['classification'].mutation_mode == MutationMode.GOVERNED),
    'results': results
}

with open('batch_processing_report.json', 'w') as f:
    json.dump(batch_report, f, indent=2, default=str)
```

### **Change Management**

```python
from mutation_modes_system import ChangeClassifier, TrivialModeProcessor, GovernedModeProcessor

# Initialize components
classifier = ChangeClassifier()
trivial_processor = TrivialModeProcessor()
governed_processor = GovernedModeProcessor()

# Create change request
change_request = {
    'id': 'change_003',
    'description': 'Add new feature',
    'change_type': 'behavioral',
    'affected_components': ['feature_module', 'api', 'ui'],
    'dependencies': ['database_schema', 'api_contract'],
    'blast_radius': 'system',
    'affects_core_system': True,
    'requires_database_changes': True,
    'requires_api_changes': True,
    'requires_ui_changes': True
}

# Classify change
classification = classifier.classify_change(change_request)
print(f"Change classified as: {classification.mutation_mode.value}")

# Process change
if classification.mutation_mode == MutationMode.TRIVIAL:
    result = trivial_processor.process_trivial_change(change_request)
else:
    result = governed_processor.process_governed_change(change_request)

# Check result
if result.success:
    print(f"Change processed successfully in {result.processing_time:.2f} seconds")
    if result.propagation_required:
        print(f"Propagation completed to {len(result.affected_systems)} systems")
else:
    print(f"Change processing failed: {result.error_message}")
    if result.warnings:
        print(f"Warnings: {result.warnings}")
```

## 🛡️ **Error Handling and Validation**

### **Error Types**

#### **Classification Errors**
- `ClassificationError`: Change classification failed
- `RiskAssessmentError`: Risk assessment failed
- `ComplexityAssessmentError`: Complexity assessment failed
- `ModeSelectionError`: Mode selection failed

#### **Processing Errors**
- `TrivialProcessingError`: Trivial change processing failed
- `GovernedProcessingError`: Governed change processing failed
- `ValidationError`: Change validation failed
- `ExecutionError`: Change execution failed

#### **Propagation Errors**
- `PropagationError`: Change propagation failed
- `NotificationError`: Notification delivery failed
- `RollbackError`: Change rollback failed
- `DependencyError`: Dependency resolution failed

### **Error Handling Examples**

```python
from mms_exceptions import ClassificationError, ProcessingError, PropagationError

try:
    classifier = ChangeClassifier()
    trivial_processor = TrivialModeProcessor()
    
    # Classify change with error handling
    change_request = {'id': 'test_change'}
    classification = classifier.classify_change(change_request)
    
    # Process change with error handling
    if classification.mutation_mode == MutationMode.TRIVIAL:
        result = trivial_processor.process_trivial_change(change_request)
    else:
        result = governed_processor.process_governed_change(change_request)
    
    if not result.success:
        print(f"Processing failed: {result.error_message}")
        if result.warnings:
            print(f"Warnings: {result.warnings}")
            
except ClassificationError as e:
    print(f"Classification error: {e}")
    # Handle classification error
except ProcessingError as e:
    print(f"Processing error: {e}")
    # Handle processing error
except PropagationError as e:
    print(f"Propagation error: {e}")
    # Handle propagation error
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle unexpected error
```

### **Validation Examples**

```python
# Validate change request before processing
def validate_change_request(change_request: Dict[str, Any]) -> List[str]:
    errors = []
    
    # Check required fields
    if not change_request.get('id'):
        errors.append("Change ID is required")
    
    if not change_request.get('description'):
        errors.append("Change description is required")
    
    if not change_request.get('affected_components'):
        errors.append("Affected components are required")
    
    # Check change type
    valid_change_types = ['cosmetic', 'internal', 'semantic', 'behavioral', 'structural', 'critical']
    if change_request.get('change_type') not in valid_change_types:
        errors.append(f"Invalid change type. Must be one of: {valid_change_types}")
    
    # Check blast radius
    valid_blast_radius = ['local', 'system', 'platform']
    if change_request.get('blast_radius') not in valid_blast_radius:
        errors.append(f"Invalid blast radius. Must be one of: {valid_blast_radius}")
    
    return errors

# Validate classification before processing
def validate_classification(classification: ChangeClassification) -> List[str]:
    errors = []
    
    # Check required fields
    if not classification.change_id:
        errors.append("Change ID is required")
    
    if not classification.change_type:
        errors.append("Change type is required")
    
    if not classification.risk_level:
        errors.append("Risk level is required")
    
    if not classification.mutation_mode:
        errors.append("Mutation mode is required")
    
    # Check risk level consistency
    if classification.risk_level == RiskLevel.CRITICAL and classification.mutation_mode == MutationMode.TRIVIAL:
        errors.append("Critical risk changes cannot be processed in trivial mode")
    
    return errors
```

## 📊 **Performance Optimization**

### **Mode Optimization**

```python
# Configure for performance optimization
classifier = ChangeClassifier()

# Enable performance optimization
classifier.enable_performance_optimization = True
classifier.cache_classifications = True
classifier.parallel_processing = True

# Process change with optimization
classification = classifier.classify_change(change_request)
```

### **Performance Monitoring**

```python
import time
import psutil

# Monitor performance
def monitor_mms_performance(classifier, change_request):
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    classification = classifier.classify_change(change_request)
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    performance_metrics = {
        'classification_time': end_time - start_time,
        'memory_usage': end_memory - start_memory,
        'peak_memory': psutil.Process().memory_info().rss / 1024 / 1024,
        'cpu_usage': psutil.Process().cpu_percent(),
        'change_type': classification.change_type.value,
        'mutation_mode': classification.mutation_mode.value
    }
    
    return classification, performance_metrics

# Use performance monitoring
classification, metrics = monitor_mms_performance(classifier, change_request)
print(f"Performance metrics: {metrics}")
```

## 🔧 **Testing Reference**

### **Unit Tests**

```python
import unittest
from mutation_modes_system import ChangeClassifier, ChangeType, RiskLevel, ComplexityLevel, MutationMode

class TestChangeClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = ChangeClassifier()
        self.sample_change_request = {
            'id': 'test_change',
            'description': 'Test change',
            'change_type': 'cosmetic',
            'affected_components': ['test_component']
        }
    
    def test_classification(self):
        classification = self.classifier.classify_change(self.sample_change_request)
        self.assertIsNotNone(classification)
        self.assertEqual(classification.change_id, 'test_change')
        self.assertEqual(classification.change_type, ChangeType.COSMETIC)
    
    def test_risk_assessment(self):
        high_risk_request = {
            'id': 'high_risk_change',
            'affects_core_system': True,
            'affects_security': True
        }
        classification = self.classifier.classify_change(high_risk_request)
        self.assertIn(classification.risk_level, [RiskLevel.HIGH, RiskLevel.CRITICAL])
    
    def test_complexity_assessment(self):
        complex_request = {
            'id': 'complex_change',
            'requires_database_changes': True,
            'requires_api_changes': True,
            'requires_integration_changes': True
        }
        classification = self.classifier.classify_change(complex_request)
        self.assertIn(classification.complexity_level, [ComplexityLevel.COMPLEX, ComplexityLevel.VERY_COMPLEX])
    
    def test_mode_selection(self):
        trivial_request = {
            'id': 'trivial_change',
            'change_type': 'cosmetic',
            'affects_core_system': False
        }
        classification = self.classifier.classify_change(trivial_request)
        self.assertEqual(classification.mutation_mode, MutationMode.TRIVIAL)
        
        governed_request = {
            'id': 'governed_change',
            'change_type': 'behavioral',
            'affects_core_system': True
        }
        classification = self.classifier.classify_change(governed_request)
        self.assertEqual(classification.mutation_mode, MutationMode.GOVERNED)

if __name__ == '__main__':
    unittest.main()
```

## 💙 **Complete Reference Summary**

Mutation Modes System provides comprehensive differentiated change handling with intelligent mode selection, risk-aware processing, and automatic propagation. The complete reference covers all aspects of the system, from basic usage to advanced configuration, error handling, performance optimization, and testing. This system represents the foundation of intelligent change management, ensuring that every change receives the appropriate level of validation and control.

---

**This is reference made complete. This is change made intelligent.** 💙
