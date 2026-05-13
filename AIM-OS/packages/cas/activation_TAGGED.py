"""Activation Tracking Component for CAS

Monitors which principles, documents, and concepts are "hot" (actively used) versus 
"cold" (available but inactive) in the AI's working attention.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import math
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
# NL_TAG: VIF-MODEL-001 | Snapshot of what's active in AI's attention. | class ActivationState | []
class ActivationState:
    """
    Snapshot of what's active in AI's attention.
    
    Tracks activation levels for principles, documents, and concepts
    based on recency, frequency, salience, and cognitive load.
    """
    timestamp: datetime
    session_id: str
    
    # Activation levels (0.0 = completely cold, 1.0 = maximally hot)
    principles_activation: Dict[str, float] = field(default_factory=dict)
    documents_activation: Dict[str, float] = field(default_factory=dict)
    concepts_activation: Dict[str, float] = field(default_factory=dict)
    
    # Context metadata
    recent_operations: List[str] = field(default_factory=list)
    documents_read: List[Tuple[str, datetime]] = field(default_factory=list)
    time_since_read: Dict[str, timedelta] = field(default_factory=dict)
    
    # Cognitive load impact
    working_attention_items: int = 0
    context_size_tokens: int = 0
    load_level: float = 0.0
    
    def is_hot(self, principle: str, threshold: float = 0.7) -> bool:
        """Check if principle is actively hot."""
        return self.principles_activation.get(principle, 0.0) >= threshold
    
    def is_cold(self, principle: str, threshold: float = 0.3) -> bool:
        """Check if principle is cold."""
        return self.principles_activation.get(principle, 0.0) < threshold
    
    def get_cold_but_needed(self, required: List[str]) -> List[str]:
        """Identify principles that are required but not activated."""
        return [p for p in required if self.is_cold(p)]


# NL_TAG: VIF-MODEL-002 | Tracks and calculates activation levels for principles/concepts/documents. | class ActivationTracker | []
class ActivationTracker:
    # NL_TAG: VIF-UTIL-001 | Check if principle is actively hot. | is_hot(self, principle, threshold) | []
    def is_hot(self, principle: str, threshold: float = 0.7) -> bool:
        """Check if principle is actively hot."""
        return self.principles_activation.get(principle, 0.0) >= threshold
    
    # NL_TAG: VIF-UTIL-002 | Check if principle is cold. | is_cold(self, principle, threshold) | []
    def is_cold(self, principle: str, threshold: float = 0.3) -> bool:
        """Check if principle is cold."""
        return self.principles_activation.get(principle, 0.0) < threshold
    
    # NL_TAG: VIF-UTIL-003 | Identify principles that are required but not activated. | get_cold_but_needed(self, required) | []
    def get_cold_but_needed(self, required: List[str]) -> List[str]:
        """Identify principles that are required but not activated."""
        return [p for p in required if self.is_cold(p)]


class ActivationTracker:
    """
    Tracks and calculates activation levels for principles/concepts/documents.
    
    Uses temporal decay, usage frequency, semantic salience, and cognitive load
    to estimate what's currently "hot" in AI's working attention.
    """
    
    # NL_TAG: VIF-UTIL-004 |   init   | __init__(self, session_id) | []
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.usage_history: Dict[str, List[datetime]] = {}
        self.last_access: Dict[str, datetime] = {}
        self.semantic_embeddings: Dict[str, List[float]] = {}
        
    # NL_TAG: VIF-UTIL-005 | Record that a principle was just used. | record_principle_use(self, principle) | []
    def record_principle_use(self, principle: str):
        """Record that a principle was just used."""
        now = datetime.utcnow()
        if principle not in self.usage_history:
            self.usage_history[principle] = []
        self.usage_history[principle].append(now)
        self.last_access[principle] = now
        logger.debug(f"Recorded principle use: {principle}")
    
    # NL_TAG: VIF-UTIL-006 | Record that a document was just read. | record_document_read(self, doc_path) | []
    def record_document_read(self, doc_path: str):
        """Record that a document was just read."""
        now = datetime.utcnow()
        if doc_path not in self.usage_history:
            self.usage_history[doc_path] = []
        self.usage_history[doc_path].append(now)
        self.last_access[doc_path] = now
        logger.debug(f"Recorded document read: {doc_path}")
    
    # NL_TAG: VIF-UTIL-007 | Calculate activation level for an item (principle/doc/concept). | calculate_activation(self, item, current_task, cognitive_load) | []
    def calculate_activation(
        self,
        item: str,
        current_task: Optional[str] = None,
        cognitive_load: float = 0.0
    ) -> float:
        """
        Calculate activation level for an item (principle/doc/concept).
        
        Formula: A = (R * Fr * S) * L_penalty
        where:
            R = Recency score (1.0 / (1 + minutes_since_use))
            Fr = Frequency score (uses_this_session / total_ops)
            S = Salience score (semantic_similarity to current_task)
            L_penalty = Load penalty (high load suppresses distant items)
        
        Args:
            item: Principle, document, or concept to calculate for
            current_task: Description of current task (for salience)
            cognitive_load: Current cognitive load (0.0-1.0)
            
        Returns:
            Activation level (0.0-1.0)
        """
        # Recency component
        if item not in self.last_access:
            return 0.0  # Never used = not activated
        
        minutes_since = (datetime.utcnow() - self.last_access[item]).total_seconds() / 60
        recency_score = 1.0 / (1.0 + minutes_since)
        
        # Frequency component
        uses_this_session = len(self.usage_history.get(item, []))
        total_operations = sum(len(hist) for hist in self.usage_history.values())
        frequency_score = uses_this_session / max(1, total_operations)
        
        # Salience component (semantic similarity to current task)
        if current_task and item in self.semantic_embeddings:
            task_embedding = self._embed_text(current_task)
            item_embedding = self.semantic_embeddings[item]
            salience_score = self._cosine_similarity(task_embedding, item_embedding)
        else:
            salience_score = 0.5  # Neutral if no task context
        
        # Cognitive load penalty (high load suppresses distant items)
        load_penalty = 1.0 - (cognitive_load * 0.5)  # Max 50% suppression
        
        # Combine components
        activation = (
            0.4 * recency_score +
            0.3 * frequency_score +
            0.2 * salience_score
        ) * load_penalty
        
        return min(1.0, activation)
    
    # NL_TAG: VIF-UTIL-008 | Capture current activation state snapshot. | capture_state(self, current_task, cognitive_load, context_tokens) | []
    def capture_state(
        self,
        current_task: Optional[str] = None,
        cognitive_load: float = 0.0,
        context_tokens: int = 0
    ) -> ActivationState:
        """
        Capture current activation state snapshot.
        
        Returns complete ActivationState with all activation levels calculated.
        """
        # Define known principles (from AIM-OS systems)
        known_principles = [
            "CMC_bitemporal", "CMC_atoms", "CMC_snapshots",
            "HHNI_retrieval", "HHNI_DVNS", "HHNI_hierarchy",
            "VIF_provenance", "VIF_confidence", "VIF_witness",
            "SEG_graph", "SEG_contradictions",
            "APOE_orchestration", "APOE_ACL", "APOE_gates",
            "SDF_quartet", "SDF_parity", "SDF_gates",
            "CAS_introspection", "CAS_failure_modes"
        ]
        
        # Calculate activations
        principles_activation = {
            p: self.calculate_activation(p, current_task, cognitive_load)
            for p in known_principles
        }
        
        # Calculate for recently read documents
        documents_activation = {
            doc: self.calculate_activation(doc, current_task, cognitive_load)
            for doc, _ in self.last_access.items()
            if "/" in doc  # Filter for paths
        }
        
        # Count working attention items (activation > 0.5)
        working_items = sum(1 for a in principles_activation.values() if a > 0.5)
        
        return ActivationState(
            timestamp=datetime.utcnow(),
            session_id=self.session_id,
            principles_activation=principles_activation,
            documents_activation=documents_activation,
            recent_operations=list(self.usage_history.keys())[-10:],
            documents_read=[(doc, ts) for doc, ts in self.last_access.items() if "/" in doc],
            time_since_read={
                item: datetime.utcnow() - ts 
                for item, ts in self.last_access.items()
            },
            working_attention_items=working_items,
            context_size_tokens=context_tokens,
            load_level=cognitive_load
        )
    
    @staticmethod
    # NL_TAG: VIF-UTIL-009 | Calculate cosine similarity between vectors. | _cosine_similarity(vec1, vec2) | []
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    @staticmethod
    # NL_TAG: VIF-UTIL-010 | Generate embedding for text. | _embed_text(text) | []
    def _embed_text(text: str) -> List[float]:
        """
        Generate embedding for text.
        
        In production, use sentence-transformers or similar.
        For testing, use simple hash-based embedding.
        """
        # Simple hash-based embedding for testing
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to float vector (normalized)
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                value = int.from_bytes(chunk, 'big') / (2**32)
                embedding.append(value)
        
        # Pad to fixed size
        while len(embedding) < 16:
            embedding.append(0.0)
        
        return embedding[:16]
    
    # NL_TAG: VIF-UTIL-011 | Generate warnings for potential activation issues. | get_activation_warnings(self, state) | []
    def get_activation_warnings(self, state: ActivationState) -> List[str]:
        """
        Generate warnings for potential activation issues.
        
        Returns list of warning messages for cold but needed principles.
        """
        warnings = []
        
        # Check for cold but needed principles
        critical_principles = [
            "CMC_bitemporal", "VIF_provenance", "SDF_quartet"
        ]
        
        for principle in critical_principles:
            if state.is_cold(principle) and principle in state.principles_activation:
                warnings.append(f"Critical principle '{principle}' is cold (activation: {state.principles_activation[principle]:.2f})")
        
        # Check for high cognitive load
        if state.load_level > 0.8:
            warnings.append(f"High cognitive load detected: {state.load_level:.2f}")
        
        # Check for too many working items
        if state.working_attention_items > 10:
            warnings.append(f"Too many working attention items: {state.working_attention_items}")
        
        return warnings
