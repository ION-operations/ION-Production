# ICIP Metric Calculation Service - L3 Detailed Implementation Guide

**Detail Level:** 3 of 5 (10,000 words)  
**Context Budget:** ~160k tokens  
**Purpose:** Complete implementation guide for Metric Calculation Service with AIM-OS integration

---

## Complete Implementation Guide

### Project Structure

```
packages/icip_metric_calculation_service/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── metric_calculation_service.py
│   │   ├── cpg_ingestion_service.py
│   │   ├── static_metric_calculator.py
│   │   ├── dynamic_metric_calculator.py
│   │   ├── quality_assessor.py
│   │   └── metric_aggregator.py
│   ├── calculators/
│   │   ├── __init__.py
│   │   ├── complexity_calculator.py
│   │   ├── quality_calculator.py
│   │   ├── maintainability_calculator.py
│   │   ├── security_calculator.py
│   │   ├── performance_calculator.py
│   │   └── test_calculator.py
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── trend_analyzer.py
│   │   ├── anomaly_detector.py
│   │   ├── predictive_analyzer.py
│   │   └── risk_assessor.py
│   ├── aimos_integration/
│   │   ├── __init__.py
│   │   ├── cmc_integration.py
│   │   ├── hhni_integration.py
│   │   ├── vif_integration.py
│   │   ├── tcs_integration.py
│   │   ├── apoe_integration.py
│   │   ├── seg_integration.py
│   │   └── iis_integration.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── metric_models.py
│   │   ├── calculation_models.py
│   │   ├── quality_models.py
│   │   └── trend_models.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── metric_validator.py
│   │   ├── performance_monitor.py
│   │   ├── error_handler.py
│   │   └── cache_manager.py
│   └── tests/
│       ├── __init__.py
│       ├── test_metric_calculation_service.py
│       ├── test_static_metric_calculator.py
│       ├── test_dynamic_metric_calculator.py
│       ├── test_quality_assessor.py
│       ├── test_metric_aggregator.py
│       ├── test_aimos_integration.py
│       └── test_performance.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── setup.py
```

### Core Implementation

#### Metric Calculation Service Core

```python
# packages/icip_metric_calculation_service/src/core/metric_calculation_service.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime

from ..models.metric_models import MetricResult, StaticMetricResult, DynamicMetricResult, QualityAssessment, AggregatedMetricResult
from ..models.calculation_models import CalculationRequest, CalculationResponse, CalculationOptions, CalculationStrategy
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration
from ..utils.metric_validator import MetricValidator
from ..utils.performance_monitor import PerformanceMonitor
from ..utils.error_handler import ErrorHandler
from ..utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class MetricCalculationService:
    """
    Core Metric Calculation Service implementation with AIM-OS integration.
    
    This service provides comprehensive metric calculation capabilities with seamless
    integration into the AIM-OS consciousness infrastructure.
    """
    
    def __init__(
        self,
        cmc_integration: CMCIntegration,
        hhni_integration: HHNIIntegration,
        vif_integration: VIFIntegration,
        tcs_integration: TCSIntegration,
        apoe_integration: APOEIntegration,
        seg_integration: SEGIntegration,
        iis_integration: IISIntegration,
        cache_manager: Optional[CacheManager] = None,
        performance_monitor: Optional[PerformanceMonitor] = None,
        error_handler: Optional[ErrorHandler] = None
    ):
        self.cmc = cmc_integration
        self.hhni = hhni_integration
        self.vif = vif_integration
        self.tcs = tcs_integration
        self.apoe = apoe_integration
        self.seg = seg_integration
        self.iis = iis_integration
        self.cache = cache_manager or CacheManager()
        self.performance = performance_monitor or PerformanceMonitor()
        self.error_handler = error_handler or ErrorHandler()
        
        # Initialize calculation services
        self.cpg_ingestion = CPGIngestionService(cmc_integration, vif_integration, tcs_integration)
        self.static_calculator = StaticMetricCalculator(cmc_integration, vif_integration, tcs_integration)
        self.dynamic_calculator = DynamicMetricCalculator(cmc_integration, vif_integration, tcs_integration)
        self.quality_assessor = QualityAssessor(cmc_integration, vif_integration, tcs_integration)
        self.metric_aggregator = MetricAggregator(cmc_integration, vif_integration, tcs_integration)
        
        # Initialize metric validator
        self.metric_validator = MetricValidator()
        
        logger.info("Metric Calculation Service initialized with AIM-OS integration")
    
    async def calculate_metrics(
        self,
        cpg: CPGGraph,
        language: str,
        file_path: str,
        options: Optional[CalculationOptions] = None
    ) -> CalculationResponse:
        """
        Calculate comprehensive metrics from CPG.
        
        Args:
            cpg: Code Property Graph from Graph Construction Service
            language: Programming language
            file_path: Path to the file
            options: Optional calculation options
            
        Returns:
            CalculationResponse with metrics and metadata
        """
        try:
            # Start performance monitoring
            with self.performance.monitor_operation("calculate_metrics"):
                # Create calculation request
                request = CalculationRequest(
                    cpg=cpg,
                    language=language,
                    file_path=file_path,
                    options=options or CalculationOptions()
                )
                
                # Check cache first
                cached_result = await self.cache.get_calculation_result(request)
                if cached_result:
                    logger.debug(f"Using cached calculation result for {file_path}")
                    return cached_result
                
                # Determine calculation strategy
                strategy = await self._determine_calculation_strategy(request)
                
                # Calculate metrics using selected strategy
                if strategy == CalculationStrategy.STATIC:
                    result = await self._calculate_static_metrics(request)
                elif strategy == CalculationStrategy.DYNAMIC:
                    result = await self._calculate_dynamic_metrics(request)
                elif strategy == CalculationStrategy.HYBRID:
                    result = await self._calculate_hybrid_metrics(request)
                else:
                    raise UnsupportedStrategyError(f"Unsupported strategy: {strategy}")
                
                # Validate calculated metrics
                validation_result = await self.metric_validator.validate_metrics(result.metrics)
                if not validation_result.valid:
                    raise MetricValidationError(validation_result.errors)
                
                # Create calculation response
                response = CalculationResponse(
                    metrics=result.metrics,
                    strategy=strategy,
                    performance_metrics=result.performance_metrics,
                    confidence=result.confidence,
                    timestamp=datetime.utcnow()
                )
                
                # Cache result
                await self.cache.store_calculation_result(request, response)
                
                # Stream to TCS timeline
                await self.tcs.stream_calculation_event(response)
                
                # Store in CMC
                await self._store_calculation_result_in_cmc(response)
                
                # Track with VIF
                await self._track_calculation_provenance(response)
                
                # Synthesize knowledge with SEG
                await self._synthesize_calculation_knowledge(response)
                
                # Enhance with IIS
                await self._enhance_calculation_with_iis(response)
                
                logger.info(f"Successfully calculated metrics for {file_path} using {strategy}")
                return response
                
        except Exception as e:
            logger.error(f"Error calculating metrics for {file_path}: {e}")
            await self.error_handler.handle_calculation_error(e, request)
            raise
    
    async def calculate_metrics_batch(
        self,
        files: List[Tuple[CPGGraph, str, str]],  # (cpg, language, file_path)
        options: Optional[CalculationOptions] = None
    ) -> List[CalculationResponse]:
        """
        Calculate metrics for multiple files concurrently.
        
        Args:
            files: List of (cpg, language, file_path) tuples
            options: Optional calculation options
            
        Returns:
            List of CalculationResponse objects
        """
        try:
            # Create calculation tasks
            tasks = [
                self.calculate_metrics(cpg, language, file_path, options)
                for cpg, language, file_path in files
            ]
            
            # Execute tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            responses = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error calculating metrics for file {i}: {result}")
                    # Create error response
                    error_response = CalculationResponse(
                        metrics=None,
                        strategy=None,
                        performance_metrics=None,
                        confidence=0.0,
                        timestamp=datetime.utcnow(),
                        error=str(result)
                    )
                    responses.append(error_response)
                else:
                    responses.append(result)
            
            logger.info(f"Batch calculation completed: {len(responses)} files processed")
            return responses
            
        except Exception as e:
            logger.error(f"Error in batch calculation: {e}")
            raise
    
    async def _calculate_static_metrics(self, request: CalculationRequest) -> CalculationResult:
        """Calculate static metrics from CPG."""
        try:
            # Ingest CPG
            ingestion_result = await self.cpg_ingestion.ingest_cpg(
                request.cpg, request.file_path, request.language
            )
            
            # Calculate static metrics
            static_metrics = await self.static_calculator.calculate_static_metrics(
                request.cpg, request.language
            )
            
            # Assess quality
            quality_assessment = await self.quality_assessor.assess_quality(
                request.cpg, static_metrics, None
            )
            
            # Aggregate metrics
            aggregated_metrics = await self.metric_aggregator.aggregate_metrics(
                static_metrics, None, quality_assessment
            )
            
            # Calculate performance metrics
            performance_metrics = await self.performance.get_calculation_metrics()
            
            # Calculate confidence
            confidence = await self._calculate_calculation_confidence(aggregated_metrics)
            
            return CalculationResult(
                metrics=aggregated_metrics,
                performance_metrics=performance_metrics,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error in static metric calculation: {e}")
            raise
    
    async def _calculate_dynamic_metrics(self, request: CalculationRequest) -> CalculationResult:
        """Calculate dynamic metrics from execution data."""
        try:
            # Get execution data
            execution_data = await self._get_execution_data(request.file_path)
            
            # Calculate dynamic metrics
            dynamic_metrics = await self.dynamic_calculator.calculate_dynamic_metrics(
                request.cpg, execution_data
            )
            
            # Assess quality
            quality_assessment = await self.quality_assessor.assess_quality(
                request.cpg, None, dynamic_metrics
            )
            
            # Aggregate metrics
            aggregated_metrics = await self.metric_aggregator.aggregate_metrics(
                None, dynamic_metrics, quality_assessment
            )
            
            # Calculate performance metrics
            performance_metrics = await self.performance.get_calculation_metrics()
            
            # Calculate confidence
            confidence = await self._calculate_calculation_confidence(aggregated_metrics)
            
            return CalculationResult(
                metrics=aggregated_metrics,
                performance_metrics=performance_metrics,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error in dynamic metric calculation: {e}")
            raise
    
    async def _calculate_hybrid_metrics(self, request: CalculationRequest) -> CalculationResult:
        """Calculate hybrid metrics combining static and dynamic approaches."""
        try:
            # Calculate static metrics
            static_metrics = await self.static_calculator.calculate_static_metrics(
                request.cpg, request.language
            )
            
            # Get execution data
            execution_data = await self._get_execution_data(request.file_path)
            
            # Calculate dynamic metrics
            dynamic_metrics = await self.dynamic_calculator.calculate_dynamic_metrics(
                request.cpg, execution_data
            )
            
            # Assess quality
            quality_assessment = await self.quality_assessor.assess_quality(
                request.cpg, static_metrics, dynamic_metrics
            )
            
            # Aggregate metrics
            aggregated_metrics = await self.metric_aggregator.aggregate_metrics(
                static_metrics, dynamic_metrics, quality_assessment
            )
            
            # Calculate performance metrics
            performance_metrics = await self.performance.get_calculation_metrics()
            
            # Calculate confidence
            confidence = await self._calculate_calculation_confidence(aggregated_metrics)
            
            return CalculationResult(
                metrics=aggregated_metrics,
                performance_metrics=performance_metrics,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error in hybrid metric calculation: {e}")
            raise
```

#### Static Metric Calculator Implementation

```python
# packages/icip_metric_calculation_service/src/calculators/complexity_calculator.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.metric_models import ComplexityMetrics, CyclomaticComplexity, CognitiveComplexity, HalsteadComplexity
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration

logger = logging.getLogger(__name__)

class ComplexityCalculator:
    """
    Calculates complexity metrics from CPG.
    
    Implements various complexity measurement algorithms including
    cyclomatic complexity, cognitive complexity, and Halstead complexity.
    """
    
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        logger.info("Complexity Calculator initialized")
    
    async def calculate_complexity_metrics(self, cpg: CPGGraph) -> ComplexityMetrics:
        """Calculate comprehensive complexity metrics."""
        try:
            # Cyclomatic complexity
            cyclomatic = await self._calculate_cyclomatic_complexity(cpg)
            
            # Cognitive complexity
            cognitive = await self._calculate_cognitive_complexity(cpg)
            
            # Halstead complexity
            halstead = await self._calculate_halstead_complexity(cpg)
            
            # Nesting depth
            nesting_depth = await self._calculate_nesting_depth(cpg)
            
            # Create complexity metrics
            metrics = ComplexityMetrics(
                cyclomatic=cyclomatic,
                cognitive=cognitive,
                halstead=halstead,
                nesting_depth=nesting_depth,
                timestamp=datetime.utcnow()
            )
            
            # Stream calculation events
            await self.tcs.stream_complexity_calculation_events(metrics)
            
            # Store in CMC
            await self._store_complexity_metrics_in_cmc(metrics)
            
            # Track with VIF
            await self._track_complexity_calculation_provenance(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating complexity metrics: {e}")
            raise
    
    async def _calculate_cyclomatic_complexity(self, cpg: CPGGraph) -> CyclomaticComplexity:
        """Calculate cyclomatic complexity."""
        try:
            # Count decision points
            decision_points = 0
            
            for node in cpg.nodes:
                if node.type in ['if', 'while', 'for', 'switch', 'case', 'catch', 'and', 'or']:
                    decision_points += 1
            
            # Cyclomatic complexity = decision points + 1
            complexity = decision_points + 1
            
            return CyclomaticComplexity(
                value=complexity,
                decision_points=decision_points,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error calculating cyclomatic complexity: {e}")
            raise
    
    async def _calculate_cognitive_complexity(self, cpg: CPGGraph) -> CognitiveComplexity:
        """Calculate cognitive complexity."""
        try:
            # Cognitive complexity calculation
            complexity = 0
            nesting_level = 0
            
            for node in cpg.nodes:
                if node.type in ['if', 'while', 'for', 'switch']:
                    # Base complexity
                    complexity += 1
                    
                    # Nesting complexity
                    complexity += nesting_level
                    nesting_level += 1
                elif node.type in ['else', 'elif']:
                    # Additional complexity for else/elif
                    complexity += 1
                elif node.type in ['break', 'continue', 'return']:
                    # Early exit reduces complexity
                    complexity -= 1
                elif node.type in ['end_block']:
                    # End of block, reduce nesting
                    nesting_level = max(0, nesting_level - 1)
            
            return CognitiveComplexity(
                value=complexity,
                nesting_level=nesting_level,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error calculating cognitive complexity: {e}")
            raise
    
    async def _calculate_halstead_complexity(self, cpg: CPGGraph) -> HalsteadComplexity:
        """Calculate Halstead complexity metrics."""
        try:
            # Count operators and operands
            operators = set()
            operands = set()
            
            for node in cpg.nodes:
                if node.type in ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '!']:
                    operators.add(node.name)
                elif node.type in ['variable', 'constant', 'literal']:
                    operands.add(node.name)
            
            # Calculate Halstead metrics
            n1 = len(operators)  # Distinct operators
            n2 = len(operands)   # Distinct operands
            N1 = sum(1 for node in cpg.nodes if node.type in ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '!'])  # Total operators
            N2 = sum(1 for node in cpg.nodes if node.type in ['variable', 'constant', 'literal'])  # Total operands
            
            # Halstead complexity measures
            vocabulary = n1 + n2
            length = N1 + N2
            difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
            effort = difficulty * length
            time = effort / 18  # Stroud number
            bugs = (effort ** (2/3)) / 3000
            
            return HalsteadComplexity(
                vocabulary=vocabulary,
                length=length,
                difficulty=difficulty,
                effort=effort,
                time=time,
                bugs=bugs,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error calculating Halstead complexity: {e}")
            raise
```

### AIM-OS Integration Implementation

#### CMC Integration

```python
# packages/icip_metric_calculation_service/src/aimos_integration/cmc_integration.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.metric_models import MetricResult, ComplexityMetrics, QualityMetrics, PerformanceMetrics

logger = logging.getLogger(__name__)

class CMCIntegration:
    """
    Integration with CMC (Context Memory Core) for storing metric data.
    
    Converts calculated metrics into CMC atoms with bitemporal tracking
    for persistent storage.
    """
    
    def __init__(self, cmc_client: CMCClient):
        self.cmc = cmc_client
        logger.info("CMC Integration initialized")
    
    async def convert_metrics_to_atoms(self, metrics: MetricResult) -> List[CMCAtom]:
        """Convert metric result to CMC atoms."""
        try:
            atoms = []
            
            # Convert complexity metrics to atoms
            if metrics.complexity:
                complexity_atoms = await self._convert_complexity_metrics_to_atoms(metrics.complexity)
                atoms.extend(complexity_atoms)
            
            # Convert quality metrics to atoms
            if metrics.quality:
                quality_atoms = await self._convert_quality_metrics_to_atoms(metrics.quality)
                atoms.extend(quality_atoms)
            
            # Convert performance metrics to atoms
            if metrics.performance:
                performance_atoms = await self._convert_performance_metrics_to_atoms(metrics.performance)
                atoms.extend(performance_atoms)
            
            logger.debug(f"Converted metrics to {len(atoms)} CMC atoms")
            return atoms
            
        except Exception as e:
            logger.error(f"Error converting metrics to atoms: {e}")
            raise
    
    async def store_atoms_with_bitemporal(self, atoms: List[CMCAtom]) -> None:
        """Store atoms with bitemporal tracking."""
        try:
            for atom in atoms:
                # Store with bitemporal tracking
                await self.cmc.store_atom_with_bitemporal(atom)
            
            logger.debug(f"Stored {len(atoms)} atoms with bitemporal tracking")
            
        except Exception as e:
            logger.error(f"Error storing atoms with bitemporal tracking: {e}")
            raise
```

### Testing Implementation

#### Unit Tests

```python
# packages/icip_metric_calculation_service/src/tests/test_metric_calculation_service.py

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from ..core.metric_calculation_service import MetricCalculationService
from ..models.metric_models import MetricResult, ComplexityMetrics, QualityMetrics
from ..models.calculation_models import CalculationRequest, CalculationOptions, CalculationStrategy
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration

class TestMetricCalculationService:
    """Test cases for Metric Calculation Service."""
    
    @pytest.fixture
    def mock_aimos_integrations(self):
        """Create mock AIM-OS integrations."""
        return {
            'cmc': Mock(spec=CMCIntegration),
            'hhni': Mock(spec=HHNIIntegration),
            'vif': Mock(spec=VIFIntegration),
            'tcs': Mock(spec=TCSIntegration),
            'apoe': Mock(spec=APOEIntegration),
            'seg': Mock(spec=SEGIntegration),
            'iis': Mock(spec=IISIntegration)
        }
    
    @pytest.fixture
    def metric_calculation_service(self, mock_aimos_integrations):
        """Create Metric Calculation Service instance with mock integrations."""
        return MetricCalculationService(
            cmc_integration=mock_aimos_integrations['cmc'],
            hhni_integration=mock_aimos_integrations['hhni'],
            vif_integration=mock_aimos_integrations['vif'],
            tcs_integration=mock_aimos_integrations['tcs'],
            apoe_integration=mock_aimos_integrations['apoe'],
            seg_integration=mock_aimos_integrations['seg'],
            iis_integration=mock_aimos_integrations['iis']
        )
    
    @pytest.fixture
    def sample_cpg(self):
        """Create sample CPG."""
        return CPGGraph(
            nodes=[],
            edges=[],
            metadata=CPGGraphMetadata(
                file_path="test.py",
                language="python",
                node_count=0,
                edge_count=0,
                construction_timestamp=datetime.utcnow(),
                version="1.0.0"
            )
        )
    
    @pytest.fixture
    def sample_metrics(self):
        """Create sample metrics."""
        return MetricResult(
            complexity=ComplexityMetrics(
                cyclomatic=CyclomaticComplexity(value=5, decision_points=4),
                cognitive=CognitiveComplexity(value=3, nesting_level=2),
                halstead=HalsteadComplexity(vocabulary=10, length=20, difficulty=2.5, effort=50, time=2.8, bugs=0.1),
                nesting_depth=2
            ),
            quality=QualityMetrics(
                quality_score=0.85,
                technical_debt=0.15,
                code_smells=2,
                maintainability=0.80
            ),
            performance=None,
            timestamp=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_calculate_metrics_success(self, metric_calculation_service, sample_cpg, sample_metrics):
        """Test successful metric calculation."""
        # Mock calculation result
        metric_calculation_service._calculate_static_metrics = AsyncMock(
            return_value=CalculationResult(
                metrics=sample_metrics,
                performance_metrics={},
                confidence=0.95
            )
        )
        
        # Mock metric validation
        metric_calculation_service.metric_validator.validate_metrics = AsyncMock(
            return_value=ValidationResult(valid=True, errors=[])
        )
        
        # Mock AIM-OS integrations
        metric_calculation_service.tcs.stream_calculation_event = AsyncMock()
        metric_calculation_service._store_calculation_result_in_cmc = AsyncMock()
        metric_calculation_service._track_calculation_provenance = AsyncMock()
        metric_calculation_service._synthesize_calculation_knowledge = AsyncMock()
        metric_calculation_service._enhance_calculation_with_iis = AsyncMock()
        
        # Execute calculation
        result = await metric_calculation_service.calculate_metrics(
            cpg=sample_cpg,
            language="python",
            file_path="test.py",
            options=CalculationOptions()
        )
        
        # Assertions
        assert result.metrics == sample_metrics
        assert result.strategy == CalculationStrategy.STATIC
        assert result.confidence == 0.95
        assert result.timestamp is not None
        
        # Verify AIM-OS integrations were called
        metric_calculation_service.tcs.stream_calculation_event.assert_called_once()
        metric_calculation_service._store_calculation_result_in_cmc.assert_called_once()
        metric_calculation_service._track_calculation_provenance.assert_called_once()
        metric_calculation_service._synthesize_calculation_knowledge.assert_called_once()
        metric_calculation_service._enhance_calculation_with_iis.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_metrics_batch_success(self, metric_calculation_service):
        """Test successful batch metric calculation."""
        # Mock individual calculation calls
        metric_calculation_service.calculate_metrics = AsyncMock(
            return_value=Mock()
        )
        
        # Execute batch calculation
        files = [
            (Mock(), "python", "file1.py"),
            (Mock(), "javascript", "file2.js"),
            (Mock(), "java", "file3.java")
        ]
        
        results = await metric_calculation_service.calculate_metrics_batch(files)
        
        # Assertions
        assert len(results) == 3
        assert metric_calculation_service.calculate_metrics.call_count == 3
    
    @pytest.mark.asyncio
    async def test_calculate_metrics_error_handling(self, metric_calculation_service, sample_cpg):
        """Test error handling in metric calculation."""
        # Mock calculation to raise exception
        metric_calculation_service._calculate_static_metrics = AsyncMock(
            side_effect=Exception("Calculation failed")
        )
        
        # Mock error handler
        metric_calculation_service.error_handler.handle_calculation_error = AsyncMock()
        
        # Execute calculation and expect exception
        with pytest.raises(Exception, match="Calculation failed"):
            await metric_calculation_service.calculate_metrics(
                cpg=sample_cpg,
                language="python",
                file_path="test.py",
                options=CalculationOptions()
            )
        
        # Verify error handler was called
        metric_calculation_service.error_handler.handle_calculation_error.assert_called_once()
```

This L3 detailed implementation guide provides comprehensive technical details for implementing the Metric Calculation Service with full AIM-OS integration, including complete code examples, testing strategies, and performance optimizations.
