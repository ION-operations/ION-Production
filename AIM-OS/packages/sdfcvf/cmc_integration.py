"""CMC Integration for SDF-CVF

Enables storage and retrieval of quartet/quintet parity results, evolution artifacts,
and trace data in CMC (Context Memory Core).

Integration Points:
- Store parity results as CMC atoms
- Store quartet/quintet snapshots for bitemporal tracking
- Retrieve historical parity data for trend analysis
- Validate schema consistency with CMC
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

# CMC imports (optional)
try:
    from cmc_service import MemoryStore
    from cmc_service.models import AtomCreate, AtomContent
    CMC_AVAILABLE = True
except ImportError:
    # Fallback for environments without CMC
    CMC_AVAILABLE = False
    MemoryStore = None
    AtomCreate = None
    AtomContent = None

# Note: CMC integration uses simplified implementations for some methods:
# - retrieve_parity_history: Returns empty list (line 216) - would use CMC query API in production
# - validate_schema: Basic structure check only (line 248) - would use CMC schema validation in production


@dataclass
class ParityAtom:
    """Represents a parity result stored in CMC"""
    atom_id: str
    parity_score: float
    quartet_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class CMCIntegration:
    """Integrates SDF-CVF with CMC for parity storage and retrieval.
    
    Provides:
    - Parity result storage (atoms)
    - Quartet/quintet snapshot storage (bitemporal tracking)
    - Historical parity retrieval (trend analysis)
    - Schema validation (consistency checks)
    """
    
    def __init__(self, cmc_store: Optional[Any] = None):
        """
        Initialize CMC integration.
        
        Args:
            cmc_store: CMC MemoryStore instance (optional, for testing can be None)
        """
        self.cmc_available = CMC_AVAILABLE
        self.cmc = cmc_store
        
        if not self.cmc_available:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("CMC integration disabled: CMC package not available")
    
    def store_parity_result(
        self,
        parity_result: Any,  # ParityResult or QuintetParityResult
        quartet_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Store parity result in CMC as atom.
        
        Used by parityCalculator subsystem to store parity metadata.
        
        Args:
            parity_result: ParityResult or QuintetParityResult instance
            quartet_id: Unique identifier for the quartet
            metadata: Optional additional metadata
            
        Returns:
            CMC atom ID if successful, None if CMC not available
        """
        if not self.cmc_available or not self.cmc:
            return None
        
        try:
            # Convert parity result to atom payload
            parity_dict = parity_result.to_dict() if hasattr(parity_result, 'to_dict') else {
                "parity_score": getattr(parity_result, 'parity_score', 0.0),
                "complete": getattr(parity_result, 'complete', False),
            }
            
            # Create atom payload
            payload = AtomCreate(
                modality="parity_result",
                content=AtomContent(
                    inline=f"Parity result for quartet {quartet_id}: {parity_dict.get('parity_score', 0.0):.3f}"
                ),
                tags={
                    "parity_score": parity_dict.get('parity_score', 0.0),
                    "quartet_id": quartet_id,
                    "complete": parity_dict.get('complete', False),
                    "system": "sdfcvf"
                },
                metadata={
                    "parity_result": parity_dict,
                    "quartet_id": quartet_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            )
            
            # Store in CMC
            atom = self.cmc.create_atom(payload, correlation_id=f"sdfcvf-parity-{quartet_id}")
            
            return atom.id
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error storing parity result in CMC: {e}")
            return None
    
    def store_quartet_snapshot(
        self,
        quartet: Any,  # Quartet or Quintet
        snapshot_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Store quartet/quintet snapshot in CMC for bitemporal tracking.
        
        Used by quartetValidator subsystem to store trace data.
        
        Args:
            quartet: Quartet or Quintet instance
            snapshot_id: Unique identifier for the snapshot
            metadata: Optional additional metadata
            
        Returns:
            CMC atom ID if successful, None if CMC not available
        """
        if not self.cmc_available or not self.cmc:
            return None
        
        try:
            # Convert quartet to atom payload
            quartet_dict = quartet.to_dict() if hasattr(quartet, 'to_dict') else {
                "code_files": getattr(quartet, 'code', []),
                "docs_files": getattr(quartet, 'docs', []),
                "tests_files": getattr(quartet, 'tests', []),
                "traces_files": getattr(quartet, 'traces', []),
            }
            
            # Create atom payload
            payload = AtomCreate(
                modality="quartet_snapshot",
                content=AtomContent(
                    inline=f"Quartet snapshot {snapshot_id}: {len(quartet_dict.get('code_files', []))} code files"
                ),
                tags={
                    "snapshot_id": snapshot_id,
                    "system": "sdfcvf",
                    "quartet_type": "quintet" if hasattr(quartet, 'nl_tags') else "quartet"
                },
                metadata={
                    "quartet": quartet_dict,
                    "snapshot_id": snapshot_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            )
            
            # Store in CMC
            atom = self.cmc.create_atom(payload, correlation_id=f"sdfcvf-snapshot-{snapshot_id}")
            
            return atom.id
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error storing quartet snapshot in CMC: {e}")
            return None
    
    def retrieve_parity_history(
        self,
        quartet_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ParityAtom]:
        """
        Retrieve historical parity results from CMC.
        
        Used for trend analysis and evolution tracking.
        
        Args:
            quartet_id: Optional quartet ID to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of ParityAtom instances
        """
        if not self.cmc_available or not self.cmc:
            return []
        
        try:
            # Query CMC for parity atoms
            # Note: This is a simplified implementation
            # In production, would use CMC query API with filters
            query_tags = {"system": "sdfcvf"}
            if quartet_id:
                query_tags["quartet_id"] = quartet_id
            
            # For now, return empty list (would implement actual CMC query)
            # atoms = self.cmc.query_atoms(tags=query_tags, limit=limit)
            
            return []
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error retrieving parity history from CMC: {e}")
            return []
    
    def validate_schema(
        self,
        data: Dict[str, Any],
        schema_type: str = "parity_result"
    ) -> Dict[str, Any]:
        """
        Validate data schema using CMC validation.
        
        Used for consistency checks.
        
        Args:
            data: Data to validate
            schema_type: Type of schema to validate against
            
        Returns:
            Validation result with 'valid' and 'errors' fields
        """
        if not self.cmc_available:
            return {
                "valid": False,
                "error": "CMC not available",
                "errors": []
            }
        
        try:
            # Simplified validation (would use actual CMC schema validation)
            # For now, basic structure check
            if schema_type == "parity_result":
                required_fields = ["parity_score", "complete"]
                missing = [field for field in required_fields if field not in data]
                
                if missing:
                    return {
                        "valid": False,
                        "errors": [f"Missing required fields: {missing}"],
                        "schema_type": schema_type
                    }
            
            return {
                "valid": True,
                "errors": [],
                "schema_type": schema_type
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error validating schema with CMC: {e}")
            return {
                "valid": False,
                "error": str(e),
                "errors": []
            }

