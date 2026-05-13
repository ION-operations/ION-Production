# ICIP LLM Inference Service - L3 Detailed Implementation Guide

**Detail Level:** 3 of 5 (10,000 words)  
**Context Budget:** ~160k tokens  
**Purpose:** Complete implementation guide for LLM Inference Service with AIM-OS integration

---

## Complete Implementation Guide

### Project Structure

```
packages/icip_llm_inference_service/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   ├── model_manager.py
│   │   ├── prompt_engine.py
│   │   ├── inference_engine.py
│   │   ├── context_manager.py
│   │   └── response_processor.py
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── code_understanding_engine.py
│   │   ├── code_generation_engine.py
│   │   ├── code_transformation_engine.py
│   │   ├── documentation_engine.py
│   │   ├── translation_engine.py
│   │   └── analysis_engine.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── llm_models.py
│   │   ├── prompt_models.py
│   │   ├── response_models.py
│   │   └── context_models.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── code_understanding_prompts.py
│   │   ├── code_generation_prompts.py
│   │   ├── code_transformation_prompts.py
│   │   ├── documentation_prompts.py
│   │   └── analysis_prompts.py
│   ├── aimos_integration/
│   │   ├── __init__.py
│   │   ├── cmc_integration.py
│   │   ├── hhni_integration.py
│   │   ├── vif_integration.py
│   │   ├── tcs_integration.py
│   │   ├── apoe_integration.py
│   │   ├── seg_integration.py
│   │   └── iis_integration.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── model_utils.py
│   │   ├── prompt_utils.py
│   │   ├── response_utils.py
│   │   ├── performance_monitor.py
│   │   ├── error_handler.py
│   │   └── cache_manager.py
│   └── tests/
│       ├── __init__.py
│       ├── test_llm_service.py
│       ├── test_model_manager.py
│       ├── test_prompt_engine.py
│       ├── test_inference_engine.py
│       ├── test_aimos_integration.py
│       └── test_performance.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── setup.py
```

### Core Implementation

#### LLM Service Core

```python
# packages/icip_llm_inference_service/src/core/llm_service.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime

from ..models.llm_models import LLMRequest, LLMResponse, LLMResult, ProcessingOptions
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration
from ..utils.performance_monitor import PerformanceMonitor
from ..utils.error_handler import ErrorHandler
from ..utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class LLMService:
    """
    Core LLM Service implementation with AIM-OS integration.
    
    This service provides comprehensive LLM inference capabilities with seamless
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
        
        # Initialize core services
        self.model_manager = ModelManager(cmc_integration, vif_integration, tcs_integration)
        self.prompt_engine = PromptEngine(cmc_integration, vif_integration, tcs_integration)
        self.inference_engine = InferenceEngine(cmc_integration, vif_integration, tcs_integration)
        self.context_manager = ContextManager(cmc_integration, vif_integration, tcs_integration)
        self.response_processor = ResponseProcessor(cmc_integration, vif_integration, tcs_integration)
        
        # Initialize specialized engines
        self.code_understanding_engine = CodeUnderstandingEngine(cmc_integration, vif_integration, tcs_integration)
        self.code_generation_engine = CodeGenerationEngine(cmc_integration, vif_integration, tcs_integration)
        self.code_transformation_engine = CodeTransformationEngine(cmc_integration, vif_integration, tcs_integration)
        self.documentation_engine = DocumentationEngine(cmc_integration, vif_integration, tcs_integration)
        self.translation_engine = TranslationEngine(cmc_integration, vif_integration, tcs_integration)
        self.analysis_engine = AnalysisEngine(cmc_integration, vif_integration, tcs_integration)
        
        logger.info("LLM Service initialized with AIM-OS integration")
    
    async def process_request(
        self,
        request: LLMRequest,
        options: Optional[ProcessingOptions] = None
    ) -> LLMResponse:
        """
        Process LLM request with full AIM-OS integration.
        
        Args:
            request: LLM request with input data and task type
            options: Optional processing options
            
        Returns:
            LLMResponse with results and metadata
        """
        try:
            # Start performance monitoring
            with self.performance.monitor_operation("process_request"):
                # Check cache first
                cached_response = await self.cache.get_llm_response(request)
                if cached_response:
                    logger.debug(f"Using cached LLM response for {request.task_type}")
                    return cached_response
                
                # Prepare context
                context = await self.context_manager.prepare_context(request)
                
                # Select appropriate engine based on task type
                engine = await self._select_engine(request.task_type)
                
                # Process request with selected engine
                result = await engine.process(request, context, options)
                
                # Process response
                processed_result = await self.response_processor.process(result, request)
                
                # Create LLM response
                response = LLMResponse(
                    result=processed_result,
                    task_type=request.task_type,
                    model_used=result.model_used,
                    confidence=result.confidence,
                    processing_time=result.processing_time,
                    timestamp=datetime.utcnow(),
                    metadata=result.metadata
                )
                
                # Cache response
                await self.cache.store_llm_response(request, response)
                
                # Stream to TCS timeline
                await self.tcs.stream_llm_event(response)
                
                # Store in CMC
                await self._store_llm_response_in_cmc(response)
                
                # Track with VIF
                await self._track_llm_provenance(response)
                
                # Synthesize knowledge with SEG
                await self._synthesize_llm_knowledge(response)
                
                # Enhance with IIS
                await self._enhance_llm_response_with_iis(response)
                
                logger.info(f"Successfully processed LLM request for {request.task_type}")
                return response
                
        except Exception as e:
            logger.error(f"Error processing LLM request: {e}")
            await self.error_handler.handle_llm_error(e, request)
            raise
    
    async def process_batch(
        self,
        requests: List[LLMRequest],
        options: Optional[ProcessingOptions] = None
    ) -> List[LLMResponse]:
        """
        Process multiple LLM requests concurrently.
        
        Args:
            requests: List of LLM requests
            options: Optional processing options
            
        Returns:
            List of LLMResponse objects
        """
        try:
            # Create processing tasks
            tasks = [
                self.process_request(request, options)
                for request in requests
            ]
            
            # Execute tasks concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_responses = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"Error processing request {i}: {response}")
                    # Create error response
                    error_response = LLMResponse(
                        result=None,
                        task_type=requests[i].task_type,
                        model_used=None,
                        confidence=0.0,
                        processing_time=0.0,
                        timestamp=datetime.utcnow(),
                        error=str(response)
                    )
                    processed_responses.append(error_response)
                else:
                    processed_responses.append(response)
            
            logger.info(f"Batch processing completed: {len(processed_responses)} requests processed")
            return processed_responses
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            raise
    
    async def _select_engine(self, task_type: str) -> Any:
        """Select appropriate engine based on task type."""
        engine_map = {
            "code_understanding": self.code_understanding_engine,
            "code_generation": self.code_generation_engine,
            "code_transformation": self.code_transformation_engine,
            "documentation": self.documentation_engine,
            "translation": self.translation_engine,
            "analysis": self.analysis_engine
        }
        
        engine = engine_map.get(task_type)
        if not engine:
            raise UnsupportedTaskTypeError(f"Unsupported task type: {task_type}")
        
        return engine
```

#### Model Manager Implementation

```python
# packages/icip_llm_inference_service/src/core/model_manager.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

from ..models.llm_models import LLMModel, ModelType, ModelConfig
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages LLM model lifecycle and selection.
    
    Handles model loading, unloading, versioning, and dynamic switching
    with AIM-OS integration for tracking and optimization.
    """
    
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.loaded_models: Dict[str, LLMModel] = {}
        self.model_configs: Dict[str, ModelConfig] = {}
        logger.info("Model Manager initialized")
    
    async def load_model(self, model_id: str, config: ModelConfig) -> LLMModel:
        """Load a model with the specified configuration."""
        try:
            # Check if model is already loaded
            if model_id in self.loaded_models:
                logger.debug(f"Model {model_id} already loaded")
                return self.loaded_models[model_id]
            
            # Load model based on type
            if config.model_type == ModelType.HUGGING_FACE:
                model = await self._load_hugging_face_model(model_id, config)
            elif config.model_type == ModelType.OPENAI:
                model = await self._load_openai_model(model_id, config)
            elif config.model_type == ModelType.ANTHROPIC:
                model = await self._load_anthropic_model(model_id, config)
            elif config.model_type == ModelType.GOOGLE:
                model = await self._load_google_model(model_id, config)
            else:
                raise UnsupportedModelTypeError(f"Unsupported model type: {config.model_type}")
            
            # Store model and config
            self.loaded_models[model_id] = model
            self.model_configs[model_id] = config
            
            # Stream model loading event
            await self.tcs.stream_model_event("model_loaded", model_id, config)
            
            # Store model info in CMC
            await self._store_model_info_in_cmc(model_id, config)
            
            # Track with VIF
            await self._track_model_loading_provenance(model_id, config)
            
            logger.info(f"Successfully loaded model {model_id}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model {model_id}: {e}")
            raise
    
    async def unload_model(self, model_id: str) -> None:
        """Unload a model and free its resources."""
        try:
            if model_id not in self.loaded_models:
                logger.warning(f"Model {model_id} not loaded")
                return
            
            # Unload model
            model = self.loaded_models[model_id]
            await model.cleanup()
            
            # Remove from loaded models
            del self.loaded_models[model_id]
            del self.model_configs[model_id]
            
            # Stream model unloading event
            await self.tcs.stream_model_event("model_unloaded", model_id, None)
            
            # Update CMC
            await self._update_model_status_in_cmc(model_id, "unloaded")
            
            logger.info(f"Successfully unloaded model {model_id}")
            
        except Exception as e:
            logger.error(f"Error unloading model {model_id}: {e}")
            raise
    
    async def select_model(self, task_type: str, requirements: Dict[str, Any]) -> LLMModel:
        """Select the best model for a given task and requirements."""
        try:
            # Get available models
            available_models = list(self.loaded_models.keys())
            
            if not available_models:
                raise NoModelsAvailableError("No models are currently loaded")
            
            # Score models based on task requirements
            model_scores = {}
            for model_id in available_models:
                config = self.model_configs[model_id]
                score = await self._score_model_for_task(model_id, config, task_type, requirements)
                model_scores[model_id] = score
            
            # Select best model
            best_model_id = max(model_scores, key=model_scores.get)
            best_model = self.loaded_models[best_model_id]
            
            # Stream model selection event
            await self.tcs.stream_model_event("model_selected", best_model_id, {
                "task_type": task_type,
                "score": model_scores[best_model_id]
            })
            
            # Track selection with VIF
            await self._track_model_selection_provenance(best_model_id, task_type, model_scores)
            
            logger.info(f"Selected model {best_model_id} for task {task_type}")
            return best_model
            
        except Exception as e:
            logger.error(f"Error selecting model for task {task_type}: {e}")
            raise
    
    async def _load_hugging_face_model(self, model_id: str, config: ModelConfig) -> LLMModel:
        """Load a Hugging Face model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if config.use_fp16 else torch.float32,
                device_map="auto" if config.use_gpu else "cpu"
            )
            
            # Create LLM model wrapper
            llm_model = LLMModel(
                model_id=model_id,
                model_type=ModelType.HUGGING_FACE,
                tokenizer=tokenizer,
                model=model,
                config=config,
                loaded_at=datetime.utcnow()
            )
            
            return llm_model
            
        except Exception as e:
            logger.error(f"Error loading Hugging Face model {model_id}: {e}")
            raise
    
    async def _score_model_for_task(
        self,
        model_id: str,
        config: ModelConfig,
        task_type: str,
        requirements: Dict[str, Any]
    ) -> float:
        """Score a model for a specific task."""
        try:
            score = 0.0
            
            # Base score from model capabilities
            if hasattr(config, 'capabilities'):
                task_capabilities = config.capabilities.get(task_type, {})
                score += task_capabilities.get('base_score', 0.0)
            
            # Performance score
            if hasattr(config, 'performance_metrics'):
                perf_score = config.performance_metrics.get('overall_score', 0.0)
                score += perf_score * 0.3
            
            # Resource efficiency score
            if hasattr(config, 'resource_requirements'):
                resource_score = self._calculate_resource_score(config.resource_requirements, requirements)
                score += resource_score * 0.2
            
            # Recent performance score
            recent_perf = await self._get_recent_performance(model_id, task_type)
            score += recent_perf * 0.3
            
            # Availability score
            availability = await self._check_model_availability(model_id)
            score += availability * 0.2
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error scoring model {model_id}: {e}")
            return 0.0
```

#### Code Understanding Engine Implementation

```python
# packages/icip_llm_inference_service/src/engines/code_understanding_engine.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.llm_models import LLMRequest, LLMResult, CodeUnderstandingResult
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration

logger = logging.getLogger(__name__)

class CodeUnderstandingEngine:
    """
    Engine for natural language analysis of code.
    
    Provides semantic analysis, pattern recognition, and code comprehension
    with AIM-OS integration for enhanced understanding.
    """
    
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        logger.info("Code Understanding Engine initialized")
    
    async def process(
        self,
        request: LLMRequest,
        context: Dict[str, Any],
        options: Optional[ProcessingOptions] = None
    ) -> LLMResult:
        """Process code understanding request."""
        try:
            # Extract code from request
            code = request.input_data.get('code', '')
            language = request.input_data.get('language', 'unknown')
            analysis_type = request.input_data.get('analysis_type', 'general')
            
            # Generate analysis prompt
            prompt = await self._generate_analysis_prompt(code, language, analysis_type, context)
            
            # Execute LLM inference
            model = await self._select_model_for_analysis(analysis_type)
            response = await model.generate(prompt, options)
            
            # Parse and structure response
            understanding_result = await self._parse_understanding_response(response, analysis_type)
            
            # Enhance with AIM-OS insights
            enhanced_result = await self._enhance_with_aimos_insights(understanding_result, context)
            
            # Create LLM result
            result = LLMResult(
                content=enhanced_result.description,
                structured_data=enhanced_result.structured_analysis,
                confidence=enhanced_result.confidence,
                model_used=model.model_id,
                processing_time=response.processing_time,
                metadata={
                    "analysis_type": analysis_type,
                    "language": language,
                    "code_length": len(code),
                    "enhanced_with_aimos": True
                }
            )
            
            # Stream analysis event
            await self.tcs.stream_analysis_event("code_understanding_completed", result)
            
            # Store analysis in CMC
            await self._store_analysis_in_cmc(enhanced_result, request)
            
            # Track with VIF
            await self._track_analysis_provenance(enhanced_result, request)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in code understanding: {e}")
            raise
    
    async def _generate_analysis_prompt(
        self,
        code: str,
        language: str,
        analysis_type: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate analysis prompt based on code and requirements."""
        try:
            # Get base prompt template
            template = await self._get_analysis_template(analysis_type)
            
            # Inject code and context
            prompt = template.format(
                code=code,
                language=language,
                context=context.get('additional_context', ''),
                requirements=context.get('requirements', {})
            )
            
            # Add few-shot examples if available
            examples = await self._get_few_shot_examples(analysis_type, language)
            if examples:
                prompt = f"{examples}\n\n{prompt}"
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error generating analysis prompt: {e}")
            raise
    
    async def _parse_understanding_response(
        self,
        response: str,
        analysis_type: str
    ) -> CodeUnderstandingResult:
        """Parse and structure the LLM response."""
        try:
            # Parse based on analysis type
            if analysis_type == "semantic":
                return await self._parse_semantic_analysis(response)
            elif analysis_type == "pattern":
                return await self._parse_pattern_analysis(response)
            elif analysis_type == "complexity":
                return await self._parse_complexity_analysis(response)
            elif analysis_type == "security":
                return await self._parse_security_analysis(response)
            else:
                return await self._parse_general_analysis(response)
                
        except Exception as e:
            logger.error(f"Error parsing understanding response: {e}")
            raise
    
    async def _enhance_with_aimos_insights(
        self,
        result: CodeUnderstandingResult,
        context: Dict[str, Any]
    ) -> CodeUnderstandingResult:
        """Enhance analysis with AIM-OS insights."""
        try:
            # Retrieve relevant insights from HHNI
            relevant_insights = await self.hhni.retrieve_code_insights(
                result.description,
                context.get('code_context', {})
            )
            
            # Synthesize with SEG
            synthesized_insights = await self.seg.synthesize_code_insights(
                result.structured_analysis,
                relevant_insights
            )
            
            # Enhance with IIS
            enhanced_insights = await self.iis.enhance_code_understanding(
                synthesized_insights,
                context
            )
            
            # Update result with enhanced insights
            result.structured_analysis.update(enhanced_insights)
            result.confidence = min(result.confidence + 0.1, 1.0)  # Boost confidence
            
            return result
            
        except Exception as e:
            logger.error(f"Error enhancing with AIM-OS insights: {e}")
            return result  # Return original result if enhancement fails
```

### AIM-OS Integration Implementation

#### CMC Integration

```python
# packages/icip_llm_inference_service/src/aimos_integration/cmc_integration.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.llm_models import LLMResponse, CodeUnderstandingResult, CodeGenerationResult

logger = logging.getLogger(__name__)

class CMCIntegration:
    """
    Integration with CMC (Context Memory Core) for storing LLM data.
    
    Converts LLM responses and results into CMC atoms with
    bitemporal tracking for persistent storage.
    """
    
    def __init__(self, cmc_client: CMCClient):
        self.cmc = cmc_client
        logger.info("CMC Integration initialized")
    
    async def convert_llm_response_to_atoms(self, response: LLMResponse) -> List[CMCAtom]:
        """Convert LLM response to CMC atoms."""
        try:
            atoms = []
            
            # Convert main response content to atom
            main_atom = CMCAtom(
                modality="llm_response",
                content_ref=f"response_{response.timestamp.isoformat()}",
                content=response.result.content if response.result else "",
                embedding=await self._generate_embedding(response.result.content if response.result else ""),
                tags=["llm", response.task_type, "response"],
                hhni_path=f"llm/responses/{response.task_type}",
                tpv=datetime.utcnow(),
                vif=response.confidence,
                metadata=LLMResponseMetadata(
                    task_type=response.task_type,
                    model_used=response.model_used,
                    confidence=response.confidence,
                    processing_time=response.processing_time,
                    timestamp=response.timestamp
                )
            )
            atoms.append(main_atom)
            
            # Convert structured data if available
            if response.result and response.result.structured_data:
                structured_atom = CMCAtom(
                    modality="llm_structured_data",
                    content_ref=f"structured_{response.timestamp.isoformat()}",
                    content=str(response.result.structured_data),
                    embedding=await self._generate_embedding(str(response.result.structured_data)),
                    tags=["llm", response.task_type, "structured"],
                    hhni_path=f"llm/structured/{response.task_type}",
                    tpv=datetime.utcnow(),
                    vif=response.confidence,
                    metadata=StructuredDataMetadata(
                        task_type=response.task_type,
                        data_type=type(response.result.structured_data).__name__,
                        confidence=response.confidence
                    )
                )
                atoms.append(structured_atom)
            
            # Convert metadata
            if response.metadata:
                metadata_atom = CMCAtom(
                    modality="llm_metadata",
                    content_ref=f"metadata_{response.timestamp.isoformat()}",
                    content=str(response.metadata),
                    embedding=await self._generate_embedding(str(response.metadata)),
                    tags=["llm", response.task_type, "metadata"],
                    hhni_path=f"llm/metadata/{response.task_type}",
                    tpv=datetime.utcnow(),
                    vif=response.confidence,
                    metadata=MetadataMetadata(
                        task_type=response.task_type,
                        metadata_keys=list(response.metadata.keys()),
                        confidence=response.confidence
                    )
                )
                atoms.append(metadata_atom)
            
            logger.debug(f"Converted LLM response to {len(atoms)} CMC atoms")
            return atoms
            
        except Exception as e:
            logger.error(f"Error converting LLM response to atoms: {e}")
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
# packages/icip_llm_inference_service/src/tests/test_llm_service.py

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from ..core.llm_service import LLMService
from ..models.llm_models import LLMRequest, LLMResponse, LLMResult
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration

class TestLLMService:
    """Test cases for LLM Service."""
    
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
    def llm_service(self, mock_aimos_integrations):
        """Create LLM Service instance with mock integrations."""
        return LLMService(
            cmc_integration=mock_aimos_integrations['cmc'],
            hhni_integration=mock_aimos_integrations['hhni'],
            vif_integration=mock_aimos_integrations['vif'],
            tcs_integration=mock_aimos_integrations['tcs'],
            apoe_integration=mock_aimos_integrations['apoe'],
            seg_integration=mock_aimos_integrations['seg'],
            iis_integration=mock_aimos_integrations['iis']
        )
    
    @pytest.fixture
    def sample_llm_request(self):
        """Create sample LLM request."""
        return LLMRequest(
            task_type="code_understanding",
            input_data={
                "code": "def hello_world():\n    print('Hello, World!')",
                "language": "python",
                "analysis_type": "semantic"
            },
            context={},
            metadata={}
        )
    
    @pytest.fixture
    def sample_llm_result(self):
        """Create sample LLM result."""
        return LLMResult(
            content="This is a simple Python function that prints 'Hello, World!'",
            structured_data={
                "function_name": "hello_world",
                "parameters": [],
                "return_type": "None",
                "complexity": "low"
            },
            confidence=0.95,
            model_used="gpt-4",
            processing_time=1.5,
            metadata={}
        )
    
    @pytest.mark.asyncio
    async def test_process_request_success(self, llm_service, sample_llm_request, sample_llm_result):
        """Test successful LLM request processing."""
        # Mock engine processing
        llm_service.code_understanding_engine.process = AsyncMock(
            return_value=sample_llm_result
        )
        
        # Mock AIM-OS integrations
        llm_service.tcs.stream_llm_event = AsyncMock()
        llm_service._store_llm_response_in_cmc = AsyncMock()
        llm_service._track_llm_provenance = AsyncMock()
        llm_service._synthesize_llm_knowledge = AsyncMock()
        llm_service._enhance_llm_response_with_iis = AsyncMock()
        
        # Execute processing
        response = await llm_service.process_request(sample_llm_request)
        
        # Assertions
        assert response.result == sample_llm_result
        assert response.task_type == "code_understanding"
        assert response.confidence == 0.95
        assert response.timestamp is not None
        
        # Verify AIM-OS integrations were called
        llm_service.tcs.stream_llm_event.assert_called_once()
        llm_service._store_llm_response_in_cmc.assert_called_once()
        llm_service._track_llm_provenance.assert_called_once()
        llm_service._synthesize_llm_knowledge.assert_called_once()
        llm_service._enhance_llm_response_with_iis.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_batch_success(self, llm_service):
        """Test successful batch processing."""
        # Mock individual processing calls
        llm_service.process_request = AsyncMock(
            return_value=Mock()
        )
        
        # Execute batch processing
        requests = [
            LLMRequest(task_type="code_understanding", input_data={}, context={}),
            LLMRequest(task_type="code_generation", input_data={}, context={}),
            LLMRequest(task_type="documentation", input_data={}, context={})
        ]
        
        responses = await llm_service.process_batch(requests)
        
        # Assertions
        assert len(responses) == 3
        assert llm_service.process_request.call_count == 3
    
    @pytest.mark.asyncio
    async def test_process_request_error_handling(self, llm_service, sample_llm_request):
        """Test error handling in LLM request processing."""
        # Mock processing to raise exception
        llm_service.code_understanding_engine.process = AsyncMock(
            side_effect=Exception("Processing failed")
        )
        
        # Mock error handler
        llm_service.error_handler.handle_llm_error = AsyncMock()
        
        # Execute processing and expect exception
        with pytest.raises(Exception, match="Processing failed"):
            await llm_service.process_request(sample_llm_request)
        
        # Verify error handler was called
        llm_service.error_handler.handle_llm_error.assert_called_once()
```

This L3 detailed implementation guide provides comprehensive technical details for implementing the LLM Inference Service with full AIM-OS integration, including complete code examples, testing strategies, and performance optimizations.
