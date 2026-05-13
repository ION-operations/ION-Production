# ICIP Data Ingestion Layer - L3 Detailed Implementation Guide

**Detail Level:** 3 of 5 (10,000 words)  
**Context Budget:** ~160k tokens  
**Purpose:** Complete implementation guide for Data Ingestion Layer with AIM-OS integration

---

## Complete Implementation Guide

### Project Structure

```
packages/icip_data_ingestion/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ingestion_service.py
│   │   ├── data_collector.py
│   │   ├── data_processor.py
│   │   ├── data_validator.py
│   │   ├── data_transformer.py
│   │   ├── data_enricher.py
│   │   └── data_router.py
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── base_connector.py
│   │   ├── git_connector.py
│   │   ├── svn_connector.py
│   │   ├── file_system_connector.py
│   │   ├── s3_connector.py
│   │   ├── api_connector.py
│   │   └── webhook_connector.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── code_processor.py
│   │   ├── metadata_processor.py
│   │   ├── dependency_processor.py
│   │   ├── config_processor.py
│   │   └── documentation_processor.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── data_models.py
│   │   ├── collection_models.py
│   │   ├── processing_models.py
│   │   └── storage_models.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── raw_storage.py
│   │   ├── processed_storage.py
│   │   ├── metadata_storage.py
│   │   └── index_storage.py
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
│   │   ├── data_utils.py
│   │   ├── validation_utils.py
│   │   ├── transformation_utils.py
│   │   ├── performance_monitor.py
│   │   └── error_handler.py
│   └── tests/
│       ├── __init__.py
│       ├── test_ingestion_service.py
│       ├── test_connectors.py
│       ├── test_processors.py
│       ├── test_aimos_integration.py
│       └── test_performance.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── setup.py
```

### Core Implementation

#### Data Ingestion Service

```python
# packages/icip_data_ingestion/src/core/ingestion_service.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime

from ..models.data_models import IngestionRequest, IngestionResponse, CollectedData, ProcessedData
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration
from ..utils.performance_monitor import PerformanceMonitor
from ..utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class IngestionService:
    """
    Core Data Ingestion Service with AIM-OS integration.
    
    This service provides comprehensive data collection capabilities with seamless
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
        self.performance = performance_monitor or PerformanceMonitor()
        self.error_handler = error_handler or ErrorHandler()
        
        # Initialize core components
        self.data_collector = DataCollector(cmc_integration, vif_integration, tcs_integration)
        self.data_processor = DataProcessor(cmc_integration, vif_integration, tcs_integration)
        self.data_validator = DataValidator(cmc_integration, vif_integration, tcs_integration)
        self.data_transformer = DataTransformer(cmc_integration, vif_integration, tcs_integration)
        self.data_enricher = DataEnricher(cmc_integration, vif_integration, tcs_integration)
        self.data_router = DataRouter(cmc_integration, vif_integration, tcs_integration)
        
        logger.info("Data Ingestion Service initialized with AIM-OS integration")
    
    async def ingest_data(
        self,
        request: IngestionRequest
    ) -> IngestionResponse:
        """
        Execute data ingestion with full AIM-OS integration.
        
        Args:
            request: Ingestion request with source configuration
            
        Returns:
            IngestionResponse with collected data and metadata
        """
        try:
            # Start performance monitoring
            with self.performance.monitor_operation("data_ingestion"):
                # Collect data from source
                collected_data = await self.data_collector.collect_data(request.source_config)
                
                # Validate collected data
                validation_result = await self.data_validator.validate_data(collected_data)
                if not validation_result.is_valid:
                    raise DataValidationError(f"Data validation failed: {validation_result.errors}")
                
                # Process collected data
                processed_data = await self.data_processor.process_data(collected_data)
                
                # Transform processed data
                transformed_data = await self.data_transformer.transform_data(processed_data)
                
                # Enrich transformed data
                enriched_data = await self.data_enricher.enrich_data(transformed_data)
                
                # Route enriched data
                routing_result = await self.data_router.route_data(enriched_data, request.routing_config)
                
                # Create ingestion response
                response = IngestionResponse(
                    collected_data=collected_data,
                    processed_data=processed_data,
                    transformed_data=transformed_data,
                    enriched_data=enriched_data,
                    routing_result=routing_result,
                    source_config=request.source_config,
                    ingestion_time=datetime.utcnow(),
                    metadata=collected_data.metadata
                )
                
                # Stream to TCS timeline
                await self.tcs.stream_ingestion_event(response)
                
                # Store in CMC
                await self._store_ingestion_data_in_cmc(response)
                
                # Track with VIF
                await self._track_ingestion_provenance(response)
                
                # Synthesize knowledge with SEG
                await self._synthesize_ingestion_knowledge(response)
                
                # Enhance with IIS
                await self._enhance_ingestion_with_iis(response)
                
                logger.info(f"Successfully ingested data from source: {request.source_config.source_id}")
                return response
                
        except Exception as e:
            logger.error(f"Error ingesting data: {e}")
            await self.error_handler.handle_ingestion_error(e, request)
            raise
    
    async def ingest_batch(
        self,
        requests: List[IngestionRequest]
    ) -> List[IngestionResponse]:
        """
        Execute multiple data ingestion operations concurrently.
        
        Args:
            requests: List of ingestion requests
            
        Returns:
            List of IngestionResponse objects
        """
        try:
            # Create ingestion tasks
            tasks = [
                self.ingest_data(request)
                for request in requests
            ]
            
            # Execute tasks concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_responses = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"Error ingesting data {i}: {response}")
                    # Create error response
                    error_response = IngestionResponse(
                        collected_data=None,
                        processed_data=None,
                        transformed_data=None,
                        enriched_data=None,
                        routing_result=None,
                        source_config=requests[i].source_config,
                        ingestion_time=datetime.utcnow(),
                        error=str(response)
                    )
                    processed_responses.append(error_response)
                else:
                    processed_responses.append(response)
            
            logger.info(f"Batch ingestion completed: {len(processed_responses)} operations executed")
            return processed_responses
            
        except Exception as e:
            logger.error(f"Error in batch ingestion: {e}")
            raise
```

#### Data Collector Implementation

```python
# packages/icip_data_ingestion/src/core/data_collector.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.data_models import SourceConfig, CollectedData, CollectionMetadata
from ..connectors.base_connector import BaseConnector
from ..connectors.git_connector import GitConnector
from ..connectors.file_system_connector import FileSystemConnector
from ..connectors.s3_connector import S3Connector
from ..connectors.api_connector import APIConnector
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration

logger = logging.getLogger(__name__)

class DataCollector:
    """
    Data collector for various sources with AIM-OS integration.
    
    Collects data from different sources using appropriate connectors
    and integrates with AIM-OS systems for tracking and storage.
    """
    
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.connectors = {
            "git": GitConnector(),
            "file_system": FileSystemConnector(),
            "s3": S3Connector(),
            "api": APIConnector()
        }
        logger.info("Data Collector initialized")
    
    async def collect_data(self, source_config: SourceConfig) -> CollectedData:
        """Collect data from source using appropriate connector."""
        try:
            # Get appropriate connector
            connector = self.connectors.get(source_config.source_type)
            if not connector:
                raise UnsupportedSourceTypeError(f"Unsupported source type: {source_config.source_type}")
            
            # Collect data
            raw_data = await connector.collect(source_config)
            
            # Create collection metadata
            metadata = CollectionMetadata(
                source_id=source_config.source_id,
                source_type=source_config.source_type,
                collection_time=datetime.utcnow(),
                data_size=len(raw_data.content),
                quality_score=await self._calculate_quality_score(raw_data),
                validation_status="pending"
            )
            
            # Create collected data
            collected_data = CollectedData(
                source_id=source_config.source_id,
                source_type=source_config.source_type,
                content=raw_data.content,
                metadata=raw_data.metadata,
                collection_metadata=metadata,
                timestamp=datetime.utcnow()
            )
            
            # Stream collection event
            await self.tcs.stream_collection_event("data_collected", {
                "source_id": source_config.source_id,
                "source_type": source_config.source_type,
                "data_size": len(raw_data.content),
                "quality_score": metadata.quality_score
            })
            
            # Store collection in CMC
            await self._store_collection_in_cmc(collected_data)
            
            # Track with VIF
            await self._track_collection_provenance(collected_data)
            
            logger.info(f"Successfully collected data from source: {source_config.source_id}")
            return collected_data
            
        except Exception as e:
            logger.error(f"Error collecting data: {e}")
            raise
    
    async def _calculate_quality_score(self, raw_data: Any) -> float:
        """Calculate quality score for collected data."""
        try:
            # Base quality score
            base_score = 0.8
            
            # Content quality factors
            content_score = await self._assess_content_quality(raw_data.content)
            
            # Metadata quality factors
            metadata_score = await self._assess_metadata_quality(raw_data.metadata)
            
            # Combine scores
            quality_score = (base_score * 0.4 + content_score * 0.3 + metadata_score * 0.3)
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating quality score: {e}")
            return 0.5  # Default fallback
    
    async def _assess_content_quality(self, content: str) -> float:
        """Assess content quality."""
        try:
            # Check content length
            if len(content) == 0:
                return 0.0
            
            # Check for encoding issues
            try:
                content.encode('utf-8')
                encoding_score = 1.0
            except UnicodeEncodeError:
                encoding_score = 0.5
            
            # Check for structure
            structure_score = 0.8  # Placeholder
            
            # Combine scores
            content_score = (encoding_score * 0.6 + structure_score * 0.4)
            
            return content_score
            
        except Exception as e:
            logger.error(f"Error assessing content quality: {e}")
            return 0.5
    
    async def _assess_metadata_quality(self, metadata: Dict[str, Any]) -> float:
        """Assess metadata quality."""
        try:
            # Check metadata completeness
            required_fields = ["source_id", "source_type", "timestamp"]
            completeness_score = sum(1 for field in required_fields if field in metadata) / len(required_fields)
            
            # Check metadata consistency
            consistency_score = 0.8  # Placeholder
            
            # Combine scores
            metadata_score = (completeness_score * 0.7 + consistency_score * 0.3)
            
            return metadata_score
            
        except Exception as e:
            logger.error(f"Error assessing metadata quality: {e}")
            return 0.5
```

#### Git Connector Implementation

```python
# packages/icip_data_ingestion/src/connectors/git_connector.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import subprocess
import tempfile
import os
import shutil

from ..models.data_models import SourceConfig, RawData, GitMetadata
from .base_connector import BaseConnector

logger = logging.getLogger(__name__)

class GitConnector(BaseConnector):
    """
    Git connector for collecting data from Git repositories.
    
    Supports cloning, fetching, and monitoring Git repositories
    with comprehensive metadata collection.
    """
    
    def __init__(self):
        super().__init__()
        self.temp_dirs = []
        logger.info("Git Connector initialized")
    
    async def collect(self, source_config: SourceConfig) -> RawData:
        """Collect data from Git repository."""
        try:
            # Validate source config
            if not source_config.url:
                raise ValueError("Git URL is required")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            self.temp_dirs.append(temp_dir)
            
            # Clone repository
            await self._clone_repository(source_config.url, temp_dir, source_config.branch)
            
            # Collect repository data
            repository_data = await self._collect_repository_data(temp_dir, source_config)
            
            # Create raw data
            raw_data = RawData(
                content=repository_data.content,
                metadata=repository_data.metadata,
                source_type="git",
                timestamp=datetime.utcnow()
            )
            
            logger.info(f"Successfully collected data from Git repository: {source_config.url}")
            return raw_data
            
        except Exception as e:
            logger.error(f"Error collecting data from Git repository: {e}")
            raise
    
    async def _clone_repository(self, url: str, temp_dir: str, branch: Optional[str] = None) -> None:
        """Clone Git repository to temporary directory."""
        try:
            # Build git clone command
            cmd = ["git", "clone", url, temp_dir]
            if branch:
                cmd.extend(["-b", branch])
            
            # Execute git clone
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise GitCloneError(f"Failed to clone repository: {result.stderr}")
            
            logger.debug(f"Successfully cloned repository to: {temp_dir}")
            
        except subprocess.TimeoutExpired:
            raise GitCloneError("Git clone operation timed out")
        except Exception as e:
            raise GitCloneError(f"Error cloning repository: {e}")
    
    async def _collect_repository_data(self, repo_dir: str, source_config: SourceConfig) -> Any:
        """Collect data from cloned repository."""
        try:
            # Collect file data
            file_data = await self._collect_file_data(repo_dir)
            
            # Collect commit history
            commit_history = await self._collect_commit_history(repo_dir)
            
            # Collect branch information
            branch_info = await self._collect_branch_info(repo_dir)
            
            # Collect repository metadata
            repo_metadata = await self._collect_repository_metadata(repo_dir)
            
            # Create repository data
            repository_data = RepositoryData(
                content=file_data,
                metadata=GitMetadata(
                    commit_history=commit_history,
                    branch_info=branch_info,
                    repository_metadata=repo_metadata,
                    source_config=source_config
                )
            )
            
            return repository_data
            
        except Exception as e:
            logger.error(f"Error collecting repository data: {e}")
            raise
    
    async def _collect_file_data(self, repo_dir: str) -> str:
        """Collect file data from repository."""
        try:
            file_data = []
            
            # Walk through repository directory
            for root, dirs, files in os.walk(repo_dir):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_dir)
                    
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Add file data
                        file_data.append(f"=== {relative_path} ===\n{content}\n")
                        
                    except UnicodeDecodeError:
                        # Skip binary files
                        logger.debug(f"Skipping binary file: {relative_path}")
                        continue
                    except Exception as e:
                        logger.warning(f"Error reading file {relative_path}: {e}")
                        continue
            
            return "\n".join(file_data)
            
        except Exception as e:
            logger.error(f"Error collecting file data: {e}")
            raise
    
    async def _collect_commit_history(self, repo_dir: str) -> List[Dict[str, Any]]:
        """Collect commit history from repository."""
        try:
            # Get commit history
            cmd = ["git", "log", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"]
            result = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Failed to get commit history: {result.stderr}")
                return []
            
            # Parse commit history
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 4)
                    if len(parts) == 5:
                        commit = {
                            "hash": parts[0],
                            "author_name": parts[1],
                            "author_email": parts[2],
                            "date": parts[3],
                            "message": parts[4]
                        }
                        commits.append(commit)
            
            return commits
            
        except Exception as e:
            logger.error(f"Error collecting commit history: {e}")
            return []
    
    async def _collect_branch_info(self, repo_dir: str) -> Dict[str, Any]:
        """Collect branch information from repository."""
        try:
            # Get branch information
            cmd = ["git", "branch", "-a"]
            result = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Failed to get branch info: {result.stderr}")
                return {}
            
            # Parse branch information
            branches = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    branch_name = line.strip().lstrip('* ').replace('remotes/origin/', '')
                    branches.append(branch_name)
            
            # Get current branch
            cmd = ["git", "branch", "--show-current"]
            result = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
            current_branch = result.stdout.strip() if result.returncode == 0 else None
            
            return {
                "branches": branches,
                "current_branch": current_branch
            }
            
        except Exception as e:
            logger.error(f"Error collecting branch info: {e}")
            return {}
    
    async def _collect_repository_metadata(self, repo_dir: str) -> Dict[str, Any]:
        """Collect repository metadata."""
        try:
            metadata = {}
            
            # Get repository URL
            cmd = ["git", "remote", "get-url", "origin"]
            result = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
            if result.returncode == 0:
                metadata["remote_url"] = result.stdout.strip()
            
            # Get repository size
            cmd = ["du", "-sh", repo_dir]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                metadata["size"] = result.stdout.strip().split()[0]
            
            # Get file count
            cmd = ["find", repo_dir, "-type", "f", "! -path", "*/.*", "|", "wc", "-l"]
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                metadata["file_count"] = int(result.stdout.strip())
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error collecting repository metadata: {e}")
            return {}
    
    def cleanup(self) -> None:
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Error cleaning up temporary directory {temp_dir}: {e}")
        self.temp_dirs.clear()
```

### AIM-OS Integration Implementation

#### CMC Integration

```python
# packages/icip_data_ingestion/src/aimos_integration/cmc_integration.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.data_models import IngestionResponse, CollectedData, ProcessedData

logger = logging.getLogger(__name__)

class CMCIntegration:
    """
    Integration with CMC (Context Memory Core) for storing ingestion data.
    
    Converts ingestion data into CMC atoms with bitemporal tracking
    for persistent storage and retrieval.
    """
    
    def __init__(self, cmc_client: CMCClient):
        self.cmc = cmc_client
        logger.info("CMC Integration initialized")
    
    async def convert_ingestion_response_to_atoms(self, response: IngestionResponse) -> List[CMCAtom]:
        """Convert ingestion response to CMC atoms."""
        try:
            atoms = []
            
            # Convert collected data to atom
            if response.collected_data:
                collected_atom = CMCAtom(
                    modality="data_collection",
                    content_ref=f"collected_{response.ingestion_time.isoformat()}",
                    content=response.collected_data.content,
                    embedding=await self._generate_embedding(response.collected_data.content),
                    tags=["ingestion", "collected", response.collected_data.source_type],
                    hhni_path=f"ingestion/collected/{response.collected_data.source_id}",
                    tpv=datetime.utcnow(),
                    vif=response.collected_data.collection_metadata.quality_score,
                    metadata=CollectedDataMetadata(
                        source_id=response.collected_data.source_id,
                        source_type=response.collected_data.source_type,
                        collection_time=response.collected_data.timestamp,
                        data_size=len(response.collected_data.content),
                        quality_score=response.collected_data.collection_metadata.quality_score
                    )
                )
                atoms.append(collected_atom)
            
            # Convert processed data to atom
            if response.processed_data:
                processed_atom = CMCAtom(
                    modality="data_processing",
                    content_ref=f"processed_{response.ingestion_time.isoformat()}",
                    content=response.processed_data.content,
                    embedding=await self._generate_embedding(response.processed_data.content),
                    tags=["ingestion", "processed", response.processed_data.data_type],
                    hhni_path=f"ingestion/processed/{response.processed_data.data_id}",
                    tpv=datetime.utcnow(),
                    vif=response.processed_data.quality_score,
                    metadata=ProcessedDataMetadata(
                        data_id=response.processed_data.data_id,
                        data_type=response.processed_data.data_type,
                        processing_time=response.processed_data.processing_time,
                        quality_score=response.processed_data.quality_score
                    )
                )
                atoms.append(processed_atom)
            
            # Convert enriched data to atom
            if response.enriched_data:
                enriched_atom = CMCAtom(
                    modality="data_enrichment",
                    content_ref=f"enriched_{response.ingestion_time.isoformat()}",
                    content=response.enriched_data.content,
                    embedding=await self._generate_embedding(response.enriched_data.content),
                    tags=["ingestion", "enriched", response.enriched_data.data_type],
                    hhni_path=f"ingestion/enriched/{response.enriched_data.data_id}",
                    tpv=datetime.utcnow(),
                    vif=response.enriched_data.quality_score,
                    metadata=EnrichedDataMetadata(
                        data_id=response.enriched_data.data_id,
                        data_type=response.enriched_data.data_type,
                        enrichment_time=response.enriched_data.enrichment_time,
                        quality_score=response.enriched_data.quality_score,
                        enrichment_metadata=response.enriched_data.enrichment_metadata
                    )
                )
                atoms.append(enriched_atom)
            
            logger.debug(f"Converted ingestion response to {len(atoms)} CMC atoms")
            return atoms
            
        except Exception as e:
            logger.error(f"Error converting ingestion response to atoms: {e}")
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
# packages/icip_data_ingestion/src/tests/test_ingestion_service.py

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from ..core.ingestion_service import IngestionService
from ..models.data_models import IngestionRequest, SourceConfig
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration

class TestIngestionService:
    """Test cases for Ingestion Service."""
    
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
    def ingestion_service(self, mock_aimos_integrations):
        """Create Ingestion Service instance with mock integrations."""
        return IngestionService(
            cmc_integration=mock_aimos_integrations['cmc'],
            hhni_integration=mock_aimos_integrations['hhni'],
            vif_integration=mock_aimos_integrations['vif'],
            tcs_integration=mock_aimos_integrations['tcs'],
            apoe_integration=mock_aimos_integrations['apoe'],
            seg_integration=mock_aimos_integrations['seg'],
            iis_integration=mock_aimos_integrations['iis']
        )
    
    @pytest.fixture
    def sample_ingestion_request(self):
        """Create sample ingestion request."""
        return IngestionRequest(
            source_config=SourceConfig(
                source_id="test_repo",
                source_type="git",
                url="https://github.com/test/repo.git",
                branch="main"
            ),
            routing_config={}
        )
    
    @pytest.mark.asyncio
    async def test_ingest_data_success(self, ingestion_service, sample_ingestion_request):
        """Test successful data ingestion."""
        # Mock data collection
        ingestion_service.data_collector.collect_data = AsyncMock(
            return_value=Mock()
        )
        
        # Mock data processing
        ingestion_service.data_processor.process_data = AsyncMock(
            return_value=Mock()
        )
        
        # Mock data validation
        ingestion_service.data_validator.validate_data = AsyncMock(
            return_value=Mock(is_valid=True)
        )
        
        # Mock data transformation
        ingestion_service.data_transformer.transform_data = AsyncMock(
            return_value=Mock()
        )
        
        # Mock data enrichment
        ingestion_service.data_enricher.enrich_data = AsyncMock(
            return_value=Mock()
        )
        
        # Mock data routing
        ingestion_service.data_router.route_data = AsyncMock(
            return_value=Mock()
        )
        
        # Mock AIM-OS integrations
        ingestion_service.tcs.stream_ingestion_event = AsyncMock()
        ingestion_service._store_ingestion_data_in_cmc = AsyncMock()
        ingestion_service._track_ingestion_provenance = AsyncMock()
        ingestion_service._synthesize_ingestion_knowledge = AsyncMock()
        ingestion_service._enhance_ingestion_with_iis = AsyncMock()
        
        # Execute ingestion
        response = await ingestion_service.ingest_data(sample_ingestion_request)
        
        # Assertions
        assert response is not None
        assert response.source_config == sample_ingestion_request.source_config
        assert response.ingestion_time is not None
        
        # Verify AIM-OS integrations were called
        ingestion_service.tcs.stream_ingestion_event.assert_called_once()
        ingestion_service._store_ingestion_data_in_cmc.assert_called_once()
        ingestion_service._track_ingestion_provenance.assert_called_once()
        ingestion_service._synthesize_ingestion_knowledge.assert_called_once()
        ingestion_service._enhance_ingestion_with_iis.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ingest_batch_success(self, ingestion_service):
        """Test successful batch ingestion."""
        # Mock individual ingestion calls
        ingestion_service.ingest_data = AsyncMock(
            return_value=Mock()
        )
        
        # Execute batch ingestion
        requests = [
            IngestionRequest(
                source_config=SourceConfig(
                    source_id="repo1",
                    source_type="git",
                    url="https://github.com/test/repo1.git"
                ),
                routing_config={}
            ),
            IngestionRequest(
                source_config=SourceConfig(
                    source_id="repo2",
                    source_type="git",
                    url="https://github.com/test/repo2.git"
                ),
                routing_config={}
            )
        ]
        
        responses = await ingestion_service.ingest_batch(requests)
        
        # Assertions
        assert len(responses) == 2
        assert ingestion_service.ingest_data.call_count == 2
    
    @pytest.mark.asyncio
    async def test_ingest_data_validation_error(self, ingestion_service, sample_ingestion_request):
        """Test data ingestion with validation error."""
        # Mock data collection
        ingestion_service.data_collector.collect_data = AsyncMock(
            return_value=Mock()
        )
        
        # Mock data validation to fail
        ingestion_service.data_validator.validate_data = AsyncMock(
            return_value=Mock(is_valid=False, errors=["Invalid data format"])
        )
        
        # Execute ingestion and expect exception
        with pytest.raises(DataValidationError, match="Data validation failed"):
            await ingestion_service.ingest_data(sample_ingestion_request)
```

This L3 detailed implementation guide provides comprehensive technical details for implementing the Data Ingestion Layer with full AIM-OS integration, including complete code examples, testing strategies, and performance optimizations.
